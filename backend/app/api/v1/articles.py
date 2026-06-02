import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.database import SyncSessionLocal
from app.core.deps import DbSession, verify_api_key
from app.core.exceptions import AppError
from app.core.response import ApiResponse, success
from app.models.article import Article
from app.schemas.article import ArticleResponse
from app.schemas.insight import ArticleInsightResponse
from app.services.extraction.service import ExtractionService

router = APIRouter(prefix="/articles", dependencies=[Depends(verify_api_key)])


def _article_response(article: Article) -> ArticleResponse:
    insight = None
    if article.insight:
        insight = ArticleInsightResponse.model_validate(article.insight)
    return ArticleResponse(
        id=article.id,
        tag_id=article.tag_id,
        feed_source_id=article.feed_source_id,
        title=article.title,
        url=article.url,
        summary_raw=article.summary_raw,
        published_at=article.published_at,
        fetched_at=article.fetched_at,
        status=article.status,
        insight=insight,
    )


@router.get("", response_model=ApiResponse[dict])
async def list_articles(
    db: DbSession,
    tag_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[dict]:
    query = (
        select(Article)
        .options(selectinload(Article.insight))
        .order_by(Article.fetched_at.desc())
    )
    count_query = select(func.count()).select_from(Article)
    if tag_id:
        query = query.where(Article.tag_id == tag_id)
        count_query = count_query.where(Article.tag_id == tag_id)
    if status:
        query = query.where(Article.status == status)
        count_query = count_query.where(Article.status == status)

    total = await db.scalar(count_query) or 0
    items = (
        await db.scalars(
            query.offset((page - 1) * page_size).limit(page_size)
        )
    ).all()
    return success(
        {
            "items": [_article_response(i) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/{article_id}", response_model=ApiResponse[ArticleResponse])
async def get_article(article_id: UUID, db: DbSession) -> ApiResponse[ArticleResponse]:
    article = await db.scalar(
        select(Article)
        .options(selectinload(Article.insight))
        .where(Article.id == article_id)
    )
    if article is None:
        raise AppError("article not found", code=404)
    return success(_article_response(article))


class _ReextractError(Exception):
    def __init__(self, message: str, code: int = 400) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


def _reextract(article_id: UUID) -> ArticleInsightResponse:
    with SyncSessionLocal() as session:
        insight = ExtractionService(session).extract_article(article_id, force=True)
        if insight is None:
            raise _ReextractError("article skipped: insufficient content", 400)
        return ArticleInsightResponse.model_validate(insight)


@router.post("/{article_id}/reextract", response_model=ApiResponse[ArticleInsightResponse])
async def reextract_article(article_id: UUID) -> ApiResponse[ArticleInsightResponse]:
    try:
        result = await asyncio.to_thread(_reextract, article_id)
    except _ReextractError as exc:
        raise AppError(exc.message, code=exc.code) from exc
    return success(result)
