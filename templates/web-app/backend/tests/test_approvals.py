from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog, RefreshToken, User
from app.repositories import count_active_refresh_tokens, create_user
from app.services import approval_service
from app.services.approval_service import ApprovalError


async def _seed_admin(db: AsyncSession, email: str) -> User:
    user = User(email=email, hashed_password="hashed", role="admin")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_role_change_pending_request(db_session: AsyncSession):
    maker = await _seed_admin(db_session, "maker@example.com")
    target = await create_user(db_session, "target@example.com", "hashed")

    req = await approval_service.request_role_change(
        db_session, maker_user_id=maker.id, target_user_id=target.id, new_role="admin"
    )
    assert req.status == "pending"
    assert req.maker_user_id == maker.id
    assert req.checker_user_id is None


@pytest.mark.asyncio
async def test_self_target_refused(db_session: AsyncSession):
    maker = await _seed_admin(db_session, "maker2@example.com")

    with pytest.raises(ApprovalError) as exc_info:
        await approval_service.request_role_change(
            db_session, maker_user_id=maker.id, target_user_id=maker.id, new_role="superadmin"
        )
    assert exc_info.value.code == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_duplicate_pending_conflict(db_session: AsyncSession):
    maker = await _seed_admin(db_session, "maker3@example.com")
    checker = await _seed_admin(db_session, "checker3@example.com")
    target = await create_user(db_session, "target3@example.com", "hashed")

    await approval_service.request_role_change(
        db_session, maker_user_id=maker.id, target_user_id=target.id, new_role="admin"
    )

    with pytest.raises(ApprovalError) as exc_info:
        await approval_service.request_role_change(
            db_session, maker_user_id=checker.id, target_user_id=target.id, new_role="support"
        )
    assert exc_info.value.code == "CONFLICT"


@pytest.mark.asyncio
async def test_maker_cannot_be_checker(db_session: AsyncSession):
    maker = await _seed_admin(db_session, "maker4@example.com")
    target = await create_user(db_session, "target4@example.com", "hashed")

    req = await approval_service.request_role_change(
        db_session, maker_user_id=maker.id, target_user_id=target.id, new_role="admin"
    )

    with pytest.raises(ApprovalError) as exc_info:
        await approval_service.decide_role_change(
            db_session, request_id=req.id, checker_user_id=maker.id, approve=True
        )
    assert exc_info.value.code == "FORBIDDEN"


@pytest.mark.asyncio
async def test_checker_approves_applies_role_and_revokes_sessions(db_session: AsyncSession):
    maker = await _seed_admin(db_session, "maker5@example.com")
    checker = await _seed_admin(db_session, "checker5@example.com")
    target = await create_user(db_session, "target5@example.com", "hashed")

    req = await approval_service.request_role_change(
        db_session, maker_user_id=maker.id, target_user_id=target.id, new_role="admin"
    )

    # Target has active session
    expiry = datetime.now(timezone.utc) + timedelta(days=30)
    db_session.add(RefreshToken(user_id=target.id, token_hash="token1", expires_at=expiry))
    await db_session.commit()

    assert await count_active_refresh_tokens(db_session, target.id) == 1

    # Checker approves
    approved = await approval_service.decide_role_change(
        db_session, request_id=req.id, checker_user_id=checker.id, approve=True
    )
    assert approved.status == "approved"
    assert approved.checker_user_id == checker.id

    # Verify target's role mutated and sessions revoked
    target_refreshed = await db_session.get(User, target.id)
    assert target_refreshed.role == "admin"
    assert await count_active_refresh_tokens(db_session, target.id) == 0

    # Second decision refused (immutable)
    with pytest.raises(ApprovalError) as exc_info:
        await approval_service.decide_role_change(
            db_session, request_id=req.id, checker_user_id=checker.id, approve=False
        )
    assert exc_info.value.code == "CONFLICT"
