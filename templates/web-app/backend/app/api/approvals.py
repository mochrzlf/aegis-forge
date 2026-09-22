"""Approvals endpoints — Maker-Checker / four-eyes (ADR-006)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, get_db, require_roles
from app.core.envelope import ErrorCode, err, ok
from app.schemas import ApprovalDecisionIn, ApprovalOut, RoleChangeIn
from app.services import approval_service
from app.services.approval_service import ApprovalError

router = APIRouter(prefix="/approvals", tags=["approvals"])


def _approval_error(exc: ApprovalError) -> HTTPException:
    status_map = {
        ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
        ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
    }
    return HTTPException(
        status_code=status_map.get(exc.code, status.HTTP_400_BAD_REQUEST),
        detail=err(exc.code, exc.message),
    )


@router.post("/role-change", status_code=status.HTTP_201_CREATED)
async def request_role_change(
    payload: RoleChangeIn,
    maker: CurrentUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Maker half: an admin proposes a role change for another user.

    Nothing is applied until a different admin approves it.
    """
    try:
        request = await approval_service.request_role_change(
            db,
            maker_user_id=maker.id,
            target_user_id=payload.target_user_id,
            new_role=payload.new_role,
            reason=payload.reason,
        )
    except ApprovalError as exc:
        raise _approval_error(exc)
    return ok(ApprovalOut.model_validate(request).model_dump())


@router.post("/{request_id}/approve")
async def approve_role_change(
    request_id: str,
    checker: CurrentUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Checker half: a second admin applies the proposed change.

    The maker of a request can never approve it themselves.
    """
    try:
        request = await approval_service.decide_role_change(
            db, request_id=request_id, checker_user_id=checker.id, approve=True
        )
    except ApprovalError as exc:
        raise _approval_error(exc)
    return ok(ApprovalOut.model_validate(request).model_dump())


@router.post("/{request_id}/reject")
async def reject_role_change(
    request_id: str,
    payload: ApprovalDecisionIn,
    checker: CurrentUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Checker half: a second admin refuses the proposed change."""
    try:
        request = await approval_service.decide_role_change(
            db,
            request_id=request_id,
            checker_user_id=checker.id,
            approve=False,
            rejection_reason=payload.rejection_reason,
        )
    except ApprovalError as exc:
        raise _approval_error(exc)
    return ok(ApprovalOut.model_validate(request).model_dump())


@router.get("", dependencies=[Depends(require_roles("admin"))])
async def list_pending_approvals(db: AsyncSession = Depends(get_db)):
    requests = await approval_service.list_pending(db)
    data = [ApprovalOut.model_validate(r).model_dump() for r in requests]
    return ok(data, meta={"page": 1, "per_page": len(data), "total": len(data)})
