from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ArticleInsightResponse(BaseModel):
    structured: dict[str, Any]
    short_news_md: str
    processed_at: datetime

    model_config = {"from_attributes": True}
