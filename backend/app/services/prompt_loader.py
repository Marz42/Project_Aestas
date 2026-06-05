"""Load prompt templates from DB by purpose (runtime source of truth)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.prompt_template import PromptTemplate


def load_prompt_by_purpose(session: Session, purpose: str) -> PromptTemplate | None:
    return session.scalar(
        select(PromptTemplate)
        .where(PromptTemplate.purpose == purpose)
        .order_by(PromptTemplate.created_at.asc())
        .limit(1)
    )
