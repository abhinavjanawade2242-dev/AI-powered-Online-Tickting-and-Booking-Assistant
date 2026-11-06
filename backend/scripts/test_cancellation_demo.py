import asyncio
from datetime import datetime, timedelta, timezone
from app.core.database import AsyncSessionLocal
from app.models import Event, TicketTier, Venue
from app.schemas import BookingReservationRequest
from app.services.booking_service import BookingService

async def test_cancellation_boundaries():
    import uuid
    run_id = str(uuid.uuid4())[:8]
    async with AsyncSessionLocal() as session:
        # Create venue
        v = Venue(id=f"v-canc-{run_id}", name="Cancellation Arena", city="Bengaluru", address="Electronic City", capacity=500)
        session.add(v)
        await session.flush()

        # Event A: Starts in 48 hours (Eligible for cancellation)
        start_48h = datetime.now(timezone.utc) + timedelta(hours=48)
        ev_48 = Event(
            id=f"ev-canc-48h-{run_id}",
            title="48H Advance Tech Summit",
            category="Technical",
            start_time=start_48h,
            end_time=start_48h + timedelta(hours=3),
            venue_id=v.id
        )
        t_48 = TicketTier(id=f"t-canc-48h-{run_id}", event_id=ev_48.id, name="Standard Pass", price=499.0, total_quantity=50, available_quantity=50)
        session.add_all([ev_48, t_48])

        # Event B: Starts in 12 hours (Ineligible for cancellation)
        start_12h = datetime.now(timezone.utc) + timedelta(hours=12)
        ev_12 = Event(
            id=f"ev-canc-12h-{run_id}",
            title="12H Imminent Concert",
            category="Cultural",
            start_time=start_12h,
            end_time=start_12h + timedelta(hours=3),
            venue_id=v.id
        )
        t_12 = TicketTier(id=f"t-canc-12h-{run_id}", event_id=ev_12.id, name="Standard Pass", price=499.0, total_quantity=50, available_quantity=50)
        session.add_all([ev_12, t_12])
        await session.commit()

        # 1. Book for Event A (>24h) and cancel
        req_a = BookingReservationRequest(
            event_id=ev_48.id,
            tier_id=t_48.id,
            quantity=1,
            customer_name="Adithya Gowda",
            customer_email="adithya@example.com"
        )
        b_a = await BookingService.reserve_tickets_atomic(session, req_a)
        await BookingService.confirm_booking(session, b_a.booking_reference)
        canc_a = await BookingService.cancel_booking(session, b_a.booking_reference, reason="Change of travel plans")
        print("=== CASE 1: CANCELLATION >= 24 HOURS (EVENT IN 48H) ===")
        print(f"Booking Ref: {canc_a.booking_reference}")
        print(f"Status: {canc_a.status}")
        print(f"Cancellation Reason: '{canc_a.cancellation_reason}'")
        print(f"Refund Status: {canc_a.refund_status}")
        print(f"Refund Amount: INR {canc_a.refund_amount} (100% full refund)")
        print(f"Inventory Restored: {t_48.available_quantity}/50")

        # 2. Book for Event B (<24h) and attempt cancel
        req_b = BookingReservationRequest(
            event_id=ev_12.id,
            tier_id=t_12.id,
            quantity=1,
            customer_name="Manohar QA",
            customer_email="manohar@example.com"
        )
        b_b = await BookingService.reserve_tickets_atomic(session, req_b)
        await BookingService.confirm_booking(session, b_b.booking_reference)
        print("\n=== CASE 2: CANCELLATION < 24 HOURS (EVENT IN 12H) ===")
        try:
            await BookingService.cancel_booking(session, b_b.booking_reference, reason="Last minute emergency")
            print("ERROR: Cancellation should have been rejected!")
        except ValueError as ex:
            print(f"Booking Ref: {b_b.booking_reference}")
            print("Cancellation Rejected with ValueError (Mapped to HTTP 400 Bad Request):")
            print(f"Rejection Reason: '{str(ex)}'")
            print(f"Status Remains: {b_b.status} (Booking not cancelled)")
            print(f"Inventory Preserved: {t_12.available_quantity}/50")

if __name__ == "__main__":
    asyncio.run(test_cancellation_boundaries())
