from unittest.mock import MagicMock, patch

from app.services.ingestion.seed import DEFAULT_FEEDS, DEFAULT_TAGS, seed_default_feeds


def test_seed_constants_cover_user_feeds() -> None:
    urls = {url for _, _, url in DEFAULT_FEEDS}
    assert "https://www.twz.com/feed" in urls
    assert "https://sspai.com/feed" in urls
    assert "https://plink.anyfeeder.com/zaobao/realtime/china" in urls
    assert "https://feeds.bbci.co.uk/news/rss.xml" in urls
    assert len(DEFAULT_TAGS) == 3


@patch("app.services.ingestion.seed.SyncSessionLocal")
def test_seed_default_feeds_idempotent(mock_session_local: MagicMock) -> None:
    session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = session
    session.scalar.return_value = None

    counts = seed_default_feeds()
    assert counts["tags_created"] == 3
    assert counts["feeds_created"] == 4
    session.commit.assert_called_once()
