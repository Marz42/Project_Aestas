from datetime import datetime

import instructor
from openai import OpenAI

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.models.prompt_template import PromptTemplate
from app.models.tag import Tag
from app.services.clustering.schemas import BriefIntroResult, ClusteringResult
from app.services.extraction.llm_client import completion_extra_body, create_openai_client
from app.services.extraction.prompts import (
    DEFAULT_BRIEFING_INTRO_SYSTEM,
    DEFAULT_BRIEFING_INTRO_USER,
    DEFAULT_CLUSTERING_SYSTEM,
    DEFAULT_CLUSTERING_USER,
)


def _structured_client(settings: Settings, client: OpenAI | None = None) -> instructor.Instructor:
    openai_client = client or create_openai_client(settings)
    return instructor.from_openai(openai_client)


def _cluster_user_message(
    tag: Tag,
    window_start: datetime,
    window_end: datetime,
    articles: list[Article],
    template: PromptTemplate | None,
) -> str:
    lines = []
    for article in articles:
        headline = article.title
        summary = ""
        if article.insight and article.insight.structured:
            headline = article.insight.structured.get("headline", headline)
            summary = article.insight.structured.get("summary", "")
        lines.append(f"{article.id} | {headline} | {summary}")
    body = "\n".join(lines)
    if template and template.user_prompt_template.strip():
        return template.user_prompt_template.format(
            tag_name=tag.name,
            window_start=window_start.strftime("%Y-%m-%d %H:%M"),
            window_end=window_end.strftime("%Y-%m-%d %H:%M"),
            article_lines=body,
        )
    return DEFAULT_CLUSTERING_USER.format(
        tag_name=tag.name,
        window_start=window_start.strftime("%Y-%m-%d %H:%M"),
        window_end=window_end.strftime("%Y-%m-%d %H:%M"),
        article_lines=body,
    )


def call_clustering_llm(
    tag: Tag,
    window_start: datetime,
    window_end: datetime,
    articles: list[Article],
    *,
    template: PromptTemplate | None = None,
    client: OpenAI | None = None,
    settings: Settings | None = None,
) -> ClusteringResult:
    settings = settings or get_settings()
    structured = _structured_client(settings, client)
    system = (
        template.system_prompt.strip()
        if template and template.system_prompt.strip()
        else DEFAULT_CLUSTERING_SYSTEM
    )
    create_kwargs: dict = {
        "model": settings.deepseek_model,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": _cluster_user_message(
                    tag, window_start, window_end, articles, template
                ),
            },
        ],
        "response_model": ClusteringResult,
    }
    extra = completion_extra_body(settings)
    if extra:
        create_kwargs["extra_body"] = extra
    return structured.chat.completions.create(**create_kwargs)


def call_brief_intro_llm(
    tag: Tag,
    window_start: datetime,
    window_end: datetime,
    event_lines: str,
    *,
    template: PromptTemplate | None = None,
    client: OpenAI | None = None,
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    structured = _structured_client(settings, client)
    system = (
        template.system_prompt.strip()
        if template and template.system_prompt.strip()
        else DEFAULT_BRIEFING_INTRO_SYSTEM
    )
    if template and template.user_prompt_template.strip():
        user = template.user_prompt_template.format(
            tag_name=tag.name,
            window_start=window_start.strftime("%Y-%m-%d %H:%M"),
            window_end=window_end.strftime("%Y-%m-%d %H:%M"),
            event_lines=event_lines,
        )
    else:
        user = DEFAULT_BRIEFING_INTRO_USER.format(
            tag_name=tag.name,
            window_start=window_start.strftime("%Y-%m-%d %H:%M"),
            window_end=window_end.strftime("%Y-%m-%d %H:%M"),
            event_lines=event_lines,
        )
    create_kwargs: dict = {
        "model": settings.deepseek_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_model": BriefIntroResult,
    }
    extra = completion_extra_body(settings)
    if extra:
        create_kwargs["extra_body"] = extra
    result: BriefIntroResult = structured.chat.completions.create(**create_kwargs)
    return result.intro_md.strip()
