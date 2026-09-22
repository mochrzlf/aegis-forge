"""Auth endpoints — refresh token ONLY via HttpOnly cookie."""
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.deps import CurrentUser, get_current_user, get_db, get_redis
from app.core.envelope import ErrorCode, err, ok
from app.core.lockout import is_locked, register_failure
from app.core.mailer import send_email
from app.core.ratelimit import client_ip, enforce_rate_limit
from app.core.security import REFRESH_COOKIE
from app.repositories import get_user_by_id
from app.schemas import (
    BackupCodesOut,
    EmailVerificationConfirmIn,
    LoginIn,
    MfaCodeIn,
    MfaEnrollOut,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    RegisterIn,
    TokenOut,
    UserOut,
)
from app.services import auth_service, mfa_service
from app.services.audit_service import write_audit
from app.services.auth_service import AuthError
from app.services.mfa_service import MfaError

router = APIRouter(prefix="/auth", tags=["auth"])


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
        ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
    }
    return HTTPException(
        status_code=status_map.get(exc.code, status.HTTP_400_BAD_REQUEST),
        detail=err(exc.code, exc.message),
    )


def _mfa_error(exc: MfaError) -> HTTPException:
    status_map = {
        ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
        ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
    }
    return HTTPException(
        status_code=status_map.get(exc.code, status.HTTP_400_BAD_REQUEST),
        detail=err(exc.code, exc.message),
    )


def _hash_email(email: str) -> str:
    """SHA-256 prefix for audit references — email is PII, never logged raw."""
    return security.email_fingerprint(email)


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
        new_user = await auth_service.register(db, payload.email, payload.password)
        access, refresh, expires = await auth_service.login(db, payload.email, payload.password)
        verify_token = await auth_service.request_email_verification(db, new_user.id)
    except AuthError as exc:
        raise _auth_error(exc)
    await send_email(
        payload.email,
        "Verify your email",
        f"Verify your account (link valid {settings.EMAIL_VERIFICATION_TOKEN_HOURS} h): "
        f"{settings.APP_BASE_URL}/verify-email?token={verify_token}\n"
        "If you did not create this account, ignore this email.",
    )
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
        user = await auth_service.authenticate(db, payload.email, payload.password)
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
    if user.mfa_enabled:
        # Half-authenticated: the refresh cookie is set, but no access token is
        # issued until the second factor is proven (ADR-008). The client
        # completes the flow at /auth/login/totp.
        refresh = await auth_service.issue_mfa_session(db, user)
        _set_refresh_cookie(response, refresh)
        response.status_code = status.HTTP_202_ACCEPTED
        return ok({"mfa_required": True})
    access, refresh, expires = await auth_service.issue_session(db, user)
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


@router.post("/password-reset/request")
async def request_password_reset(
    payload: PasswordResetRequestIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Email a single-use reset link (ADR-007).

    The response is identical whether or not the address is registered — an
    unauthenticated caller may not learn which accounts exist.
    """
    await enforce_rate_limit(
        redis,
        f"rl:pwreset:ip:{client_ip(request)}",
        settings.RATE_LIMIT_PASSWORD_RESET_REQUEST_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    await enforce_rate_limit(
        redis,
        f"rl:pwreset:user:{payload.email.lower()}",
        settings.RATE_LIMIT_PASSWORD_RESET_EMAIL,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    token = await auth_service.request_password_reset(db, payload.email)
    if token is not None:
        await send_email(
            payload.email,
            "Reset your password",
            f"Reset link (valid {settings.PASSWORD_RESET_TOKEN_MINUTES} min): "
            f"{settings.APP_BASE_URL}/reset-password?token={token}\n"
            "If you did not request this, ignore this email — your password is unchanged.",
        )
    return ok({"requested": True})


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    payload: PasswordResetConfirmIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Redeem a reset link and set a new password (ADR-007)."""
    await enforce_rate_limit(
        redis,
        f"rl:pwreset-confirm:ip:{client_ip(request)}",
        settings.RATE_LIMIT_PASSWORD_RESET_CONFIRM_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    try:
        user = await auth_service.confirm_password_reset(db, payload.token, payload.new_password)
    except AuthError as exc:
        raise _auth_error(exc)
    return ok({"user_id": user.id, "password_changed": True})


@router.post("/email-verification/request")
async def request_email_verification(
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Send (or resend) a verification link for the caller's own address (ADR-007)."""
    await enforce_rate_limit(
        redis,
        f"rl:verifyreq:ip:{client_ip(request)}",
        settings.RATE_LIMIT_EMAIL_VERIFICATION_REQUEST_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    try:
        token = await auth_service.request_email_verification(db, user.id)
    except AuthError as exc:
        raise _auth_error(exc)
    db_user = await get_user_by_id(db, user.id)
    await send_email(
        db_user.email,
        "Verify your email",
        f"Verify your account (link valid {settings.EMAIL_VERIFICATION_TOKEN_HOURS} h): "
        f"{settings.APP_BASE_URL}/verify-email?token={token}\n"
        "If you did not request this, ignore this email.",
    )
    return ok({"verification_sent": True})


@router.post("/email-verification/confirm")
async def confirm_email_verification(
    payload: EmailVerificationConfirmIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Redeem a verification link (ADR-007)."""
    await enforce_rate_limit(
        redis,
        f"rl:verifyconf:ip:{client_ip(request)}",
        settings.RATE_LIMIT_EMAIL_VERIFICATION_CONFIRM_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    try:
        user = await auth_service.confirm_email_verification(db, payload.token)
    except AuthError as exc:
        raise _auth_error(exc)
    return ok({"user_id": user.id, "email_verified": True})


# --- MFA / TOTP step-up (ADR-008) --------------------------------------------


@router.post("/mfa/enroll")
async def enroll_mfa(
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Mint a TOTP secret. Inactive until the client proves it at /activate."""
    await enforce_rate_limit(
        redis,
        f"rl:mfa:ip:{client_ip(request)}",
        settings.RATE_LIMIT_MFA_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    try:
        secret, otpauth_uri = await mfa_service.enroll(db, user.id)
    except MfaError as exc:
        raise _mfa_error(exc)
    # The secret is shown once, in-band, for manual entry — it is not emailed
    # and it is not logged.
    return ok(MfaEnrollOut(secret=secret, otpauth_uri=otpauth_uri).model_dump())


@router.post("/mfa/activate")
async def activate_mfa(
    payload: MfaCodeIn,
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Confirm the first TOTP code and switch MFA on. Backup codes: once only."""
    await enforce_rate_limit(
        redis,
        f"rl:mfa:ip:{client_ip(request)}",
        settings.RATE_LIMIT_MFA_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    try:
        codes = await mfa_service.activate(db, redis, user.id, payload.code)
    except MfaError as exc:
        raise _mfa_error(exc)
    return ok(BackupCodesOut(backup_codes=codes).model_dump())


@router.post("/login/totp")
async def login_totp(
    payload: MfaCodeIn,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Complete the half-authenticated login from /auth/login (ADR-008)."""
    await enforce_rate_limit(
        redis,
        f"rl:mfa:ip:{client_ip(request)}",
        settings.RATE_LIMIT_MFA_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    presented = request.cookies.get(REFRESH_COOKIE)
    if not presented:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err(ErrorCode.UNAUTHORIZED, "Missing refresh token"),
        )
    try:
        access, refresh, expires = await auth_service.complete_mfa_login(
            db, redis, presented, payload.code
        )
    except AuthError as exc:
        # A failed second factor voids the pending session — the client must
        # re-authenticate from /auth/login.
        _clear_refresh_cookie(response)
        raise _auth_error(exc)
    _set_refresh_cookie(response, refresh)
    return ok(TokenOut(access_token=access, expires_in=expires).model_dump())


@router.post("/step-up")
async def step_up(
    payload: MfaCodeIn,
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Trade a TOTP code for a short-lived step-up token (security-iam-policy
    §41, ADR-008). Required by /users/me DELETE and every later step-up consumer."""
    await enforce_rate_limit(
        redis,
        f"rl:mfa:ip:{client_ip(request)}",
        settings.RATE_LIMIT_MFA_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    db_user = await get_user_by_id(db, user.id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err(ErrorCode.NOT_FOUND, "Account not found"),
        )
    if not db_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err(ErrorCode.FORBIDDEN, "MFA is not active on this account"),
        )
    method = await mfa_service.verify_code(db, redis, db_user, payload.code)
    if method is None:
        await write_audit(
            db,
            actor_user_id=user.id,
            action="user.mfa.step_up_failed",
            resource=f"user:{user.id}",
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err(ErrorCode.UNAUTHORIZED, "Invalid TOTP code"),
        )
    token = security.create_step_up_token(db_user.id, db_user.role)
    await write_audit(
        db,
        actor_user_id=user.id,
        action="user.mfa.step_up",
        resource=f"user:{user.id}",
        detail=f"Step-up granted via {method}",
    )
    await db.commit()
    return ok(
        {
            "step_up_token": token,
            "expires_in": settings.MFA_STEP_UP_TOKEN_MINUTES * 60,
        }
    )


@router.post("/mfa/disable")
async def disable_mfa(
    payload: MfaCodeIn,
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Turn MFA off. A live code is required — weakening an account is not free."""
    await enforce_rate_limit(
        redis,
        f"rl:mfa:ip:{client_ip(request)}",
        settings.RATE_LIMIT_MFA_IP,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    try:
        await mfa_service.disable(db, redis, user.id, payload.code)
    except MfaError as exc:
        raise _mfa_error(exc)
    return ok({"mfa_disabled": True})
