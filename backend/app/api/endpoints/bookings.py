from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Booking
from app.services.booking_service import BookingService
from app.services.concurrency import InsufficientInventoryError, LockAcquisitionError
from app.schemas import (
    BookingReservationRequest,
    BookingConfirmRequest,
    BookingCancelRequest,
    BookingCancelPathRequest,
    BookingResponse,
    DigitalTicketResponse,
    CustomerResponse,
    PaymentSimulationRequest,
    PaymentSimulationResponse,
    ApiResponse,
)

router = APIRouter(prefix="/bookings", tags=["Stage 4, 5, 6 & 7: Booking & Lifecycle"])


def _serialize_booking(booking) -> BookingResponse:
    customer_resp = None
    if booking.user:
        customer_resp = CustomerResponse(
            id=booking.user.id,
            full_name=booking.user.full_name,
            email=booking.user.email,
            phone=booking.user.phone,
            created_at=booking.user.created_at
        )

    tickets_resp = []
    if booking.tickets:
        tickets_resp = [
            DigitalTicketResponse(
                id=t.id,
                ticket_code=t.ticket_code,
                tier_id=t.tier_id,
                tier_name=booking.ticket_tier.name if booking.ticket_tier else None,
                qr_payload=t.qr_payload,
                status=t.status,
                issued_at=t.issued_at
            )
            for t in booking.tickets
        ]

    return BookingResponse(
        id=booking.id,
        booking_reference=booking.booking_reference,
        event_id=booking.event_id,
        event_title=booking.event.title if booking.event else None,
        tier_id=booking.tier_id,
        tier_name=booking.ticket_tier.name if booking.ticket_tier else None,
        quantity=booking.quantity,
        unit_price=float(booking.unit_price),
        total_amount=float(booking.total_amount),
        currency=booking.currency,
        status=booking.status,
        hold_expires_at=booking.hold_expires_at,
        cancellation_reason=booking.cancellation_reason,
        refund_amount=float(booking.refund_amount) if booking.refund_amount is not None else None,
        refund_status=booking.refund_status,
        customer=customer_resp,
        tickets=tickets_resp,
        created_at=booking.created_at
    )


@router.post("/reserve", response_model=BookingResponse, status_code=status.HTTP_201_CREATED, summary="Stage 4 & 5: Reserve Tickets with Anti-Overbooking Lock")
async def reserve_tickets(
    req: BookingReservationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Stage 4 & 5: Selection & Booking.
    - Distributed Lock prevents race conditions across instances.
    - Database row-level lock ensures atomic inventory decrement.
    - Establishes a temporary reservation hold (default: 10 minutes).
    """
    try:
        booking = await BookingService.reserve_tickets_atomic(db=db, req=req)
        # Fetch relationships for response
        refreshed = await BookingService.get_booking_by_reference(db, booking.booking_reference)
        return _serialize_booking(refreshed)
    except InsufficientInventoryError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except LockAcquisitionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/lock", response_model=BookingResponse, status_code=status.HTTP_201_CREATED, summary="Stage 4 & 5: Lock / Hold Inventory Alias")
async def lock_inventory_alias(
    req: BookingReservationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Stage 4 & 5: Selection & Booking.
    Alias endpoint for /reserve supporting quick inventory hold/locking.
    """
    return await reserve_tickets(req=req, db=db)


@router.post("/confirm", response_model=BookingResponse, summary="Stage 6: Confirm Booking & Generate Digital Tickets")
async def confirm_booking(
    req: BookingConfirmRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Stage 6: Confirmation.
    Validates the reservation hold, finalizes the order status to CONFIRMED,
    and generates unique digital tickets with gate-scan QR payloads.
    """
    try:
        booking = await BookingService.confirm_booking(
            db=db,
            booking_reference=req.booking_reference,
            payment_reference=req.payment_reference
        )
        return _serialize_booking(booking)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my-bookings", response_model=list[BookingResponse], summary="Retrieve booking history for authenticated user")
async def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Section 2.D: Retrieve authenticated user's personal booking history.
    """
    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.ticket_tier),
            selectinload(Booking.event),
            selectinload(Booking.tickets)
        )
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
    )
    result = await db.execute(stmt)
    bookings = result.scalars().all()
    return [_serialize_booking(b) for b in bookings]


@router.get("/{booking_reference}", response_model=BookingResponse, summary="Stage 7: Retrieve Booking & Digital Tickets")
async def get_booking(
    booking_reference: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Stage 7: Post-booking Retrieval.
    User can retrieve ticket details, track booking status, and view QR gate credentials.
    """
    booking = await BookingService.get_booking_by_reference(db, booking_reference.strip().upper())
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return _serialize_booking(booking)


@router.post("/{booking_reference}/payment-simulation", response_model=PaymentSimulationResponse, summary="Sandbox: Simulate Payment (SUCCESS, FAILURE, PENDING)")
async def simulate_payment(
    booking_reference: str,
    req: PaymentSimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Sandbox Payment Gateway Simulation Endpoint.
    - SUCCESS: Confirms booking, transitions status to CONFIRMED, and issues digital tickets.
    - FAILURE: Keeps reservation hold active, marks payment FAILED, allows customer to retry.
    - PENDING: Sets status to PAYMENT_PENDING, holding inventory until reconciliation.
    """
    booking = await BookingService.get_booking_by_reference(db, booking_reference.strip().upper())
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

    outcome = req.simulated_outcome.strip().upper()
    if outcome == "SUCCESS":
        try:
            confirmed = await BookingService.confirm_booking(
                db=db,
                booking_reference=booking.booking_reference,
                payment_reference=f"SIM-TXN-{req.payment_method}"
            )
            tickets_resp = [
                DigitalTicketResponse(
                    id=t.id,
                    ticket_code=t.ticket_code,
                    tier_id=t.tier_id,
                    tier_name=confirmed.ticket_tier.name if confirmed.ticket_tier else None,
                    qr_payload=t.qr_payload,
                    status=t.status,
                    issued_at=t.issued_at
                )
                for t in confirmed.tickets
            ]
            return PaymentSimulationResponse(
                booking_reference=confirmed.booking_reference,
                status=confirmed.status,
                payment_status="SUCCESS",
                simulated_outcome="SUCCESS",
                total_amount=float(confirmed.total_amount),
                currency=confirmed.currency,
                message="Sandbox payment successful. Booking confirmed and digital tickets issued.",
                tickets=tickets_resp
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    elif outcome == "FAILURE":
        return PaymentSimulationResponse(
            booking_reference=booking.booking_reference,
            status=booking.status,
            payment_status="FAILED",
            simulated_outcome="FAILURE",
            total_amount=float(booking.total_amount),
            currency=booking.currency,
            message="Sandbox payment failed or card was declined. You may retry while your hold remains active.",
            tickets=[]
        )

    elif outcome == "PENDING":
        booking.status = "PAYMENT_PENDING"
        await db.commit()
        return PaymentSimulationResponse(
            booking_reference=booking.booking_reference,
            status="PAYMENT_PENDING",
            payment_status="PENDING",
            simulated_outcome="PENDING",
            total_amount=float(booking.total_amount),
            currency=booking.currency,
            message="Payment outcome is pending gateway settlement. Inventory hold remains active.",
            tickets=[]
        )

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported outcome '{req.simulated_outcome}'. Must be SUCCESS, FAILURE, or PENDING.")


@router.post("/cancel", response_model=BookingResponse, summary="Stage 7: Cancel Booking & Release Inventory")
async def cancel_booking(
    req: BookingCancelRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Stage 7: Post-booking Cancellation.
    Atomically cancels booking, voids digital tickets, and safely returns held seats back to the ticket tier inventory.
    """
    try:
        booking = await BookingService.cancel_booking(
            db=db,
            booking_reference=req.booking_reference,
            reason=req.reason
        )
        return _serialize_booking(booking)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{booking_reference}/cancel", response_model=BookingResponse, summary="Stage 7: Cancel Booking via URL Path Alias")
async def cancel_booking_path_alias(
    booking_reference: str,
    req: Optional[BookingCancelPathRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Stage 7: Post-booking Cancellation.
    Alias endpoint allowing booking_reference in URL path.
    """
    reason = req.reason if req and req.reason else "Customer requested cancellation"
    try:
        booking = await BookingService.cancel_booking(
            db=db,
            booking_reference=booking_reference.strip().upper(),
            reason=reason
        )
        return _serialize_booking(booking)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

