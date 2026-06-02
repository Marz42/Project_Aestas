from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "aestas",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    beat_schedule={
        "worker-heartbeat": {
            "task": "app.workers.tasks.worker_heartbeat",
            "schedule": float(settings.celery_heartbeat_interval_seconds),
        },
        "fetch-all-feeds": {
            "task": "app.workers.tasks.fetch_all_feeds",
            "schedule": float(settings.fetch_interval_minutes * 60),
        },
    },
)
