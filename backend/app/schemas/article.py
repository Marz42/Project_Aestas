from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.insight import ArticleInsightResponse


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
    insight: ArticleInsightResponse | None = None

    model_config = {"from_attributes": True}
