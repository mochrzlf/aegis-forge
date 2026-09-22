"""Maker-Checker / four-eyes approval workflow (AGENTS.md §3.2.1, ADR-006).

A privileged change is recorded as a *pending* approval_requests row and only
applied when a different person approves it. The maker/checker split is enforced
three ways: service check, router check, and a CHECK constraint in the database,
so no single bug lets one person both request and execute a change.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ApprovalRequest
from app.repositories import get_user_by_id, revoke_all_refresh_tokens
from app.services.audit_service import write_audit


class ApprovalError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


# A pending request older than this is stale and must be re-requested.
APPROVAL_TTL = timedelta(hours=72)
ALLOWED_ROLES = {"member", "support", "admin", "superadmin"}


async def request_role_change(
    db: AsyncSession, *, maker_user_id: str, target_user_id: str, new_role: str, reason: str | None = None
) -> ApprovalRequest:
    """An admin (maker) proposes a role change. Nothing is applied yet.

    The maker cannot target themselves: requesting your own promotion is exactly
    the privilege-creep pattern four-eyes exists to prevent, and even though a
    second approver would still be required, the request itself is a conflict of
    interest we refuse to record as legitimate.
    """
    target = await get_user_by_id(db, target_user_id)
    if not target:
        raise ApprovalError("NOT_FOUND", "Target user not found")

    if maker_user_id == target_user_id:
        raise ApprovalError("VALIDATION_ERROR", "You cannot request a change to your own account")

    if new_role not in ALLOWED_ROLES:
        raise ApprovalError("VALIDATION_ERROR", f"Unknown role: {new_role}")

    # One pending request per target+action. Two open approvals for the same
    # promotion race each other and confuse whichever checker acts second.
    existing = await db.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.target_entity_id == target_user_id,
            ApprovalRequest.action_type == "user.role_change",
            ApprovalRequest.status == "pending",
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ApprovalError("CONFLICT", "A pending role-change request already exists for this user")

    now = datetime.now(timezone.utc)
    request = ApprovalRequest(
        action_type="user.role_change",
        target_entity_type="users",
        target_entity_id=target_user_id,
        payload={"new_role": new_role, "previous_role": target.role},
        maker_user_id=maker_user_id,
        expires_at=now + APPROVAL_TTL,
    )
    db.add(request)
    await db.flush()

    await write_audit(
        db,
        actor_user_id=maker_user_id,
        action="approval.requested",
        resource=f"approval:{request.id}",
        detail=f"Role change for user {target_user_id} to {new_role}"
        + (f" — {reason}" if reason else ""),
    )
    await db.commit()
    await db.refresh(request)
    return request


async def decide_role_change(
    db: AsyncSession, *, request_id: str, checker_user_id: str, approve: bool, rejection_reason: str | None = None
) -> ApprovalRequest:
    """A second admin (checker) approves or rejects a pending request.

    On approval the role change is applied and every live session for the target
    is revoked in the same transaction, so the user cannot keep using a token
    minted under the old, lower-privilege role (privilege-creep guard,
    security-access-matrix.md §4.B.2).
    """
    res = await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == request_id))
    request = res.scalar_one_or_none()
    if not request:
        raise ApprovalError("NOT_FOUND", "Approval request not found")

    if request.status != "pending":
        raise ApprovalError("CONFLICT", f"Request already {request.status}")

    # Four-eyes, checked before any mutation: the maker may not be the checker.
    # The DB CHECK constraint is the last line of defence if this check is bypassed.
    if request.maker_user_id == checker_user_id:
        raise ApprovalError("FORBIDDEN", "The maker of a request cannot also be its checker")

    now = datetime.now(timezone.utc)
    # SQLite returns naive datetimes; Postgres returns tz-aware ones. Normalise
    # so the comparison is well-defined on either driver.
    expires_at = request.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        request.status = "rejected"
        request.rejection_reason = "Expired with no decision"
        request.checker_user_id = checker_user_id
        request.resolved_at = now
        await write_audit(
            db,
            actor_user_id=checker_user_id,
            action="approval.expired",
            resource=f"approval:{request.id}",
            detail="Request expired before a checker decided",
        )
        await db.commit()
        raise ApprovalError("VALIDATION_ERROR", "This request has expired")

    request.checker_user_id = checker_user_id
    request.status = "approved" if approve else "rejected"
    request.rejection_reason = None if approve else (rejection_reason or "Rejected by checker")
    request.resolved_at = now

    sessions_revoked = 0
    if approve:
        target = await get_user_by_id(db, request.target_entity_id)
        if not target:
            raise ApprovalError("NOT_FOUND", "Target user no longer exists")
        new_role = request.payload["new_role"]
        previous_role = target.role
        target.role = new_role
        # Force re-login under the new role: a token issued as `member` must not
        # keep working now that the account is `admin`.
        sessions_revoked = await revoke_all_refresh_tokens(db, target.id)

    await write_audit(
        db,
        actor_user_id=checker_user_id,
        action="approval.approved" if approve else "approval.rejected",
        resource=f"approval:{request.id}",
        detail=(
            f"Role change applied: user {request.target_entity_id} "
            f"{previous_role} -> {new_role}, {sessions_revoked} session(s) revoked"
            if approve
            else request.rejection_reason
        ),
    )
    await db.commit()
    await db.refresh(request)
    return request


async def list_pending(db: AsyncSession) -> list[ApprovalRequest]:
    res = await db.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.status == "pending")
        .order_by(ApprovalRequest.created_at)
    )
    return list(res.scalars().all())
