"""Application settings — everything from env, nothing hardcoded."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "aegis-web-app"
    APP_ENV: str = "development"
    API_PREFIX: str = "/api/v1"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "strict"
    COOKIE_PATH: str = "/api/v1/auth"

    POSTGRES_USER: str = "aegis"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "aegis_app"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str

    REDIS_HOST: str = "cache"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://cache:6379/0"

    # Rate limiting on /auth/* (ADR-003). Limits are per identifier per window.
    # Two bounds each: a tight per-user limit and a looser shared per-IP limit
    # that stops one attacker spreading guesses across many accounts.
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_LOGIN_USER: int = 10
    RATE_LIMIT_LOGIN_IP: int = 30
    RATE_LIMIT_REGISTER_IP: int = 5
    RATE_LIMIT_REFRESH_IP: int = 60

    # Account lockout after repeated login failures (ADR-004). Both knobs share
    # one horizon: failures age out after the same span a lock lasts.
    LOCKOUT_MAX_FAILURES: int = 5
    LOCKOUT_SECONDS: int = 900

    # Password reset + email verification tokens (ADR-007). Opaque random
    # secrets, stored SHA-256-hashed, single-use — same pattern as refresh
    # tokens (ADR-002), shorter lives because they travel by email.
    PASSWORD_RESET_TOKEN_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_HOURS: int = 24
    APP_BASE_URL: str = "http://localhost:8000"

    # Outbound mail via the local Mailpit relay (ADR-007). An empty SMTP_HOST
    # disables delivery without breaking the endpoints — links are simply never
    # sent, and never echoed into an API response either.
    SMTP_HOST: str = ""
    SMTP_PORT: int = 1025
    SMTP_FROM: str = "no-reply@aegis-web-app.local"

    # Rate limiting on the token endpoints (ADR-003). The *request* endpoints are
    # unauthenticated, so they carry the tightest bounds and a per-address limit
    # on top, to keep one mailbox from being flooded with reset links.
    RATE_LIMIT_PASSWORD_RESET_REQUEST_IP: int = 5
    RATE_LIMIT_PASSWORD_RESET_EMAIL: int = 3
    RATE_LIMIT_PASSWORD_RESET_CONFIRM_IP: int = 10
    RATE_LIMIT_EMAIL_VERIFICATION_REQUEST_IP: int = 5
    RATE_LIMIT_EMAIL_VERIFICATION_CONFIRM_IP: int = 10

    LOG_LEVEL: str = "info"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
