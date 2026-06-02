from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    slug: str = Field(max_length=32)
    name: str = Field(max_length=64)
    prompt_template_id: UUID | None = None


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    prompt_template_id: UUID | None = None


class TagResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    prompt_template_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
