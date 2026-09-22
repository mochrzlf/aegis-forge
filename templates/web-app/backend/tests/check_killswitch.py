"""Runnable self-check for the JML kill-switch (ADR-005) — no pytest.

Uses an in-memory SQLite session to run the real repository UPDATE, so the
revocation predicate is exercised against actual SQL, not a mock. The schema is
created from the ORM metadata, so it needs no Alembic migration here.

Run from the backend directory:
    python3 tests/check_killswitch.py
"""
import asyncio
import os
import sys

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://aegis:a@db:5432/aegis_app")
os.environ.setdefault("JWT_SECRET", "x" * 48)
os.environ.setdefault("POSTGRES_PASSWORD", "change_me_strong_password")

sys.path.insert(0, ".")

from datetime import datetime, timedelta, timezone  # noqa: E402

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.models import Base, RefreshToken  # noqa: E402
from app.repositories import (  # noqa: E402
    count_active_refresh_tokens,
    create_user,
    revoke_all_refresh_tokens,
)


async def main():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        victim = await create_user(db, "victim@example.com", "hashed")
        other = await create_user(db, "other@example.com", "hashed")

        expiry = datetime.now(timezone.utc) + timedelta(days=30)

        # Two live sessions for the victim, one already revoked, one live for
        # another user — the last must never be touched.
        live_ids = []
        for _ in range(2):
            token = RefreshToken(user_id=victim.id, token_hash=f"live-{_}", expires_at=expiry)
            db.add(token)
            live_ids.append(token)
        stale = RefreshToken(
            user_id=victim.id,
            token_hash="stale",
            expires_at=expiry,
            revoked_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.add(stale)
        db.add(RefreshToken(user_id=other.id, token_hash="other-live", expires_at=expiry))
        await db.commit()

        assert await count_active_refresh_tokens(db, victim.id) == 2
        revoked = await revoke_all_refresh_tokens(db, victim.id)
        assert revoked == 2, f"expected 2 live sessions revoked, got {revoked}"
        assert await count_active_refresh_tokens(db, victim.id) == 0
        print("  both live victim sessions revoked — OK")

        # The other user's session must be untouched (blast-radius guard).
        assert await count_active_refresh_tokens(db, other.id) == 1
        print("  other user's sessions untouched — OK")

        # Revoking again on an already-locked account is a no-op, not an error.
        assert await revoke_all_refresh_tokens(db, victim.id) == 0
        print("  re-invocation is idempotent — OK")

    await engine.dispose()
    print("killswitch self-check: PASS")


if __name__ == "__main__":
    asyncio.run(main())
