import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import generate_booking_reference, generate_ticket_code, generate_qr_payload
from app.models import Booking, TicketTier, Event, User, DigitalTicket
from app.schemas import BookingReservationRequest, BookingResponse, DigitalTicketResponse, CustomerResponse
from app.services.business_rules import BusinessRulesEngine
from app.services.pricing_service import PricingService
from app.services.concurrency import (
    distributed_lock,
    acquire_ticket_tier_for_update,
    InsufficientInventoryError,
)

logger = logging.getLogger("ticketing.booking_service")


class BookingService:

    @staticmethod
    async def get_or_create_user(
        db: AsyncSession,
        email: str,
        full_name: str,
        phone: Optional[str] = None
    ) -> User:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                email=email,
                full_name=full_name,
                phone=phone
            )
            db.add(user)
            await db.flush()
        else:
            # Update user profile information if provided
            if full_name:
                user.full_name = full_name
            if phone:
                user.phone = phone
            await db.flush()

        return user

    @staticmethod
    async def reserve_tickets_atomic(
        db: AsyncSession,
        req: BookingReservationRequest
    ) -> Booking:
        """
        Stage 4 & 5: Selection & Booking.
        Atomically checks inventory, acquires distributed Redis lock + DB row lock,
        decrements available count, and establishes a temporary reservation hold.
        """
        # 0. Validate business rules (e.g., ticket limits per booking)
        BusinessRulesEngine.validate_ticket_quantity(req.quantity)

        lock_resource = f"tier:{req.tier_id}"

        # 1. Acquire Distributed Redis Lock
        async with distributed_lock(
            resource_key=lock_resource,
            timeout_seconds=settings.LOCK_EXPIRY_SECONDS,
            blocking_timeout_seconds=5.0
        ):
            # 2. Acquire Relational Row-Level Lock (FOR UPDATE)
            tier = await acquire_ticket_tier_for_update(db, req.tier_id)

            if tier.event_id != req.event_id:
                raise ValueError("Tier ID does not belong to the specified event ID.")

            # Validate currency constraint
            BusinessRulesEngine.validate_currency(tier.currency)

            # 3. Strict Anti-Overbooking verification
            if tier.available_quantity < req.quantity:
                logger.warning(
                    "Insufficient inventory for tier %s: requested %s, available %s",
                    tier.name, req.quantity, tier.available_quantity
                )
                raise InsufficientInventoryError(
                    f"Only {tier.available_quantity} tickets available for {tier.name}. Requested {req.quantity}."
                )

            # 4. Atomic inventory decrement
            tier.available_quantity -= req.quantity
            tier.version += 1
            await db.flush()

            # 5. Create or retrieve Customer
            user = await BookingService.get_or_create_user(
                db,
                email=req.customer_email,
                full_name=req.customer_name,
                phone=req.customer_phone
            )

            # 6. Calculate transparent pricing quote (supports promo code, group discounts)
            price_quote = PricingService.calculate_quote(
                unit_price=float(tier.price),
                quantity=req.quantity,
                promo_code=getattr(req, "promo_code", None)
            )

            # 7. Create Booking in PENDING state with configurable hold expiration
            booking_ref = generate_booking_reference()
            hold_expires_at = BusinessRulesEngine.calculate_hold_expiration(settings.HOLD_DURATION_MINUTES)

            booking = Booking(
                booking_reference=booking_ref,
                user_id=user.id,
                event_id=req.event_id,
                tier_id=req.tier_id,
                quantity=req.quantity,
                unit_price=tier.price,
                total_amount=price_quote.total_payable,
                currency=tier.currency,
                status="PENDING",
                hold_expires_at=hold_expires_at,
            )
            db.add(booking)
            await db.commit()
            await db.refresh(booking)

            logger.info(
                "Successfully reserved %d tickets for booking ref %s (Hold until %s)",
                req.quantity, booking.booking_reference, hold_expires_at.isoformat()
            )
            return booking

    @staticmethod
    async def confirm_booking(
        db: AsyncSession,
        booking_reference: str,
        payment_reference: Optional[str] = None
    ) -> Booking:
        """
        Stage 6: Confirmation.
        Validates reservation hold, flips status to CONFIRMED, and issues digital tickets with QR payloads.
        """
        stmt = (
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.ticket_tier),
                selectinload(Booking.event),
                selectinload(Booking.tickets)
            )
            .where(Booking.booking_reference == booking_reference)
        )
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()

        if not booking:
            raise ValueError(f"Booking with reference {booking_reference} not found.")

        if booking.status == "CONFIRMED":
            return booking  # Idempotent response

        if booking.status != "PENDING":
            raise ValueError(f"Booking cannot be confirmed because status is '{booking.status}'.")

        # Check if reservation hold expired via BusinessRulesEngine
        is_valid_cb, cb_msg = BusinessRulesEngine.validate_payment_callback(booking.status, booking.hold_expires_at)
        if not is_valid_cb:
            booking.status = "EXPIRED"
            await db.commit()
            raise ValueError(cb_msg)

        # Finalize booking status
        booking.status = "CONFIRMED"
        booking.hold_expires_at = None

        # Issue digital tickets for the quantity booked (General Admission - no numbered seats)
        for _ in range(booking.quantity):
            ticket_code = generate_ticket_code()
            qr_payload = generate_qr_payload(
                ticket_code=ticket_code,
                booking_ref=booking.booking_reference,
                event_id=booking.event_id,
                tier_name=booking.ticket_tier.name,
            )

            ticket = DigitalTicket(
                ticket_code=ticket_code,
                booking_id=booking.id,
                tier_id=booking.tier_id,
                seat_number=None,  # General Admission: no numbered seat assigned
                qr_payload=qr_payload,
                status="ACTIVE",
                booking=booking,
            )
            db.add(ticket)

        await db.commit()
        refreshed_booking = await db.scalar(
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.ticket_tier),
                selectinload(Booking.event),
                selectinload(Booking.tickets)
            )
            .where(Booking.id == booking.id)
        )
        logger.info("Booking %s confirmed with %d digital tickets issued", booking.booking_reference, booking.quantity)
        return refreshed_booking or booking

    @staticmethod
    async def cancel_booking(
        db: AsyncSession,
        booking_reference: str,
        reason: Optional[str] = None
    ) -> Booking:
        """
        Stage 7: Post-booking Cancellation.
        Cancels booking, voids digital tickets, and atomically releases reserved seats back to available inventory.
        """
        stmt = (
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.ticket_tier),
                selectinload(Booking.event),
                selectinload(Booking.tickets)
            )
            .where(Booking.booking_reference == booking_reference)
        )
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()

        if not booking:
            raise ValueError(f"Booking reference {booking_reference} not found.")

        if booking.status == "CANCELLED":
            return booking

        if booking.status not in ["CONFIRMED", "PENDING"]:
            raise ValueError(f"Booking status is {booking.status}; cannot be cancelled.")

        # Enforce 24-hour cancellation policy for confirmed bookings via BusinessRulesEngine
        if booking.status == "CONFIRMED" and booking.event:
            is_eligible, policy_msg = BusinessRulesEngine.validate_cancellation_eligibility(booking.event.start_time)
            if not is_eligible:
                raise ValueError(policy_msg)

        was_confirmed = (booking.status == "CONFIRMED")

        # Distributed lock to safely restore inventory
        async with distributed_lock(
            resource_key=f"tier:{booking.tier_id}",
            timeout_seconds=settings.LOCK_EXPIRY_SECONDS
        ):
            tier = await acquire_ticket_tier_for_update(db, booking.tier_id)

            # Re-increment available inventory
            tier.available_quantity += booking.quantity
            tier.version += 1

            booking.status = "CANCELLED"
            booking.cancellation_reason = reason or "User requested cancellation"
            refund_amount, refund_status = BusinessRulesEngine.calculate_cancellation_refund(
                total_amount=booking.total_amount,
                is_eligible=was_confirmed
            )
            booking.refund_amount = refund_amount
            booking.refund_status = refund_status
            if was_confirmed:
                logger.info(
                    "100%% Sandbox refund of ₹%.2f issued for booking %s",
                    float(booking.total_amount),
                    booking.booking_reference
                )

            # Void issued digital tickets
            for tix in booking.tickets:
                tix.status = "CANCELLED"

            await db.commit()
            refreshed_booking = await db.scalar(
                select(Booking)
                .options(
                    selectinload(Booking.user),
                    selectinload(Booking.ticket_tier),
                    selectinload(Booking.event),
                    selectinload(Booking.tickets)
                )
                .where(Booking.id == booking.id)
            )

            logger.info(
                "Booking %s cancelled. Restored %d tickets to tier %s (New total: %d)",
                booking.booking_reference, booking.quantity, tier.name, tier.available_quantity
            )
            return refreshed_booking or booking

    @staticmethod
    async def get_booking_by_reference(
        db: AsyncSession,
        booking_reference: str
    ) -> Optional[Booking]:
        """Stage 7: Retrieve booking and digital tickets."""
        stmt = (
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.ticket_tier),
                selectinload(Booking.event),
                selectinload(Booking.tickets)
            )
            .where(Booking.booking_reference == booking_reference)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def expire_stale_reservations(db: AsyncSession) -> int:
        """
        Background maintenance job:
        Finds all PENDING bookings whose hold_expires_at has passed,
        releases held tickets back to inventory, and marks booking as EXPIRED.
        """
        now = datetime.utcnow()
        stmt = (
            select(Booking)
            .where(
                Booking.status == "PENDING",
                Booking.hold_expires_at < now
            )
        )
        result = await db.execute(stmt)
        expired_bookings = result.scalars().all()

        count = 0
        for booking in expired_bookings:
            try:
                async with distributed_lock(resource_key=f"tier:{booking.tier_id}", timeout_seconds=5):
                    tier = await acquire_ticket_tier_for_update(db, booking.tier_id)
                    tier.available_quantity += booking.quantity
                    booking.status = "EXPIRED"
                    await db.commit()
                    count += 1
            except Exception as e:
                logger.error("Failed to expire booking %s: %s", booking.booking_reference, e)
                await db.rollback()

        if count > 0:
            logger.info("Expired %d stale reservation holds and restored inventory.", count)
        return count

