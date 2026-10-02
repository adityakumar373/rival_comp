"""baseline: competitor table

Revision ID: 0001
Revises:
Create Date: 2026-08-13

NOTE: If your database already has the `competitor` table (created
manually, per the earlier project handoff), do NOT run this migration.
Instead run:
    alembic stamp 0001
then continue with `alembic upgrade head` to apply everything after it.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "competitor",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("website", sa.String(500), nullable=False),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("competitor")
