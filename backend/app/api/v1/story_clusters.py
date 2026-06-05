import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.deps import DbSession, verify_api_key
from app.core.response import ApiResponse, success
from app.models.article import Article
from app.models.story_cluster import StoryCluster, StoryClusterArticle
from app.models.tag import Tag

router = APIRouter(prefix="/story-clusters", dependencies=[Depends(verify_api_key)])


class ClusterArticleItem(BaseModel):
    article_id: uuid.UUID
    title: str
    url: str
    source_name: str | None
    role: str


class StoryClusterResponse(BaseModel):
    id: uuid.UUID
    tag_id: uuid.UUID
    tag_name: str | None = None
    window_start: datetime
    window_end: datetime
    title: str
    summary: str
    article_count: int
    sort_order: int
    articles: list[ClusterArticleItem] = []


def _to_response(cluster: StoryCluster, tag_name: str | None) -> StoryClusterResponse:
    articles: list[ClusterArticleItem] = []
    for member in cluster.members:
        article = member.article
        if article is None:
            continue
        source_name = article.feed_source.name if article.feed_source else None
        articles.append(
            ClusterArticleItem(
                article_id=article.id,
                title=article.title,
                url=article.url,
                source_name=source_name,
                role=member.role,
            )
        )
    return StoryClusterResponse(
        id=cluster.id,
        tag_id=cluster.tag_id,
        tag_name=tag_name,
        window_start=cluster.window_start,
        window_end=cluster.window_end,
        title=cluster.title,
        summary=cluster.summary,
        article_count=cluster.article_count,
        sort_order=cluster.sort_order,
        articles=articles,
    )


@router.get("", response_model=ApiResponse[dict])
async def list_story_clusters(
    db: DbSession,
    tag_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[dict]:
    query = (
        select(StoryCluster)
        .options(
            selectinload(StoryCluster.members)
            .selectinload(StoryClusterArticle.article)
            .selectinload(Article.feed_source)
        )
        .order_by(StoryCluster.window_start.desc(), StoryCluster.sort_order)
    )
    if tag_id:
        query = query.where(StoryCluster.tag_id == tag_id)

    count_q = select(func.count()).select_from(StoryCluster)
    if tag_id:
        count_q = count_q.where(StoryCluster.tag_id == tag_id)
    total = int(await db.scalar(count_q) or 0)
    items = (
        await db.scalars(query.offset((page - 1) * page_size).limit(page_size))
    ).all()
    tag_names: dict[uuid.UUID, str] = {}
    for cluster in items:
        if cluster.tag_id not in tag_names:
            tag = await db.get(Tag, cluster.tag_id)
            tag_names[cluster.tag_id] = tag.name if tag else ""

    return success(
        {
            "items": [
                _to_response(c, tag_names.get(c.tag_id)).model_dump()
                for c in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/{cluster_id}", response_model=ApiResponse[StoryClusterResponse])
async def get_story_cluster(
    cluster_id: uuid.UUID,
    db: DbSession,
) -> ApiResponse[StoryClusterResponse]:
    cluster = await db.scalar(
        select(StoryCluster)
        .options(
            selectinload(StoryCluster.members)
            .selectinload(StoryClusterArticle.article)
            .selectinload(Article.feed_source)
        )
        .where(StoryCluster.id == cluster_id)
    )
    if cluster is None:
        from app.core.exceptions import AppError

        raise AppError("story cluster not found", code=404)
    tag = await db.get(Tag, cluster.tag_id)
    return success(_to_response(cluster, tag.name if tag else None))
