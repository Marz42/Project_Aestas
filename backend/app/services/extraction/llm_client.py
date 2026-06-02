import instructor
from openai import OpenAI

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.models.tag import Tag
from app.services.extraction.schemas import ArticleInsightStructured

SYSTEM_PROMPT = """你是专业新闻编辑助手。根据原文提取线索，严禁编造未出现的事实或数据。
输出必须完全依据原文；source_url 必须与用户提供的链接一致。"""


def build_user_prompt(article: Article, tag: Tag) -> str:
    body = article.content_md or article.summary_raw or ""
    return (
        f"板块: {tag.name} ({tag.slug})\n"
        f"标题: {article.title}\n"
        f"原文链接: {article.url}\n\n"
        f"正文或摘要:\n{body[:12000]}"
    )


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
    client: OpenAI | None = None,
    settings: Settings | None = None,
) -> ArticleInsightStructured:
    settings = settings or get_settings()
    openai_client = client or create_openai_client(settings)
    structured_client = instructor.from_openai(openai_client)

    parsed = structured_client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(article, tag)},
        ],
        response_model=ArticleInsightStructured,
    )
    parsed.source_url = article.url
    return parsed
