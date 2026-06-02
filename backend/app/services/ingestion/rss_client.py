from datetime import UTC, datetime
from time import struct_time

import feedparser
import httpx

from app.core.config import Settings, get_settings
from app.services.ingestion.types import ParsedRssEntry


def _parse_published(entry: feedparser.FeedParserDict) -> datetime | None:
    published: struct_time | None = entry.get("published_parsed") or entry.get(
        "updated_parsed"
    )
    if not published:
        return None
    return datetime(*published[:6], tzinfo=UTC)


def parse_feed_content(content: bytes, feed_url: str) -> list[ParsedRssEntry]:
    parsed = feedparser.parse(content, response_headers={"url": feed_url})
    if parsed.bozo and not parsed.entries:
        raise ValueError(parsed.bozo_exception or "Failed to parse RSS feed")

    entries: list[ParsedRssEntry] = []
    for entry in parsed.entries:
        link = entry.get("link") or entry.get("id")
        title = entry.get("title")
        if not link or not title:
            continue
        summary = entry.get("summary") or entry.get("description")
        if isinstance(summary, str):
            summary_text: str | None = summary[:8000] if summary else None
        else:
            summary_text = None
        entries.append(
            ParsedRssEntry(
                title=str(title).strip()[:512],
                url=str(link).strip()[:2048],
                summary=summary_text,
                published_at=_parse_published(entry),
            )
        )
    return entries


def fetch_feed_entries(
    feed_url: str,
    settings: Settings | None = None,
) -> list[ParsedRssEntry]:
    settings = settings or get_settings()
    timeout = httpx.Timeout(30.0, connect=10.0)
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(
            feed_url,
            headers={"User-Agent": f"{settings.app_name}/0.1 RSS fetcher"},
        )
        response.raise_for_status()
    return parse_feed_content(response.content, feed_url)
