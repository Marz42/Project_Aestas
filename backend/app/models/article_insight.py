import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.article import Article


class ArticleInsight(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "article_insights"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    structured: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    short_news_md: Mapped[str] = mapped_column(Text, nullable=False)
    content_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String(32)),
        nullable=False,
        server_default="{}",
    )
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    embedded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    article: Mapped["Article"] = relationship(back_populates="insight")
