import logging
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.core.time_windows import current_brief_window
from app.models.article import Article
from app.models.story_cluster import StoryCluster, StoryClusterArticle
from app.models.tag import Tag
from app.models.tag_brief import TagBrief, TagBriefItem
from app.services.briefing.markdown import render_cluster_brief_md
from app.services.clustering.llm_grouping import call_brief_intro_llm
from app.services.clustering.match_utils import cluster_matches_tag
from app.services.clustering.service import ClusteringService
from app.services.prompt_loader import load_prompt_by_purpose

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

    def _load_clusters(
        self,
        tag: Tag,
        window_start: datetime,
        window_end: datetime,
    ) -> list[StoryCluster]:
        clusters = list(
            self._session.scalars(
                select(StoryCluster)
                .options(
                    selectinload(StoryCluster.members)
                    .selectinload(StoryClusterArticle.article)
                    .selectinload(Article.feed_source),
                    selectinload(StoryCluster.members)
                    .selectinload(StoryClusterArticle.article)
                    .selectinload(Article.insight),
                )
                .where(
                    StoryCluster.window_start < window_end,
                    StoryCluster.window_end > window_start,
                )
                .order_by(StoryCluster.sort_order)
            ).all()
        )
        return [c for c in clusters if cluster_matches_tag(c, tag)]

    def _generate_intro(
        self,
        tag: Tag,
        window_start: datetime,
        window_end: datetime,
        clusters: list[StoryCluster],
    ) -> str:
        if not clusters:
            return ""
        lines = [
            f"- {c.title}: {c.summary[:200]}"
            for c in clusters[:30]
        ]
        template = load_prompt_by_purpose(self._session, "briefing_intro")
        try:
            return call_brief_intro_llm(
                tag,
                window_start,
                window_end,
                "\n".join(lines),
                template=template,
                settings=self._settings,
            )
        except Exception:
            logger.exception("Failed to generate intro for tag %s", tag.slug)
            return "\n".join(lines[:5])

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

        clustering = ClusteringService(self._session, self._settings)
        if clustering._settings.clustering_mode.lower() == "llm":
            clustering.cluster_for_tag(
                tag_id,
                window_start=window_start,
                window_end=window_end,
                force=force,
            )
        elif force:
            clustering.cluster_window(
                window_start=window_start,
                window_end=window_end,
                force=True,
            )
        clusters = self._load_clusters(tag, window_start, window_end)
        intro_md = self._generate_intro(tag, window_start, window_end, clusters)
        article_count = sum(c.article_count for c in clusters)
        content_md = render_cluster_brief_md(
            tag,
            window_start,
            window_end,
            clusters,
            intro_md=intro_md,
            article_count=article_count,
        )
        title = f"{tag.name} 简报 · {window_start.strftime('%Y-%m-%d %H:%M')} UTC"

        brief = TagBrief(
            tag_id=tag_id,
            window_start=window_start,
            window_end=window_end,
            title=title,
            intro_md=intro_md,
            content_md=content_md,
            status="generated",
        )
        self._session.add(brief)
        self._session.flush()

        for order, cluster in enumerate(clusters):
            self._session.add(
                TagBriefItem(
                    tag_brief_id=brief.id,
                    story_cluster_id=cluster.id,
                    article_id=None,
                    sort_order=order,
                )
            )

        self._session.commit()
        self._session.refresh(brief)
        logger.info(
            "Generated brief for tag %s: clusters=%s articles=%s",
            tag.slug,
            len(clusters),
            article_count,
        )
        return brief, len(clusters)

    def generate_all_tags(
        self,
        *,
        force: bool = False,
    ) -> list[BriefingStats]:
        tags = self._session.scalars(select(Tag).order_by(Tag.slug)).all()
        window_start, window_end = current_brief_window(self._settings)
        clustering = ClusteringService(self._session, self._settings)
        if clustering._settings.clustering_mode.lower() != "llm":
            try:
                clustering.cluster_window(
                    window_start=window_start,
                    window_end=window_end,
                    force=force,
                )
            except Exception:
                logger.exception("Vector clustering failed before generate_all_tags")
                self._session.rollback()

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
