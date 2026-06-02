import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.tag import Tag


class TagBrief(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tag_briefs"
    __table_args__ = (
        UniqueConstraint("tag_id", "window_start", name="uq_tag_briefs_tag_window"),
    )

    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    window_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="generated")
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tag: Mapped["Tag"] = relationship(back_populates="briefs")
    items: Mapped[list["TagBriefItem"]] = relationship(
        back_populates="brief",
        cascade="all, delete-orphan",
    )


class TagBriefItem(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "tag_brief_items"

    tag_brief_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tag_briefs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)

    brief: Mapped["TagBrief"] = relationship(back_populates="items")
    article: Mapped["Article"] = relationship()
