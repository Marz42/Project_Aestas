import uuid
from datetime import UTC, datetime

from app.models.article import Article
from app.models.feed_source import FeedSource
from app.models.story_cluster import StoryCluster, StoryClusterArticle
from app.models.tag import Tag
from app.services.briefing.markdown import render_cluster_brief_md


def test_render_cluster_brief_md_multi_source() -> None:
    tag = Tag(id=uuid.uuid4(), slug="military", name="军事")
    feed_a = FeedSource(
        id=uuid.uuid4(),
        tag_id=tag.id,
        name="BBC",
        feed_url="https://bbc.com/rss",
    )
    feed_b = FeedSource(
        id=uuid.uuid4(),
        tag_id=tag.id,
        name="TWZ",
        feed_url="https://twz.com/feed",
    )
    article_a = Article(
        id=uuid.uuid4(),
        feed_source_id=feed_a.id,
        tag_id=tag.id,
        title="A",
        url="https://bbc.com/1",
        fetched_at=datetime.now(UTC),
        status="extracted",
        dedup_key="a",
        feed_source=feed_a,
    )
    article_b = Article(
        id=uuid.uuid4(),
        feed_source_id=feed_b.id,
        tag_id=tag.id,
        title="B",
        url="https://twz.com/1",
        fetched_at=datetime.now(UTC),
        status="extracted",
        dedup_key="b",
        feed_source=feed_b,
    )
    cluster = StoryCluster(
        id=uuid.uuid4(),
        tag_id=tag.id,
        window_start=datetime(2026, 6, 2, 0, 0, tzinfo=UTC),
        window_end=datetime(2026, 6, 2, 8, 0, tzinfo=UTC),
        title="航母部署",
        summary="多源报道同一部署事件。",
        article_count=2,
        sort_order=0,
    )
    member_a = StoryClusterArticle(
        id=uuid.uuid4(),
        story_cluster_id=cluster.id,
        article_id=article_a.id,
        role="primary",
        article=article_a,
    )
    member_b = StoryClusterArticle(
        id=uuid.uuid4(),
        story_cluster_id=cluster.id,
        article_id=article_b.id,
        role="supporting",
        article=article_b,
    )
    cluster.members = [member_a, member_b]

    md = render_cluster_brief_md(
        tag,
        cluster.window_start,
        cluster.window_end,
        [cluster],
        intro_md="本期军事板块综述。",
        article_count=2,
    )
    assert "## 本期综述" in md
    assert "航母部署" in md
    assert "https://bbc.com/1" in md
    assert "https://twz.com/1" in md
    assert "1 个事件" in md
    assert "2 篇报道" in md
