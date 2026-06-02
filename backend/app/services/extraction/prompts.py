from app.models.article import Article
from app.models.prompt_template import PromptTemplate
from app.models.tag import Tag

DEFAULT_SYSTEM_PROMPT = """你是专业新闻编辑助手。根据原文提取线索，严禁编造未出现的事实或数据。
输出必须完全依据原文；source_url 必须与用户提供的链接一致。"""

DEFAULT_USER_TEMPLATE = """板块: {tag_name} ({tag_slug})
标题: {title}
原文链接: {url}

正文或摘要:
{body}"""


def resolve_system_prompt(template: PromptTemplate | None) -> str:
    if template and template.system_prompt.strip():
        return template.system_prompt.strip()
    return DEFAULT_SYSTEM_PROMPT


def resolve_user_prompt(
    article: Article,
    tag: Tag,
    template: PromptTemplate | None,
) -> str:
    body = (article.content_md or article.summary_raw or "").strip()[:12000]
    if template and template.user_prompt_template.strip():
        return template.user_prompt_template.format(
            tag_name=tag.name,
            tag_slug=tag.slug,
            title=article.title,
            url=article.url,
            body=body,
        )
    return DEFAULT_USER_TEMPLATE.format(
        tag_name=tag.name,
        tag_slug=tag.slug,
        title=article.title,
        url=article.url,
        body=body,
    )
