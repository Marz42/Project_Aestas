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

    from app.services.extraction.service import ExtractionService

    with SyncSessionLocal() as session:
        extract_stats = ExtractionService(session).extract_pending(limit=30)

    return {
        "articles_created": total_created,
        "feeds": summary,
        "extracted": extract_stats.processed,
        "extract_skipped": extract_stats.skipped,
        "extract_failed": extract_stats.failed,
    }


@celery_app.task(name="app.workers.tasks.extract_pending_articles")
def extract_pending_articles() -> dict[str, int]:
    from app.core.database import SyncSessionLocal
    from app.services.extraction.service import ExtractionService

    with SyncSessionLocal() as session:
        stats = ExtractionService(session).extract_pending(limit=20)
    return {
        "processed": stats.processed,
        "skipped": stats.skipped,
        "failed": stats.failed,
    }


@celery_app.task(name="app.workers.tasks.generate_tag_briefs")
def generate_tag_briefs() -> dict[str, int]:
    from app.core.database import SyncSessionLocal
    from app.services.briefing.service import BriefingService

    with SyncSessionLocal() as session:
        results = BriefingService(session).generate_all_tags(force=False)
    return {
        "briefs": len([r for r in results if r.created]),
        "items": sum(r.item_count for r in results),
    }
