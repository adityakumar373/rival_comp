"""create sources table

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

source_type_enum = postgresql.ENUM(
    "company_website",
    "blog",
    "pricing_page",
    "career_page",
    "news_feed",
    "linkedin",
    "g2",
    "trustpilot",
    name="source_type_enum",
)


def upgrade() -> None:
    source_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "competitor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("competitor.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_type", source_type_enum, nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("scrape_frequency", sa.Integer(), nullable=False, server_default="1440"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_sources_competitor", "sources", ["competitor_id"])


def downgrade() -> None:
    op.drop_index("idx_sources_competitor", table_name="sources")
    op.drop_table("sources")
    source_type_enum.drop(op.get_bind(), checkfirst=True)
