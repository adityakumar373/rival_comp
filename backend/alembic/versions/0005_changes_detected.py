"""create changes_detected table

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "changes_detected",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "previous_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content_versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "new_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("lines_added", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lines_removed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("similarity_ratio", sa.Float(), nullable=False),
        sa.Column("diff_text", sa.Text(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_changes_source", "changes_detected", ["source_id"])


def downgrade() -> None:
    op.drop_index("idx_changes_source", table_name="changes_detected")
    op.drop_table("changes_detected")
