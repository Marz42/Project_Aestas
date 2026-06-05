"""M5 story clusters and brief intro

Revision ID: 004
Revises: 003
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "story_clusters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("article_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tag_id",
            "window_start",
            "sort_order",
            name="uq_story_clusters_tag_window_order",
        ),
    )
    op.create_index("ix_story_clusters_tag_id", "story_clusters", ["tag_id"])

    op.create_table(
        "story_cluster_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("story_cluster_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False, server_default="supporting"),
        sa.ForeignKeyConstraint(
            ["story_cluster_id"], ["story_clusters.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("article_id"),
    )
    op.create_index(
        "ix_story_cluster_articles_story_cluster_id",
        "story_cluster_articles",
        ["story_cluster_id"],
    )

    op.add_column(
        "articles",
        sa.Column(
            "source_origin",
            sa.String(length=16),
            nullable=False,
            server_default="rss",
        ),
    )
    op.add_column(
        "articles",
        sa.Column("story_cluster_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_articles_story_cluster_id",
        "articles",
        "story_clusters",
        ["story_cluster_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_articles_story_cluster_id", "articles", ["story_cluster_id"])

    op.add_column(
        "tag_briefs",
        sa.Column("intro_md", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "tag_brief_items",
        sa.Column("story_cluster_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.alter_column("tag_brief_items", "article_id", existing_type=postgresql.UUID(), nullable=True)
    op.create_foreign_key(
        "fk_tag_brief_items_story_cluster_id",
        "tag_brief_items",
        "story_clusters",
        ["story_cluster_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tag_brief_items_story_cluster_id", "tag_brief_items", type_="foreignkey")
    op.drop_column("tag_brief_items", "story_cluster_id")
    op.alter_column("tag_brief_items", "article_id", existing_type=postgresql.UUID(), nullable=False)
    op.drop_column("tag_briefs", "intro_md")
    op.drop_constraint("fk_articles_story_cluster_id", "articles", type_="foreignkey")
    op.drop_index("ix_articles_story_cluster_id", table_name="articles")
    op.drop_column("articles", "story_cluster_id")
    op.drop_column("articles", "source_origin")
    op.drop_table("story_cluster_articles")
    op.drop_table("story_clusters")
