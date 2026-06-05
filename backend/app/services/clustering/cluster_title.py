from datetime import datetime

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.models.prompt_template import PromptTemplate
from app.models.story_cluster import StoryCluster
from app.services.extraction.llm_client import completion_extra_body, create_openai_client
from app.services.extraction.prompts import (
    DEFAULT_CLUSTER_TITLE_SYSTEM,
    DEFAULT_CLUSTER_TITLE_USER,
)


class ClusterTitleResult(BaseModel):
    title: str = Field(max_length=200)
    summary: str = Field(max_length=800)


def _source_lines(articles: list[Article]) -> str:
    lines: list[str] = []
    for article in articles:
        headline = article.title
        summary = ""
        if article.insight and article.insight.structured:
            headline = article.insight.structured.get("headline", headline)
            summary = article.insight.structured.get("summary", "")
        lines.append(f"- {headline}: {summary[:300]}")
    return "\n".join(lines)


def polish_cluster_title(
    cluster: StoryCluster,
    articles: list[Article],
    *,
    template: PromptTemplate | None = None,
    client: OpenAI | None = None,
    settings: Settings | None = None,
) -> tuple[str, str]:
    settings = settings or get_settings()
    openai_client = client or create_openai_client(settings)
    structured = instructor.from_openai(openai_client)
    system = (
        template.system_prompt.strip()
        if template and template.system_prompt.strip()
        else DEFAULT_CLUSTER_TITLE_SYSTEM
    )
    if template and template.user_prompt_template.strip():
        user = template.user_prompt_template.format(
            source_lines=_source_lines(articles),
            window_start="",
            window_end="",
            tag_name="",
            article_lines="",
            event_lines="",
        )
    else:
        user = DEFAULT_CLUSTER_TITLE_USER.format(source_lines=_source_lines(articles))

    create_kwargs: dict = {
        "model": settings.deepseek_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_model": ClusterTitleResult,
    }
    extra = completion_extra_body(settings)
    if extra:
        create_kwargs["extra_body"] = extra
    result: ClusterTitleResult = structured.chat.completions.create(**create_kwargs)
    return result.title.strip(), result.summary.strip()
