"""Runnable self-check for Maker-Checker approvals (ADR-006) — no pytest.

Uses an in-memory SQLite session to run the real service logic and the real
UPDATE predicates, not a mock. The schema is created from ORM metadata, so it
needs no Alembic migration here.

Covers the invariants an auditor asks about:
  - the maker cannot be the checker of their own request
  - the maker cannot target their own account at all
  - only one pending request exists per target+action
  - approval actually applies the role AND revokes live sessions
  - a second decision on the same request is refused, not silently re-applied

Run from the backend directory:
    python3 tests/check_approvals.py
"""
import asyncio
import os
import sys

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://aegis:a@db:5432/aegis_app")
os.environ.setdefault("JWT_SECRET", "x" * 48)
os.environ.setdefault("POSTGRES_PASSWORD", "change_me_strong_password")

sys.path.insert(0, ".")

from datetime import datetime, timedelta, timezone  # noqa: E402

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.models import AuditLog, Base, RefreshToken, User  # noqa: E402
from app.repositories import count_active_refresh_tokens, create_user  # noqa: E402
from app.services import approval_service  # noqa: E402
from app.services.approval_service import ApprovalError  # noqa: E402


async def _seed_admin(db: AsyncSession, email: str) -> User:
    user = User(email=email, hashed_password="hashed", role="admin")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def main():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        maker = await _seed_admin(db, "maker@example.com")
        checker = await _seed_admin(db, "checker@example.com")
        target = await create_user(db, "target@example.com", "hashed")

        # 1. A request for someone else's account is accepted and stays pending.
        req = await approval_service.request_role_change(
            db, maker_user_id=maker.id, target_user_id=target.id, new_role="admin"
        )
        assert req.status == "pending"
        assert req.maker_user_id == maker.id and req.checker_user_id is None
        print("  role-change request created as pending — OK")


        # 2. Self-targeting is refused: nobody may request their own promotion.
        try:
            await approval_service.request_role_change(
                db, maker_user_id=maker.id, target_user_id=maker.id, new_role="superadmin"
            )
            raise AssertionError("self-target request should have been refused")
        except ApprovalError as exc:
            assert exc.code == "VALIDATION_ERROR"
        print("  self-target request refused — OK")

        # 3. A second pending request for the same target+action is refused.
        try:
            await approval_service.request_role_change(
                db, maker_user_id=checker.id, target_user_id=target.id, new_role="support"
            )
            raise AssertionError("duplicate pending request should have been refused")
        except ApprovalError as exc:
            assert exc.code == "CONFLICT"
        print("  duplicate pending request refused — OK")

        # 4. Four-eyes: the maker cannot approve their own request.
        try:
            await approval_service.decide_role_change(
                db, request_id=req.id, checker_user_id=maker.id, approve=True
            )
            raise AssertionError("maker approving own request should be forbidden")
        except ApprovalError as exc:
            assert exc.code == "FORBIDDEN"
        print("  maker-as-checker refused — OK")

        # 5. Approval by a different admin applies the role and revokes the
        # target's live sessions — an old token must not survive the promotion.
        expiry = datetime.now(timezone.utc) + timedelta(days=30)
        db.add(RefreshToken(user_id=target.id, token_hash="t1", expires_at=expiry))
        db.add(RefreshToken(user_id=target.id, token_hash="t2", expires_at=expiry))
        await db.commit()
        assert await count_active_refresh_tokens(db, target.id) == 2

        decided = await approval_service.decide_role_change(
            db, request_id=req.id, checker_user_id=checker.id, approve=True
        )
        assert decided.status == "approved"
        assert decided.checker_user_id == checker.id

        res = await db.execute(select(User).where(User.id == target.id))
        assert res.scalar_one().role == "admin", "role change was not applied"
        assert await count_active_refresh_tokens(db, target.id) == 0, "sessions survived promotion"
        print("  approval applied role + revoked 2 sessions — OK")

        # 6. Deciding an already-resolved request is refused, never re-applied.
        try:
            await approval_service.decide_role_change(
                db, request_id=req.id, checker_user_id=checker.id, approve=True
            )
            raise AssertionError("second decision should have been refused")
        except ApprovalError as exc:
            assert exc.code == "CONFLICT"
        print("  re-decision refused — OK")

        # 7. An expired pending request is auto-closed, not silently honoured.
        stale_target = await create_user(db, "stale@example.com", "hashed")
        stale = await approval_service.request_role_change(
            db, maker_user_id=maker.id, target_user_id=stale_target.id, new_role="admin"
        )
        stale.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        await db.commit()
        try:
            await approval_service.decide_role_change(
                db, request_id=stale.id, checker_user_id=checker.id, approve=True
            )
            raise AssertionError("expired request should not be applied")
        except ApprovalError as exc:
            assert exc.code == "VALIDATION_ERROR"
        await db.refresh(stale)
        assert stale.status == "rejected", "expired request was not auto-closed"
        print("  expired request auto-closed, not applied — OK")

        # 8. Rejection records the reason and touches nothing else.
        rej_target = await create_user(db, "rej@example.com", "hashed")
        rej = await approval_service.request_role_change(
            db, maker_user_id=maker.id, target_user_id=rej_target.id, new_role="support"
        )
        decided = await approval_service.decide_role_change(
            db, request_id=rej.id, checker_user_id=checker.id, approve=False,
            rejection_reason="Not justified",
        )
        assert decided.status == "rejected" and decided.rejection_reason == "Not justified"
        res = await db.execute(select(User).where(User.id == rej_target.id))
        assert res.scalar_one().role == "member", "rejection must not change the role"
        print("  rejection recorded without applying change — OK")

        # 9. Every transition left an audit row — the maker-checker chain is
        # traceable end to end.
        res = await db.execute(select(AuditLog).where(AuditLog.action.like("approval%")))
        actions = sorted(row.action for row in res.scalars().all())
        assert "approval.requested" in actions
        assert "approval.approved" in actions
        assert "approval.rejected" in actions
        assert "approval.expired" in actions
        print(f"  audit chain complete ({len(actions)} rows) — OK")

    await engine.dispose()
    print("approvals self-check: PASS")


if __name__ == "__main__":
    asyncio.run(main())
