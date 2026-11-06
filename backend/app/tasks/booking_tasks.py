import asyncio
import logging
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.booking_service import BookingService

logger = logging.getLogger("ticketing.celery.tasks")


@celery_app.task(name="app.tasks.booking_tasks.clean_expired_holds")
def clean_expired_holds():
    """
    Celery background worker task that sweeps for expired ticket reservations
    and releases held inventory back to availability.
    """
    async def _sweep():
        async with AsyncSessionLocal() as session:
            return await BookingService.expire_stale_reservations(session)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    count = loop.run_until_complete(_sweep())
    logger.info("Celery hold cleaner: sweeped and restored %d expired bookings", count)
    return {"expired_count": count}


@celery_app.task(name="app.tasks.booking_tasks.send_booking_notification")
def send_booking_notification(booking_reference: str, email: str):
    """
    Simulates asynchronous notification dispatch (email/SMS) with digital ticket attachments.
    """
    logger.info("Dispatched digital ticket confirmation email for %s to %s", booking_reference, email)
    return {"status": "sent", "booking_reference": booking_reference, "recipient": email}

