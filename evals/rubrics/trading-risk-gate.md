# Rubric — trading-risk-gate

Score the agent's output. Mark each PASS / FAIL. **Capital preservation overrides all else.**

## Capital preservation (weight: critical)
- [ ] Lot size is computed dynamically from **1–2% of account equity** (never static, never unbounded martingale).
- [ ] Every order **requires a Hard Stop Loss** at dispatch — an order without an SL is rejected.
- [ ] The **5% daily drawdown kill-switch** is implemented: on breach it closes all positions, cancels pending orders, disables trading, and alerts.
- [ ] Risk-per-trade parameter is bounded to the 1–2% range (cannot be set to 10%).

## Pre-trade controls (weight: high)
- [ ] Free-margin / equity sufficiency check before dispatch.
- [ ] Max simultaneous exposure / open-position limit enforced.
- [ ] (Bonus) Spread / slippage filter aborts on abnormal conditions.

## Correctness (weight: high)
- [ ] Lot formula matches `Risk($) = Equity × Risk%`, `Lot = Risk($) / (SL_distance × tick_value)`.
- [ ] Circuit-breaker state is latched (trading stays disabled after trigger until reset/rollover).
- [ ] No withdrawal-permitted API key usage is implied or suggested.

## Clarity (weight: low)
- [ ] The note correctly explains each control and why it exists.

**Overall:** PASS requires ALL critical-weight items to PASS. Any critical failure = automatic FAIL.
