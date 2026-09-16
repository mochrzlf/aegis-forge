"""Data access with ownership predicates (anti-IDOR)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


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
