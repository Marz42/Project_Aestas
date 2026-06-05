from app.models.article import Article
from app.models.prompt_template import PromptTemplate
from app.models.tag import Tag
from app.services.taxonomy.constants import format_taxonomy_for_prompt

CHINESE_OUTPUT_RULE = """
输出语言：headline、summary、key_facts、why_it_matters 必须使用简体中文。
专有名词、装备型号可保留英文并附中文说明；禁止大段英文摘要。"""

CONTENT_TAG_RULE = """
content_tags：从【预定义标签池】挑选 1~3 个最符合新闻内容的 slug（可多选，禁止单选敷衍）。
【预定义标签池】：{taxonomy_list}
只能使用列表中的 slug，禁止自造标签。"""

DEFAULT_SYSTEM_PROMPT = (
    """你是专业新闻编辑助手。根据原文提取线索，严禁编造未出现的事实或数据。
输出必须完全依据原文；source_url 必须与用户提供的链接一致。"""
    + CHINESE_OUTPUT_RULE
    + CONTENT_TAG_RULE
)

DEFAULT_USER_TEMPLATE = """板块: {tag_name} ({tag_slug})
标题: {title}
原文链接: {url}

正文或摘要:
{body}"""

DEFAULT_CLUSTERING_SYSTEM = (
    """你是新闻编辑。将同一板块、同一时间窗内的多篇报道按「同一新闻事件」分组。
仅合并明显报道同一事件的条目；不确定时单独成组。输出简体中文标题与摘要。"""
    + CHINESE_OUTPUT_RULE
)

DEFAULT_CLUSTERING_USER = """板块: {tag_name}
时间窗: {window_start} — {window_end} (UTC)

待分组报道（每行格式为 article_id | headline | summary）:
{article_lines}

请输出分组结果。"""

DEFAULT_BRIEFING_INTRO_SYSTEM = (
    """你是垂直板块新闻主编。根据本期各事件摘要，撰写一段「本期综述」：
2-4 段简体中文，概括本时间窗内该板块最重要动态，不编造事实。"""
    + CHINESE_OUTPUT_RULE
)

DEFAULT_BRIEFING_INTRO_USER = """板块: {tag_name}
时间窗: {window_start} — {window_end} (UTC)

本期事件列表:
{event_lines}

请撰写本期综述（Markdown 正文，无需标题）。"""

DEFAULT_CLUSTER_TITLE_SYSTEM = (
    """你是新闻编辑。根据同一事件的多源报道，撰写简洁的中文事件标题与摘要。
不编造事实；标题一句话，摘要 2-3 句。"""
    + CHINESE_OUTPUT_RULE
)

DEFAULT_CLUSTER_TITLE_USER = """事件多源报道:
{source_lines}

请输出事件标题与摘要。"""


def _inject_taxonomy(system: str) -> str:
    if "{taxonomy_list}" in system:
        return system.format(taxonomy_list=format_taxonomy_for_prompt())
    return system


def resolve_system_prompt(template: PromptTemplate | None) -> str:
    if template and template.system_prompt.strip():
        return _inject_taxonomy(template.system_prompt.strip())
    return _inject_taxonomy(DEFAULT_SYSTEM_PROMPT)


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
