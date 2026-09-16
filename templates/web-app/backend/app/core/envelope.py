"""Standard API envelope — every response uses this shape (AGENTS.md §3.1)."""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Meta(BaseModel):
    page: Optional[int] = None
    per_page: Optional[int] = None
    total: Optional[int] = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}


class SuccessEnvelope(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: Optional[Meta] = None


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorBody


def ok(data: Any, meta: Optional[Meta] = None) -> dict:
    return {"success": True, "data": data, "meta": meta}


def err(code: str, message: str, details: Optional[dict] = None) -> dict:
    return {"success": False, "error": {"code": code, "message": message, "details": details or {}}}


# Fixed error-code set (do not invent new codes — extend the PRD instead).
class ErrorCode:
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
