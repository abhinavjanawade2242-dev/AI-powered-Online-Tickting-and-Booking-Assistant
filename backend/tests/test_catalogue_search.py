"""
Search & Catalogue Automated Test Suite
Technovate 2.0 | PS-07 AI-Powered Online Ticketing and Booking Assistant
Member 3: Abhilash (Catalogue/Data + QA Support)
Task: AB-04 Search Test Cases (At least 8 reproducible test cases)

Tests search by title, category, venue, active status, case-insensitivity,
empty results, and partial matches against the catalogue API.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_tc01_exact_title_search(async_client: AsyncClient):
    """TC-01: Exact Title Search - Match specific event title."""
    res = await async_client.get("/api/v1/events?search=Technovate 2026")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    titles = [e["title"] for e in data]
    assert any("Technovate 2026" in t for t in titles)


@pytest.mark.asyncio
async def test_tc02_partial_keyword_search(async_client: AsyncClient):
    """TC-02: Partial/Substring Search - Match keyword within title or description."""
    res = await async_client.get("/api/v1/events?search=hackathon")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any("Hackathon" in e["title"] or "hackathon" in e["description"].lower() for e in data)


@pytest.mark.asyncio
async def test_tc03_category_filtering_technical(async_client: AsyncClient):
    """TC-03: Category Filtering - Filter exclusively by 'Technical' category."""
    res = await async_client.get("/api/v1/events?category=Technical")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    for event in data:
        assert event["category"] == "Technical"


@pytest.mark.asyncio
async def test_tc04_category_filtering_cultural(async_client: AsyncClient):
    """TC-04: Category Filtering - Filter exclusively by 'Cultural' category."""
    res = await async_client.get("/api/v1/events?category=Cultural")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    for event in data:
        assert event["category"] == "Cultural"


@pytest.mark.asyncio
async def test_tc05_venue_filtering(async_client: AsyncClient):
    """TC-05: Venue Filtering - Return only events hosted at a specific venue."""
    res = await async_client.get("/api/v1/events?venue_id=venue-tech-hub")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    for event in data:
        assert event["venue_id"] == "venue-tech-hub"


@pytest.mark.asyncio
async def test_tc06_empty_result_nonexistent_query(async_client: AsyncClient):
    """TC-06: Empty Result - Query with zero matching records returns [] without error."""
    res = await async_client.get("/api/v1/events?search=NonExistentQuantumTeleportation2099")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_tc07_inactive_event_excluded_from_public_search(async_client: AsyncClient):
    """TC-07: Inactive Event Filtering - Draft/Inactive events must NOT appear in public listing."""
    res = await async_client.get("/api/v1/events")
    assert res.status_code == 200
    data = res.json()
    event_ids = [e["id"] for e in data]
    # 'event-draft-robot-wars' is marked INACTIVE and should not appear in active public search
    assert "event-draft-robot-wars" not in event_ids
    for event in data:
        assert event["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_tc08_case_insensitive_search(async_client: AsyncClient):
    """TC-08: Case-Insensitivity - 'TECHNOVATE' vs 'technovate' return identical matches."""
    res_upper = await async_client.get("/api/v1/events?search=TECHNOVATE")
    res_lower = await async_client.get("/api/v1/events?search=technovate")
    assert res_upper.status_code == 200
    assert res_lower.status_code == 200
    ids_upper = {e["id"] for e in res_upper.json()}
    ids_lower = {e["id"] for e in res_lower.json()}
    assert ids_upper == ids_lower
    assert len(ids_upper) >= 1


@pytest.mark.asyncio
async def test_tc09_multiword_and_cultural_search(async_client: AsyncClient):
    """TC-09: Multi-word & Cultural Query - 'Kannada Drama' matches theatrical event."""
    res = await async_client.get("/api/v1/events?search=Kannada Drama")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any("Tughlaq" in e["title"] or "Kannada" in e["title"] for e in data)


@pytest.mark.asyncio
async def test_tc10_availability_and_inr_currency(async_client: AsyncClient):
    """TC-10: Availability check for catalogue events confirms INR currency & positive quantity."""
    res = await async_client.get("/api/v1/events/event-technovate-hack/availability")
    assert res.status_code == 200
    data = res.json()
    assert data["event_id"] == "event-technovate-hack"
    assert len(data["tiers"]) >= 1
    for tier in data["tiers"]:
        assert tier["currency"] == "INR"
        assert tier["price"] > 0
        assert tier["available_quantity"] > 0

