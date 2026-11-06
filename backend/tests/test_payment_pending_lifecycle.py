
from datetime import datetime, timedelta

import pytest

from app.models import TicketTier
from app.services.booking_service import BookingService


async def create_test_booking(client, sample_event_data, email):
    """Create a fresh booking for lifecycle testing."""
    response = await client.post(
        "/api/v1/bookings/reserve",
        json={
            "event_id": sample_event_data["event"].id,
            "tier_id": sample_event_data["tier_vip"].id,
            "quantity": 2,
            "customer_name": "Lifecycle QA Tester",
            "customer_email": email,
            "customer_phone": "9876543210",
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_payment_pending_booking_can_be_cancelled(
    client, db_session, sample_event_data
):
    """PAYMENT_PENDING cancellation restores reserved inventory."""

    booking_data = await create_test_booking(
        client,
        sample_event_data,
        "lifecycle.cancel@example.com",
    )

    booking = await BookingService.get_booking_by_reference(
        db_session,
        booking_data["booking_reference"],
    )

    assert booking is not None

    booking.status = "PAYMENT_PENDING"
    await db_session.commit()

    tier = await db_session.get(TicketTier, booking.tier_id)
    available_before_cancel = tier.available_quantity

    cancelled = await BookingService.cancel_booking(
        db_session,
        booking.booking_reference,
        reason="Payment pending cancellation QA",
    )

    await db_session.refresh(tier)

    assert cancelled.status == "CANCELLED"
    assert tier.available_quantity == (
        available_before_cancel + booking.quantity
    )
    assert cancelled.refund_status == "NONE"


@pytest.mark.asyncio
async def test_expired_payment_pending_booking_restores_inventory(
    client, db_session, sample_event_data
):
    """Expired PAYMENT_PENDING booking restores inventory exactly once."""

    booking_data = await create_test_booking(
        client,
        sample_event_data,
        "lifecycle.expiry@example.com",
    )

    booking = await BookingService.get_booking_by_reference(
        db_session,
        booking_data["booking_reference"],
    )

    assert booking is not None

    booking.status = "PAYMENT_PENDING"
    booking.hold_expires_at = datetime.utcnow() - timedelta(minutes=1)

    await db_session.commit()

    tier = await db_session.get(TicketTier, booking.tier_id)
    available_before_expiry = tier.available_quantity

    expired_count = await BookingService.expire_stale_reservations(
        db_session
    )

    await db_session.refresh(booking)
    await db_session.refresh(tier)

    assert expired_count == 1
    assert booking.status == "EXPIRED"
    assert tier.available_quantity == (
        available_before_expiry + booking.quantity
    )

    # Running expiry again must not restore inventory a second time.
    second_expired_count = await BookingService.expire_stale_reservations(
        db_session
    )

    await db_session.refresh(tier)

    assert second_expired_count == 0
    assert tier.available_quantity == (
        available_before_expiry + booking.quantity
    )
