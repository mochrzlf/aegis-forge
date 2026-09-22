"""Pydantic DTOs — validate at the boundary (AGENTS.md §3.1)."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str
    status: str

    class Config:
        from_attributes = True


class PasswordResetRequestIn(BaseModel):
    """Ask for a reset link (ADR-007). The endpoint always answers 200 — the
    presence or absence of an account is not information an unauthenticated
    caller may have.
    """
    email: EmailStr


class PasswordResetConfirmIn(BaseModel):
    """Redeem a reset link. The new password is held to the same strength floor
    as registration so a reset cannot be used to weaken an account.
    """
    token: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


class EmailVerificationConfirmIn(BaseModel):
    """Redeem an email-verification link (ADR-007)."""
    token: str = Field(min_length=1, max_length=128)


class UserStatusIn(BaseModel):
    """Admin-only account status change (JML kill-switch, ADR-005)."""
    status: str = Field(pattern="^(active|suspended|terminated)$")
    reason: str | None = Field(default=None, max_length=256)


class RoleChangeIn(BaseModel):
    """Maker-Checker role promotion request (ADR-006). The maker submits the
    proposed change; a different admin must approve it before it takes effect.
    """
    target_user_id: str
    new_role: str = Field(pattern="^(member|support|admin|superadmin)$")
    reason: str | None = Field(default=None, max_length=256)


class ApprovalDecisionIn(BaseModel):
    """Checker approves or rejects a pending request (ADR-006)."""
    rejection_reason: str | None = Field(default=None, max_length=256)


class ApprovalOut(BaseModel):
    id: str
    action_type: str
    target_entity_type: str
    target_entity_id: str
    payload: dict
    maker_user_id: str
    checker_user_id: str | None = None
    status: str
    rejection_reason: str | None = None
    expires_at: datetime
    created_at: datetime
    resolved_at: datetime | None = None

    class Config:
        from_attributes = True
