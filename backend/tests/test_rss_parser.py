from pathlib import Path

from app.services.ingestion.rss_client import parse_feed_content

FIXTURE = Path(__file__).parent / "fixtures" / "sample_rss.xml"


def test_parse_feed_content_extracts_entries() -> None:
    content = FIXTURE.read_bytes()
    entries = parse_feed_content(content, "https://example.com/feed.xml")
    assert len(entries) == 2
    assert entries[0].title == "First Article"
    assert entries[0].url == "https://example.com/news/1"
    assert entries[0].summary == "Summary one"
    assert entries[0].published_at is not None
    assert entries[1].title == "Second Article"
