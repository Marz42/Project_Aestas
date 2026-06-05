import logging
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.core.time_windows import current_brief_window
from app.models.article import Article
from app.models.story_cluster import StoryCluster, StoryClusterArticle
from app.models.tag import Tag
from app.services.clustering.incremental_cluster import IncrementalClusterEngine
from app.services.clustering.llm_grouping import call_clustering_llm
from app.services.clustering.match_utils import cluster_matches_tag
from app.services.prompt_loader import load_prompt_by_purpose

logger = logging.getLogger(__name__)


@dataclass
class ClusteringStats:
    tag_id: uuid.UUID
    cluster_count: int
    article_count: int
    created: bool


class ClusteringService:
    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self._session = session
        self._settings = settings or get_settings()

    def _articles_in_window(
        self,
        tag_id: uuid.UUID,
        window_start: datetime,
        window_end: datetime,
    ) -> list[Article]:
        return list(
            self._session.scalars(
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
        )

    def _clear_clusters_for_tag(
        self,
        tag_id: uuid.UUID,
        window_start: datetime,
    ) -> None:
        cluster_ids = list(
            self._session.scalars(
                select(StoryCluster.id).where(
                    StoryCluster.tag_id == tag_id,
                    StoryCluster.window_start == window_start,
                )
            ).all()
        )
        if not cluster_ids:
            return
        self._session.execute(
            delete(StoryClusterArticle).where(
                StoryClusterArticle.story_cluster_id.in_(cluster_ids)
            )
        )
        self._session.execute(
            delete(StoryCluster).where(StoryCluster.id.in_(cluster_ids))
        )
        articles = self._session.scalars(
            select(Article).where(Article.story_cluster_id.in_(cluster_ids))
        ).all()
        for article in articles:
            article.story_cluster_id = None
        self._session.flush()

    def _solo_clusters(
        self,
        tag: Tag,
        window_start: datetime,
        window_end: datetime,
        articles: list[Article],
    ) -> list[StoryCluster]:
        clusters: list[StoryCluster] = []
        for order, article in enumerate(articles):
            structured = article.insight.structured if article.insight else {}
            title = structured.get("headline", article.title)
            summary = structured.get("summary", article.title)
            cluster = StoryCluster(
                tag_id=tag.id,
                window_start=window_start,
                window_end=window_end,
                title=title,
                summary=summary,
                article_count=1,
                sort_order=order,
            )
            self._session.add(cluster)
            self._session.flush()
            self._session.add(
                StoryClusterArticle(
                    story_cluster_id=cluster.id,
                    article_id=article.id,
                    role="primary",
                )
            )
            article.story_cluster_id = cluster.id
            clusters.append(cluster)
        self._session.commit()
        return clusters

    def _cluster_for_tag_llm(
        self,
        tag: Tag,
        window_start: datetime,
        window_end: datetime,
        *,
        force: bool = False,
    ) -> list[StoryCluster]:
        existing = self._session.scalar(
            select(StoryCluster.id)
            .where(
                StoryCluster.tag_id == tag.id,
                StoryCluster.window_start == window_start,
            )
            .limit(1)
        )
        if existing and not force:
            return list(
                self._session.scalars(
                    select(StoryCluster)
                    .where(
                        StoryCluster.tag_id == tag.id,
                        StoryCluster.window_start == window_start,
                    )
                    .order_by(StoryCluster.sort_order)
                ).all()
            )
        if existing and force:
            self._clear_clusters_for_tag(tag.id, window_start)

        articles = self._articles_in_window(tag.id, window_start, window_end)
        if not articles:
            return []

        template = load_prompt_by_purpose(self._session, "clustering")
        try:
            result = call_clustering_llm(
                tag, window_start, window_end, articles, template=template
            )
        except Exception:
            logger.exception(
                "LLM clustering failed for tag %s, using solo clusters", tag.slug
            )
            self._session.rollback()
            return self._solo_clusters(tag, window_start, window_end, articles)

        id_to_article = {str(a.id): a for a in articles}
        assigned: set[str] = set()
        clusters: list[StoryCluster] = []

        for order, group in enumerate(result.groups):
            member_ids = [aid for aid in group.article_ids if aid in id_to_article]
            if not member_ids:
                continue
            cluster = StoryCluster(
                tag_id=tag.id,
                window_start=window_start,
                window_end=window_end,
                title=group.title,
                summary=group.summary,
                article_count=len(member_ids),
                sort_order=order,
            )
            self._session.add(cluster)
            self._session.flush()
            for idx, aid in enumerate(member_ids):
                article = id_to_article[aid]
                role = "primary" if idx == 0 else "supporting"
                self._session.add(
                    StoryClusterArticle(
                        story_cluster_id=cluster.id,
                        article_id=article.id,
                        role=role,
                    )
                )
                article.story_cluster_id = cluster.id
                assigned.add(aid)
            clusters.append(cluster)

        for order, article in enumerate(
            [a for a in articles if str(a.id) not in assigned],
            start=len(clusters),
        ):
            structured = article.insight.structured if article.insight else {}
            cluster = StoryCluster(
                tag_id=tag.id,
                window_start=window_start,
                window_end=window_end,
                title=structured.get("headline", article.title),
                summary=structured.get("summary", ""),
                article_count=1,
                sort_order=order,
            )
            self._session.add(cluster)
            self._session.flush()
            self._session.add(
                StoryClusterArticle(
                    story_cluster_id=cluster.id,
                    article_id=article.id,
                    role="primary",
                )
            )
            article.story_cluster_id = cluster.id
            clusters.append(cluster)

        self._session.commit()
        logger.info(
            "LLM clustered tag %s: clusters=%s articles=%s",
            tag.slug,
            len(clusters),
            len(articles),
        )
        return clusters

    def cluster_window(
        self,
        *,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
        force: bool = False,
    ) -> list[StoryCluster]:
        if window_start is None or window_end is None:
            window_start, window_end = current_brief_window(self._settings)
        return IncrementalClusterEngine(self._session, self._settings).run(
            window_start,
            window_end,
            force=force,
        )

    def _clusters_for_tag(
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
                    .selectinload(Article.insight)
                )
                .where(
                    StoryCluster.window_start < window_end,
                    StoryCluster.window_end > window_start,
                )
                .order_by(StoryCluster.sort_order)
            ).all()
        )
        return [c for c in clusters if cluster_matches_tag(c, tag)]

    def cluster_for_tag(
        self,
        tag_id: uuid.UUID,
        *,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
        force: bool = False,
        mode: str | None = None,
    ) -> list[StoryCluster]:
        tag = self._session.get(Tag, tag_id)
        if tag is None:
            raise ValueError(f"Tag not found: {tag_id}")

        if window_start is None or window_end is None:
            window_start, window_end = current_brief_window(self._settings)

        clustering_mode = (mode or self._settings.clustering_mode).lower()
        if clustering_mode == "llm":
            return self._cluster_for_tag_llm(
                tag, window_start, window_end, force=force
            )

        self.cluster_window(
            window_start=window_start,
            window_end=window_end,
            force=force,
        )
        return self._clusters_for_tag(tag, window_start, window_end)

    def cluster_all_tags(
        self,
        *,
        force: bool = False,
        mode: str | None = None,
    ) -> list[ClusteringStats]:
        tags = self._session.scalars(select(Tag).order_by(Tag.slug)).all()
        window_start, window_end = current_brief_window(self._settings)
        clustering_mode = (mode or self._settings.clustering_mode).lower()

        if clustering_mode == "llm":
            results: list[ClusteringStats] = []
            for tag in tags:
                try:
                    clusters = self._cluster_for_tag_llm(
                        tag, window_start, window_end, force=force
                    )
                    article_count = sum(c.article_count for c in clusters)
                    results.append(
                        ClusteringStats(
                            tag_id=tag.id,
                            cluster_count=len(clusters),
                            article_count=article_count,
                            created=True,
                        )
                    )
                except Exception:
                    logger.exception("Failed LLM clustering for tag %s", tag.slug)
                    self._session.rollback()
                    results.append(
                        ClusteringStats(
                            tag_id=tag.id,
                            cluster_count=0,
                            article_count=0,
                            created=False,
                        )
                    )
            return results

        try:
            all_clusters = self.cluster_window(
                window_start=window_start,
                window_end=window_end,
                force=force,
            )
            loaded = list(
                self._session.scalars(
                    select(StoryCluster)
                    .options(
                        selectinload(StoryCluster.members)
                        .selectinload(StoryClusterArticle.article)
                        .selectinload(Article.insight)
                    )
                    .where(
                        StoryCluster.window_start < window_end,
                        StoryCluster.window_end > window_start,
                    )
                ).all()
            )
            results = []
            for tag in tags:
                matched = [c for c in loaded if cluster_matches_tag(c, tag)]
                article_count = sum(c.article_count for c in matched)
                results.append(
                    ClusteringStats(
                        tag_id=tag.id,
                        cluster_count=len(matched),
                        article_count=article_count,
                        created=bool(all_clusters),
                    )
                )
            return results
        except Exception:
            logger.exception("Vector clustering failed for window")
            self._session.rollback()
            return [
                ClusteringStats(
                    tag_id=tag.id,
                    cluster_count=0,
                    article_count=0,
                    created=False,
                )
                for tag in tags
            ]
