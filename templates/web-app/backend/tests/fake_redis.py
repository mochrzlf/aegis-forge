"""Minimal in-memory Redis stand-in for the runnable self-checks.

Implements only the commands the modules under test use — enough to verify
counting and window logic offline, with no live cache and no test framework.
Run any check with plain `python3 tests/check_*.py` from the backend directory.
"""
import time
from collections import defaultdict


class _Pipeline:
    """Records calls and replays them in order against the owning fake."""

    def __init__(self, redis: "FakeRedis"):
        self._redis = redis
        self._ops: list[tuple[str, tuple]] = []

    def __getattr__(self, name: str):
        def record(*args):
            self._ops.append((name, args))
            return self

        return record

    async def execute(self):
        results = []
        for name, args in self._ops:
            results.append(await getattr(self._redis, name)(*args))
        return results


class FakeRedis:
    def __init__(self):
        self._kv: dict[str, str] = {}
        self._zsets: dict[str, dict[str, float]] = defaultdict(dict)
        self._ttls: dict[str, float] = {}

    def pipeline(self) -> _Pipeline:
        return _Pipeline(self)

    def _alive(self, key: str) -> bool:
        exp = self._ttls.get(key)
        if exp is not None and exp < time.time():
            self._kv.pop(key, None)
            self._zsets.pop(key, None)
            self._ttls.pop(key, None)
            return False
        return True

    async def get(self, key: str):
        return self._kv.get(key) if self._alive(key) else None

    async def set(self, key: str, value, ex: int | None = None, nx: bool = False):
        if nx and self._alive(key) and key in self._kv:
            return None
        self._kv[key] = value
        if ex:
            self._ttls[key] = time.time() + ex
        return True

    async def delete(self, key: str) -> int:
        existed = key in self._kv or key in self._zsets
        self._kv.pop(key, None)
        self._zsets.pop(key, None)
        self._ttls.pop(key, None)
        return 1 if existed else 0

    async def incr(self, key: str) -> int:
        if not self._alive(key):
            self._kv.pop(key, None)
        value = int(self._kv.get(key, 0)) + 1
        self._kv[key] = str(value)
        return value

    async def expire(self, key: str, ttl: int) -> bool:
        if not self._alive(key):
            return False
        self._ttls[key] = time.time() + ttl
        return True

    async def zadd(self, key: str, mapping: dict) -> int:
        self._zsets[key].update(mapping)
        return len(mapping)

    async def zremrangebyscore(self, key: str, _min, _max) -> int:
        before = len(self._zsets[key])
        self._zsets[key] = {m: s for m, s in self._zsets[key].items() if s > _max}
        return before - len(self._zsets[key])

    async def zcard(self, key: str) -> int:
        return len(self._zsets[key])
