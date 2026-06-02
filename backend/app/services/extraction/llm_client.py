import instructor
from openai import OpenAI

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.models.prompt_template import PromptTemplate
from app.models.tag import Tag
from app.services.extraction.prompts import resolve_system_prompt, resolve_user_prompt
from app.services.extraction.schemas import ArticleInsightStructured


def create_openai_client(settings: Settings | None = None) -> OpenAI:
    settings = settings or get_settings()
    if not settings.deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY is not configured")
    return OpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )


def call_deepseek_for_insight(
    article: Article,
    tag: Tag,
    *,
    prompt_template: PromptTemplate | None = None,
    client: OpenAI | None = None,
    settings: Settings | None = None,
) -> ArticleInsightStructured:
    settings = settings or get_settings()
    openai_client = client or create_openai_client(settings)
    structured_client = instructor.from_openai(openai_client)

    parsed = structured_client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[
            {"role": "system", "content": resolve_system_prompt(prompt_template)},
            {
                "role": "user",
                "content": resolve_user_prompt(article, tag, prompt_template),
            },
        ],
        response_model=ArticleInsightStructured,
    )
    parsed.source_url = article.url
    return parsed
