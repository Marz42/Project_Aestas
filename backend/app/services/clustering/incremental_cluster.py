import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.models.story_cluster import StoryCluster, StoryClusterArticle
from app.models.tag import Tag
from app.services.clustering.ann_search import ann_search_candidates
from app.services.clustering.cluster_title import polish_cluster_title
from app.services.clustering.embedding import EmbeddingService
from app.services.clustering.reranker import score_articles
from app.services.clustering.text_utils import article_content_tags
from app.services.prompt_loader import load_prompt_by_purpose

logger = logging.getLogger(__name__)


@dataclass
class _WorkingCluster:
    cluster_id: uuid.UUID
    tag_id: uuid.UUID
    member_ids: list[uuid.UUID] = field(default_factory=list)


class IncrementalClusterEngine:
    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self._session = session
        self._settings = settings or get_settings()
        self._article_map: dict[uuid.UUID, Article] = {}
        self._assigned: dict[uuid.UUID, uuid.UUID] = {}
        self._clusters: dict[uuid.UUID, _WorkingCluster] = {}

    def _clear_window(self, window_start: datetime, window_end: datetime) -> None:
        """Remove clusters overlapping [window_start, window_end).

        Uses overlap (not exact window_start equality) because brief windows are
        rolling; older LLM clusters may share articles but use a different
        window_start timestamp.
        """
        cluster_ids = list(
            self._session.scalars(
                select(StoryCluster.id).where(
                    StoryCluster.window_start < window_end,
                    StoryCluster.window_end > window_start,
                )
            ).all()
        )
        if not cluster_ids:
            article_ids = list(
                self._session.scalars(
                    select(Article.id).where(
                        Article.fetched_at >= window_start,
                        Article.fetched_at < window_end,
                    )
                ).all()
            )
            if article_ids:
                self._session.execute(
                    delete(StoryClusterArticle).where(
                        StoryClusterArticle.article_id.in_(article_ids)
                    )
                )
                for article in self._session.scalars(
                    select(Article).where(Article.id.in_(article_ids))
                ).all():
                    article.story_cluster_id = None
                self._session.flush()
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

    def _load_articles(
        self,
        window_start: datetime,
        window_end: datetime,
    ) -> list[Article]:
        articles = list(
            self._session.scalars(
                select(Article)
                .options(
                    selectinload(Article.insight),
                    selectinload(Article.tag),
                )
                .where(
                    Article.status == "extracted",
                    Article.fetched_at >= window_start,
                    Article.fetched_at < window_end,
                )
                .order_by(Article.fetched_at.asc())
            ).all()
        )
        self._article_map = {a.id: a for a in articles}
        return articles

    def _ensure_embeddings(self, articles: list[Article]) -> None:
        embedder = EmbeddingService(self._session, self._settings)
        for article in articles:
            if article.insight and article.insight.embedding is None:
                embedder.embed_insight(article.insight, article)
        self._session.flush()

    def _cluster_members(self, cluster_id: uuid.UUID) -> list[Article]:
        wc = self._clusters[cluster_id]
        return [self._article_map[mid] for mid in wc.member_ids if mid in self._article_map]

    def _score_against_members(
        self,
        source: Article,
        members: list[Article],
    ) -> tuple[float, float]:
        if not members:
            return 0.0, 0.0
        scored = score_articles(source, members, self._settings)
        values = [score for _, score in scored]
        return max(values), sum(values) / len(values)

    def _create_cluster(
        self,
        members: list[Article],
        window_start: datetime,
        window_end: datetime,
        sort_order: int,
    ) -> uuid.UUID:
        primary = members[0]
        tag = self._session.get(Tag, primary.tag_id)
        structured = primary.insight.structured if primary.insight else {}
        title = structured.get("headline", primary.title)
        summary = structured.get("summary", "")
        cluster = StoryCluster(
            tag_id=primary.tag_id,
            window_start=window_start,
            window_end=window_end,
            title=title,
            summary=summary,
            article_count=len(members),
            sort_order=sort_order,
        )
        self._session.add(cluster)
        self._session.flush()

        for idx, article in enumerate(members):
            if article.id in self._assigned:
                logger.warning(
                    "Skip duplicate cluster member %s (already in cluster %s)",
                    article.id,
                    self._assigned[article.id],
                )
                continue
            role = "primary" if idx == 0 else "supporting"
            self._session.add(
                StoryClusterArticle(
                    story_cluster_id=cluster.id,
                    article_id=article.id,
                    role=role,
                )
            )
            article.story_cluster_id = cluster.id
            self._assigned[article.id] = cluster.id

        self._clusters[cluster.id] = _WorkingCluster(
            cluster_id=cluster.id,
            tag_id=primary.tag_id,
            member_ids=[m.id for m in members],
        )
        return cluster.id

    def _maybe_polish_title(self, cluster_id: uuid.UUID) -> None:
        cluster = self._session.get(StoryCluster, cluster_id)
        if cluster is None:
            return
        members = self._cluster_members(cluster_id)
        if not members:
            return
        template = load_prompt_by_purpose(self._session, "cluster_title")
        try:
            title, summary = polish_cluster_title(
                cluster, members, template=template, settings=self._settings
            )
            cluster.title = title
            cluster.summary = summary
        except Exception:
            logger.exception("Cluster title polish failed for %s", cluster_id)

    def _assign_to_cluster(
        self,
        article: Article,
        cluster_id: uuid.UUID,
    ) -> None:
        if article.id in self._assigned:
            return
        wc = self._clusters[cluster_id]
        wc.member_ids.append(article.id)
        cluster = self._session.get(StoryCluster, cluster_id)
        if cluster:
            cluster.article_count = len(wc.member_ids)
        self._session.add(
            StoryClusterArticle(
                story_cluster_id=cluster_id,
                article_id=article.id,
                role="supporting",
            )
        )
        article.story_cluster_id = cluster_id
        self._assigned[article.id] = cluster_id

    def run(
        self,
        window_start: datetime,
        window_end: datetime,
        *,
        force: bool = False,
    ) -> list[StoryCluster]:
        if force:
            self._clear_window(window_start, window_end)
        else:
            existing = self._session.scalar(
                select(StoryCluster.id)
                .where(
                    StoryCluster.window_start < window_end,
                    StoryCluster.window_end > window_start,
                )
                .limit(1)
            )
            if existing:
                return list(
                    self._session.scalars(
                        select(StoryCluster)
                        .where(
                            StoryCluster.window_start < window_end,
                            StoryCluster.window_end > window_start,
                        )
                        .order_by(StoryCluster.sort_order)
                    ).all()
                )

        articles = self._load_articles(window_start, window_end)
        if not articles:
            return []

        self._ensure_embeddings(articles)
        missing_tags = sum(
            1
            for a in articles
            if not (
                (a.insight and a.insight.content_tags)
                or (a.insight and (a.insight.structured or {}).get("content_tags"))
            )
        )
        missing_embed = sum(
            1
            for a in articles
            if not a.insight or a.insight.embedding is None
        )
        if missing_tags or missing_embed:
            logger.warning(
                "Vector cluster window %s–%s: %s articles, %s missing content_tags, %s missing embedding (reextract/embed-pending)",
                window_start,
                window_end,
                len(articles),
                missing_tags,
                missing_embed,
            )
        pair_threshold = self._settings.rerank_pair_threshold
        avg_min = self._settings.rerank_cluster_avg_min
        sort_order = 0

        for article in articles:
            if article.id in self._assigned:
                continue
            if not article.insight or article.insight.embedding is None:
                self._create_cluster(
                    [article], window_start, window_end, sort_order
                )
                sort_order += 1
                continue

            tags = article_content_tags(article)

            candidate_ids = ann_search_candidates(
                self._session,
                article_id=article.id,
                query_vector=list(article.insight.embedding),
                content_tags=tags,
                window_start=window_start,
                window_end=window_end,
                settings=self._settings,
            )
            candidates = [
                self._article_map[cid]
                for cid in candidate_ids
                if cid in self._article_map
            ]
            scored = score_articles(article, candidates, self._settings)

            best_cluster_id: uuid.UUID | None = None
            best_avg = -1.0

            for candidate, pair_score in scored:
                if pair_score < pair_threshold:
                    continue
                if candidate.id not in self._assigned:
                    continue
                cluster_id = self._assigned[candidate.id]
                members = self._cluster_members(cluster_id)
                pair_max, avg_score = self._score_against_members(article, members)
                if pair_max < pair_threshold or avg_score < avg_min:
                    continue
                if avg_score > best_avg:
                    best_avg = avg_score
                    best_cluster_id = cluster_id

            if best_cluster_id is not None:
                self._assign_to_cluster(article, best_cluster_id)
                continue

            best_pair: Article | None = None
            best_pair_score = pair_threshold
            for candidate, pair_score in scored:
                if candidate.id == article.id:
                    continue
                if candidate.id in self._assigned:
                    continue
                if pair_score >= best_pair_score:
                    best_pair_score = pair_score
                    best_pair = candidate

            if best_pair is not None:
                self._create_cluster(
                    [article, best_pair],
                    window_start,
                    window_end,
                    sort_order,
                )
                sort_order += 1
                continue

            self._create_cluster([article], window_start, window_end, sort_order)
            sort_order += 1

        for cluster_id in list(self._clusters.keys()):
            self._maybe_polish_title(cluster_id)

        self._session.commit()
        logger.info(
            "Vector clustering done: %s clusters for window %s–%s",
            len(self._clusters),
            window_start,
            window_end,
        )
        return list(
            self._session.scalars(
                select(StoryCluster)
                .where(
                    StoryCluster.window_start < window_end,
                    StoryCluster.window_end > window_start,
                )
                .order_by(StoryCluster.sort_order)
            ).all()
        )
