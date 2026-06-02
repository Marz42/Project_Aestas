import pytest
from sqlalchemy import func, select

from app.core.database import SyncSessionLocal, check_sync_db
from app.models.article import Article
from app.models.feed_source import FeedSource
from app.services.ingestion.seed import seed_default_feeds
from app.services.ingestion.service import IngestionService


@pytest.mark.integration
def test_seed_and_fetch_sspai(postgres_available: bool) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")

    check_sync_db()
    seed_default_feeds()

    with SyncSessionLocal() as session:
        source = session.scalar(
            select(FeedSource).where(
                FeedSource.feed_url == "https://sspai.com/feed"
            )
        )
        assert source is not None
        before = session.scalar(select(func.count()).select_from(Article)) or 0
        stats = IngestionService(session).fetch_source(source.id, force=True)
        after = session.scalar(select(func.count()).select_from(Article)) or 0

    assert stats.entries_seen > 0
    assert stats.articles_created == after - before
