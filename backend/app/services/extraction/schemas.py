from pydantic import BaseModel, Field, field_validator

from app.services.taxonomy.constants import TAXONOMY_SLUGS


class ArticleInsightStructured(BaseModel):
    headline: str = Field(max_length=200, description="简体中文一句话标题")
    summary: str = Field(max_length=800, description="简体中文 2-3 句摘要")
    key_facts: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="简体中文要点列表",
    )
    why_it_matters: str = Field(max_length=500, description="简体中文：对板块的影响")
    source_url: str = Field(max_length=2048)
    content_tags: list[str] = Field(
        min_length=1,
        max_length=3,
        description="1~3 个 taxonomy slug，来自预定义标签池",
    )

    @field_validator("content_tags")
    @classmethod
    def validate_content_tags(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("content_tags must contain at least one tag")
        deduped: list[str] = []
        for tag in value:
            slug = tag.strip().lower()
            if slug not in TAXONOMY_SLUGS:
                raise ValueError(f"invalid content_tag: {tag}")
            if slug not in deduped:
                deduped.append(slug)
        if len(deduped) > 3:
            raise ValueError("content_tags must have at most 3 items")
        return deduped
