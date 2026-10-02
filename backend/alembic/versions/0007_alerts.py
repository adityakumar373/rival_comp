"""create alerts table

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "insight_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_insights.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "competitor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("competitor.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("impact_score", sa.Integer(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_alerts_competitor", "alerts", ["competitor_id"])


def downgrade() -> None:
    op.drop_index("idx_alerts_competitor", table_name="alerts")
    op.drop_table("alerts")
