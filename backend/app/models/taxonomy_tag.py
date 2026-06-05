from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TaxonomyTag(Base):
    __tablename__ = "taxonomy_tags"

    slug: Mapped[str] = mapped_column(String(32), primary_key=True)
    name_zh: Mapped[str] = mapped_column(String(64), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
