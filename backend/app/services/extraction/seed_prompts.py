from sqlalchemy import select

from app.core.database import SyncSessionLocal
from app.models.prompt_template import PromptTemplate
from app.models.tag import Tag
from app.services.extraction.prompts import (
    DEFAULT_BRIEFING_INTRO_SYSTEM,
    DEFAULT_BRIEFING_INTRO_USER,
    DEFAULT_CLUSTER_TITLE_SYSTEM,
    DEFAULT_CLUSTER_TITLE_USER,
    DEFAULT_CLUSTERING_SYSTEM,
    DEFAULT_CLUSTERING_USER,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_TEMPLATE,
)

BUILTIN_PROMPTS = [
    {
        "name": "默认-新闻提炼",
        "purpose": "extraction",
        "description": "通用单条新闻结构化提炼（全中文）",
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
        "user_prompt_template": DEFAULT_USER_TEMPLATE,
    },
    {
        "name": "军事-深度线索",
        "purpose": "extraction",
        "description": "强调装备参数与地缘影响",
        "system_prompt": DEFAULT_SYSTEM_PROMPT
        + "\n特别关注：装备型号、部署地点、各方反应。",
        "user_prompt_template": DEFAULT_USER_TEMPLATE,
    },
    {
        "name": "默认-事件聚类",
        "purpose": "clustering",
        "description": "同板块时间窗内 LLM 批量事件分组",
        "system_prompt": DEFAULT_CLUSTERING_SYSTEM,
        "user_prompt_template": DEFAULT_CLUSTERING_USER,
    },
    {
        "name": "默认-简报导语",
        "purpose": "briefing_intro",
        "description": "板块周期综述（文首本期综述）",
        "system_prompt": DEFAULT_BRIEFING_INTRO_SYSTEM,
        "user_prompt_template": DEFAULT_BRIEFING_INTRO_USER,
    },
    {
        "name": "默认-事件标题润色",
        "purpose": "cluster_title",
        "description": "多源事件簇标题与摘要润色",
        "system_prompt": DEFAULT_CLUSTER_TITLE_SYSTEM,
        "user_prompt_template": DEFAULT_CLUSTER_TITLE_USER,
    },
]


def seed_default_prompts() -> dict[str, int]:
    with SyncSessionLocal() as session:
        created = 0
        updated = 0
        extraction_id = None
        for spec in BUILTIN_PROMPTS:
            existing = session.scalar(
                select(PromptTemplate).where(PromptTemplate.name == spec["name"])
            )
            if existing:
                if spec["purpose"] == "extraction" and extraction_id is None:
                    extraction_id = existing.id
                if spec["name"] in ("默认-新闻提炼", "默认-事件标题润色"):
                    existing.system_prompt = spec["system_prompt"]
                    existing.user_prompt_template = spec["user_prompt_template"]
                    updated += 1
                continue
            row = PromptTemplate(**spec)
            session.add(row)
            session.flush()
            if spec["purpose"] == "extraction" and extraction_id is None:
                extraction_id = row.id
            created += 1

        tags_linked = 0
        if extraction_id:
            tags_without = session.scalars(
                select(Tag).where(Tag.prompt_template_id.is_(None))
            ).all()
            for tag in tags_without:
                tag.prompt_template_id = extraction_id
            tags_linked = len(tags_without)

        session.commit()
        return {"prompts_created": created, "prompts_updated": updated, "tags_linked": tags_linked}
