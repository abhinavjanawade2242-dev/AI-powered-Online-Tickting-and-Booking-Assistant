import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_stage_1_and_2_discovery_and_recommendation(client: AsyncClient, sample_event_data):
    """
    Stage 1: Discovery (Search events & venues)
    Stage 2: Recommendation (Curated event lists)
    """
    # 1. Search events
    res = await client.get("/api/v1/events?city=New York")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 1
    assert "Automated Test Rock Fest" in events[0]["title"]

    # 2. Recommendations
    rec_res = await client.get("/api/v1/events/recommendations?city=New York")
    assert rec_res.status_code == 200
    recs = rec_res.json()
    assert len(recs) >= 1


@pytest.mark.asyncio
async def test_stage_3_availability(client: AsyncClient, sample_event_data):
    """
    Stage 3: Availability (Check ticket inventory and pricing tiers)
    """
    event_id = sample_event_data["event"].id
    res = await client.get(f"/api/v1/events/{event_id}/availability")
    assert res.status_code == 200
    data = res.json()
    assert data["event_id"] == event_id
    assert data["total_available_tickets"] == 55  # 5 VIP + 50 GA
    assert len(data["tiers"]) == 2


@pytest.mark.asyncio
async def test_stage_4_5_6_7_booking_lifecycle(client: AsyncClient, sample_event_data):
    """
    Stage 4: Selection
    Stage 5: Booking (Reserve with distributed lock)
    Stage 6: Confirmation (Generate digital tickets with QR)
    Stage 7: Post-booking (Retrieve & Cancel)
    """
    event_id = sample_event_data["event"].id
    tier_id = sample_event_data["tier_vip"].id

    # Stage 4 & 5: Reserve Tickets
    reserve_payload = {
        "event_id": event_id,
        "tier_id": tier_id,
        "quantity": 2,
        "customer_name": "Daniel Craig",
        "customer_email": "daniel.craig@example.com",
        "customer_phone": "+1-555-007"
    }
    reserve_res = await client.post("/api/v1/bookings/reserve", json=reserve_payload)
    assert reserve_res.status_code == 201
    booking_data = reserve_res.json()
    booking_ref = booking_data["booking_reference"]
    assert booking_data["status"] == "PENDING"
    assert booking_data["quantity"] == 2
    assert booking_data["total_amount"] == 400.0

    # Stage 6: Confirmation
    confirm_payload = {
        "booking_reference": booking_ref,
        "payment_reference": "PAY-STRIPE-TEST-123"
    }
    confirm_res = await client.post("/api/v1/bookings/confirm", json=confirm_payload)
    assert confirm_res.status_code == 200
    confirmed_data = confirm_res.json()
    assert confirmed_data["status"] == "CONFIRMED"
    assert len(confirmed_data["tickets"]) == 2
    ticket_code = confirmed_data["tickets"][0]["ticket_code"]

    # Stage 6: Digital Ticket QR Image endpoint
    qr_res = await client.get(f"/api/v1/tickets/{ticket_code}/qr")
    assert qr_res.status_code == 200
    assert "qr_base64" in qr_res.json()

    # Stage 7: Gate Entrance Verification
    ticket_details = confirmed_data["tickets"][0]
    verify_res = await client.post("/api/v1/tickets/verify", json={"qr_payload": ticket_details["qr_payload"]})
    assert verify_res.status_code == 200
    assert verify_res.json()["is_valid"] is True

    # Stage 7: Retrieve booking
    get_res = await client.get(f"/api/v1/bookings/{booking_ref}")
    assert get_res.status_code == 200
    assert get_res.json()["booking_reference"] == booking_ref

    # Stage 7: Cancel booking
    cancel_res = await client.post("/api/v1/bookings/cancel", json={
        "booking_reference": booking_ref,
        "reason": "Customer changed travel plans"
    })
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
    assert cancel_res.json()["refund_status"] == "REFUNDED"


@pytest.mark.asyncio
async def test_offline_sync_replay_flow(client: AsyncClient, sample_event_data):
    """
    Test Offline Queue Synchronization Endpoint:
    Simulates client reconnecting and submitting a locally queued booking request.
    Verifies that server revalidates stock and returns an active 10-minute hold.
    """
    event_id = sample_event_data["event"].id
    tier_id = sample_event_data["tier_vip"].id

    sync_payload = {
        "client_request_id": "c1f7a28e-offline-test-001",
        "event_id": event_id,
        "tier_id": tier_id,
        "quantity": 2,
        "customer_name": "Adithya Frontend",
        "customer_email": "adithya@example.com"
    }

    res = await client.post("/api/v1/offline/sync", json=sync_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ACCEPTED_LOCKED"
    assert data["booking_reference"].startswith("BK-")
    assert data["total_amount"] == 400.0  # 2 * 200.00
    assert data["currency"] == "INR"
    assert data["hold_expires_at"] is not None


@pytest.mark.asyncio
async def test_free_event_booking_and_confirmation(client: AsyncClient, db_session, sample_event_data):
    """
    Test Free Admission (₹0.00 ticket tier):
    Verifies that zero-price events are fully supported, reserved, and confirmed without charge.
    """
    from app.models import TicketTier
    event = sample_event_data["event"]

    # Create a free tier
    free_tier = TicketTier(
        id="tier-free-workshop",
        event_id=event.id,
        name="Free Student Entry",
        price=0.00,
        currency="INR",
        total_quantity=20,
        available_quantity=20,
        version=1
    )
    db_session.add(free_tier)
    await db_session.commit()

    # Reserve 2 free tickets
    res = await client.post("/api/v1/bookings/reserve", json={
        "event_id": event.id,
        "tier_id": free_tier.id,
        "quantity": 2,
        "customer_name": "Student Free Pass",
        "customer_email": "student@college.edu"
    })
    assert res.status_code == 201
    booking = res.json()
    assert booking["total_amount"] == 0.0
    assert booking["status"] == "PENDING"
    booking_ref = booking["booking_reference"]

    # Confirm free booking without monetary charge
    confirm_res = await client.post("/api/v1/bookings/confirm", json={
        "booking_reference": booking_ref,
        "payment_reference": "FREE_CAMPUS_REGISTRATION"
    })
    assert confirm_res.status_code == 200
    confirmed = confirm_res.json()
    assert confirmed["status"] == "CONFIRMED"
    assert confirmed["total_amount"] == 0.0
    assert len(confirmed["tickets"]) == 2
    assert confirmed["tickets"][0]["ticket_code"].startswith("TIX-")

