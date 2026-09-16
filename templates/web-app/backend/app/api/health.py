"""Liveness/readiness probes (AGENTS.md §4 backend-checklist §5)."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_redis
from app.core.envelope import ok

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz():
    return ok({"status": "alive"})


@router.get("/readyz")
async def readyz(db: AsyncSession = Depends(get_db)):
    checks = {"db": "ok", "cache": "ok"}
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        checks["db"] = "error"
    try:
        redis = await get_redis()
        await redis.ping()
    except Exception:
        checks["cache"] = "error"
    ready = all(v == "ok" for v in checks.values())
    return ok({"status": "ready" if ready else "degraded", "checks": checks})
