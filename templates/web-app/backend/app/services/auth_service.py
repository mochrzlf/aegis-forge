"""Auth business logic: register, login, refresh (RTR), logout.

Refresh Token Rotation (RTR) + reuse detection (AGENTS.md §4.1 / ADR-002):
- Every refresh issues a NEW token pair and revokes the old one.
- If an already-revoked token is presented (replay), ALL descendant sessions
  for that user are revoked and a security incident is audited.
"""
from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.models import AuthToken, RefreshToken, User
from app.repositories import create_user, get_user_by_email, get_user_by_id, revoke_all_refresh_tokens
from app.services.audit_service import write_audit


class AuthError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


PURPOSE_PASSWORD_RESET = "password_reset"
PURPOSE_EMAIL_VERIFICATION = "email_verification"


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


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    """Check credentials and account state.

    The shared precondition of every login path, so MFA and plain login cannot
    drift on what "valid credentials" means.
    """
    user = await get_user_by_email(db, email)
    if not user or not security.verify_password(password, user.hashed_password):
        raise AuthError("UNAUTHORIZED", "Invalid credentials")
    if user.status != "active":
        raise AuthError("FORBIDDEN", "Account is not active")
    return user


async def login(db: AsyncSession, email: str, password: str) -> tuple[str, str, int]:
    user = await authenticate(db, email, password)
    return await issue_session(db, user)


async def issue_session(db: AsyncSession, user: User) -> tuple[str, str, int]:
    """Full login for a user who has passed every factor."""
    access, refresh = await _issue_token_pair(db, user)
    await write_audit(db, actor_user_id=user.id, action="user.login", resource=f"user:{user.id}")
    return access, refresh, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


async def issue_mfa_session(db: AsyncSession, user: User) -> str:
    """Half-authenticated session: a refresh token exists, but no access token
    is issued until the second factor is proven (ADR-008)."""
    _, refresh = await _issue_token_pair(db, user)
    await write_audit(
        db,
        actor_user_id=user.id,
        action="user.login_mfa_challenge",
        resource=f"user:{user.id}",
    )
    return refresh


async def complete_mfa_login(
    db: AsyncSession, redis: Redis, presented_token: str, code: str
) -> tuple[str, str, int]:
    """Finish an MFA login: validate the pending refresh token and the TOTP
    code, then rotate to a fully authenticated session."""
    from app.services import mfa_service

    token_hash = security.hash_refresh_token(presented_token)
    res = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = res.scalar_one_or_none()
    if stored is None:
        raise AuthError("UNAUTHORIZED", "Invalid refresh token")

    now = datetime.now(timezone.utc)
    expires_at = stored.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if stored.revoked_at is not None or expires_at < now:
        raise AuthError("UNAUTHORIZED", "Invalid refresh token")

    res_user = await db.execute(select(User).where(User.id == stored.user_id))
    user = res_user.scalar_one_or_none()
    if not user or not user.mfa_enabled:
        raise AuthError("FORBIDDEN", "MFA is not required for this account")

    method = await mfa_service.verify_code(db, redis, user, code)
    if method is None:
        await write_audit(
            db,
            actor_user_id=user.id,
            action="user.mfa.login_failed",
            resource=f"user:{user.id}",
            detail="Failed second factor on MFA login",
        )
        await db.commit()
        raise AuthError("UNAUTHORIZED", "Invalid TOTP code")

    stored.revoked_at = now
    access, new_refresh = await _issue_token_pair(db, user, parent_id=stored.id)
    await write_audit(
        db,
        actor_user_id=user.id,
        action="user.login",
        resource=f"user:{user.id}",
        detail=f"Login completed via MFA ({method})",
    )
    return access, new_refresh, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


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


async def _claim_auth_token(db: AsyncSession, raw_token: str, purpose: str) -> AuthToken:
    """Look up an emailed token and validate it. Consumes nothing on failure.

    The three failure modes are deliberately indistinguishable to the caller —
    "no such token", "already used" and "expired" all answer the same way, so a
    guess cannot learn which links might still be live.
    """
    res = await db.execute(
        select(AuthToken).where(
            AuthToken.token_hash == security.hash_token(raw_token),
            AuthToken.purpose == purpose,
        )
    )
    record = res.scalar_one_or_none()
    if record is None:
        raise AuthError("UNAUTHORIZED", "Invalid link")

    if record.consumed_at is not None:
        raise AuthError("UNAUTHORIZED", "Invalid link")

    # SQLite returns naive datetimes; Postgres returns tz-aware ones. Normalise
    # so the comparison is well-defined on either driver (same fix as ADR-006).
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise AuthError("UNAUTHORIZED", "Invalid link")

    return record


async def request_password_reset(db: AsyncSession, email: str) -> str | None:
    """Create a single-use reset token. Returns the raw token, or None if no
    account matches.

    None is deliberately not an error: this endpoint is unauthenticated, and
    distinguishing "sent" from "no such user" would turn it into an
    account-enumeration oracle. The caller answers 200 either way.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None

    token = security.new_opaque_token()
    db.add(AuthToken(
        user_id=user.id,
        token_hash=security.hash_token(token),
        purpose=PURPOSE_PASSWORD_RESET,
        expires_at=security.password_reset_token_expiry(),
    ))
    await write_audit(
        db,
        actor_user_id=user.id,
        action="user.password_reset_requested",
        resource=f"auth:reset:{security.email_fingerprint(email)}",
    )
    await db.commit()
    return token


async def confirm_password_reset(db: AsyncSession, raw_token: str, new_password: str) -> User:
    """Redeem a reset token and set the new password.

    The password change and the session revocation run in one transaction: a
    browser tab hijacked before the reset must not keep working on the old
    credentials (same blast-radius rule as the JML kill-switch, ADR-005).
    """
    record = await _claim_auth_token(db, raw_token, PURPOSE_PASSWORD_RESET)

    user = await get_user_by_id(db, record.user_id)
    if not user:
        raise AuthError("NOT_FOUND", "Account no longer exists")
    if user.status != "active":
        raise AuthError("FORBIDDEN", "Account is not active")

    record.consumed_at = datetime.now(timezone.utc)
    user.hashed_password = security.hash_password(new_password)
    sessions_revoked = await revoke_all_refresh_tokens(db, user.id)

    await write_audit(
        db,
        actor_user_id=user.id,
        action="user.password_reset",
        resource=f"user:{user.id}",
        detail=f"Password changed via reset token; {sessions_revoked} session(s) revoked",
    )
    await db.commit()
    await db.refresh(user)
    return user


async def request_email_verification(db: AsyncSession, user_id: str) -> str:
    """Create a single-use verification token for the caller's own address."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise AuthError("NOT_FOUND", "Account not found")
    if user.email_verified_at is not None:
        raise AuthError("VALIDATION_ERROR", "Email is already verified")

    token = security.new_opaque_token()
    db.add(AuthToken(
        user_id=user.id,
        token_hash=security.hash_token(token),
        purpose=PURPOSE_EMAIL_VERIFICATION,
        expires_at=security.email_verification_token_expiry(),
    ))
    await write_audit(
        db,
        actor_user_id=user.id,
        action="user.email_verification_requested",
        resource=f"user:{user.id}",
    )
    await db.commit()
    return token


async def confirm_email_verification(db: AsyncSession, raw_token: str) -> User:
    """Redeem a verification token and mark the address verified."""
    record = await _claim_auth_token(db, raw_token, PURPOSE_EMAIL_VERIFICATION)

    user = await get_user_by_id(db, record.user_id)
    if not user:
        raise AuthError("NOT_FOUND", "Account no longer exists")

    record.consumed_at = datetime.now(timezone.utc)
    user.email_verified_at = datetime.now(timezone.utc)

    await write_audit(
        db,
        actor_user_id=user.id,
        action="user.email_verified",
        resource=f"user:{user.id}",
    )
    await db.commit()
    await db.refresh(user)
    return user
