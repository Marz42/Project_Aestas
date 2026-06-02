import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.models.article import Article
from app.models.tag import Tag
from app.services.extraction.schemas import ArticleInsightStructured
from app.services.extraction.service import ExtractionService


@pytest.fixture
def article_with_tag() -> tuple[Article, Tag]:
    tag = Tag(id=uuid.uuid4(), slug="tech", name="科技")
    article = Article(
        id=uuid.uuid4(),
        feed_source_id=uuid.uuid4(),
        tag_id=tag.id,
        title="Article",
        url="https://example.com/a",
        summary_raw="x" * 50,
        content_md=None,
        published_at=None,
        fetched_at=None,
        status="pending",
        dedup_key="key-a",
    )
    article.insight = None
    return article, tag


def test_extract_article_skips_short_content(article_with_tag: tuple[Article, Tag]) -> None:
    article, _tag = article_with_tag
    article.summary_raw = "short"
    session = MagicMock()
    session.scalar.return_value = article

    result = ExtractionService(session).extract_article(article.id)
    assert result is None
    assert article.status == "skipped"


def test_extract_article_calls_deepseek(article_with_tag: tuple[Article, Tag]) -> None:
    article, tag = article_with_tag
    session = MagicMock()
    session.scalar.return_value = article
    session.get.return_value = tag

    structured = ArticleInsightStructured(
        headline="H",
        summary="S",
        key_facts=["f"],
        why_it_matters="w",
        source_url=article.url,
    )

    with patch(
        "app.services.extraction.service.call_deepseek_for_insight",
        return_value=structured,
    ):
        insight = ExtractionService(session).extract_article(article.id)

    assert insight is not None
    session.add.assert_called()
    assert article.status == "extracted"
