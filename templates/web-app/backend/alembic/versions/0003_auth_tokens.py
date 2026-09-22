"""auth_tokens table + users.email_verified_at — password reset & email
verification tokens (AGENTS.md §3.2, gap-analysis 1.5, ADR-007)

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verification state lives on the user as a timestamp, mirroring
    # docs/schema.sql §1 — NULL means "not verified yet".
    op.add_column(
        "users",
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
    )

    # One table for both flows: the lifecycle (issue / verify / consume) is
    # identical, only the purpose and the expiry differ. The raw token is never
    # stored — only its SHA-256 hash, exactly like refresh_tokens (ADR-002).
    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("purpose", sa.String(32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        # Single-use is enforced in the service, but the purpose CHECK keeps a
        # caller from re-classifying a token after it is stored.
        sa.CheckConstraint(
            "purpose IN ('password_reset', 'email_verification')", name="chk_auth_token_purpose"
        ),
    )
    op.create_index("ix_auth_tokens_token_hash", "auth_tokens", ["token_hash"], unique=True)
    op.create_index("ix_auth_tokens_user_purpose", "auth_tokens", ["user_id", "purpose"])


def downgrade() -> None:
    op.drop_index("ix_auth_tokens_user_purpose", table_name="auth_tokens")
    op.drop_index("ix_auth_tokens_token_hash", table_name="auth_tokens")
    op.drop_table("auth_tokens")
    op.drop_column("users", "email_verified_at")
