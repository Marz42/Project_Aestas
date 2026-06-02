import asyncio
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SyncSessionLocal
from app.core.deps import DbSession, verify_api_key
from app.core.exceptions import AppError
from app.core.response import ApiResponse, success
from app.models.feed_source import FeedSource
from app.models.tag import Tag
from app.schemas.feed_source import (
    FeedSourceCreate,
    FeedSourceResponse,
    FeedSourceUpdate,
    FetchResultResponse,
)
from app.services.ingestion.service import IngestionService

router = APIRouter(prefix="/feed-sources", dependencies=[Depends(verify_api_key)])


@router.get("", response_model=ApiResponse[dict])
async def list_feed_sources(
    db: DbSession,
    tag_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[dict]:
    query = select(FeedSource).order_by(FeedSource.name)
    count_query = select(func.count()).select_from(FeedSource)
    if tag_id:
        query = query.where(FeedSource.tag_id == tag_id)
        count_query = count_query.where(FeedSource.tag_id == tag_id)

    total = await db.scalar(count_query) or 0
    items = (
        await db.scalars(
            query.offset((page - 1) * page_size).limit(page_size)
        )
    ).all()
    return success(
        {
            "items": [FeedSourceResponse.model_validate(i) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.post("", response_model=ApiResponse[FeedSourceResponse])
async def create_feed_source(
    body: FeedSourceCreate, db: DbSession
) -> ApiResponse[FeedSourceResponse]:
    tag = await db.get(Tag, body.tag_id)
    if tag is None:
        raise AppError("tag not found", code=404)
    source = FeedSource(
        tag_id=body.tag_id,
        name=body.name,
        feed_url=str(body.feed_url),
        fetch_interval_minutes=body.fetch_interval_minutes,
        is_active=body.is_active,
        source_type="rss",
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return success(FeedSourceResponse.model_validate(source))


@router.patch("/{source_id}", response_model=ApiResponse[FeedSourceResponse])
async def update_feed_source(
    source_id: UUID, body: FeedSourceUpdate, db: DbSession
) -> ApiResponse[FeedSourceResponse]:
    source = await db.get(FeedSource, source_id)
    if source is None:
        raise AppError("feed source not found", code=404)
    if body.name is not None:
        source.name = body.name
    if body.feed_url is not None:
        source.feed_url = str(body.feed_url)
    if body.fetch_interval_minutes is not None:
        source.fetch_interval_minutes = body.fetch_interval_minutes
    if body.is_active is not None:
        source.is_active = body.is_active
    await db.commit()
    await db.refresh(source)
    return success(FeedSourceResponse.model_validate(source))


def _run_fetch(source_id: uuid.UUID, force: bool) -> FetchResultResponse:
    try:
        with SyncSessionLocal() as session:
            stats = IngestionService(session).fetch_source(source_id, force=force)
    except ValueError as exc:
        raise AppError(str(exc), code=400) from exc
    except Exception as exc:
        raise AppError(f"feed fetch failed: {exc}", code=500) from exc
    return FetchResultResponse(
        feed_source_id=stats.feed_source_id,
        entries_seen=stats.entries_seen,
        articles_created=stats.articles_created,
        articles_skipped=stats.articles_skipped,
    )


@router.post("/{source_id}/fetch", response_model=ApiResponse[FetchResultResponse])
async def fetch_feed_source(source_id: UUID) -> ApiResponse[FetchResultResponse]:
    result = await asyncio.to_thread(_run_fetch, source_id, True)
    return success(result)
