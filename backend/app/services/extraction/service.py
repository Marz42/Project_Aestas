import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.models.article_insight import ArticleInsight
from app.models.tag import Tag
from app.services.extraction.llm_client import call_deepseek_for_insight
from app.services.extraction.markdown import render_short_news_md

logger = logging.getLogger(__name__)

MIN_CONTENT_CHARS = 40


@dataclass
class ExtractionStats:
    processed: int = 0
    skipped: int = 0
    failed: int = 0


class ExtractionService:
    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self._session = session
        self._settings = settings or get_settings()

    def extract_article(
        self,
        article_id: uuid.UUID,
        *,
        force: bool = False,
    ) -> ArticleInsight | None:
        article = self._session.scalar(
            select(Article)
            .options(selectinload(Article.insight))
            .where(Article.id == article_id)
        )
        if article is None:
            raise ValueError(f"Article not found: {article_id}")

        if article.insight and not force:
            return article.insight

        if force and article.insight:
            self._session.delete(article.insight)
            self._session.flush()
            article.status = "pending"

        tag = self._session.get(Tag, article.tag_id)
        if tag is None:
            raise ValueError(f"Tag not found for article {article_id}")

        body = (article.content_md or article.summary_raw or "").strip()
        if len(body) < MIN_CONTENT_CHARS:
            article.status = "skipped"
            self._session.commit()
            return None

        try:
            structured = call_deepseek_for_insight(
                article, tag, settings=self._settings
            )
            short_md = render_short_news_md(structured)
            if article.insight:
                self._session.delete(article.insight)
                self._session.flush()

            insight = ArticleInsight(
                article_id=article.id,
                structured=structured.model_dump(),
                short_news_md=short_md,
            )
            self._session.add(insight)
            article.status = "extracted"
            self._session.commit()
            self._session.refresh(insight)
            return insight
        except Exception:
            logger.exception("Failed to extract article %s", article_id)
            article.status = "failed"
            self._session.commit()
            raise

    def extract_pending(self, *, limit: int = 20) -> ExtractionStats:
        stats = ExtractionStats()
        pending = self._session.scalars(
            select(Article)
            .where(Article.status == "pending")
            .order_by(Article.fetched_at.asc())
            .limit(limit)
        ).all()

        for article in pending:
            try:
                result = self.extract_article(article.id)
                if result is None:
                    stats.skipped += 1
                else:
                    stats.processed += 1
            except Exception:
                stats.failed += 1
                self._session.rollback()

        return stats
