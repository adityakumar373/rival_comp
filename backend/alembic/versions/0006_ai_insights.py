"""create ai_insights table

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

insight_category_enum = postgresql.ENUM(
    "pricing", "hiring", "product", "partnership", "marketing",
    "news", "market_activity", "other",
    name="insight_category_enum",
)


def upgrade() -> None:
    insight_category_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "ai_insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "change_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("changes_detected.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "competitor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("competitor.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", insight_category_enum, nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("impact_score", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_ai_insights_competitor", "ai_insights", ["competitor_id"])
    op.create_index("idx_ai_insights_impact", "ai_insights", ["impact_score"])


def downgrade() -> None:
    op.drop_index("idx_ai_insights_impact", table_name="ai_insights")
    op.drop_index("idx_ai_insights_competitor", table_name="ai_insights")
    op.drop_table("ai_insights")
    insight_category_enum.drop(op.get_bind(), checkfirst=True)
