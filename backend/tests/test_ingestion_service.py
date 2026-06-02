import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models.feed_source import FeedSource
from app.services.ingestion.service import IngestionService
from app.services.ingestion.types import ParsedRssEntry


@pytest.fixture
def feed_source() -> FeedSource:
    return FeedSource(
        id=uuid.uuid4(),
        tag_id=uuid.uuid4(),
        name="Test Feed",
        feed_url="https://example.com/feed",
        source_type="rss",
        fetch_interval_minutes=480,
        is_active=True,
        last_fetched_at=None,
    )


def test_fetch_source_creates_articles(feed_source: FeedSource) -> None:
    session = MagicMock()
    session.get.return_value = feed_source
    session.scalar.side_effect = [None, None]
    entries = [
        ParsedRssEntry("A", "https://example.com/a", "sum", None),
        ParsedRssEntry("B", "https://example.com/b", None, None),
    ]

    with patch(
        "app.services.ingestion.service.fetch_feed_entries",
        return_value=entries,
    ):
        stats = IngestionService(session).fetch_source(feed_source.id, force=True)

    assert stats.entries_seen == 2
    assert stats.articles_created == 2
    assert stats.articles_skipped == 0
    assert session.add.call_count == 2
    session.commit.assert_called_once()


def test_fetch_source_skips_duplicate(feed_source: FeedSource) -> None:
    session = MagicMock()
    session.get.return_value = feed_source
    session.scalar.side_effect = [uuid.uuid4(), None]
    entries = [
        ParsedRssEntry("A", "https://example.com/a", None, None),
        ParsedRssEntry("B", "https://example.com/b", None, None),
    ]

    with patch(
        "app.services.ingestion.service.fetch_feed_entries",
        return_value=entries,
    ):
        stats = IngestionService(session).fetch_source(feed_source.id, force=True)

    assert stats.articles_created == 1
    assert stats.articles_skipped == 1


def test_is_due_respects_interval(feed_source: FeedSource) -> None:
    feed_source.last_fetched_at = datetime.now(UTC)
    feed_source.fetch_interval_minutes = 480
    session = MagicMock()
    service = IngestionService(session)
    assert service._is_due(feed_source) is False

    feed_source.last_fetched_at = None
    assert service._is_due(feed_source) is True
