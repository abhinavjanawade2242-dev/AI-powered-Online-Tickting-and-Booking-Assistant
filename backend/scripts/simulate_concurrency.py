import asyncio
import logging
import time
from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.models import Venue, Event, TicketTier
from app.schemas import BookingReservationRequest
from app.services.booking_service import BookingService
from app.services.concurrency import InsufficientInventoryError, LockAcquisitionError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("concurrency.sim")


async def setup_test_tier(session, total_seats: int = 5) -> str:
    """Sets up a fresh event with a constrained inventory tier for stress testing."""
    venue = Venue(
        id=f"venue-stress-{int(time.time())}",
        name="High-Demand Arena",
        description="Stress testing venue",
        address="100 Concurrency Blvd",
        city="Cloud City",
        capacity=50000
    )
    session.add(venue)
    await session.flush()

    event = Event(
        id=f"event-stress-{int(time.time())}",
        venue_id=venue.id,
        title="Ultra-Exclusive Flash Sale Concert",
        category="Concert",
        start_time=datetime.utcnow() + timedelta(days=1),
        end_time=datetime.utcnow() + timedelta(days=1, hours=3),
        status="ACTIVE"
    )
    session.add(event)
    await session.flush()

    tier = TicketTier(
        id=f"tier-stress-{int(time.time())}",
        event_id=event.id,
        name="Limited VIP Front Row",
        price=1500.00,
        currency="INR",
        total_quantity=total_seats,
        available_quantity=total_seats,
    )
    session.add(tier)
    await session.commit()
    logger.info("Created test tier with exactly %d seats: %s", total_seats, tier.id)
    return tier.id, event.id


async def simulate_user_booking(user_id: int, event_id: str, tier_id: str, results: dict):
    """Simulates an individual customer attempting to book 1 ticket."""
    req = BookingReservationRequest(
        event_id=event_id,
        tier_id=tier_id,
        quantity=1,
        customer_name=f"Customer #{user_id}",
        customer_email=f"user_{user_id}_{int(time.time())}@example.com"
    )
    async with AsyncSessionLocal() as session:
        try:
            booking = await BookingService.reserve_tickets_atomic(session, req)
            # Confirm booking
            confirmed = await BookingService.confirm_booking(session, booking.booking_reference)
            results["successful"].append(confirmed.booking_reference)
            logger.info("✅ User #%02d SUCCEEDED -> Booking Ref: %s", user_id, confirmed.booking_reference)
        except InsufficientInventoryError:
            results["insufficient_inventory"] += 1
            logger.info("❌ User #%02d REJECTED  -> Sold Out / Insufficient Inventory", user_id)
        except LockAcquisitionError:
            results["lock_timeout"] += 1
            logger.warning("⏱️ User #%02d TIMED OUT -> Concurrency Lock Contention", user_id)
        except Exception as e:
            results["errors"].append(str(e))
            logger.error("💥 User #%02d ERROR    -> %s", user_id, e)


async def run_stress_test(num_concurrent_users: int = 50, available_tickets: int = 5):
    logger.info("=" * 70)
    logger.info("STARTING HIGH-CONCURRENCY ANTI-OVERBOOKING STRESS TEST")
    logger.info("Available Tickets: %d | Concurrent Customer Requests: %d", available_tickets, num_concurrent_users)
    logger.info("=" * 70)

    await init_db()

    async with AsyncSessionLocal() as session:
        tier_id, event_id = await setup_test_tier(session, total_seats=available_tickets)

    results = {
        "successful": [],
        "insufficient_inventory": 0,
        "lock_timeout": 0,
        "errors": []
    }

    start_time = time.perf_counter()

    # Launch all booking attempts in parallel using asyncio.gather
    tasks = [
        simulate_user_booking(i, event_id, tier_id, results)
        for i in range(1, num_concurrent_users + 1)
    ]
    await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start_time

    # Verify final remaining inventory in database
    async with AsyncSessionLocal() as session:
        stmt = select(TicketTier).where(TicketTier.id == tier_id)
        tier_res = await session.execute(stmt)
        final_tier = tier_res.scalar_one()

    logger.info("=" * 70)
    logger.info("STRESS TEST RESULTS SUMMARY")
    logger.info("=" * 70)
    logger.info("Execution Time:                %.3f seconds", elapsed)
    logger.info("Successful Bookings:           %d / %d", len(results["successful"]), available_tickets)
    logger.info("Rejected (Clean Sold Out):     %d", results["insufficient_inventory"])
    logger.info("Lock Contention Timeouts:      %d", results["lock_timeout"])
    logger.info("Unexpected Errors:             %d", len(results["errors"]))
    logger.info("Final DB Available Quantity:   %d (Must be >= 0)", final_tier.available_quantity)

    # Assert strict zero-overbooking invariant
    assert len(results["successful"]) <= available_tickets, "OVERBOOKING DETECTED! CRITICAL BUG!"
    assert final_tier.available_quantity >= 0, "NEGATIVE INVENTORY! CRITICAL BUG!"
    logger.info("🎯 RESULT: ZERO OVERBOOKING GUARANTEE VERIFIED SUCCESSFULLY! 🛡️")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_stress_test(num_concurrent_users=30, available_tickets=5))

