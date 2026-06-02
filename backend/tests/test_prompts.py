import uuid

from app.models.article import Article
from app.models.prompt_template import PromptTemplate
from app.models.tag import Tag
from app.services.extraction.prompts import resolve_system_prompt, resolve_user_prompt


def test_resolve_user_prompt_uses_template() -> None:
    tag = Tag(id=uuid.uuid4(), slug="tech", name="科技")
    article = Article(
        id=uuid.uuid4(),
        feed_source_id=uuid.uuid4(),
        tag_id=tag.id,
        title="T",
        url="https://example.com/x",
        summary_raw="content",
        content_md=None,
        published_at=None,
        fetched_at=None,
        status="pending",
        dedup_key="k",
    )
    template = PromptTemplate(
        id=uuid.uuid4(),
        name="custom",
        purpose="extraction",
        description=None,
        system_prompt="sys",
        user_prompt_template="URL={url} TAG={tag_name}",
    )
    text = resolve_user_prompt(article, tag, template)
    assert text == "URL=https://example.com/x TAG=科技"


def test_resolve_system_prompt_fallback() -> None:
    assert "编辑助手" in resolve_system_prompt(None)
