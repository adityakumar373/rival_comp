"""add sources.last_scraped_at; create scraped_content, content_versions

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sources",
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "scraped_content",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("raw_html", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("hash", sa.String(64), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_scraped_content_source", "scraped_content", ["source_id"])
    op.create_index("idx_scraped_content_date", "scraped_content", ["scraped_at"])

    op.create_table(
        "content_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("source_id", "version_number", name="uq_content_versions_source_version"),
    )
    op.create_index("idx_content_versions_source", "content_versions", ["source_id"])


def downgrade() -> None:
    op.drop_index("idx_content_versions_source", table_name="content_versions")
    op.drop_table("content_versions")

    op.drop_index("idx_scraped_content_date", table_name="scraped_content")
    op.drop_index("idx_scraped_content_source", table_name="scraped_content")
    op.drop_table("scraped_content")

    op.drop_column("sources", "last_scraped_at")
