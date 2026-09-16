"""Users endpoints — demonstrates RBAC + anti-IDOR ownership predicate."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, get_current_user, get_db, require_roles
from app.core.envelope import ErrorCode, err, ok
from app.repositories import get_owned_user, get_user_by_id
from app.schemas import UserOut

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
    from sqlalchemy import select
    from app.models import User
    res = await db.execute(select(User))
    users = [UserOut.model_validate(u).model_dump() for u in res.scalars().all()]
    return ok(users, meta={"page": 1, "per_page": len(users), "total": len(users)})
