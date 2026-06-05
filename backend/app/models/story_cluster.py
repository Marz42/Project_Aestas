import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.tag import Tag


class StoryCluster(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "story_clusters"
    __table_args__ = (
        UniqueConstraint(
            "tag_id",
            "window_start",
            "sort_order",
            name="uq_story_clusters_tag_window_order",
        ),
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
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    article_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    tag: Mapped["Tag"] = relationship()
    members: Mapped[list["StoryClusterArticle"]] = relationship(
        back_populates="cluster",
        cascade="all, delete-orphan",
    )


class StoryClusterArticle(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "story_cluster_articles"

    story_cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("story_clusters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="supporting")

    cluster: Mapped["StoryCluster"] = relationship(back_populates="members")
    article: Mapped["Article"] = relationship()
