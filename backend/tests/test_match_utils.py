import uuid
from datetime import UTC, datetime

from app.models.article import Article
from app.models.article_insight import ArticleInsight
from app.models.story_cluster import StoryCluster, StoryClusterArticle
from app.models.tag import Tag
from app.services.clustering.match_utils import cluster_matches_tag


def test_cluster_matches_tag_by_member_feed_tag() -> None:
    tag = Tag(
        id=uuid.uuid4(),
        slug="tech",
        name="科技",
        taxonomy_slugs=["technology", "cyber"],
    )
    article = Article(
        id=uuid.uuid4(),
        feed_source_id=uuid.uuid4(),
        tag_id=tag.id,
        title="A",
        url="https://a.com",
        fetched_at=datetime.now(UTC),
        status="extracted",
        dedup_key="a",
    )
    cluster = StoryCluster(
        id=uuid.uuid4(),
        tag_id=uuid.uuid4(),
        window_start=datetime.now(UTC),
        window_end=datetime.now(UTC),
        title="E",
        summary="S",
        article_count=1,
        sort_order=0,
    )
    member = StoryClusterArticle(
        id=uuid.uuid4(),
        story_cluster_id=cluster.id,
        article_id=article.id,
        role="primary",
        article=article,
    )
    cluster.members = [member]
    assert cluster_matches_tag(cluster, tag)


def test_cluster_matches_tag_by_content_tags_overlap() -> None:
    tag = Tag(
        id=uuid.uuid4(),
        slug="military",
        name="军事",
        taxonomy_slugs=["military_conflict", "politics"],
    )
    other_tag_id = uuid.uuid4()
    article = Article(
        id=uuid.uuid4(),
        feed_source_id=uuid.uuid4(),
        tag_id=other_tag_id,
        title="B",
        url="https://b.com",
        fetched_at=datetime.now(UTC),
        status="extracted",
        dedup_key="b",
    )
    insight = ArticleInsight(
        id=uuid.uuid4(),
        article_id=article.id,
        structured={},
        short_news_md="md",
        content_tags=["military_conflict", "diplomacy"],
    )
    article.insight = insight
    cluster = StoryCluster(
        id=uuid.uuid4(),
        tag_id=other_tag_id,
        window_start=datetime.now(UTC),
        window_end=datetime.now(UTC),
        title="E",
        summary="S",
        article_count=1,
        sort_order=0,
    )
    member = StoryClusterArticle(
        id=uuid.uuid4(),
        story_cluster_id=cluster.id,
        article_id=article.id,
        role="primary",
        article=article,
    )
    cluster.members = [member]
    assert cluster_matches_tag(cluster, tag)
