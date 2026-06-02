from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PromptTemplateCreate(BaseModel):
    name: str = Field(max_length=128)
    purpose: str = Field(default="extraction", max_length=32)
    description: str | None = Field(default=None, max_length=255)
    system_prompt: str
    user_prompt_template: str


class PromptTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    purpose: str | None = Field(default=None, max_length=32)
    description: str | None = None
    system_prompt: str | None = None
    user_prompt_template: str | None = None


class PromptTemplateResponse(BaseModel):
    id: UUID
    name: str
    purpose: str
    description: str | None
    system_prompt: str
    user_prompt_template: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
