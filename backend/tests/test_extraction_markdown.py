from app.services.extraction.markdown import render_short_news_md
from app.services.extraction.schemas import ArticleInsightStructured


def test_render_short_news_md_includes_fields() -> None:
    structured = ArticleInsightStructured(
        headline="测试标题",
        summary="两句摘要。",
        key_facts=["事实 A", "事实 B"],
        why_it_matters="影响说明",
        source_url="https://example.com/a",
    )
    md = render_short_news_md(structured)
    assert "测试标题" in md
    assert "事实 A" in md
    assert "https://example.com/a" in md
