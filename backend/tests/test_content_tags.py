import pytest
from pydantic import ValidationError

from app.services.extraction.schemas import ArticleInsightStructured


def test_content_tags_requires_one_to_three() -> None:
    with pytest.raises(ValidationError):
        ArticleInsightStructured(
            headline="h",
            summary="s",
            key_facts=[],
            why_it_matters="w",
            source_url="https://x.com",
            content_tags=[],
        )


def test_content_tags_rejects_unknown_slug() -> None:
    with pytest.raises(ValidationError):
        ArticleInsightStructured(
            headline="h",
            summary="s",
            key_facts=[],
            why_it_matters="w",
            source_url="https://x.com",
            content_tags=["made_up_tag"],
        )


def test_content_tags_dedupes_and_lowercases() -> None:
    model = ArticleInsightStructured(
        headline="h",
        summary="s",
        key_facts=[],
        why_it_matters="w",
        source_url="https://x.com",
        content_tags=["Technology", "technology", "politics"],
    )
    assert model.content_tags == ["technology", "politics"]
