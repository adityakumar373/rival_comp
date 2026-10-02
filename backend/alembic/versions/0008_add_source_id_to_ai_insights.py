"""add source_id to ai_insights

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-01

Adds the source_id FK column that was in the model and the 0006
migration definition but was never applied to the live database
because the table had already been created without it.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add source_id if it doesn't already exist (idempotent)
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='ai_insights' AND column_name='source_id'"
    ))
    if result.fetchone() is None:
        op.add_column(
            "ai_insights",
            sa.Column(
                "source_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("sources.id", ondelete="SET NULL"),
                nullable=True,   # nullable so existing rows don't break
            ),
        )
        op.create_index("idx_ai_insights_source", "ai_insights", ["source_id"])


def downgrade() -> None:
    op.drop_index("idx_ai_insights_source", table_name="ai_insights")
    op.drop_column("ai_insights", "source_id")
