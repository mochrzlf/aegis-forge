"""Runnable self-check for password reset + email verification (ADR-007) — no pytest.

Uses an in-memory SQLite session to run the real service logic and the real
UPDATE predicates, not a mock. The schema is created from ORM metadata, so it
needs no Alembic migration here. Mail is never touched: delivery lives in the
router, the service only mints and redeems tokens.

Covers the invariants an auditor asks about:
  - only the hash of a token is stored, never the raw value
  - an unknown address neither creates a token nor reports an error
  - a redemption actually changes the password and consumes the token
  - replayed and expired links are refused, and refused without consuming
  - a successful reset kills every live session
  - a suspended account cannot rotate its own password
  - verification marks the account and its token is single-use
  - a verification token can never be used as a reset token
  - the audit chain is complete and carries no raw PII

Run from the backend directory:
    python3 tests/check_reset_verify.py
"""
import asyncio
import os
import sys

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://aegis:a@db:5432/aegis_app")
os.environ.setdefault("JWT_SECRET", "x" * 48)
os.environ.setdefault("POSTGRES_PASSWORD", "change_me_strong_password")

sys.path.insert(0, ".")

from datetime import datetime, timedelta, timezone  # noqa: E402

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.core import security  # noqa: E402
from app.models import AuditLog, AuthToken, Base, RefreshToken, User  # noqa: E402
from app.repositories import (  # noqa: E402
    count_active_refresh_tokens,
    create_user,
    get_user_by_email,
)
from app.services import auth_service  # noqa: E402
from app.services.auth_service import AuthError  # noqa: E402


async def _password(db: AsyncSession, email: str) -> str:
    return (await get_user_by_email(db, email)).hashed_password


async def main():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        user = await create_user(db, "victim@example.com", security.hash_password("old-password-1234"))

        # 1. Request mints a token; only its hash reaches the database.
        raw = await auth_service.request_password_reset(db, "victim@example.com")
        assert raw and len(raw) > 20
        res = await db.execute(select(AuthToken).where(AuthToken.purpose == "password_reset"))
        record = res.scalar_one()
        assert record.token_hash != raw
        assert record.consumed_at is None
        assert security.hash_token(raw) == record.token_hash
        print("  reset token stored hashed, not raw — OK")

        # 2. An unknown address mints nothing and errors nothing.
        assert await auth_service.request_password_reset(db, "nobody@example.com") is None
        res = await db.execute(select(AuthToken).where(AuthToken.purpose == "password_reset"))
        assert len(res.scalars().all()) == 1
        print("  unknown email creates no token, no error — OK")

        # 3. Confirm changes the password and consumes the token.
        await auth_service.confirm_password_reset(db, raw, "new-strong-password-1234")
        assert security.verify_password("new-strong-password-1234", await _password(db, "victim@example.com"))
        assert not security.verify_password("old-password-1234", await _password(db, "victim@example.com"))
        await db.refresh(record)
        assert record.consumed_at is not None
        print("  confirm set the new password + consumed the token — OK")

        # 4. A replayed token is refused (single-use).
        try:
            await auth_service.confirm_password_reset(db, raw, "another-password-1234")
            raise AssertionError("replay should have been refused")
        except AuthError as exc:
            assert exc.code == "UNAUTHORIZED"
        print("  replay refused — OK")

        # 5. An expired token is refused, unconsumed, and changes nothing.
        expired_raw = await auth_service.request_password_reset(db, "victim@example.com")
        res = await db.execute(select(AuthToken).where(AuthToken.token_hash == security.hash_token(expired_raw)))
        expired = res.scalar_one()
        expired.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        await db.commit()
        before = await _password(db, "victim@example.com")
        try:
            await auth_service.confirm_password_reset(db, expired_raw, "expired-password-1234")
            raise AssertionError("expired token should have been refused")
        except AuthError as exc:
            assert exc.code == "UNAUTHORIZED"
        assert await _password(db, "victim@example.com") == before, "expired token changed the password"
        await db.refresh(expired)
        assert expired.consumed_at is None, "a failed redemption must not consume the token"
        print("  expired refused, unconsumed, password unchanged — OK")

        # 6. A successful reset revokes every live session of the account.
        other = await create_user(db, "other@example.com", security.hash_password("pw-other-12345"))
        live_expiry = datetime.now(timezone.utc) + timedelta(days=30)
        for n in range(2):
            db.add(RefreshToken(user_id=other.id, token_hash=f"live-{n}", expires_at=live_expiry))
        db.add(RefreshToken(
            user_id=other.id,
            token_hash="dead",
            expires_at=live_expiry,
            revoked_at=datetime.now(timezone.utc) - timedelta(hours=1),
        ))
        await db.commit()
        assert await count_active_refresh_tokens(db, other.id) == 2

        reset_raw = await auth_service.request_password_reset(db, "other@example.com")
        await auth_service.confirm_password_reset(db, reset_raw, "reset-password-12345")
        assert await count_active_refresh_tokens(db, other.id) == 0, "sessions survived the reset"
        print("  reset revoked both live sessions — OK")

        # 7. A suspended account cannot redeem a reset token (JML control).
        suspended = await create_user(db, "suspended@example.com", security.hash_password("pw-suspended-1234"))
        suspended.status = "suspended"
        await db.commit()
        susp_raw = await auth_service.request_password_reset(db, "suspended@example.com")
        try:
            await auth_service.confirm_password_reset(db, susp_raw, "whatever-password-1234")
            raise AssertionError("suspended account should not be able to reset")
        except AuthError as exc:
            assert exc.code == "FORBIDDEN"
        print("  suspended account reset refused — OK")

        # 8. Verification marks the account and its token is single-use.
        verify_raw = await auth_service.request_email_verification(db, user.id)
        await auth_service.confirm_email_verification(db, verify_raw)
        res = await db.execute(select(User).where(User.id == user.id))
        assert res.scalar_one().email_verified_at is not None, "email was not marked verified"
        try:
            await auth_service.confirm_email_verification(db, verify_raw)
            raise AssertionError("verification replay should have been refused")
        except AuthError as exc:
            assert exc.code == "UNAUTHORIZED"
        print("  email verified + verification token single-use — OK")

        # 9. An already-verified account cannot request another link.
        try:
            await auth_service.request_email_verification(db, user.id)
            raise AssertionError("re-verification should have been refused")
        except AuthError as exc:
            assert exc.code == "VALIDATION_ERROR"
        print("  re-verification of a verified account refused — OK")

        # 10. Purposes do not mix: a verification link is not a reset link.
        verify_raw2 = await auth_service.request_email_verification(db, other.id)
        try:
            await auth_service.confirm_password_reset(db, verify_raw2, "cross-purpose-12345")
            raise AssertionError("a verification token should not redeem as a reset")
        except AuthError as exc:
            assert exc.code == "UNAUTHORIZED"
        print("  purpose scoping enforced — OK")

        # 11. The audit chain is complete and carries no raw PII or raw token.
        res = await db.execute(select(AuditLog))
        rows = res.scalars().all()
        actions = {row.action for row in rows}
        for expected in (
            "user.password_reset_requested",
            "user.password_reset",
            "user.email_verification_requested",
            "user.email_verified",
        ):
            assert expected in actions, f"missing audit action: {expected}"

        raw_tokens = [raw, expired_raw, reset_raw, verify_raw, verify_raw2]
        for row in rows:
            text = f"{row.resource or ''} {row.detail or ''}"
            assert "@example.com" not in text, f"raw email address in audit row: {text!r}"
            for raw_token in raw_tokens:
                assert raw_token not in text, f"raw token in audit row: {text!r}"
        print(f"  audit chain complete + PII-free ({len(rows)} rows) — OK")

    await engine.dispose()
    print("reset+verification self-check: PASS")


if __name__ == "__main__":
    asyncio.run(main())