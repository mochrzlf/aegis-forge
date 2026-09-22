"""Security primitives: password hashing, JWT, refresh-token rotation helpers.

Refresh tokens are random opaque strings stored HASHED (SHA-256) server-side;
only the access token is a JWT. The refresh token travels ONLY in an
HttpOnly cookie — never in a JSON body (AGENTS.md §4.1).
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    # Raises jwt.PyJWTError on invalid/expired — caller maps to 401.
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


def new_opaque_token() -> str:
    """Unguessable bearer secret — refresh tokens, reset links, verification links."""
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """Store the hash, never the raw token (ADR-002 / ADR-007)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def email_fingerprint(email: str) -> str:
    """Short SHA-256 of an address for audit references — PII, never logged raw."""
    return hashlib.sha256(email.lower().encode("utf-8")).hexdigest()[:16]


def new_refresh_token() -> str:
    return new_opaque_token()


def hash_refresh_token(token: str) -> str:
    return hash_token(token)


def refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def password_reset_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_MINUTES)


def email_verification_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_HOURS)


# HttpOnly refresh-token cookie name (AGENTS.md §4.1); shared by auth + users.
REFRESH_COOKIE = "refresh_token"


def create_step_up_token(subject: str, role: str) -> str:
    """Short-lived JWT: holder cleared a fresh TOTP challenge (ADR-008)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "step_up": True,
        "iat": now,
        "exp": now + timedelta(minutes=settings.MFA_STEP_UP_TOKEN_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
