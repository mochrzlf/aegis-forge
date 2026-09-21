"""Pydantic DTOs — validate at the boundary (AGENTS.md §3.1)."""
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


class UserStatusIn(BaseModel):
    """Admin-only account status change (JML kill-switch, ADR-005)."""
    status: str = Field(pattern="^(active|suspended|terminated)$")
    reason: str | None = Field(default=None, max_length=256)
