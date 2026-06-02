import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.tag import Tag


class FeedSource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "feed_sources"

    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    feed_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="rss",
    )
    fetch_interval_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=480,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    tag: Mapped["Tag"] = relationship(back_populates="feed_sources")
    articles: Mapped[list["Article"]] = relationship(back_populates="feed_source")
