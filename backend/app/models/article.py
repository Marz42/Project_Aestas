import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.article_insight import ArticleInsight
    from app.models.feed_source import FeedSource
    from app.models.tag import Tag


class Article(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "articles"
    __table_args__ = (UniqueConstraint("url", name="uq_articles_url"),)

    feed_source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feed_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    summary_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )
    dedup_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source_origin: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="rss",
    )
    story_cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("story_clusters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    feed_source: Mapped["FeedSource"] = relationship(back_populates="articles")
    tag: Mapped["Tag"] = relationship(back_populates="articles")
    insight: Mapped["ArticleInsight | None"] = relationship(
        back_populates="article",
        uselist=False,
    )
