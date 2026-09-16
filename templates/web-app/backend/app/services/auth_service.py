"""Auth business logic: register, login, refresh (RTR), logout.

Refresh Token Rotation (RTR) + reuse detection (AGENTS.md §4.1 / ADR-002):
- Every refresh issues a NEW token pair and revokes the old one.
- If an already-revoked token is presented (replay), ALL descendant sessions
  for that user are revoked and a security incident is audited.
"""
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.models import RefreshToken, User
from app.repositories import create_user, get_user_by_email
from app.services.audit_service import write_audit


class AuthError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


async def register(db: AsyncSession, email: str, password: str) -> User:
    if await get_user_by_email(db, email):
        raise AuthError("VALIDATION_ERROR", "Email already registered")
    user = await create_user(db, email, security.hash_password(password))
    await write_audit(db, actor_user_id=user.id, action="user.register", resource=f"user:{user.id}")
    return user


async def _issue_token_pair(db: AsyncSession, user: User, parent_id: str | None = None) -> tuple[str, str]:
    access = security.create_access_token(subject=user.id, role=user.role)
    refresh = security.new_refresh_token()
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=security.hash_refresh_token(refresh),
        parent_id=parent_id,
        expires_at=security.refresh_token_expiry(),
    ))
    await db.commit()
    return access, refresh


async def login(db: AsyncSession, email: str, password: str) -> tuple[str, str, int]:
    user = await get_user_by_email(db, email)
    if not user or not security.verify_password(password, user.hashed_password):
        raise AuthError("UNAUTHORIZED", "Invalid credentials")
    if user.status != "active":
        raise AuthError("FORBIDDEN", "Account is not active")
    access, refresh = await _issue_token_pair(db, user)
    await write_audit(db, actor_user_id=user.id, action="user.login", resource=f"user:{user.id}")
    return access, refresh, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


async def refresh(db: AsyncSession, presented_token: str) -> tuple[str, str, int]:
    token_hash = security.hash_refresh_token(presented_token)
    res = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = res.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if stored is None:
        raise AuthError("UNAUTHORIZED", "Invalid refresh token")

    if stored.revoked_at is not None:
        # REPLAY: an old token was reused -> revoke ALL sessions for the user.
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == stored.user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await write_audit(
            db, actor_user_id=stored.user_id,
            action="security.refresh_token_reuse_detected",
            resource=f"user:{stored.user_id}",
            detail="Revoked all sessions after refresh-token replay",
        )
        await db.commit()
        raise AuthError("UNAUTHORIZED", "Session revoked due to token reuse")

    if stored.expires_at < now:
        raise AuthError("UNAUTHORIZED", "Refresh token expired")

    # Rotate: revoke old, issue new pair chained to it.
    stored.revoked_at = now
    res_user = await db.execute(select(User).where(User.id == stored.user_id))
    user = res_user.scalar_one()
    access, new_refresh = await _issue_token_pair(db, user, parent_id=stored.id)
    return access, new_refresh, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


async def logout(db: AsyncSession, presented_token: str) -> None:
    token_hash = security.hash_refresh_token(presented_token)
    now = datetime.now(timezone.utc)
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.token_hash == token_hash, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    await db.commit()
