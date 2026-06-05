import uuid
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings


def ann_search_candidates(
    session: Session,
    *,
    article_id: uuid.UUID,
    query_vector: list[float],
    content_tags: list[str],
    window_start: datetime,
    window_end: datetime,
    top_k: int | None = None,
    settings: Settings | None = None,
) -> list[uuid.UUID]:
    settings = settings or get_settings()
    limit = top_k or settings.ann_top_k
    if not content_tags:
        return []

    vector_literal = "[" + ",".join(str(v) for v in query_vector) + "]"
    result = session.execute(
        text(
            """
            SELECT a.id
            FROM article_insights i
            JOIN articles a ON a.id = i.article_id
            WHERE i.content_tags && CAST(:content_tags AS varchar[])
              AND a.fetched_at >= :window_start
              AND a.fetched_at < :window_end
              AND a.status = 'extracted'
              AND a.id != :article_id
              AND i.embedding IS NOT NULL
            ORDER BY i.embedding <=> CAST(:query_vec AS vector)
            LIMIT :top_k
            """
        ),
        {
            "content_tags": content_tags,
            "window_start": window_start,
            "window_end": window_end,
            "article_id": article_id,
            "query_vec": vector_literal,
            "top_k": limit,
        },
    )
    return [row[0] for row in result.fetchall()]
