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
def fetch_all_feeds() -> dict[str, int | list[dict[str, str | int]]]:
    from app.core.database import SyncSessionLocal
    from app.services.ingestion.service import IngestionService

    with SyncSessionLocal() as session:
        results = IngestionService(session).fetch_all_active(force=False)

    summary = [
        {
            "feed_source_id": str(r.feed_source_id),
            "created": r.articles_created,
            "skipped": r.articles_skipped,
        }
        for r in results
    ]
    total_created = sum(r.articles_created for r in results)
    logger.info("fetch_all_feeds done: created=%s feeds=%s", total_created, len(results))
    return {"articles_created": total_created, "feeds": summary}
