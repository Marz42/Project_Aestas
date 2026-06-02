"""Regression: TWZ feeds include article URLs longer than dedup_key varchar(128)."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.models.feed_source import FeedSource
from app.services.ingestion.service import IngestionService
from app.services.ingestion.types import ParsedRssEntry
LONG_URL = (
    "https://www.twz.com/news-features/cost-to-link-lucas-kamikaze-drones-to-starlink-"
    "highlights-pentagons-ever-growing-dependence-on-spacex"
)


def test_fetch_source_accepts_long_article_urls() -> None:
    feed_source = FeedSource(
        id=uuid4(),
        tag_id=uuid4(),
        name="TWZ",
        feed_url="https://www.twz.com/feed",
        source_type="rss",
        fetch_interval_minutes=480,
        is_active=True,
        last_fetched_at=None,
    )
    session = MagicMock()
    session.get.return_value = feed_source
    session.scalar.return_value = None

    entries = [
        ParsedRssEntry(
            title="Long URL article",
            url=LONG_URL,
            summary="summary",
            published_at=None,
        )
    ]

    with patch(
        "app.services.ingestion.service.fetch_feed_entries",
        return_value=entries,
    ):
        stats = IngestionService(session).fetch_source(feed_source.id, force=True)

    assert stats.articles_created == 1
    added = session.add.call_args[0][0]
    assert added.url == LONG_URL
    assert len(added.dedup_key) == 64
