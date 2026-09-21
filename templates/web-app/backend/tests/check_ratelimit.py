"""Runnable self-check for app.core.ratelimit — no pytest, no external deps.

Run from the backend directory:
    python3 tests/check_ratelimit.py
"""
import asyncio
import sys

sys.path.insert(0, ".")

from app.core.ratelimit import is_rate_limited
from tests.fake_redis import FakeRedis


async def main():
    redis = FakeRedis()
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
