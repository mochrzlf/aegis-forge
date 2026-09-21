"""Auth endpoints — refresh token ONLY via HttpOnly cookie."""
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db, get_redis
from app.core.envelope import ErrorCode, err, ok
from app.core.lockout import is_locked, register_failure
from app.core.ratelimit import client_ip, enforce_rate_limit
from app.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from app.services import auth_service
from app.services.audit_service import write_audit
from app.services.auth_service import AuthError

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path=settings.COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE, path=settings.COOKIE_PATH)


def _auth_error(exc: AuthError) -> HTTPException:
    status_map = {
        ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
        ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    return HTTPException(
        status_code=status_map.get(exc.code, status.HTTP_400_BAD_REQUEST),
        detail=err(exc.code, exc.message),
    )


def _hash_email(email: str) -> str:
    """SHA-256 prefix for audit references — email is PII, never logged raw."""
    return hashlib.sha256(email.encode("utf-8")).hexdigest()[:16]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterIn,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    # Open registration is the cheapest denial-of-service vector here, so it
    # carries the tightest limit and needs no account to hit it.
    await enforce_rate_limit(
        redis,
        f"rl:register:ip:{client_ip(request)}",
        settings.RATE_LIMIT_REGISTER_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    try:
        await auth_service.register(db, payload.email, payload.password)
        access, refresh, expires = await auth_service.login(db, payload.email, payload.password)
    except AuthError as exc:
        raise _auth_error(exc)
    _set_refresh_cookie(response, refresh)
    return ok(TokenOut(access_token=access, expires_in=expires).model_dump())


@router.post("/login")
async def login(
    payload: LoginIn,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    # Two bounds: a per-account limit that stalls password guessing, and a
    # looser per-IP limit that stalls the same guessing spread across many
    # accounts (AGENTS.md §3.2; ADR-003).
    await enforce_rate_limit(
        redis,
        f"rl:login:user:{payload.email.lower()}",
        settings.RATE_LIMIT_LOGIN_USER,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    await enforce_rate_limit(
        redis,
        f"rl:login:ip:{client_ip(request)}",
        settings.RATE_LIMIT_LOGIN_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    # Locked accounts are refused before any password is hashed or compared.
    if await is_locked(redis, payload.email):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=err(
                ErrorCode.LOCKED,
                "Account temporarily locked after repeated failed logins. Try again later.",
            ),
        )
    try:
        access, refresh, expires = await auth_service.login(db, payload.email, payload.password)
    except AuthError as exc:
        # Only a genuine credential failure counts towards the lock — a
        # non-active account (FORBIDDEN) or validation errors must not.
        if exc.code == ErrorCode.UNAUTHORIZED:
            if await register_failure(redis, payload.email):
                await write_audit(
                    db,
                    actor_user_id=None,
                    action="user.locked",
                    resource=f"auth:lockout:{_hash_email(payload.email)}",
                    detail=f"Locked after {settings.LOCKOUT_MAX_FAILURES} failed logins",
                )
        raise _auth_error(exc)
    _set_refresh_cookie(response, refresh)
    return ok(TokenOut(access_token=access, expires_in=expires).model_dump())


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    # Throttled by IP only: the caller cannot be identified until the presented
    # token is validated, so a per-user bound is not available yet.
    await enforce_rate_limit(
        redis,
        f"rl:refresh:ip:{client_ip(request)}",
        settings.RATE_LIMIT_REFRESH_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err(ErrorCode.UNAUTHORIZED, "Missing refresh token"),
        )
    try:
        access, new_refresh, expires = await auth_service.refresh(db, token)
    except AuthError as exc:
        _clear_refresh_cookie(response)
        raise _auth_error(exc)
    _set_refresh_cookie(response, new_refresh)
    return ok(TokenOut(access_token=access, expires_in=expires).model_dump())


@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get(REFRESH_COOKIE)
    if token:
        await auth_service.logout(db, token)
    _clear_refresh_cookie(response)
    return ok({"logged_out": True})
