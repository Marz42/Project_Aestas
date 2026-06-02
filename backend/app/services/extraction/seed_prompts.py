from sqlalchemy import select

from app.core.database import SyncSessionLocal
from app.models.prompt_template import PromptTemplate
from app.models.tag import Tag
from app.services.extraction.prompts import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_TEMPLATE

BUILTIN_PROMPTS = [
    {
        "name": "默认-新闻提炼",
        "purpose": "extraction",
        "description": "通用单条新闻结构化提炼",
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
]


def seed_default_prompts() -> dict[str, int]:
    with SyncSessionLocal() as session:
        created = 0
        first_id = None
        for spec in BUILTIN_PROMPTS:
            existing = session.scalar(
                select(PromptTemplate).where(PromptTemplate.name == spec["name"])
            )
            if existing:
                if first_id is None:
                    first_id = existing.id
                continue
            row = PromptTemplate(**spec)
            session.add(row)
            session.flush()
            if first_id is None:
                first_id = row.id
            created += 1

        tags_linked = 0
        if first_id:
            tags_without = session.scalars(
                select(Tag).where(Tag.prompt_template_id.is_(None))
            ).all()
            for tag in tags_without:
                tag.prompt_template_id = first_id
            tags_linked = len(tags_without)

        session.commit()
        return {"prompts_created": created, "tags_linked": tags_linked}
