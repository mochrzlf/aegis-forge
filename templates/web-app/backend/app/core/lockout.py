"""Temporary account lockout after repeated login failures (AGENTS.md §3.2, ADR-004).

Complements the rate limiter rather than duplicating it: rate limiting bounds
request *volume*, lockout bounds *failed attempts per account* and pulls the
account out of reach while the lock expires. State lives in Redis, so a lock
clears itself automatically — no cleanup job, no stuck rows.

Emails are normalized to lowercase before use as a key component.
"""
from redis.asyncio import Redis

from app.core.config import settings


def _keys(email: str) -> tuple[str, str]:
    normalized = email.lower()
    return f"fails:{normalized}", f"lock:{normalized}"


async def is_locked(redis: Redis, email: str) -> bool:
    _, lock = _keys(email)
    return bool(await redis.get(lock))


async def register_failure(redis: Redis, email: str) -> bool:
    """Record a failed login. Returns True when this failure trips the lock.

    The failure counter is given a TTL only on its *first* increment, so a
    patient attacker cannot keep resetting the window with one attempt per
    interval — the lock still trips on N failures within the window.
    """
    fails, lock = _keys(email)
    count = await redis.incr(fails)
    if count == 1:
        await redis.expire(fails, settings.LOCKOUT_SECONDS)
    if count >= settings.LOCKOUT_MAX_FAILURES:
        # NX: the lock timestamp is set once, by the failure that trips it.
        return bool(await redis.set(lock, "1", ex=settings.LOCKOUT_SECONDS, nx=True))
    return False


async def unlock(redis: Redis, email: str) -> None:
    """Clear both the lock and the failure counter (manual admin unlock)."""
    fails, lock = _keys(email)
    pipe = redis.pipeline()
    pipe.delete(fails)
    pipe.delete(lock)
    await pipe.execute()
