import asyncio
from datetime import datetime, timedelta
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.redis import close_redis
from app.main import app
from app.models import Venue, Event, TicketTier, User

import os

# Use a file-based SQLite database with async driver for test execution
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_ticketing.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_redis():
    yield
    await close_redis()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def sample_event_data(db_session: AsyncSession):
    """Seed baseline test event with venue and ticket tiers."""
    venue = Venue(
        id="venue-test-01",
        name="Madison Test Arena",
        description="Test arena for automated test suite",
        address="123 Test St",
        city="New York",
        capacity=5000,
        amenities="Fast Entry, Test Lounges"
    )
    db_session.add(venue)
    await db_session.flush()

    event = Event(
        id="event-test-01",
        venue_id=venue.id,
        title="Automated Test Rock Fest",
        description="High intensity testing concert",
        category="Concert",
        start_time=datetime.utcnow() + timedelta(days=5),
        end_time=datetime.utcnow() + timedelta(days=5, hours=3),
        status="ACTIVE"
    )
    db_session.add(event)
    await db_session.flush()

    tier_vip = TicketTier(
        id="tier-test-vip",
        event_id=event.id,
        name="VIP Exclusive",
        price=200.00,
        currency="INR",
        total_quantity=5,
        available_quantity=5,
    )
    tier_ga = TicketTier(
        id="tier-test-ga",
        event_id=event.id,
        name="General Admission",
        price=50.00,
        currency="INR",
        total_quantity=50,
        available_quantity=50,
    )
    db_session.add_all([tier_vip, tier_ga])
    await db_session.commit()

    return {
        "venue": venue,
        "event": event,
        "tier_vip": tier_vip,
        "tier_ga": tier_ga
    }

