from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ArticleResponse(BaseModel):
    id: UUID
    tag_id: UUID
    feed_source_id: UUID
    title: str
    url: str
    summary_raw: str | None
    published_at: datetime | None
    fetched_at: datetime
    status: str

    model_config = {"from_attributes": True}
