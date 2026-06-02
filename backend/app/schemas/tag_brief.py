from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TagBriefGenerateRequest(BaseModel):
    tag_id: UUID | None = None
    window_start: datetime | None = None
    window_end: datetime | None = None
    force: bool = False


class TagBriefResponse(BaseModel):
    id: UUID
    tag_id: UUID
    tag_name: str | None = None
    window_start: datetime
    window_end: datetime
    title: str
    content_md: str
    status: str
    item_count: int = 0
    generated_at: datetime

    model_config = {"from_attributes": True}


class BriefingTaskResult(BaseModel):
    tag_id: UUID
    brief_id: UUID | None
    item_count: int
    created: bool
