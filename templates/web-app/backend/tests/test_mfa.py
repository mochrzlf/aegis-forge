from datetime import datetime, timezone
import pytest
import pyotp
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.models import User
from app.services import auth_service, mfa_service
from app.services.auth_service import AuthError
from app.services.mfa_service import MfaError
from tests.fake_redis import FakeRedis


async def _seed_user(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        hashed_password=security.hash_password("password12345"),
        role="member",
        status="active",
        email_verified_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_mfa_enroll_and_activate(db_session: AsyncSession, fake_redis: FakeRedis):
    user = await _seed_user(db_session, "mfa1@example.com")

    # Enroll
    secret, uri = await mfa_service.enroll(db_session, user.id)
    assert secret is not None
    assert "otpauth://" in uri

    # Inactive before first code
    await db_session.refresh(user)
    assert user.mfa_enabled is False

    # Wrong code fails
    with pytest.raises(MfaError):
        await mfa_service.activate(db_session, fake_redis, user.id, "000000")

    # Correct TOTP code activates MFA
    totp = pyotp.TOTP(secret)
    codes = await mfa_service.activate(db_session, fake_redis, user.id, totp.now())
    assert len(codes) == 10
    await db_session.refresh(user)
    assert user.mfa_enabled is True


@pytest.mark.asyncio
async def test_totp_anti_replay(db_session: AsyncSession, fake_redis: FakeRedis):
    user = await _seed_user(db_session, "mfa2@example.com")
    secret, _ = await mfa_service.enroll(db_session, user.id)
    totp = pyotp.TOTP(secret)
    code = totp.now()
    await mfa_service.activate(db_session, fake_redis, user.id, code)

    await db_session.refresh(user)
    first = await mfa_service.verify_code(db_session, fake_redis, user, code)
    assert first == "totp"

    # Re-verifying the EXACT SAME code inside the validity window must fail (anti-replay)
    again = await mfa_service.verify_code(db_session, fake_redis, user, code)
    assert again is None


@pytest.mark.asyncio
async def test_mfa_login_flow(db_session: AsyncSession):
    fake_redis = FakeRedis()
    user = await _seed_user(db_session, "mfa3@example.com")
    secret, _ = await mfa_service.enroll(db_session, user.id)
    totp = pyotp.TOTP(secret)
    await mfa_service.activate(db_session, fake_redis, user.id, totp.now())

    # Step 1: Issue pending challenge refresh token
    await db_session.refresh(user)
    pending_token = await auth_service.issue_mfa_session(db_session, user)
    assert pending_token is not None

    # Step 2: Complete login with fresh TOTP code
    redis_login = FakeRedis()
    access, refresh, expires_in = await auth_service.complete_mfa_login(
        db_session, redis_login, pending_token, pyotp.TOTP(secret).now()
    )
    assert access is not None
    assert refresh is not None
    assert expires_in > 0

    # Step 3: Replaying the consumed pending refresh token must fail
    with pytest.raises(AuthError) as exc_info:
        await auth_service.complete_mfa_login(db_session, redis_login, pending_token, pyotp.TOTP(secret).now())
    assert exc_info.value.code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_mfa_disable(db_session: AsyncSession):
    fake_redis = FakeRedis()
    user = await _seed_user(db_session, "mfa4@example.com")
    secret, _ = await mfa_service.enroll(db_session, user.id)
    totp = pyotp.TOTP(secret)
    await mfa_service.activate(db_session, fake_redis, user.id, totp.now())

    await db_session.refresh(user)
    assert user.mfa_enabled is True

    # Disable with fresh code and fresh redis
    redis_disable = FakeRedis()
    await mfa_service.disable(db_session, redis_disable, user.id, pyotp.TOTP(secret).now())

    await db_session.refresh(user)
    assert user.mfa_enabled is False
    assert user.mfa_secret is None


def test_step_up_token_semantics():
    payload = security.decode_access_token(security.create_step_up_token("u1", "member"))
    assert payload.get("step_up") is True
    assert payload["sub"] == "u1"

    access_payload = security.decode_access_token(security.create_access_token("u1", "member"))
    assert "step_up" not in access_payload
