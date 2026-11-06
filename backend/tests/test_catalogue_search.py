
"""
Search & Catalogue Automated Test Suite
Technovate 2.0 | PS-07 AI-Powered Online Ticketing and Booking Assistant
Member 3: Catalogue/Data + QA Support
Task: AB-04 Search Test Cases
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.models import Venue, Event, TicketTier


@pytest_asyncio.fixture
async def catalogue_data(db_session):
    """Create catalogue records required by search tests."""

    venue = Venue(
        id="venue-tech-hub",
        name="Tech Hub",
        description="Technovate event venue",
        address="Mysuru",
        city="Mysuru",
        capacity=1000,
    )

    start = datetime.utcnow() + timedelta(days=30)

    events = [
        Event(
            id="event-technovate-hack",
            venue_id="venue-tech-hub",
            title="Technovate 2026 Hackathon",
            description="Annual technology hackathon",
            category="Technical",
            start_time=start,
            end_time=start + timedelta(hours=8),
            status="ACTIVE",
        ),
        Event(
            id="event-kannada-drama",
            venue_id="venue-tech-hub",
            title="Tughlaq Kannada Drama",
            description="Kannada theatrical cultural performance",
            category="Cultural",
            start_time=start,
            end_time=start + timedelta(hours=3),
            status="ACTIVE",
        ),
        Event(
            id="event-draft-robot-wars",
            venue_id="venue-tech-hub",
            title="Robot Wars",
            description="Inactive robotics event",
            category="Technical",
            start_time=start,
            end_time=start + timedelta(hours=3),
            status="INACTIVE",
        ),
    ]

    tier = TicketTier(
        id="tier-technovate-general",
        event_id="event-technovate-hack",
        name="General Admission",
        price=250,
        currency="INR",
        total_quantity=100,
        available_quantity=100,
    )

    db_session.add(venue)
    db_session.add_all(events)
    db_session.add(tier)

    await db_session.commit()


@pytest_asyncio.fixture
async def async_client(db_session, catalogue_data):
    """Create an API client using the test database."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_tc01_exact_title_search(async_client):
    res = await async_client.get(
        "/api/v1/events?search=Technovate 2026"
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any("Technovate 2026" in e["title"] for e in data)


@pytest.mark.asyncio
async def test_tc02_partial_keyword_search(async_client):
    res = await async_client.get(
        "/api/v1/events?search=hackathon"
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(
        "Hackathon" in e["title"]
        or "hackathon" in e["description"].lower()
        for e in data
    )


@pytest.mark.asyncio
async def test_tc03_category_filtering_technical(async_client):
    res = await async_client.get(
        "/api/v1/events?category=Technical"
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(e["category"] == "Technical" for e in data)


@pytest.mark.asyncio
async def test_tc04_category_filtering_cultural(async_client):
    res = await async_client.get(
        "/api/v1/events?category=Cultural"
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(e["category"] == "Cultural" for e in data)


@pytest.mark.asyncio
async def test_tc05_venue_filtering(async_client):
    res = await async_client.get(
        "/api/v1/events?venue_id=venue-tech-hub"
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(e["venue_id"] == "venue-tech-hub" for e in data)


@pytest.mark.asyncio
async def test_tc06_empty_result_nonexistent_query(async_client):
    res = await async_client.get(
        "/api/v1/events?search=NonExistentQuantumTeleportation2099"
    )
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_tc07_inactive_event_excluded_from_public_search(async_client):
    res = await async_client.get("/api/v1/events")
    assert res.status_code == 200
    data = res.json()

    event_ids = [e["id"] for e in data]

    assert "event-draft-robot-wars" not in event_ids

    for event in data:
        assert event["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_tc08_case_insensitive_search(async_client):
    res_upper = await async_client.get(
        "/api/v1/events?search=TECHNOVATE"
    )
    res_lower = await async_client.get(
        "/api/v1/events?search=technovate"
    )

    assert res_upper.status_code == 200
    assert res_lower.status_code == 200

    ids_upper = {e["id"] for e in res_upper.json()}
    ids_lower = {e["id"] for e in res_lower.json()}

    assert ids_upper == ids_lower
    assert len(ids_upper) >= 1


@pytest.mark.asyncio
async def test_tc09_multiword_and_cultural_search(async_client):
    res = await async_client.get(
        "/api/v1/events?search=Kannada Drama"
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(
        "Tughlaq" in e["title"] or "Kannada" in e["title"]
        for e in data
    )


@pytest.mark.asyncio
async def test_tc10_availability_and_inr_currency(async_client):
    res = await async_client.get(
        "/api/v1/events/event-technovate-hack/availability"
    )

    assert res.status_code == 200

    data = res.json()

    assert data["event_id"] == "event-technovate-hack"
    assert len(data["tiers"]) >= 1

    for tier in data["tiers"]:
        assert tier["currency"] == "INR"
        assert tier["price"] > 0
        assert tier["available_quantity"] > 0
