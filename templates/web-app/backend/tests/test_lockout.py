import pytest
from app.core import lockout
from app.core.config import settings
from tests.fake_redis import FakeRedis


@pytest.mark.asyncio
async def test_fresh_account_not_locked(fake_redis: FakeRedis):
    email = "test@example.com"
    assert await lockout.is_locked(fake_redis, email) is False
    assert await lockout.register_failure(fake_redis, email) is False


@pytest.mark.asyncio
async def test_locks_at_threshold(fake_redis: FakeRedis):
    email = "victim@example.com"
    max_failures = settings.LOCKOUT_MAX_FAILURES

    for _ in range(max_failures - 1):
        assert await lockout.register_failure(fake_redis, email) is False

    # N-th failure must lock
    assert await lockout.register_failure(fake_redis, email) is True
    assert await lockout.is_locked(fake_redis, email) is True


@pytest.mark.asyncio
async def test_lockout_account_isolation(fake_redis: FakeRedis):
    email1 = "locked@example.com"
    email2 = "innocent@example.com"
    max_failures = settings.LOCKOUT_MAX_FAILURES

    for _ in range(max_failures):
        await lockout.register_failure(fake_redis, email1)

    assert await lockout.is_locked(fake_redis, email1) is True
    assert await lockout.is_locked(fake_redis, email2) is False


@pytest.mark.asyncio
async def test_unlock_resets_lock_and_counter(fake_redis: FakeRedis):
    email = "locked@example.com"
    for _ in range(settings.LOCKOUT_MAX_FAILURES):
        await lockout.register_failure(fake_redis, email)

    assert await lockout.is_locked(fake_redis, email) is True

    await lockout.unlock(fake_redis, email)
    assert await lockout.is_locked(fake_redis, email) is False
    assert await lockout.register_failure(fake_redis, email) is False
