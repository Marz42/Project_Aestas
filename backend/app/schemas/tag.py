from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    slug: str = Field(max_length=32)
    name: str = Field(max_length=64)


class TagResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
