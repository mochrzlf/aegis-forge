import os
from pydantic import BaseModel


class Settings(BaseModel):
    APP_NAME: str = "Aegis Forge Trading Bridge"
    MAX_RISK_PER_TRADE_PERCENT: float = float(os.getenv("MAX_RISK_PER_TRADE_PERCENT", "2.0"))
    MAX_DAILY_DRAWDOWN_PERCENT: float = float(os.getenv("MAX_DAILY_DRAWDOWN_PERCENT", "5.0"))
    MAX_ALLOWED_SPREAD_POINTS: float = float(os.getenv("MAX_ALLOWED_SPREAD_POINTS", "30.0"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))


settings = Settings()
