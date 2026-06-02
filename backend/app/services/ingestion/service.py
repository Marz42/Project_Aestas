import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.models.feed_source import FeedSource
from app.services.ingestion.rss_client import fetch_feed_entries
from app.services.ingestion.types import IngestionStats
from app.services.ingestion.url_utils import normalize_url

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self._session = session
        self._settings = settings or get_settings()

    def fetch_source(
        self,
        feed_source_id: uuid.UUID,
        *,
        force: bool = False,
    ) -> IngestionStats:
        source = self._session.get(FeedSource, feed_source_id)
        if source is None:
            raise ValueError(f"Feed source not found: {feed_source_id}")
        if not source.is_active:
            return IngestionStats(feed_source_id, 0, 0, 0)

        if not force and not self._is_due(source):
            logger.info("Skipping feed %s (not due yet)", source.name)
            return IngestionStats(feed_source_id, 0, 0, 0)

        entries = fetch_feed_entries(source.feed_url, self._settings)
        now = datetime.now(UTC)
        created = 0
        skipped = 0

        for entry in entries:
            dedup_key = normalize_url(entry.url)
            exists = self._session.scalar(
                select(Article.id).where(Article.dedup_key == dedup_key).limit(1)
            )
            if exists:
                skipped += 1
                continue

            article = Article(
                feed_source_id=source.id,
                tag_id=source.tag_id,
                title=entry.title,
                url=entry.url,
                summary_raw=entry.summary,
                content_md=None,
                published_at=entry.published_at,
                fetched_at=now,
                status="pending",
                dedup_key=dedup_key,
            )
            self._session.add(article)
            created += 1

        source.last_fetched_at = now
        self._session.commit()

        logger.info(
            "Fetched %s: seen=%s created=%s skipped=%s",
            source.name,
            len(entries),
            created,
            skipped,
        )
        return IngestionStats(
            feed_source_id=source.id,
            entries_seen=len(entries),
            articles_created=created,
            articles_skipped=skipped,
        )

    def fetch_all_active(self, *, force: bool = False) -> list[IngestionStats]:
        sources = self._session.scalars(
            select(FeedSource).where(FeedSource.is_active.is_(True))
        ).all()
        results: list[IngestionStats] = []
        for source in sources:
            try:
                results.append(self.fetch_source(source.id, force=force))
            except Exception:
                logger.exception("Failed to fetch feed %s", source.name)
                self._session.rollback()
        return results

    def _is_due(self, source: FeedSource) -> bool:
        if source.last_fetched_at is None:
            return True
        interval = source.fetch_interval_minutes
        if interval <= 0:
            interval = self._settings.fetch_interval_minutes
        due_at = source.last_fetched_at + timedelta(minutes=interval)
        return datetime.now(UTC) >= due_at
