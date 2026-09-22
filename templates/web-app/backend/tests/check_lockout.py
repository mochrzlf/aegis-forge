"""Runnable self-check for app.core.lockout — no pytest, no external deps.

Run from the backend directory:
    python3 tests/check_lockout.py
"""
import asyncio
import sys

# Settings are required at import time; provide placeholder values so the check
# runs without a .env file. Real values come from the environment in service.
import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://aegis:a@db:5432/aegis_app")
os.environ.setdefault("JWT_SECRET", "x" * 48)
os.environ.setdefault("POSTGRES_PASSWORD", "change_me_strong_password")

sys.path.insert(0, ".")

from app.core import lockout  # noqa: E402
from app.core.config import settings  # noqa: E402
from tests.fake_redis import FakeRedis  # noqa: E402


async def main():
    redis = FakeRedis()
    email = "victim@example.com"

    # A fresh account is neither locked nor tripped by a single failure.
    assert await lockout.is_locked(redis, email) is False
    assert await lockout.register_failure(redis, email) is False

    # The lock must trip exactly on the Nth failure, not before.
    max_failures = settings.LOCKOUT_MAX_FAILURES
    for _ in range(max_failures - 2):  # already 2 recorded above
        assert await lockout.register_failure(redis, email) is False
    assert await lockout.register_failure(redis, email) is True, "must lock at the threshold"
    assert await lockout.is_locked(redis, email) is True
    print(f"  locks after {max_failures} failures, not before — OK")

    # Another account must be untouched (per-account isolation).
    assert await lockout.is_locked(redis, "other@example.com") is False
    print("  per-account isolation — OK")

    # Unlock clears both the lock and the failure counter.
    await lockout.unlock(redis, email)
    assert await lockout.is_locked(redis, email) is False
    assert await lockout.register_failure(redis, email) is False
    print("  unlock resets lock + failure counter — OK")

    print("lockout self-check: PASS")


if __name__ == "__main__":
    asyncio.run(main())
