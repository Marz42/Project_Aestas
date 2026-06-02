from pydantic import BaseModel, Field


class ArticleInsightStructured(BaseModel):
    headline: str = Field(max_length=200)
    summary: str = Field(max_length=800)
    key_facts: list[str] = Field(default_factory=list, max_length=8)
    why_it_matters: str = Field(max_length=500)
    source_url: str = Field(max_length=2048)
