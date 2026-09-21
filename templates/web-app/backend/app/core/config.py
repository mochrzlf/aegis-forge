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

    LOG_LEVEL: str = "info"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
