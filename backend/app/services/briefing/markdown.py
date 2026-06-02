from datetime import datetime

from app.models.article import Article
from app.models.article_insight import ArticleInsight
from app.models.tag import Tag


def render_tag_brief_md(
    tag: Tag,
    window_start: datetime,
    window_end: datetime,
    rows: list[tuple[Article, ArticleInsight]],
) -> str:
    start_s = window_start.strftime("%Y-%m-%d %H:%M")
    end_s = window_end.strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# {tag.name} 简报 · {start_s} — {end_s} (UTC)",
        "",
        f"> 共 {len(rows)} 条 · 由 Project Aestas 自动生成",
        "",
    ]
    if not rows:
        lines.append("_本时间窗内暂无已提炼新闻。_")
        return "\n".join(lines)

    for index, (article, insight) in enumerate(rows, start=1):
        structured = insight.structured
        headline = structured.get("headline", article.title)
        summary = structured.get("summary", "")
        lines.extend(
            [
                f"## {index}. {headline}",
                "",
                summary,
                "",
            ]
        )
        facts = structured.get("key_facts") or []
        if facts:
            lines.append("**要点**")
            lines.extend(f"- {fact}" for fact in facts)
            lines.append("")
        why = structured.get("why_it_matters")
        if why:
            lines.append(f"**影响**: {why}")
            lines.append("")
        lines.append(f"**原文**: {article.url}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
