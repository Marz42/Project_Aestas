import asyncio
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select

from app.core.database import SyncSessionLocal
from app.core.deps import DbSession, verify_api_key
from app.core.exceptions import AppError
from app.core.response import ApiResponse, success
from app.models.tag import Tag
from app.models.tag_brief import TagBrief, TagBriefItem
from app.schemas.tag_brief import (
    BriefingTaskResult,
    TagBriefGenerateRequest,
    TagBriefResponse,
)
from app.services.briefing.service import BriefingService

router = APIRouter(prefix="/tag-briefs", dependencies=[Depends(verify_api_key)])


def _brief_to_response(brief: TagBrief, tag_name: str | None, item_count: int) -> TagBriefResponse:
    return TagBriefResponse(
        id=brief.id,
        tag_id=brief.tag_id,
        tag_name=tag_name,
        window_start=brief.window_start,
        window_end=brief.window_end,
        title=brief.title,
        intro_md=brief.intro_md,
        content_md=brief.content_md,
        status=brief.status,
        item_count=item_count,
        generated_at=brief.generated_at,
    )


async def _item_count(db: DbSession, brief_id: UUID) -> int:
    return int(
        await db.scalar(
            select(func.count())
            .select_from(TagBriefItem)
            .where(TagBriefItem.tag_brief_id == brief_id)
        )
        or 0
    )


@router.get("", response_model=ApiResponse[dict])
async def list_tag_briefs(
    db: DbSession,
    tag_id: UUID | None = Query(default=None),
    window_start: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[dict]:
    query = (
        select(TagBrief, Tag.name)
        .join(Tag, Tag.id == TagBrief.tag_id)
        .order_by(TagBrief.generated_at.desc())
    )
    count_query = select(func.count()).select_from(TagBrief)
    if tag_id:
        query = query.where(TagBrief.tag_id == tag_id)
        count_query = count_query.where(TagBrief.tag_id == tag_id)
    if window_start:
        query = query.where(TagBrief.window_start == window_start)
        count_query = count_query.where(TagBrief.window_start == window_start)

    total = await db.scalar(count_query) or 0
    rows = (
        await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    ).all()

    items: list[TagBriefResponse] = []
    for brief, tag_name in rows:
        count = await _item_count(db, brief.id)
        items.append(_brief_to_response(brief, tag_name, count))

    return success(
        {"items": items, "total": total, "page": page, "page_size": page_size}
    )


@router.get("/{brief_id}", response_model=ApiResponse[TagBriefResponse])
async def get_tag_brief(brief_id: UUID, db: DbSession) -> ApiResponse[TagBriefResponse]:
    row = await db.execute(
        select(TagBrief, Tag.name)
        .join(Tag, Tag.id == TagBrief.tag_id)
        .where(TagBrief.id == brief_id)
    )
    result = row.one_or_none()
    if result is None:
        raise AppError("tag brief not found", code=404)
    brief, tag_name = result
    count = await _item_count(db, brief.id)
    return success(_brief_to_response(brief, tag_name, count))


@router.get("/{brief_id}/download", response_class=PlainTextResponse)
async def download_tag_brief(brief_id: UUID, db: DbSession) -> PlainTextResponse:
    brief = await db.get(TagBrief, brief_id)
    if brief is None:
        raise AppError("tag brief not found", code=404)
    return PlainTextResponse(
        content=brief.content_md,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="brief-{brief_id}.md"'
        },
    )


def _generate_one(body: TagBriefGenerateRequest) -> TagBriefResponse:
    with SyncSessionLocal() as session:
        if body.tag_id is None:
            raise ValueError("tag_id required")
        brief, item_count = BriefingService(session).generate_for_tag(
            body.tag_id,
            window_start=body.window_start,
            window_end=body.window_end,
            force=body.force,
        )
        tag = session.get(Tag, brief.tag_id)
        tag_name = tag.name if tag else None
    return _brief_to_response(brief, tag_name, item_count)


def _generate_all(force: bool) -> list[BriefingTaskResult]:
    with SyncSessionLocal() as session:
        stats = BriefingService(session).generate_all_tags(force=force)
    return [
        BriefingTaskResult(
            tag_id=s.tag_id,
            brief_id=s.brief_id,
            item_count=s.item_count,
            created=s.created,
        )
        for s in stats
    ]


@router.post("/generate", response_model=ApiResponse)
async def generate_tag_brief(body: TagBriefGenerateRequest) -> ApiResponse:
    if body.tag_id is None:
        results = await asyncio.to_thread(_generate_all, body.force)
        return success(results)
    result = await asyncio.to_thread(_generate_one, body)
    return success(result)
