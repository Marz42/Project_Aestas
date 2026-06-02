from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.core.deps import DbSession, verify_api_key
from app.core.exceptions import AppError
from app.core.response import ApiResponse, success
from app.models.article import Article
from app.schemas.article import ArticleResponse

router = APIRouter(prefix="/articles", dependencies=[Depends(verify_api_key)])


@router.get("", response_model=ApiResponse[dict])
async def list_articles(
    db: DbSession,
    tag_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[dict]:
    query = select(Article).order_by(Article.fetched_at.desc())
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
            "items": [ArticleResponse.model_validate(i) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/{article_id}", response_model=ApiResponse[ArticleResponse])
async def get_article(article_id: UUID, db: DbSession) -> ApiResponse[ArticleResponse]:
    article = await db.get(Article, article_id)
    if article is None:
        raise AppError("article not found", code=404)
    return success(ArticleResponse.model_validate(article))
