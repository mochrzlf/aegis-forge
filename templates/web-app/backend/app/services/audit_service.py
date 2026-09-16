"""Append-only audit writer (AGENTS.md §3.2.3)."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


async def write_audit(
    db: AsyncSession,
    *,
    actor_user_id: str | None,
    action: str,
    resource: str | None = None,
    detail: str | None = None,
) -> None:
    db.add(AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource=resource,
        detail=detail,
    ))
    await db.commit()
