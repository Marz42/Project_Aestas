from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ParsedRssEntry:
    title: str
    url: str
    summary: str | None
    published_at: datetime | None


@dataclass
class IngestionStats:
    feed_source_id: UUID
    entries_seen: int
    articles_created: int
    articles_skipped: int
