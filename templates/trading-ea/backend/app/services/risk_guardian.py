"""Aegis Forge — Trading EA Risk Guardian Service.

Adheres strictly to the Capital Preservation Doctrine:
- Max 1-2% risk per trade (Dynamic Lot Sizing)
- Hard Stop Loss mandatory (No trade without SL, Anti-Martingale)
- Emergency Circuit Breaker (Max daily drawdown kill-switch)
- Spread & Slippage Protection
- API Key Hardening: Refuses startup if withdrawal permissions are detected
"""
import math
from typing import Any


class RiskViolationError(Exception):
    """Raised when an order or parameter violates risk management boundaries."""
    pass


class SecurityRiskError(Exception):
    """Raised when security boundaries (like withdrawal permissions) are violated."""
    pass


class RiskGuardian:
    def __init__(
        self,
        max_risk_percent: float = 2.0,
        max_daily_drawdown_percent: float = 5.0,
        max_allowed_spread_points: float = 30.0,
    ):
        self.max_risk_percent = max_risk_percent
        self.max_daily_drawdown_percent = max_daily_drawdown_percent
        self.max_allowed_spread_points = max_allowed_spread_points
        self._circuit_breaker_tripped = False
        self._trip_reason: str | None = None

    def validate_api_permissions(self, permissions: list[str]) -> bool:
        """Enforce strict API permission segregation.

        Rejects keys with withdrawal capabilities to prevent capital drain on compromise.
        """
        forbidden_keywords = {"withdraw", "withdrawal", "enable_withdrawals", "transfer_funds"}
        for perm in permissions:
            normalized = perm.strip().lower().replace(" ", "_")
            if normalized in forbidden_keywords or any(k in normalized for k in forbidden_keywords):
                raise SecurityRiskError(
                    f"CRITICAL SECURITY VIOLATION: Permission '{perm}' detected! "
                    "Trading API keys MUST NOT have withdrawal capabilities."
                )
        return True

    def calculate_lot_size(
        self,
        account_equity: float,
        stop_loss_points: float,
        tick_value: float = 1.0,
        risk_percent: float = 1.0,
        min_lot: float = 0.01,
        max_lot: float = 50.0,
        lot_step: float = 0.01,
    ) -> float:
        """Calculate dynamic lot size based on account equity and stop loss distance.

        Formula:
            Risk Amount ($) = Equity * (Risk % / 100)
            Lot Size = Risk Amount / (SL Points * Tick Value)
        """
        if account_equity <= 0:
            raise RiskViolationError("Account equity must be positive.")

        if stop_loss_points <= 0:
            raise RiskViolationError(
                "HARD STOP LOSS MANDATORY: Stop loss distance must be greater than zero. "
                "Unhedged or zero-SL trading is strictly prohibited."
            )

        if risk_percent <= 0 or risk_percent > self.max_risk_percent:
            raise RiskViolationError(
                f"Risk percentage {risk_percent}% exceeds allowed institutional ceiling "
                f"of {self.max_risk_percent}% per trade."
            )

        risk_amount = account_equity * (risk_percent / 100.0)
        risk_per_lot = stop_loss_points * tick_value
        if risk_per_lot <= 0:
            raise RiskViolationError("Risk per lot calculation yielded non-positive value.")

        raw_lot = risk_amount / risk_per_lot

        # Quantize to lot step
        steps = math.floor(raw_lot / lot_step)
        calculated_lot = round(steps * lot_step, 4)

        if calculated_lot < min_lot:
            raise RiskViolationError(
                f"Calculated lot size {calculated_lot} is below broker minimum {min_lot}."
            )

        return min(calculated_lot, max_lot)

    def check_spread(self, current_spread_points: float) -> bool:
        """Verify spread is within allowable threshold before order dispatch."""
        if current_spread_points > self.max_allowed_spread_points:
            return False
        return True

    def evaluate_drawdown(
        self, day_start_equity: float, current_equity: float
    ) -> dict[str, Any]:
        """Evaluate real-time daily drawdown against the emergency circuit breaker threshold."""
        if day_start_equity <= 0:
            return {"status": "ERROR", "message": "Invalid day_start_equity"}

        drawdown_pct = ((day_start_equity - current_equity) / day_start_equity) * 100.0

        if drawdown_pct >= self.max_daily_drawdown_percent or self._circuit_breaker_tripped:
            self._circuit_breaker_tripped = True
            self._trip_reason = (
                f"Daily drawdown {drawdown_pct:.2f}% reached threshold "
                f"{self.max_daily_drawdown_percent:.2f}%"
            )
            return {
                "status": "TRIPPED",
                "circuit_breaker_active": True,
                "current_drawdown_percent": round(drawdown_pct, 2),
                "action": "CLOSE_ALL_AND_HALT",
                "message": self._trip_reason,
            }

        return {
            "status": "HEALTHY",
            "circuit_breaker_active": False,
            "current_drawdown_percent": max(0.0, round(drawdown_pct, 2)),
            "action": "ALLOW_TRADING",
        }

    def reset_circuit_breaker(self) -> None:
        """Manual operator reset after rollover / risk assessment."""
        self._circuit_breaker_tripped = False
        self._trip_reason = None

    @property
    def is_tripped(self) -> bool:
        return self._circuit_breaker_tripped
