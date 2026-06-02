from app.services.extraction.schemas import ArticleInsightStructured


def render_short_news_md(structured: ArticleInsightStructured) -> str:
    facts = structured.key_facts or []
    facts_block = "\n".join(f"- {fact}" for fact in facts) if facts else "- （无）"
    return (
        f"### {structured.headline}\n\n"
        f"{structured.summary}\n\n"
        f"**要点**\n{facts_block}\n\n"
        f"**影响**: {structured.why_it_matters}\n\n"
        f"**原文**: {structured.source_url}\n"
    )
