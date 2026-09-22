"""MFA / TOTP step-up (AGENTS.md §3.2.1, gap-analysis 1.6, ADR-008).

TOTP per RFC 6238 via pyotp — the one dependency exception sanctioned by
gap-analysis rule 5. Backup codes are one-time bearer secrets stored hashed,
identical to the auth_tokens pattern (ADR-002/007).

Replay defence: a TOTP code stays valid across a couple of 30s windows
(pyotp valid_window=1), so a code that verified once is marked used in Redis
for 3 windows. A stolen code cannot be replayed inside its own lifetime.
"""
import hashlib
import secrets
from datetime import datetime, timezone

import pyotp
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import MfaBackupCode, User
from app.services.audit_service import write_audit


class MfaError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _replay_key(user_id: str, code: str) -> str:
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()[:16]
    return f"totp_used:{user_id}:{digest}"


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


async def _verify_totp(redis: Redis, user: User, code: str) -> bool:
    """True only for a fresh, unreplayed code."""
    if not user.mfa_secret:
        return False
    if not pyotp.TOTP(user.mfa_secret).verify(code):
        return False
    # NX: the first presentation wins; every later one inside the TTL is replay.
    marked = await redis.set(
        _replay_key(user.id, code), "1", ex=settings.TOTP_REPLAY_TTL_SECONDS, nx=True
    )
    return bool(marked)


async def _consume_backup_code(db: AsyncSession, user: User, code: str) -> bool:
    res = await db.execute(
        select(MfaBackupCode).where(
            MfaBackupCode.user_id == user.id,
            MfaBackupCode.code_hash == _hash_code(code),
            MfaBackupCode.used_at.is_(None),
        )
    )
    record = res.scalar_one_or_none()
    if record is None:
        return False
    record.used_at = _now()
    return True


async def verify_code(db: AsyncSession, redis: Redis, user: User, code: str) -> str | None:
    """Verify a TOTP code or a backup code. Returns how it verified, or None.

    TOTP is tried first — the common case — and only then the backup-code
    table, so a brute-force scan of backup hashes costs a DB query per guess.
    """
    if not user.mfa_enabled:
        return None
    if await _verify_totp(redis, user, code):
        return "totp"
    if await _consume_backup_code(db, user, code):
        return "backup"
    return None


async def enroll(db: AsyncSession, user_id: str) -> tuple[str, str]:
    """Mint a TOTP secret and its provisioning URI. Not active until verified."""
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise MfaError("NOT_FOUND", "Account not found")
    if user.mfa_enabled:
        raise MfaError("CONFLICT", "MFA is already active on this account")

    user.mfa_secret = pyotp.random_base32()
    uri = pyotp.TOTP(user.mfa_secret).provisioning_uri(
        name=user.email, issuer_name=settings.APP_NAME
    )
    await write_audit(
        db, actor_user_id=user.id, action="user.mfa.enrolled", resource=f"user:{user.id}"
    )
    await db.commit()
    return user.mfa_secret, uri


async def activate(db: AsyncSession, redis: Redis, user_id: str, code: str) -> list[str]:
    """Confirm the first TOTP code and activate MFA. Returns backup codes once."""
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise MfaError("NOT_FOUND", "Account not found")
    if not user.mfa_secret:
        raise MfaError("VALIDATION_ERROR", "No pending MFA enrollment — enroll first")
    if user.mfa_enabled:
        raise MfaError("CONFLICT", "MFA is already active on this account")
    # Enrollment confirmation is TOTP-only — backup codes do not exist yet, and
    # this code is what proves the authenticator app is actually set up.
    if not pyotp.TOTP(user.mfa_secret).verify(code):
        raise MfaError("UNAUTHORIZED", "Invalid TOTP code")

    user.mfa_enabled = True
    codes = await _issue_backup_codes(db, user)
    await write_audit(
        db, actor_user_id=user.id, action="user.mfa.activated", resource=f"user:{user.id}"
    )
    await db.commit()
    return codes


async def _issue_backup_codes(db: AsyncSession, user: User) -> list[str]:
    """Fresh one-time codes; any older unused ones are revoked first."""
    now = _now()
    await db.execute(
        update(MfaBackupCode)
        .where(MfaBackupCode.user_id == user.id, MfaBackupCode.used_at.is_(None))
        .values(used_at=now)
    )
    codes = [secrets.token_urlsafe(8) for _ in range(settings.MFA_BACKUP_CODE_COUNT)]
    for raw in codes:
        db.add(MfaBackupCode(user_id=user.id, code_hash=_hash_code(raw)))
    return codes


async def disable(db: AsyncSession, redis: Redis, user_id: str, code: str) -> None:
    """Turn MFA off. Requires a live code — weakening an account is not free."""
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise MfaError("NOT_FOUND", "Account not found")
    if not user.mfa_enabled:
        raise MfaError("CONFLICT", "MFA is not active on this account")
    if await verify_code(db, redis, user, code) is None:
        raise MfaError("UNAUTHORIZED", "Invalid TOTP code")

    user.mfa_secret = None
    user.mfa_enabled = False
    await db.execute(
        update(MfaBackupCode).where(MfaBackupCode.user_id == user.id).values(used_at=_now())
    )
    await write_audit(
        db, actor_user_id=user.id, action="user.mfa.disabled", resource=f"user:{user.id}"
    )
    await db.commit()

