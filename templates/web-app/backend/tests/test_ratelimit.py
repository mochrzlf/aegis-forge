import pytest
from app.core.ratelimit import is_rate_limited
from tests.fake_redis import FakeRedis


@pytest.mark.asyncio
async def test_ratelimit_allows_up_to_limit_and_blocks(fake_redis: FakeRedis):
    limit, window = 3, 60
    for i in range(limit):
        allowed = await is_rate_limited(fake_redis, "key1", limit, window)
        assert allowed is False, f"hit {i+1} should pass"

    blocked = await is_rate_limited(fake_redis, "key1", limit, window)
    assert blocked is True, "hit beyond limit must be blocked"


@pytest.mark.asyncio
async def test_ratelimit_isolates_identifiers(fake_redis: FakeRedis):
    limit, window = 3, 60
    for _ in range(limit):
        await is_rate_limited(fake_redis, "key1", limit, window)

    # Different key must not be blocked
    other = await is_rate_limited(fake_redis, "key2", limit, window)
    assert other is False


@pytest.mark.asyncio
async def test_ratelimit_expires_after_window(fake_redis: FakeRedis):
    limit, window = 3, 60
    for _ in range(limit):
        await is_rate_limited(fake_redis, "key1", limit, window)

    # Expire hits
    expired = fake_redis._zsets["key1"]
    fake_redis._zsets["key1"] = {m: s - window - 1 for m, s in expired.items()}

    assert await is_rate_limited(fake_redis, "key1", limit, window) is False
