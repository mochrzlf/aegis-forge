from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.models import AuthToken, RefreshToken, User
from app.repositories import count_active_refresh_tokens, create_user
from app.services import auth_service
from app.services.auth_service import AuthError


@pytest.mark.asyncio
async def test_password_reset_flow(db_session: AsyncSession):
    user = await create_user(db_session, "reset@example.com", security.hash_password("oldpass12345"))
    raw_token = await auth_service.request_password_reset(db_session, "reset@example.com")
    assert raw_token is not None

    # Active session before reset
    expiry = datetime.now(timezone.utc) + timedelta(days=30)
    db_session.add(RefreshToken(user_id=user.id, token_hash="live-session", expires_at=expiry))
    await db_session.commit()
    assert await count_active_refresh_tokens(db_session, user.id) == 1

    # Confirm reset
    await auth_service.confirm_password_reset(db_session, raw_token, "newpass12345")

    # Verify session revoked
    assert await count_active_refresh_tokens(db_session, user.id) == 0

    # Verify old password no longer works
    refreshed_user = await db_session.get(User, user.id)
    assert security.verify_password("oldpass12345", refreshed_user.hashed_password) is False
    assert security.verify_password("newpass12345", refreshed_user.hashed_password) is True

    # Replay of reset token fails
    with pytest.raises(AuthError) as exc_info:
        await auth_service.confirm_password_reset(db_session, raw_token, "anotherpass123")
    assert exc_info.value.code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_email_verification_flow(db_session: AsyncSession):
    user = await create_user(db_session, "verify@example.com", security.hash_password("pass12345678"))
    assert user.email_verified_at is None

    raw_token = await auth_service.request_email_verification(db_session, user.id)
    assert raw_token is not None

    # Confirm verification
    await auth_service.confirm_email_verification(db_session, raw_token)

    refreshed = await db_session.get(User, user.id)
    assert refreshed.email_verified_at is not None

    # Replay verification fails
    with pytest.raises(AuthError) as exc_info:
        await auth_service.confirm_email_verification(db_session, raw_token)
    assert exc_info.value.code == "UNAUTHORIZED"
