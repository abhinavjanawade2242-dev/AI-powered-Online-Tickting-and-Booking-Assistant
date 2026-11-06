import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_agent_conversational_workflow(client: AsyncClient, sample_event_data):
    """
    Validates that the AI conversational assistant guides the user through the 7 stages:
    1. Discovery ("Find concerts in New York")
    2. Recommendation
    3. Availability ("Check ticket availability")
    4. Selection & 5. Booking ("Book 2 tickets for Alice, alice@example.com")
    6. Confirmation (Receives booking ref & digital ticket)
    7. Post-booking ("Check status of BK-XXXXXX" & "Cancel booking BK-XXXXXX")
    """
    session_id = "test_user_session_101"

    # Turn 1: Discovery
    res1 = await client.post("/api/v1/chat", json={
        "message": "Find rock concerts in New York",
        "session_id": session_id
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["current_stage"] in ["Discovery", "Recommendation"]
    assert "Rock Fest" in data1["message"]

    # Turn 2: Availability
    res2 = await client.post("/api/v1/chat", json={
        "message": "Check ticket availability and price",
        "session_id": session_id
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["current_stage"] == "Availability"
    assert "VIP Exclusive" in data2["message"]

    # Turn 3: Booking & Confirmation
    res3 = await client.post("/api/v1/chat", json={
        "message": "Book 2 tickets for Bob Dylan, bob@example.com",
        "session_id": session_id
    })
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["current_stage"] == "Confirmation"
    assert "Booking Confirmed" in data3["message"]
    booking_ref = data3["context_data"].get("last_booking_ref")
    assert booking_ref is not None
    assert booking_ref.startswith("BK-")

    # Turn 4: Post-booking status retrieval
    res4 = await client.post("/api/v1/chat", json={
        "message": f"What is the status of {booking_ref}?",
        "session_id": session_id
    })
    assert res4.status_code == 200
    data4 = res4.json()
    assert data4["current_stage"] == "Post-booking"
    assert "CONFIRMED" in data4["message"]

    # Turn 5: Post-booking cancellation
    res5 = await client.post("/api/v1/chat", json={
        "message": f"Please cancel booking {booking_ref}",
        "session_id": session_id
    })
    assert res5.status_code == 200
    data5 = res5.json()
    assert data5["current_stage"] == "Post-booking"
    assert "Cancelled Successfully" in data5["message"]

