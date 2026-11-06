from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.booking_service import BookingService
from app.services.concurrency import InsufficientInventoryError
from app.schemas import (
    BookingReservationRequest,
    OfflineSyncRequest,
    OfflineSyncResponse,
)

router = APIRouter(prefix="/offline", tags=["Offline Queue & Reconnection Synchronization"])


@router.post("/sync", response_model=OfflineSyncResponse, summary="Offline Queue Replay: Revalidate & Hold Seats")
async def sync_offline_booking(
    req: OfflineSyncRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Offline Queue Replay Endpoint.
    Submitted by client after network reconnection to revalidate and hold seats.
    - If inventory is available: atomically reserves tickets and returns a 10-minute hold.
    - If inventory is sold out: returns a clean REJECTED_SOLD_OUT status without booking creation.
    """
    try:
        reservation_req = BookingReservationRequest(
            event_id=req.event_id,
            tier_id=req.tier_id,
            quantity=req.quantity,
            customer_name=req.customer_name,
            customer_email=req.customer_email
        )
        booking = await BookingService.reserve_tickets_atomic(db=db, req=reservation_req)
        return OfflineSyncResponse(
            client_request_id=req.client_request_id,
            status="ACCEPTED_LOCKED",
            booking_reference=booking.booking_reference,
            hold_expires_at=booking.hold_expires_at,
            total_amount=float(booking.total_amount),
            currency=booking.currency,
            checkout_url=f"/web/checkout/{booking.booking_reference}",
            message="Reconnection successful. Tickets are held for 10 minutes. Please complete payment."
        )
    except InsufficientInventoryError:
        return OfflineSyncResponse(
            client_request_id=req.client_request_id,
            status="REJECTED_SOLD_OUT",
            message="Tickets sold out while you were offline. Please select another tier or event."
        )
    except Exception as e:
        return OfflineSyncResponse(
            client_request_id=req.client_request_id,
            status="REJECTED_INVALID",
            message=str(e)
        )

