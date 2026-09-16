"""Auth endpoints — refresh token ONLY via HttpOnly cookie."""
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db
from app.core.envelope import ErrorCode, err, ok
from app.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from app.services import auth_service
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


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterIn, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        await auth_service.register(db, payload.email, payload.password)
        access, refresh, expires = await auth_service.login(db, payload.email, payload.password)
    except AuthError as exc:
        raise _auth_error(exc)
    _set_refresh_cookie(response, refresh)
    return ok(TokenOut(access_token=access, expires_in=expires).model_dump())


@router.post("/login")
async def login(payload: LoginIn, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        access, refresh, expires = await auth_service.login(db, payload.email, payload.password)
    except AuthError as exc:
        raise _auth_error(exc)
    _set_refresh_cookie(response, refresh)
    return ok(TokenOut(access_token=access, expires_in=expires).model_dump())


@router.post("/refresh")
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
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
