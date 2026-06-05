"""M5b-2 taxonomy, content_tags, pgvector embeddings

Revision ID: 005
Revises: 004
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "taxonomy_tags",
        sa.Column("slug", sa.String(length=32), nullable=False),
        sa.Column("name_zh", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("slug"),
    )

    op.add_column(
        "tags",
        sa.Column(
            "taxonomy_slugs",
            sa.ARRAY(sa.String(length=32)),
            nullable=False,
            server_default="{}",
        ),
    )

    op.add_column(
        "article_insights",
        sa.Column(
            "content_tags",
            sa.ARRAY(sa.String(length=32)),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "article_insights",
        sa.Column("embedding", Vector(1024), nullable=True),
    )
    op.add_column(
        "article_insights",
        sa.Column("embedding_model", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "article_insights",
        sa.Column("embedded_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_article_insights_content_tags_gin",
        "article_insights",
        ["content_tags"],
        postgresql_using="gin",
    )
    op.execute(
        """
        CREATE INDEX ix_article_insights_embedding_hnsw
        ON article_insights
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_article_insights_embedding_hnsw")
    op.drop_index("ix_article_insights_content_tags_gin", table_name="article_insights")
    op.drop_column("article_insights", "embedded_at")
    op.drop_column("article_insights", "embedding_model")
    op.drop_column("article_insights", "embedding")
    op.drop_column("article_insights", "content_tags")
    op.drop_column("tags", "taxonomy_slugs")
    op.drop_table("taxonomy_tags")
    op.execute("DROP EXTENSION IF EXISTS vector")
