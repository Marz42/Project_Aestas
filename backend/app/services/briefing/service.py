import logging
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.core.time_windows import current_brief_window
from app.models.article import Article
from app.models.article_insight import ArticleInsight
from app.models.tag import Tag
from app.models.tag_brief import TagBrief, TagBriefItem
from app.services.briefing.markdown import render_tag_brief_md

logger = logging.getLogger(__name__)


@dataclass
class BriefingStats:
    tag_id: uuid.UUID
    brief_id: uuid.UUID | None
    item_count: int
    created: bool


class BriefingService:
    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self._session = session
        self._settings = settings or get_settings()

    def generate_for_tag(
        self,
        tag_id: uuid.UUID,
        *,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
        force: bool = False,
    ) -> tuple[TagBrief, int]:
        tag = self._session.get(Tag, tag_id)
        if tag is None:
            raise ValueError(f"Tag not found: {tag_id}")

        if window_start is None or window_end is None:
            window_start, window_end = current_brief_window(self._settings)

        existing = self._session.scalar(
            select(TagBrief).where(
                TagBrief.tag_id == tag_id,
                TagBrief.window_start == window_start,
            )
        )
        if existing and not force:
            item_count = int(
                self._session.scalar(
                    select(func.count())
                    .select_from(TagBriefItem)
                    .where(TagBriefItem.tag_brief_id == existing.id)
                )
                or 0
            )
            return existing, item_count
        if existing and force:
            self._session.delete(existing)
            self._session.flush()

        articles = self._session.scalars(
            select(Article)
            .options(selectinload(Article.insight))
            .where(
                Article.tag_id == tag_id,
                Article.status == "extracted",
                Article.fetched_at >= window_start,
                Article.fetched_at < window_end,
            )
            .order_by(Article.fetched_at.desc())
        ).all()

        rows: list[tuple[Article, ArticleInsight]] = []
        for article in articles:
            if article.insight is None:
                continue
            rows.append((article, article.insight))

        content_md = render_tag_brief_md(tag, window_start, window_end, rows)
        title = f"{tag.name} 简报 · {window_start.strftime('%Y-%m-%d %H:%M')} UTC"

        brief = TagBrief(
            tag_id=tag_id,
            window_start=window_start,
            window_end=window_end,
            title=title,
            content_md=content_md,
            status="generated",
        )
        self._session.add(brief)
        self._session.flush()

        for order, (article, _) in enumerate(rows):
            self._session.add(
                TagBriefItem(
                    tag_brief_id=brief.id,
                    article_id=article.id,
                    sort_order=order,
                )
            )

        self._session.commit()
        self._session.refresh(brief)
        logger.info(
            "Generated brief for tag %s: items=%s window=%s..%s",
            tag.slug,
            len(rows),
            window_start,
            window_end,
        )
        return brief, len(rows)

    def generate_all_tags(
        self,
        *,
        force: bool = False,
    ) -> list[BriefingStats]:
        tags = self._session.scalars(select(Tag).order_by(Tag.slug)).all()
        window_start, window_end = current_brief_window(self._settings)
        results: list[BriefingStats] = []

        for tag in tags:
            try:
                brief, item_count = self.generate_for_tag(
                    tag.id,
                    window_start=window_start,
                    window_end=window_end,
                    force=force,
                )
                results.append(
                    BriefingStats(
                        tag_id=tag.id,
                        brief_id=brief.id,
                        item_count=item_count,
                        created=True,
                    )
                )
            except Exception:
                logger.exception("Failed to generate brief for tag %s", tag.slug)
                self._session.rollback()
                results.append(
                    BriefingStats(
                        tag_id=tag.id,
                        brief_id=None,
                        item_count=0,
                        created=False,
                    )
                )

        return results
