from app.models.article import Article


def article_rerank_text(article: Article) -> str:
    if article.insight and article.insight.structured:
        structured = article.insight.structured
        headline = structured.get("headline", article.title)
        summary = structured.get("summary", "")
        facts = structured.get("key_facts") or []
        fact_block = "\n".join(facts[:3])
        parts = [headline, summary]
        if fact_block:
            parts.append(fact_block)
        return "\n".join(p for p in parts if p).strip()
    return article.title


def article_content_tags(article: Article) -> list[str]:
    if article.insight and article.insight.content_tags:
        return list(article.insight.content_tags)
    if article.insight and article.insight.structured:
        raw = article.insight.structured.get("content_tags") or []
        if raw:
            return list(raw)
    if article.tag and article.tag.taxonomy_slugs:
        return list(article.tag.taxonomy_slugs)
    return ["other"]
