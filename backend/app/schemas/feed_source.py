from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class FeedSourceCreate(BaseModel):
    tag_id: UUID
    name: str = Field(max_length=255)
    feed_url: HttpUrl
    fetch_interval_minutes: int = Field(default=480, ge=0)
    is_active: bool = True


class FeedSourceUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    feed_url: HttpUrl | None = None
    fetch_interval_minutes: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class FeedSourceResponse(BaseModel):
    id: UUID
    tag_id: UUID
    name: str
    feed_url: str
    source_type: str
    fetch_interval_minutes: int
    is_active: bool
    last_fetched_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FetchResultResponse(BaseModel):
    feed_source_id: UUID
    entries_seen: int
    articles_created: int
    articles_skipped: int
