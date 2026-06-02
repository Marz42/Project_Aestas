import logging

from app.core.database import check_sync_db
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.worker_heartbeat")
def worker_heartbeat() -> dict[str, str]:
    """M1 smoke task: proves Beat -> Worker -> DB path."""
    check_sync_db()
    logger.info("worker_heartbeat: database OK")
    return {"status": "ok"}


@celery_app.task(name="app.workers.tasks.fetch_all_feeds")
def fetch_all_feeds() -> dict[str, str]:
    """M2 will implement RSS ingestion; M1 registers the beat slot."""
    logger.info(
        "fetch_all_feeds: stub (M2); interval configured via FETCH_INTERVAL_MINUTES"
    )
    return {"status": "stub"}
