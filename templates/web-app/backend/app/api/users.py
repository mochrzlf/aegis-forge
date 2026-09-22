"""Users endpoints — demonstrates RBAC + anti-IDOR ownership predicate."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import REFRESH_COOKIE
from app.core.deps import (
    CurrentUser,
    get_current_user,
    get_db,
    get_redis,
    require_roles,
    require_step_up,
)
from app.core.envelope import ErrorCode, err, ok
from app.core.lockout import unlock as clear_lockout
from app.models import User
from app.repositories import get_owned_user, get_user_by_id, revoke_all_refresh_tokens
from app.schemas import UserOut, UserStatusIn
from app.services.audit_service import write_audit

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_me(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_id(db, user.id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=err(ErrorCode.NOT_FOUND, "User not found"))
    return ok(UserOut.model_validate(db_user).model_dump())


@router.get("/{user_id}")
async def read_user(
    user_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Anti-IDOR: non-admin may only read their OWN record; ownership enforced
    # in the query predicate, not just a path check (AGENTS.md §3.2.2).
    if user.role == "admin":
        db_user = await get_user_by_id(db, user_id)
    else:
        db_user = await get_owned_user(db, user_id, current_user_id=user.id)
    if not db_user:
        # 404 (not 403) to avoid leaking existence (IDOR probe -> 403/404).
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=err(ErrorCode.NOT_FOUND, "User not found"))
    return ok(UserOut.model_validate(db_user).model_dump())


@router.get("", dependencies=[Depends(require_roles("admin"))])
async def list_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User))
    users = [UserOut.model_validate(u).model_dump() for u in res.scalars().all()]
    return ok(users, meta={"page": 1, "per_page": len(users), "total": len(users)})


@router.post("/{user_id}/unlock")
async def unlock_account(
    user_id: str,
    actor: CurrentUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Admin-only: lift a temporary login lock (ADR-004).

    Deliberately a state-changing, audit-logged action — not a silent one —
    because unlocking an account under attack removes a protective control.
    """
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=err(ErrorCode.NOT_FOUND, "User not found"))
    await clear_lockout(redis, db_user.email)
    await write_audit(
        db,
        actor_user_id=actor.id,
        action="user.unlock",
        resource=f"user:{db_user.id}",
        detail="Admin lifted login lockout",
    )
    return ok({"user_id": db_user.id, "lockout_cleared": True})


@router.put("/{user_id}/status")
async def set_user_status(
    user_id: str,
    payload: UserStatusIn,
    actor: CurrentUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """JML kill-switch: change account status (ADR-005).

    Suspending or terminating a user immediately revokes every live session, so
    a dismissed or compromised account cannot keep using an issued token.
    """
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=err(ErrorCode.NOT_FOUND, "User not found"))

    previous = db_user.status
    if previous == payload.status:
        return ok({"user_id": db_user.id, "status": payload.status, "sessions_revoked": 0})

    # Self-protection: an admin removing their own access would lock out every
    # other admin's ability to manage the account. Guard, and say so plainly.
    if payload.status in {"suspended", "terminated"} and actor.id == db_user.id:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err(ErrorCode.VALIDATION_ERROR, "Admins may not suspend or terminate their own account"),
        )

    db_user.status = payload.status

    sessions_revoked = 0
    if payload.status in {"suspended", "terminated"}:
        sessions_revoked = await revoke_all_refresh_tokens(db, db_user.id)
        await clear_lockout(redis, db_user.email)

    await write_audit(
        db,
        actor_user_id=actor.id,
        action=f"user.status.{previous}_to_{payload.status}",
        resource=f"user:{db_user.id}",
        detail=payload.reason or f"Status changed from {previous} to {payload.status}",
    )
    return ok({
        "user_id": db_user.id,
        "previous_status": previous,
        "status": payload.status,
        "sessions_revoked": sessions_revoked,
    })


@router.delete("/me")
async def delete_own_account(
    response: Response,
    user: CurrentUser = Depends(require_step_up()),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Self-service account closure — requires a fresh TOTP step-up (ADR-008).

    The first step-up consumer in the skeleton: security-iam-policy.md §41
    demands re-authentication for account deletion, and JML revocation applies
    just as much to a self-terminated account as to an admin-terminated one.
    """
    db_user = await get_user_by_id(db, user.id)
    if not db_user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=err(ErrorCode.NOT_FOUND, "User not found")
        )
    if db_user.status == "terminated":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=err(ErrorCode.CONFLICT, "Account is already terminated"),
        )

    previous = db_user.status
    db_user.status = "terminated"
    sessions_revoked = await revoke_all_refresh_tokens(db, db_user.id)
    await clear_lockout(redis, db_user.email)

    await write_audit(
        db,
        actor_user_id=db_user.id,
        action="user.self_deleted",
        resource=f"user:{db_user.id}",
        detail=f"Self-terminated from status {previous}; {sessions_revoked} session(s) revoked",
    )
    response.delete_cookie(REFRESH_COOKIE, path=settings.COOKIE_PATH)
    return ok(
        {
            "user_id": db_user.id,
            "status": "terminated",
            "sessions_revoked": sessions_revoked,
        }
    )
