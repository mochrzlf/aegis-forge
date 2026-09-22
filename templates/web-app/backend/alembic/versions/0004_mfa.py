"""users.mfa_secret / mfa_enabled + mfa_backup_codes — TOTP step-up (gap 1.6)

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("mfa_secret", sa.String(64), nullable=True))
    op.add_column(
        "users",
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default=sa.false()),
    )

    # Backup codes are bearer secrets, so like auth_tokens only a hash is kept.
    op.create_table(
        "mfa_backup_codes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_mfa_backup_codes_user", "mfa_backup_codes", ["user_id"])
    op.create_index("ix_mfa_backup_codes_hash", "mfa_backup_codes", ["code_hash"])


def downgrade() -> None:
    op.drop_index("ix_mfa_backup_codes_hash", table_name="mfa_backup_codes")
    op.drop_index("ix_mfa_backup_codes_user", table_name="mfa_backup_codes")
    op.drop_table("mfa_backup_codes")
    op.drop_column("users", "mfa_enabled")
    op.drop_column("users", "mfa_secret")
