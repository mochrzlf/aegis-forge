import pytest
from app.services.risk_guardian import RiskGuardian, RiskViolationError, SecurityRiskError


@pytest.fixture
def guardian() -> RiskGuardian:
    return RiskGuardian(
        max_risk_percent=2.0,
        max_daily_drawdown_percent=5.0,
        max_allowed_spread_points=30.0,
    )


def test_dynamic_lot_calculation_standard(guardian: RiskGuardian):
    # Example from blueprint:
    # Equity = $10,000
    # Risk per trade = 1.0% ($100)
    # Stop Loss = 500 points (50 pips on 5-digit quote)
    # Tick value = $1.0 per lot per 5 points (or $10 per pip -> 500 points = $100 for 0.20 lot with tick_value 1.0)
    # Calculation: 100 / (500 * 1.0) = 0.20 lot
    lot = guardian.calculate_lot_size(
        account_equity=10000.0,
        stop_loss_points=500.0,
        tick_value=1.0,
        risk_percent=1.0,
    )
    assert lot == 0.20


def test_hard_stop_loss_mandatory(guardian: RiskGuardian):
    # Zero or negative stop loss must be rejected
    with pytest.raises(RiskViolationError) as exc_info:
        guardian.calculate_lot_size(
            account_equity=10000.0,
            stop_loss_points=0.0,
            tick_value=1.0,
            risk_percent=1.0,
        )
    assert "HARD STOP LOSS MANDATORY" in str(exc_info.value)


def test_excessive_risk_rejected(guardian: RiskGuardian):
    # Exceeding institutional ceiling of 2% must be rejected
    with pytest.raises(RiskViolationError) as exc_info:
        guardian.calculate_lot_size(
            account_equity=10000.0,
            stop_loss_points=500.0,
            tick_value=1.0,
            risk_percent=2.5,
        )
    assert "exceeds allowed institutional ceiling" in str(exc_info.value)


def test_spread_filter(guardian: RiskGuardian):
    # Normal spread allows trading
    assert guardian.check_spread(15.0) is True
    # Spread widening beyond threshold blocks trading
    assert guardian.check_spread(35.0) is False


def test_circuit_breaker_drawdown_evaluation(guardian: RiskGuardian):
    # Healthy session (2% loss)
    healthy = guardian.evaluate_drawdown(day_start_equity=10000.0, current_equity=9800.0)
    assert healthy["status"] == "HEALTHY"
    assert healthy["circuit_breaker_active"] is False

    # Emergency Drawdown breach (6% loss, > 5% max limit)
    tripped = guardian.evaluate_drawdown(day_start_equity=10000.0, current_equity=9400.0)
    assert tripped["status"] == "TRIPPED"
    assert tripped["circuit_breaker_active"] is True
    assert tripped["action"] == "CLOSE_ALL_AND_HALT"
    assert guardian.is_tripped is True

    # Operator reset
    guardian.reset_circuit_breaker()
    assert guardian.is_tripped is False


def test_api_permission_hardening(guardian: RiskGuardian):
    # Safe permissions pass
    assert guardian.validate_api_permissions(["spot_trading", "read_info"]) is True

    # Withdrawal capabilities must be rejected with critical error
    with pytest.raises(SecurityRiskError) as exc_info:
        guardian.validate_api_permissions(["spot_trading", "enable_withdrawals"])
    assert "CRITICAL SECURITY VIOLATION" in str(exc_info.value)

    with pytest.raises(SecurityRiskError) as exc_info:
        guardian.validate_api_permissions(["transfer_funds"])
    assert "CRITICAL SECURITY VIOLATION" in str(exc_info.value)
