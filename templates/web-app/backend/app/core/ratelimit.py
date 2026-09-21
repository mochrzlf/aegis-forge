"""Sliding-window rate limiting on auth endpoints (AGENTS.md §3.2, ADR-003).

Two parts, deliberately separated:
  * ``is_rate_limited``  — pure counting logic, easy to unit-test.
  * ``enforce_rate_limit`` — thin FastAPI wiring that turns a breach into a 429.

No new dependency: it runs on the Redis client already configured in
``app.core.deps``. Redis is declared for this purpose; making the claim real
closes gap-analysis item 1.1.
"""
import time

import secrets
from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

from app.core.envelope import ErrorCode, err


async def is_rate_limited(
    redis: Redis, key: str, limit: int, window_seconds: int
) -> bool:
    """Sliding-window counter over a Redis sorted set.

    Returns True when more than ``limit`` hits occurred in the trailing window.
    Each hit is stored with the current timestamp as its score, so the window
    slides with every call instead of snapping to fixed minute boundaries.
    """
    now = time.time()
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_seconds)  # drop expired hits
    pipe.zadd(key, {secrets.token_hex(8): now})          # record this hit
    pipe.expire(key, window_seconds)                     # cleanup after idle
    pipe.zcard(key)                                      # count hits in window
    _, _, _, count = await pipe.execute()
    return count > limit


def client_ip(request: Request) -> str:
    """Best-effort client IP.

    Trust boundary: ``X-Forwarded-For`` is attacker-controlled unless the service
    sits behind a trusted reverse proxy that overwrites it. We take the first
    entry only when the header is present; behind a spoofable proxy, deploy a
    trusted-proxy allowlist instead (see ADR-003).
    """
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def enforce_rate_limit(
    redis: Redis, key: str, limit: int, window_seconds: int
) -> None:
    """Raise 429 when the caller has exceeded ``limit`` in the window."""
    if await is_rate_limited(redis, key, limit, window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=err(
                ErrorCode.RATE_LIMITED,
                "Too many requests. Please slow down and try again shortly.",
            ),
            headers={"Retry-After": str(window_seconds)},
        )
