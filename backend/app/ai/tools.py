import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import BookingReservationRequest
from app.services.event_service import EventService
from app.services.inventory_service import InventoryService
from app.services.booking_service import BookingService
from app.services.concurrency import InsufficientInventoryError, LockAcquisitionError

logger = logging.getLogger("ticketing.ai.tools")


class AgentTools:
    """
    Executes domain tools corresponding to the 7-stage workflow.
    Can be invoked by LangChain tool handlers or native LLM agents.
    """

    @staticmethod
    async def search_events_and_venues(
        db: AsyncSession,
        query: Optional[str] = None,
        city: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Stage 1 & 2: Search events and venues based on keywords, city, or genre."""
        events = await EventService.search_events(
            db=db,
            query=query,
            city=city,
            category=category,
            limit=5
        )

        if not events:
            # Fallback to recommendations
            events = await EventService.get_recommendations(db=db, category=category, city=city, limit=3)

        results = []
        for e in events:
            min_price = min([float(t.price) for t in e.ticket_tiers]) if e.ticket_tiers else 0.0
            results.append({
                "event_id": e.id,
                "title": e.title,
                "category": e.category,
                "venue_name": e.venue.name if e.venue else "TBA",
                "city": e.venue.city if e.venue else "TBA",
                "start_time": e.start_time.strftime("%Y-%m-%d %H:%M"),
                "starting_price": f"₹{min_price:.2f}",
                "description": e.description[:120] + "..." if e.description and len(e.description) > 120 else e.description,
            })

        return {
            "found_count": len(results),
            "events": results
        }

    @staticmethod
    async def check_ticket_availability(
        db: AsyncSession,
        event_id: str
    ) -> Dict[str, Any]:
        """Stage 3: Check real-time seat inventory, tiers, and pricing for an event."""
        try:
            inventory = await InventoryService.get_event_inventory(db, event_id)
            tiers_data = []
            for t in inventory["tiers"]:
                tiers_data.append({
                    "tier_id": t.tier_id,
                    "tier_name": t.name,
                    "price": f"₹{t.price:.2f}",
                    "available_quantity": t.available_quantity,
                    "status": "Sold Out" if t.is_sold_out else f"{t.available_quantity} remaining",
                })

            return {
                "event_id": inventory["event_id"],
                "event_title": inventory["title"],
                "total_available_tickets": inventory["total_available_tickets"],
                "tiers": tiers_data
            }
        except Exception as e:
            logger.error("Failed to check inventory for %s: %s", event_id, e)
            return {"error": str(e)}

    @staticmethod
    async def reserve_and_book_tickets(
        db: AsyncSession,
        event_id: str,
        tier_id: str,
        quantity: int,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Stage 4 & 5: Reserve and Book.
        Atomically acquires distributed lock, decrements inventory, and confirms booking.
        """
        try:
            req = BookingReservationRequest(
                event_id=event_id,
                tier_id=tier_id,
                quantity=quantity,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
            )
            # Step 1: Atomic reservation with distributed lock
            booking = await BookingService.reserve_tickets_atomic(db, req)

            # Step 2: Auto-confirm and issue digital tickets
            confirmed_booking = await BookingService.confirm_booking(
                db,
                booking_reference=booking.booking_reference
            )

            tickets = [
                {
                    "ticket_code": t.ticket_code,
                    "seat_number": t.seat_number,
                    "status": t.status,
                }
                for t in confirmed_booking.tickets
            ]

            return {
                "success": True,
                "booking_reference": confirmed_booking.booking_reference,
                "status": confirmed_booking.status,
                "event_id": confirmed_booking.event_id,
                "tier_name": confirmed_booking.ticket_tier.name,
                "quantity": confirmed_booking.quantity,
                "total_amount": f"₹{float(confirmed_booking.total_amount):.2f} {confirmed_booking.currency}",
                "customer": {
                    "name": confirmed_booking.user.full_name,
                    "email": confirmed_booking.user.email
                },
                "tickets": tickets,
                "message": f"Successfully confirmed! Your booking reference is {confirmed_booking.booking_reference}."
            }
        except InsufficientInventoryError as e:
            return {"success": False, "error": "INSUFFICIENT_INVENTORY", "message": str(e)}
        except LockAcquisitionError as e:
            return {"success": False, "error": "HIGH_CONCURRENCY_LOCK_TIMEOUT", "message": str(e)}
        except Exception as e:
            logger.error("Booking error: %s", e)
            return {"success": False, "error": "BOOKING_ERROR", "message": str(e)}

    @staticmethod
    async def get_booking_details(
        db: AsyncSession,
        booking_reference: str
    ) -> Dict[str, Any]:
        """Stage 7: Retrieve booking and digital ticket status."""
        booking = await BookingService.get_booking_by_reference(db, booking_reference.strip().upper())
        if not booking:
            return {
                "found": False,
                "message": f"No booking found matching reference '{booking_reference}'."
            }

        tickets = [
            {
                "ticket_code": t.ticket_code,
                "seat_number": t.seat_number,
                "status": t.status,
                "qr_payload": t.qr_payload
            }
            for t in booking.tickets
        ]

        return {
            "found": True,
            "booking_reference": booking.booking_reference,
            "status": booking.status,
            "event_title": booking.event.title,
            "start_time": booking.event.start_time.strftime("%Y-%m-%d %H:%M"),
            "venue_name": booking.event.venue.name if booking.event.venue else "N/A",
            "tier_name": booking.ticket_tier.name,
            "quantity": booking.quantity,
            "total_amount": f"₹{float(booking.total_amount):.2f}",
            "customer_name": booking.user.full_name,
            "tickets": tickets
        }

    @staticmethod
    async def cancel_booking(
        db: AsyncSession,
        booking_reference: str,
        reason: Optional[str] = "Customer request"
    ) -> Dict[str, Any]:
        """Stage 7: Cancel booking and release tickets back to inventory."""
        try:
            booking = await BookingService.cancel_booking(
                db,
                booking_reference=booking_reference.strip().upper(),
                reason=reason
            )
            return {
                "success": True,
                "booking_reference": booking.booking_reference,
                "status": booking.status,
                "quantity_released": booking.quantity,
                "message": f"Booking {booking.booking_reference} has been cancelled. {booking.quantity} ticket(s) returned to inventory."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Could not cancel booking: {str(e)}"
            }

