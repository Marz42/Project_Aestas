import uuid
from unittest.mock import MagicMock, patch

from app.models.article import Article
from app.models.tag import Tag
from app.services.extraction.llm_client import (
    call_deepseek_for_insight,
    completion_extra_body,
    create_openai_client,
)
from app.services.extraction.prompts import resolve_user_prompt
from app.services.extraction.schemas import ArticleInsightStructured


def test_build_user_prompt_contains_url() -> None:
    tag = Tag(id=uuid.uuid4(), slug="tech", name="科技")
    article = Article(
        id=uuid.uuid4(),
        feed_source_id=uuid.uuid4(),
        tag_id=tag.id,
        title="Title",
        url="https://example.com/news",
        summary_raw="body text",
        content_md=None,
        published_at=None,
        fetched_at=None,
        status="pending",
        dedup_key="k",
    )
    prompt = resolve_user_prompt(article, tag, None)
    assert "https://example.com/news" in prompt
    assert "科技" in prompt


def test_completion_extra_body_disables_thinking_for_v4() -> None:
    from app.core.config import Settings

    assert completion_extra_body(Settings(deepseek_model="deepseek-v4-flash")) == {
        "thinking": {"type": "disabled"}
    }
    assert completion_extra_body(Settings(deepseek_model="deepseek-chat")) is None


def test_create_openai_client_requires_api_key() -> None:
    from app.core.config import Settings

    settings = Settings(deepseek_api_key="")
    try:
        create_openai_client(settings)
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_call_deepseek_for_insight_sets_source_url() -> None:
    tag = Tag(id=uuid.uuid4(), slug="tech", name="科技")
    article = Article(
        id=uuid.uuid4(),
        feed_source_id=uuid.uuid4(),
        tag_id=tag.id,
        title="T",
        url="https://example.com/x",
        summary_raw="x" * 80,
        content_md=None,
        published_at=None,
        fetched_at=None,
        status="pending",
        dedup_key="k",
    )
    parsed = ArticleInsightStructured(
        headline="H",
        summary="S",
        key_facts=[],
        why_it_matters="W",
        source_url="wrong",
    )
    mock_client = MagicMock()
    mock_structured = MagicMock()
    mock_structured.chat.completions.create.return_value = parsed

    settings = MagicMock(deepseek_model="deepseek-v4-flash")

    with patch(
        "app.services.extraction.llm_client.instructor.from_openai",
        return_value=mock_structured,
    ):
        result = call_deepseek_for_insight(
            article, tag, client=mock_client, settings=settings
        )

    assert result.source_url == article.url
    call_kwargs = mock_structured.chat.completions.create.call_args.kwargs
    assert call_kwargs["extra_body"] == {"thinking": {"type": "disabled"}}
