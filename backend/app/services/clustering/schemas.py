import uuid

from pydantic import BaseModel, Field


class ClusterGroupOutput(BaseModel):
    title: str = Field(max_length=300, description="事件中文标题")
    summary: str = Field(max_length=1200, description="事件中文合并摘要")
    article_ids: list[str] = Field(
        min_length=1,
        description="属于该事件的 article_id 列表（UUID 字符串）",
    )


class ClusteringResult(BaseModel):
    groups: list[ClusterGroupOutput] = Field(min_length=1)


class BriefIntroResult(BaseModel):
    intro_md: str = Field(max_length=4000, description="本期综述 Markdown 正文")
