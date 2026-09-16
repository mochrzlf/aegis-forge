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

    LOG_LEVEL: str = "info"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
