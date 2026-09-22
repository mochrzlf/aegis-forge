"""Data access with ownership predicates (anti-IDOR)."""
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshToken, User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, hashed_password: str, role: str = "member") -> User:
    user = User(email=email, hashed_password=hashed_password, role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_owned_user(db: AsyncSession, user_id: str, current_user_id: str) -> User | None:
    """Ownership predicate: a non-admin may only touch their own row.
    `WHERE id = :id AND id = :currentUserId` — anti-IDOR (AGENTS.md §3.2.2)."""
    res = await db.execute(
        select(User).where(User.id == user_id, User.id == current_user_id)
    )
    return res.scalar_one_or_none()


async def count_active_refresh_tokens(db: AsyncSession, user_id: str) -> int:
    res = await db.execute(
        select(RefreshToken.id)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
    )
    return len(res.scalars().all())


async def revoke_all_refresh_tokens(db: AsyncSession, user_id: str) -> int:
    """Kill-switch primitive: revoke every live session for a user (AGENTS.md §3.2.1).

    Returns the number of sessions revoked, for audit context. The WHERE clause
    is scoped to `user_id` so one user's suspension can never touch another's
    tokens — the ownership rule applied at the data layer, not just the API.
    """
    now = datetime.now(timezone.utc)
    res = await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    return res.rowcount

