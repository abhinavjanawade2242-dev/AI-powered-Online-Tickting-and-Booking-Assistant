import os
from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "ticketing_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.booking_tasks"]
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    beat_schedule={
        "expire-stale-ticket-holds-every-60s": {
            "task": "app.tasks.booking_tasks.clean_expired_holds",
            "schedule": 60.0,  # Run every 60 seconds
        },
    }
)

