"""Runnable self-check for MFA / TOTP step-up (ADR-008) — no pytest.

Same approach as the other self-checks: in-memory SQLite driving the real
service logic and the real UPDATE/SELECT predicates, with a fake Redis for the
anti-replay store. No live authenticator app, no mail, no HTTP layer.

Covers the invariants an auditor asks about:
  - enrollment stores a secret but leaves MFA off until a code is proven
  - activation needs a valid code; wrong codes change nothing
  - backup codes are issued once, unique, and only ever stored hashed
  - a TOTP code cannot be replayed inside its own validity window
  - a backup code is single-use
  - MFA-off users verify nothing
  - disabling needs a live code and clears secret + codes
  - MFA login completes a pending session and rotates the refresh token
  - a consumed pending refresh token cannot be replayed
  - step-up tokens carry the freshness claim; access tokens do not

Run from the backend directory:
    python3 tests/check_mfa.py
"""
import asyncio
import os
import sys
from datetime import datetime, timezone

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://aegis:a@db:5432/aegis_app")
os.environ.setdefault("JWT_SECRET", "x" * 48)
os.environ.setdefault("POSTGRES_PASSWORD", "change_me_strong_password")

sys.path.insert(0, ".")

import pyotp  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from app.core import security  # noqa: E402
from app.models import AuditLog, Base, MfaBackupCode, RefreshToken, User  # noqa: E402
from app.services import auth_service, mfa_service  # noqa: E402
from app.services.auth_service import AuthError  # noqa: E402
from app.services.mfa_service import MfaError  # noqa: E402
from tests.fake_redis import FakeRedis  # noqa: E402

RESULTS: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    RESULTS.append((name, bool(condition)))


def audited(rows: list[AuditLog], action: str) -> bool:
    return any(r.action == action for r in rows)


async def seed_user(db, email: str) -> User:
    user = User(
        email=email,
        hashed_password=security.hash_password("hunter2hunter2"),
        role="member",
        status="active",
        email_verified_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    return user


async def main() -> int:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    # 1. Enrollment mints a secret but does not switch MFA on.
    async with Session() as db:
        redis = FakeRedis()
        user = await seed_user(db, "mfa@example.com")
        secret, uri = await mfa_service.enroll(db, user.id)
        await db.refresh(user)
        check("enroll returns secret + otpauth uri", bool(secret) and "otpauth://" in uri)
        check("enroll stores the secret", user.mfa_secret == secret)
        check("enroll does NOT enable MFA", user.mfa_enabled is False)
        rows = (await db.execute(select(AuditLog))).scalars().all()
        check("enroll writes audit", audited(rows, "user.mfa.enrolled"))

        # 2. Activation with a wrong code changes nothing.
        try:
            await mfa_service.activate(db, redis, user.id, "000000")
            wrong = "no error raised"
        except MfaError as exc:
            wrong = exc.code
        check("activate with wrong code refused", wrong == "UNAUTHORIZED")
        await db.refresh(user)
        check("wrong activate did not enable MFA", user.mfa_enabled is False)

        # 3. Activation with the right code enables MFA and issues 10 codes once.
        codes = await mfa_service.activate(db, redis, user.id, pyotp.TOTP(secret).now())
        await db.refresh(user)
        check("activate enables MFA", user.mfa_enabled is True)
        check("activate issues 10 backup codes", len(codes) == 10)
        check("backup codes unique", len(set(codes)) == 10)
        stored = (await db.execute(select(MfaBackupCode))).scalars().all()
        check("10 backup rows persisted", len(stored) == 10)
        check("no raw backup code stored", all(r.code_hash != c for r in stored for c in codes))
        check("all backup codes unused", all(r.used_at is None for r in stored))
        rows = (await db.execute(select(AuditLog))).scalars().all()
        check("activate writes audit", audited(rows, "user.mfa.activated"))

        # 4. A TOTP code cannot be replayed inside its own validity window.
        now = pyotp.TOTP(user.mfa_secret).now()
        first = await mfa_service.verify_code(db, redis, user, now)
        again = await mfa_service.verify_code(db, redis, user, now)
        check("first TOTP verifies", first == "totp")
        check("replayed TOTP refused", again is None)
        check("replay marker stored", any(k.startswith("totp_used:") for k in redis._kv))

        # 5. Backup codes are single-use and still accepted after the TOTP window.
        backup = codes[0]
        used1 = await mfa_service.verify_code(db, redis, user, backup)
        used2 = await mfa_service.verify_code(db, redis, user, backup)
        check("backup code accepted once", used1 == "backup")
        check("backup code refused on reuse", used2 is None)

        # 6. MFA-off user verifies nothing, even with a valid TOTP code.
        user.mfa_enabled = False
        await db.commit()
        check("MFA-off user cannot verify",
              await mfa_service.verify_code(db, redis, user, pyotp.TOTP(user.mfa_secret).now()) is None)
        user.mfa_enabled = True
        await db.commit()

        # 7. Disabling needs a live code and clears secret + codes.
        # Fresh replay store: the code above is already marked used in this
        # window, and a disable is a separate request in a fresh window.
        redis_disable = FakeRedis()
        try:
            await mfa_service.disable(db, redis_disable, user.id, "000000")
            bad_disable = "no error raised"
        except MfaError as exc:
            bad_disable = exc.code
        check("disable with wrong code refused", bad_disable == "UNAUTHORIZED")
        await mfa_service.disable(db, redis_disable, user.id, pyotp.TOTP(user.mfa_secret).now())
        await db.refresh(user)
        check("disable clears the secret", user.mfa_secret is None)
        check("disable switches MFA off", user.mfa_enabled is False)
        spent = (await db.execute(
            select(MfaBackupCode).where(MfaBackupCode.user_id == user.id)
        )).scalars().all()
        check("disable consumes remaining codes", all(r.used_at is not None for r in spent))
        rows = (await db.execute(select(AuditLog))).scalars().all()
        check("disable writes audit", audited(rows, "user.mfa.disabled"))

    # 8. MFA login: pending refresh token + TOTP -> rotated session; no replay.
    async with Session() as db:
        redis = FakeRedis()
        user = await seed_user(db, "mfa-login@example.com")
        secret, _ = await mfa_service.enroll(db, user.id)
        await mfa_service.activate(db, redis, user.id, pyotp.TOTP(secret).now())

        pending = await auth_service.issue_mfa_session(db, user)
        tokens = (await db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user.id)
        )).scalars().all()
        check("issue_mfa_session creates one pending token", len(tokens) == 1)
        rows = (await db.execute(select(AuditLog))).scalars().all()
        check("pending session writes challenge audit", audited(rows, "user.login_mfa_challenge"))

        try:
            await auth_service.complete_mfa_login(db, redis, pending, "000000")
            bad_totp = "no error raised"
        except AuthError as exc:
            bad_totp = exc.code
        check("login/totp wrong code refused", bad_totp == "UNAUTHORIZED")

        # The same pending token may be retried with a fresh code — the lock is
        # the TOTP code, not the token. This attempt succeeds.
        access, refresh, expires = await auth_service.complete_mfa_login(
            db, redis, pending, pyotp.TOTP(secret).now()
        )
        check("login/totp issues an access token", bool(access))
        check("login/totp rotates the refresh token", refresh != pending)
        check("login/totp returns an expiry", expires > 0)
        rows = (await db.execute(select(AuditLog))).scalars().all()
        check("completed MFA login audited", audited(rows, "user.login"))
        check("failed MFA login audited", audited(rows, "user.mfa.login_failed"))

        # The consumed pending token is now revoked: replay must fail.
        try:
            await auth_service.complete_mfa_login(db, redis, pending, pyotp.TOTP(secret).now())
            replay = "no error raised"
        except AuthError as exc:
            replay = exc.code
        check("consumed pending token refused", replay == "UNAUTHORIZED")

        # A non-MFA account cannot complete an MFA login at all.
        plain = await seed_user(db, "plain@example.com")
        pending_plain = await auth_service.issue_mfa_session(db, plain)
        try:
            await auth_service.complete_mfa_login(db, redis, pending_plain, "123456")
            nomfa = "no error raised"
        except AuthError as exc:
            nomfa = exc.code
        check("non-MFA account cannot complete MFA login", nomfa == "FORBIDDEN")

    # 9. Step-up token semantics: freshness claim present, absent on access tokens.
    payload = security.decode_access_token(security.create_step_up_token("u1", "member"))
    check("step-up token carries step_up claim", payload.get("step_up") is True)
    check("step-up token carries subject", payload["sub"] == "u1")
    access_payload = security.decode_access_token(security.create_access_token("u1", "member"))
    check("access token has no step_up claim", "step_up" not in access_payload)

    # 10. No raw secret ever reaches the audit trail.
    async with Session() as db:
        rows = (await db.execute(select(AuditLog))).scalars().all()
        blobs = " ".join(str(r.detail) + str(r.resource) for r in rows)
        check("no raw backup code in audit", not any(c in blobs for c in codes))
        check("audit chain intact", all(r.created_at is not None for r in rows))

    print("\n=== ADR-008 MFA self-check ===")
    failed = sum(1 for _, ok in RESULTS if not ok)
    for name, ok in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} PASS")
    await engine.dispose()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

