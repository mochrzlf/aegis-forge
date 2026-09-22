"""approval_requests table — Maker-Checker / four-eyes (AGENTS.md §3.2.1)

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "approval_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("action_type", sa.String(60), nullable=False),
        sa.Column("target_entity_type", sa.String(50), nullable=False),
        sa.Column("target_entity_id", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("maker_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("checker_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("rejection_reason", sa.String(255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        # Four-eyes at the data layer: the person who requests a change can never
        # be the one who approves it. Enforced in the service too, but a CHECK
        # constraint survives a bug in any caller (AGENTS.md §3.2.1).
        sa.CheckConstraint("maker_user_id <> checker_user_id", name="chk_maker_checker_different"),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')", name="chk_approval_status"
        ),
    )
    op.create_index(
        "ix_approval_requests_status", "approval_requests", ["status", "expires_at"]
    )
    op.create_index("ix_approval_requests_maker", "approval_requests", ["maker_user_id"])


def downgrade() -> None:
    op.drop_index("ix_approval_requests_maker", table_name="approval_requests")
    op.drop_index("ix_approval_requests_status", table_name="approval_requests")
    op.drop_table("approval_requests")
