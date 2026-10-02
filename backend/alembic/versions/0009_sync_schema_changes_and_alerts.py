"""sync schema for changes_detected and alerts tables

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Sync changes_detected columns
    cd_cols = [
        row[0] for row in conn.execute(
            sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='changes_detected'")
        ).fetchall()
    ]

    if "previous_version_id" not in cd_cols:
        op.add_column(
            "changes_detected",
            sa.Column(
                "previous_version_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("content_versions.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )

    if "new_version_id" not in cd_cols:
        op.add_column(
            "changes_detected",
            sa.Column(
                "new_version_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("content_versions.id", ondelete="CASCADE"),
                nullable=True,  # nullable initially for existing rows
            ),
        )

    if "lines_added" not in cd_cols:
        op.add_column(
            "changes_detected",
            sa.Column("lines_added", sa.Integer(), nullable=False, server_default="0"),
        )

    if "lines_removed" not in cd_cols:
        op.add_column(
            "changes_detected",
            sa.Column("lines_removed", sa.Integer(), nullable=False, server_default="0"),
        )

    if "similarity_ratio" not in cd_cols:
        op.add_column(
            "changes_detected",
            sa.Column("similarity_ratio", sa.Float(), nullable=False, server_default="0.0"),
        )

    if "diff_text" not in cd_cols:
        op.add_column(
            "changes_detected",
            sa.Column("diff_text", sa.Text(), nullable=False, server_default=""),
        )

    if "change_summary" not in cd_cols:
        op.add_column(
            "changes_detected",
            sa.Column("change_summary", sa.Text(), nullable=True),
        )

    # 2. Sync alerts columns
    alert_cols = [
        row[0] for row in conn.execute(
            sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='alerts'")
        ).fetchall()
    ]

    if "message" not in alert_cols:
        op.add_column(
            "alerts",
            sa.Column("message", sa.Text(), nullable=False, server_default="Competitive Alert"),
        )

    if "impact_score" not in alert_cols:
        op.add_column(
            "alerts",
            sa.Column("impact_score", sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    pass
