from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.services.risk_guardian import RiskGuardian, RiskViolationError, SecurityRiskError

router = APIRouter(prefix="/risk", tags=["Risk Management"])
guardian = RiskGuardian(
    max_risk_percent=settings.MAX_RISK_PER_TRADE_PERCENT,
    max_daily_drawdown_percent=settings.MAX_DAILY_DRAWDOWN_PERCENT,
    max_allowed_spread_points=settings.MAX_ALLOWED_SPREAD_POINTS,
)


class OrderValidationRequest(BaseModel):
    account_equity: float = Field(gt=0, description="Current account equity in account currency")
    stop_loss_points: float = Field(gt=0, description="Stop loss distance in points/pips")
    tick_value: float = Field(default=1.0, gt=0, description="Tick value per lot")
    risk_percent: float = Field(default=1.0, gt=0, le=2.0, description="Risk % of equity (max 2%)")
    current_spread_points: float = Field(default=15.0, ge=0, description="Current live spread in points")


class OrderValidationResponse(BaseModel):
    allowed: bool
    calculated_lot_size: float | None = None
    reason: str | None = None


class DrawdownCheckRequest(BaseModel):
    day_start_equity: float = Field(gt=0, description="Account equity at session open")
    current_equity: float = Field(gt=0, description="Current real-time account equity")


class ApiPermissionCheckRequest(BaseModel):
    permissions: list[str] = Field(description="List of permissions granted to API key")


@router.post("/validate-order", response_model=OrderValidationResponse)
def validate_order(req: OrderValidationRequest):
    if guardian.is_tripped:
        return OrderValidationResponse(
            allowed=False,
            reason="Circuit breaker active! All trading halted."
        )

    if not guardian.check_spread(req.current_spread_points):
        return OrderValidationResponse(
            allowed=False,
            reason=f"Spread {req.current_spread_points} exceeds ceiling {guardian.max_allowed_spread_points} points."
        )

    try:
        lot = guardian.calculate_lot_size(
            account_equity=req.account_equity,
            stop_loss_points=req.stop_loss_points,
            tick_value=req.tick_value,
            risk_percent=req.risk_percent,
        )
        return OrderValidationResponse(allowed=True, calculated_lot_size=lot)
    except RiskViolationError as e:
        return OrderValidationResponse(allowed=False, reason=str(e))


@router.post("/circuit-breaker/check")
def check_circuit_breaker(req: DrawdownCheckRequest):
    return guardian.evaluate_drawdown(req.day_start_equity, req.current_equity)


@router.post("/circuit-breaker/reset")
def reset_circuit_breaker():
    guardian.reset_circuit_breaker()
    return {"status": "SUCCESS", "message": "Circuit breaker reset by operator."}


@router.post("/verify-api-permissions")
def verify_api_permissions(req: ApiPermissionCheckRequest):
    try:
        guardian.validate_api_permissions(req.permissions)
        return {"status": "OK", "message": "API key permissions verified (No withdrawal permissions detected)."}
    except SecurityRiskError as e:
        raise HTTPException(status_code=400, detail=str(e))
