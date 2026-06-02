import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import DbSession, verify_api_key
from app.core.exceptions import AppError
from app.core.response import ApiResponse, success
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse

router = APIRouter(prefix="/tags", dependencies=[Depends(verify_api_key)])


@router.get("", response_model=ApiResponse[list[TagResponse]])
async def list_tags(db: DbSession) -> ApiResponse[list[TagResponse]]:
    tags = (await db.scalars(select(Tag).order_by(Tag.slug))).all()
    return success([TagResponse.model_validate(t) for t in tags])


@router.post("", response_model=ApiResponse[TagResponse])
async def create_tag(body: TagCreate, db: DbSession) -> ApiResponse[TagResponse]:
    existing = await db.scalar(select(Tag).where(Tag.slug == body.slug))
    if existing:
        raise AppError(f"tag slug already exists: {body.slug}", code=400)
    tag = Tag(slug=body.slug, name=body.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return success(TagResponse.model_validate(tag))


@router.get("/{tag_id}", response_model=ApiResponse[TagResponse])
async def get_tag(tag_id: uuid.UUID, db: DbSession) -> ApiResponse[TagResponse]:
    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise AppError("tag not found", code=404)
    return success(TagResponse.model_validate(tag))
