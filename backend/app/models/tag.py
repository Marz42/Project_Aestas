import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.feed_source import FeedSource
    from app.models.prompt_template import PromptTemplate
    from app.models.tag_brief import TagBrief


class Tag(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tags"

    slug: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_templates.id", ondelete="SET NULL"),
        nullable=True,
    )

    feed_sources: Mapped[list["FeedSource"]] = relationship(
        back_populates="tag",
    )
    articles: Mapped[list["Article"]] = relationship(back_populates="tag")
    briefs: Mapped[list["TagBrief"]] = relationship(back_populates="tag")
    prompt_template: Mapped["PromptTemplate | None"] = relationship(
        back_populates="tags",
    )
