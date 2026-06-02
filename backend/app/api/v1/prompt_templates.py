from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.core.deps import DbSession, verify_api_key
from app.core.exceptions import AppError
from app.core.response import ApiResponse, success
from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
)

router = APIRouter(prefix="/prompt-templates", dependencies=[Depends(verify_api_key)])


@router.get("", response_model=ApiResponse[list[PromptTemplateResponse]])
async def list_prompt_templates(
    db: DbSession,
    purpose: str | None = Query(default=None),
) -> ApiResponse[list[PromptTemplateResponse]]:
    query = select(PromptTemplate).order_by(PromptTemplate.name)
    if purpose:
        query = query.where(PromptTemplate.purpose == purpose)
    items = (await db.scalars(query)).all()
    return success([PromptTemplateResponse.model_validate(i) for i in items])


@router.post("", response_model=ApiResponse[PromptTemplateResponse])
async def create_prompt_template(
    body: PromptTemplateCreate, db: DbSession
) -> ApiResponse[PromptTemplateResponse]:
    item = PromptTemplate(
        name=body.name,
        purpose=body.purpose,
        description=body.description,
        system_prompt=body.system_prompt,
        user_prompt_template=body.user_prompt_template,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return success(PromptTemplateResponse.model_validate(item))


@router.get("/{template_id}", response_model=ApiResponse[PromptTemplateResponse])
async def get_prompt_template(
    template_id: UUID, db: DbSession
) -> ApiResponse[PromptTemplateResponse]:
    item = await db.get(PromptTemplate, template_id)
    if item is None:
        raise AppError("prompt template not found", code=404)
    return success(PromptTemplateResponse.model_validate(item))


@router.patch("/{template_id}", response_model=ApiResponse[PromptTemplateResponse])
async def update_prompt_template(
    template_id: UUID, body: PromptTemplateUpdate, db: DbSession
) -> ApiResponse[PromptTemplateResponse]:
    item = await db.get(PromptTemplate, template_id)
    if item is None:
        raise AppError("prompt template not found", code=404)
    for field in ("name", "purpose", "description", "system_prompt", "user_prompt_template"):
        value = getattr(body, field)
        if value is not None:
            setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return success(PromptTemplateResponse.model_validate(item))


@router.delete("/{template_id}", response_model=ApiResponse[dict[str, str]])
async def delete_prompt_template(
    template_id: UUID, db: DbSession
) -> ApiResponse[dict[str, str]]:
    item = await db.get(PromptTemplate, template_id)
    if item is None:
        raise AppError("prompt template not found", code=404)
    await db.delete(item)
    await db.commit()
    return success({"deleted": str(template_id)})
