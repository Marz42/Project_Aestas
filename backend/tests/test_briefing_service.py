import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.models.article import Article
from app.models.article_insight import ArticleInsight
from app.models.tag import Tag
from app.models.tag_brief import TagBrief
from app.services.briefing.service import BriefingService


def test_generate_for_tag_creates_brief() -> None:
    tag = Tag(id=uuid.uuid4(), slug="tech", name="科技")
    article = Article(
        id=uuid.uuid4(),
        feed_source_id=uuid.uuid4(),
        tag_id=tag.id,
        title="T",
        url="https://example.com/1",
        summary_raw="s",
        content_md=None,
        published_at=None,
        fetched_at=datetime.now(UTC),
        status="extracted",
        dedup_key="d1",
    )
    insight = ArticleInsight(
        id=uuid.uuid4(),
        article_id=article.id,
        structured={"headline": "H", "summary": "S", "key_facts": [], "why_it_matters": "W"},
        short_news_md="md",
    )
    article.insight = insight

    session = MagicMock()
    session.get.return_value = tag
    session.scalar.return_value = None
    session.scalars.return_value.all.return_value = [article]

    brief, count = BriefingService(session).generate_for_tag(
        tag.id,
        window_start=datetime(2020, 1, 1, tzinfo=UTC),
        window_end=datetime(2030, 1, 1, tzinfo=UTC),
    )

    assert isinstance(brief, TagBrief)
    assert count == 1
    assert "科技 简报" in brief.content_md
    session.commit.assert_called()
