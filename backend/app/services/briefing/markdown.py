from datetime import datetime

from app.models.article import Article
from app.models.article_insight import ArticleInsight
from app.models.feed_source import FeedSource
from app.models.story_cluster import StoryCluster
from app.models.tag import Tag


def _source_label(article: Article) -> str:
    if article.feed_source:
        return article.feed_source.name
    return "来源"


def render_tag_brief_md(
    tag: Tag,
    window_start: datetime,
    window_end: datetime,
    rows: list[tuple[Article, ArticleInsight]],
    *,
    intro_md: str = "",
) -> str:
    """Legacy article-per-item layout (fallback)."""
    start_s = window_start.strftime("%Y-%m-%d %H:%M")
    end_s = window_end.strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# {tag.name} 简报 · {start_s} — {end_s} (UTC)",
        "",
        f"> 共 {len(rows)} 条 · 由 Project Aestas 自动生成",
        "",
    ]
    if intro_md.strip():
        lines.extend(["## 本期综述", "", intro_md.strip(), "", "---", ""])
    if not rows:
        lines.append("_本时间窗内暂无已提炼新闻。_")
        return "\n".join(lines)

    for index, (article, insight) in enumerate(rows, start=1):
        structured = insight.structured
        headline = structured.get("headline", article.title)
        summary = structured.get("summary", "")
        lines.extend([f"## {index}. {headline}", "", summary, ""])
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


def render_cluster_brief_md(
    tag: Tag,
    window_start: datetime,
    window_end: datetime,
    clusters: list[StoryCluster],
    *,
    intro_md: str = "",
    article_count: int = 0,
) -> str:
    start_s = window_start.strftime("%Y-%m-%d %H:%M")
    end_s = window_end.strftime("%Y-%m-%d %H:%M")
    total_articles = article_count or sum(c.article_count for c in clusters)
    lines = [
        f"# {tag.name} 简报 · {start_s} — {end_s} (UTC)",
        "",
        f"> 共 {len(clusters)} 个事件 · {total_articles} 篇报道 · Project Aestas",
        "",
    ]
    if intro_md.strip():
        lines.extend(["## 本期综述", "", intro_md.strip(), "", "---", ""])
    if not clusters:
        lines.append("_本时间窗内暂无已聚类事件。_")
        return "\n".join(lines)

    for index, cluster in enumerate(clusters, start=1):
        lines.extend([f"## {index}. {cluster.title}", "", cluster.summary, "", "**报道来源**"])
        members = sorted(
            cluster.members,
            key=lambda m: (0 if m.role == "primary" else 1, str(m.article_id)),
        )
        for member in members:
            article = member.article
            if article is None:
                continue
            label = _source_label(article)
            lines.append(f"- [{label}]({article.url})")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
