"""Database session + Redis client + auth/RBAC dependencies."""
from typing import AsyncGenerator

import redis.asyncio as aioredis
import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.envelope import ErrorCode, err

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

_redis: aioredis.Redis | None = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


def _unauthorized(message: str = "Authentication required") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=err(ErrorCode.UNAUTHORIZED, message),
    )


class CurrentUser:
    def __init__(self, user_id: str, role: str):
        self.id = user_id
        self.role = role


async def get_current_user(request: Request) -> CurrentUser:
    # Access token travels in the Authorization header (short-lived JWT).
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise _unauthorized()
    token = auth.removeprefix("Bearer ").strip()
    try:
        from app.core.security import decode_access_token
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise _unauthorized("Invalid or expired token")
    return CurrentUser(user_id=payload["sub"], role=payload.get("role", "member"))


async def get_step_up_user(request: Request) -> CurrentUser:
    # Bearer must be a step-up token — minted minutes ago, only after a fresh
    # TOTP challenge (ADR-008). A normal access token will not do.
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise _unauthorized("Step-up authentication required")
    token = auth.removeprefix("Bearer ").strip()
    try:
        from app.core.security import decode_access_token
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise _unauthorized("Invalid or expired step-up token")
    if not payload.get("step_up"):
        raise _unauthorized("Step-up authentication required")
    return CurrentUser(user_id=payload["sub"], role=payload.get("role", "member"))


def require_step_up():
    """Fresh-TOTP guard for critical actions (AGENTS.md §3.2.4, ADR-008).

    Complements RBAC: role proves *who* the caller is, step-up proves they are
    the account holder *right now*, which is what security-iam-policy.md §41
    demands for destructive actions.
    """
    async def checker(user: CurrentUser = Depends(get_step_up_user)) -> CurrentUser:
        return user
    return checker


def require_roles(*roles: str):
    """RBAC guard — server-side, on every protected route (AGENTS.md §3.2.1)."""
    async def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=err(ErrorCode.FORBIDDEN, "Insufficient role"),
            )
        return user
    return checker
