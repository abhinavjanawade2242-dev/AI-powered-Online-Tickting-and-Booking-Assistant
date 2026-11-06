import asyncio
from datetime import datetime, timedelta
import pytest
from sqlalchemy import select
from app.models import TicketTier
from app.schemas import BookingReservationRequest
from app.services.booking_service import BookingService
from app.services.concurrency import InsufficientInventoryError
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_anti_overbooking_concurrency(db_session, sample_event_data):
    """
    Stress test anti-overbooking logic:
    Only 5 VIP tickets are available.
    Simulate 20 concurrent customer requests attempting to reserve 1 ticket each.
    Verifies that EXACTLY 5 reservations succeed and 15 are cleanly rejected.
    """
    tier_vip = sample_event_data["tier_vip"]
    event = sample_event_data["event"]
    tier_id = tier_vip.id
    event_id = event.id
    total_available = tier_vip.available_quantity  # 5

    num_concurrent_users = 20
    successful_bookings = []
    rejected_bookings = []

    async def attempt_booking(user_idx: int):
        req = BookingReservationRequest(
            event_id=event_id,
            tier_id=tier_id,
            quantity=1,
            customer_name=f"Customer {user_idx}",
            customer_email=f"customer{user_idx}@example.com"
        )
        async with TestingSessionLocal() as session:
            try:
                booking = await BookingService.reserve_tickets_atomic(session, req)
                successful_bookings.append(booking.booking_reference)
            except InsufficientInventoryError:
                rejected_bookings.append(user_idx)

    tasks = [attempt_booking(i) for i in range(num_concurrent_users)]
    await asyncio.gather(*tasks)

    # Invariants
    assert len(successful_bookings) == total_available, f"Expected exactly {total_available} successful bookings, got {len(successful_bookings)}"
    assert len(rejected_bookings) == (num_concurrent_users - total_available)

    # Check database state
    async with TestingSessionLocal() as session:
        stmt = select(TicketTier).where(TicketTier.id == tier_id)
        result = await session.execute(stmt)
        updated_tier = result.scalar_one()
        assert updated_tier.available_quantity == 0, f"Available quantity should be 0, got {updated_tier.available_quantity}"


@pytest.mark.asyncio
async def test_booking_cancellation_restores_inventory(db_session, sample_event_data):
    """
    Test Stage 7 post-booking cancellation:
    Verifies that cancelling a booking safely returns inventory to the pool.
    """
    tier_vip = sample_event_data["tier_vip"]
    event = sample_event_data["event"]
    initial_inventory = tier_vip.available_quantity  # 5

    # Reserve 2 tickets
    req = BookingReservationRequest(
        event_id=event.id,
        tier_id=tier_vip.id,
        quantity=2,
        customer_name="Alice Smith",
        customer_email="alice@example.com"
    )
    booking = await BookingService.reserve_tickets_atomic(db_session, req)
    confirmed = await BookingService.confirm_booking(db_session, booking.booking_reference)
    assert confirmed.status == "CONFIRMED"
    assert len(confirmed.tickets) == 2

    # Verify inventory decremented to 3
    stmt = select(TicketTier).where(TicketTier.id == tier_vip.id)
    res = await db_session.execute(stmt)
    tier = res.scalar_one()
    assert tier.available_quantity == initial_inventory - 2

    # Cancel booking
    cancelled = await BookingService.cancel_booking(
        db_session,
        booking_reference=booking.booking_reference,
        reason="Schedule conflict"
    )
    assert cancelled.status == "CANCELLED"
    assert cancelled.refund_status == "REFUNDED"
    assert float(cancelled.refund_amount) == float(confirmed.total_amount)

    # Verify inventory is restored back to initial 5
    res = await db_session.execute(stmt)
    tier_after = res.scalar_one()
    assert tier_after.available_quantity == initial_inventory


@pytest.mark.asyncio
async def test_cancellation_rejected_within_24_hours(db_session, sample_event_data):
    """
    Test 24-hour boundary condition:
    Confirmed bookings cannot be cancelled if the event starts in less than 24 hours.
    """
    tier_vip = sample_event_data["tier_vip"]
    event = sample_event_data["event"]

    # Temporarily move event start time to 12 hours in the future (< 24 hours)
    event.start_time = datetime.utcnow() + timedelta(hours=12)
    event.end_time = datetime.utcnow() + timedelta(hours=15)
    await db_session.commit()

    req = BookingReservationRequest(
        event_id=event.id,
        tier_id=tier_vip.id,
        quantity=1,
        customer_name="Bob Jones",
        customer_email="bob@example.com"
    )
    booking = await BookingService.reserve_tickets_atomic(db_session, req)
    confirmed = await BookingService.confirm_booking(db_session, booking.booking_reference)
    assert confirmed.status == "CONFIRMED"

    # Attempting to cancel within 24h boundary must fail
    with pytest.raises(ValueError) as exc_info:
        await BookingService.cancel_booking(
            db_session,
            booking_reference=booking.booking_reference,
            reason="Last minute change"
        )
    assert "Cancellations are only permitted at least 24 hours prior" in str(exc_info.value)

