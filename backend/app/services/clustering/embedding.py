import logging
import os
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.models.article_insight import ArticleInsight
from app.services.clustering.text_utils import article_rerank_text

logger = logging.getLogger(__name__)

_embedder = None


def _get_embedder(settings: Settings):
    global _embedder
    if _embedder is None:
        os.environ.setdefault("HF_HOME", settings.hf_home)
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model: %s", settings.embedding_model)
        _embedder = SentenceTransformer(settings.embedding_model)
    return _embedder


def embed_text(text: str, settings: Settings | None = None) -> list[float]:
    settings = settings or get_settings()
    model = _get_embedder(settings)
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


class EmbeddingService:
    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self._session = session
        self._settings = settings or get_settings()

    def embed_insight(self, insight: ArticleInsight, article: Article) -> None:
        text = article_rerank_text(article)
        if not text.strip():
            return
        vector = embed_text(text, self._settings)
        insight.embedding = vector
        insight.embedding_model = self._settings.embedding_model
        insight.embedded_at = datetime.now(UTC)

    def embed_article(self, article_id: uuid.UUID) -> bool:
        article = self._session.scalar(
            select(Article)
            .options(selectinload(Article.insight))
            .where(Article.id == article_id)
        )
        if article is None or article.insight is None:
            return False
        if article.insight.embedding is not None:
            return True
        self.embed_insight(article.insight, article)
        self._session.commit()
        return True

    def embed_pending(self, *, limit: int = 50) -> dict[str, int]:
        rows = self._session.scalars(
            select(Article)
            .join(ArticleInsight, ArticleInsight.article_id == Article.id)
            .options(selectinload(Article.insight))
            .where(
                Article.status == "extracted",
                ArticleInsight.embedding.is_(None),
            )
            .order_by(Article.fetched_at.asc())
            .limit(limit)
        ).all()
        embedded = 0
        failed = 0
        for article in rows:
            try:
                if article.insight is None:
                    continue
                self.embed_insight(article.insight, article)
                embedded += 1
            except Exception:
                logger.exception("Failed to embed article %s", article.id)
                failed += 1
                self._session.rollback()
        if embedded:
            self._session.commit()
        return {"embedded": embedded, "failed": failed}
