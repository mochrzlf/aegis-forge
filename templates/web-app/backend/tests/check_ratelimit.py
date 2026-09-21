"""Runnable self-check for app.core.ratelimit — no pytest, no external deps.

Run from the backend directory:
    python3 tests/check_ratelimit.py

It exercises the sliding-window logic against a small in-memory Redis stand-in,
so the counting and expiry behaviour is verified without a live cache.
"""
import asyncio
import sys
from collections import defaultdict

sys.path.insert(0, ".")

from app.core.ratelimit import is_rate_limited


class _FakeRedis:
    """Minimal stand-in: implements only the four commands the limiter uses."""

    def __init__(self):
        self._zsets: dict[str, dict[str, float]] = defaultdict(dict)

    def pipeline(self):
        return _FakePipeline(self)

    async def _zremrangebyscore(self, key, _min, _max):
        zset = self._zsets[key]
        self._zsets[key] = {m: s for m, s in zset.items() if s > _max}

    async def _zadd(self, key, mapping):
        self._zsets[key].update(mapping)

    async def _expire(self, key, _ttl):
        pass  # idle cleanup is irrelevant to in-memory tests

    async def _zcard(self, key):
        return len(self._zsets[key])


class _FakePipeline:
    def __init__(self, redis: _FakeRedis):
        self._redis = redis
        self._steps = []

    def zremrangebyscore(self, key, _min, _max):
        self._steps.append((self._redis._zremrangebyscore, key, _min, _max))
        return self

    def zadd(self, key, mapping):
        self._steps.append((self._redis._zadd, key, mapping))
        return self

    def expire(self, key, ttl):
        self._steps.append((self._redis._expire, key, ttl))
        return self

    def zcard(self, key):
        self._steps.append((self._redis._zcard, key))
        return self

    async def execute(self):
        results = []
        for func, key, *args in self._steps:
            results.append(await func(key, *args))
        return results


async def main():
    redis = _FakeRedis()

    limit, window = 3, 60

    # Within the window: first `limit` calls are allowed, the next is not.
    for i in range(limit):
        assert await is_rate_limited(redis, "k", limit, window) is False, f"hit {i + 1} should pass"
    assert await is_rate_limited(redis, "k", limit, window) is True, "hit beyond limit must be blocked"
    print(f"  allows {limit} hits, blocks the {limit + 1}th — OK")

    # Different identifiers must not interfere with each other.
    assert await is_rate_limited(redis, "other", limit, window) is False, "keys must be isolated"
    print("  separate identifiers counted independently — OK")

    # After the window passes, hits must be forgotten (score-based expiry).
    expired = redis._zsets["k"]
    redis._zsets["k"] = {m: s - window - 1 for m, s in expired.items()}
    assert await is_rate_limited(redis, "k", limit, window) is False, "expired hits must not count"
    print("  hits outside the window are discarded — OK")

    print("ratelimit self-check: PASS")


if __name__ == "__main__":
    asyncio.run(main())
