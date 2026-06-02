import uuid
from datetime import UTC, datetime

from app.models.article import Article
from app.models.article_insight import ArticleInsight
from app.models.tag import Tag
from app.services.briefing.markdown import render_tag_brief_md


def test_render_tag_brief_md_empty() -> None:
    tag = Tag(id=uuid.uuid4(), slug="tech", name="科技")
    start = datetime(2026, 6, 2, 0, 0, tzinfo=UTC)
    end = datetime(2026, 6, 2, 8, 0, tzinfo=UTC)
    md = render_tag_brief_md(tag, start, end, [])
    assert "科技 简报" in md
    assert "暂无" in md


def test_render_tag_brief_md_with_items() -> None:
    tag = Tag(id=uuid.uuid4(), slug="military", name="军事")
    article = Article(
        id=uuid.uuid4(),
        feed_source_id=uuid.uuid4(),
        tag_id=tag.id,
        title="Raw",
        url="https://example.com/x",
        summary_raw=None,
        content_md=None,
        published_at=None,
        fetched_at=datetime.now(UTC),
        status="extracted",
        dedup_key="k",
    )
    insight = ArticleInsight(
        id=uuid.uuid4(),
        article_id=article.id,
        structured={
            "headline": "Headline",
            "summary": "Summary text",
            "key_facts": ["fact"],
            "why_it_matters": "matter",
            "source_url": article.url,
        },
        short_news_md="",
    )
    start = datetime(2026, 6, 2, 0, 0, tzinfo=UTC)
    end = datetime(2026, 6, 2, 8, 0, tzinfo=UTC)
    md = render_tag_brief_md(tag, start, end, [(article, insight)])
    assert "## 1. Headline" in md
    assert article.url in md
