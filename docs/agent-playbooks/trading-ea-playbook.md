# EA / Algorithmic Trading Playbook

> Follow the phases in order. Each phase is a **gate**. **Capital preservation overrides everything** — see `docs/security/trading-risk-policy.md` and blueprint `docs/blueprints/ea-trading-blueprint.md` (incl. §6 Tool Selection Matrix).

---

## PHASE 0 — Context Load
1. Read `AGENTS.md` in full (rigid risk management pillar).
2. Read `docs/blueprints/ea-trading-blueprint.md` — especially §2 (risk formulas) and §6 (tool selection).
3. Read `docs/security/trading-risk-policy.md` and `docs/diagrams/ea-trading-execution-flow.md`.

**✅ Verify:** You can recite the dynamic lot formula, the 5% daily-drawdown kill-switch behavior, and which toolchain applies to the target instrument (§6.1).

---

## PHASE 1 — Specify (Strategy Sheet)
1. Define the **Strategy Specification**: instrument(s), timeframe, entry/exit rules, session/news filters, and the risk parameters (risk % per trade, max daily DD, max simultaneous exposure).
2. Select the toolchain per blueprint §6.1 (MQL5+MetaAPI for Forex/CFD; freqtrade/ccxt stack for crypto).

**✅ Verify:** Every rule is unambiguous and machine-translatable; risk % ∈ [1%, 2%]; kill-switch threshold = 5% daily DD.

---

## PHASE 2 — Threat Model
1. New ADR in `docs/adr/` covering: API-key compromise (withdrawal permission), runaway/martingale logic, execution without SL, data-feed failure, VPS/runtime hang.

**✅ Verify:** Threats map to controls — withdrawal permission disabled, mandatory Hard SL, watchdog heartbeat, circuit breaker.

---

## PHASE 3 — Risk Gate (Pre-Trade Controls)
1. Implement the **Pre-Trade Risk Management Gate** (blueprint §1): daily-DD validator, margin check, dynamic lot calculator, spread/slippage filter, max-exposure check.
2. Implement the autonomous circuit breaker (blueprint §2.2) exactly.

**✅ Verify:** No order can dispatch without (a) a computed Hard SL and (b) passing all risk filters. Kill-switch closes all, cancels pendings, disables trading, alerts.

---

## PHASE 4 — Implement (Strategy + Execution)
1. Implement signal logic in the selected stack (MQL5 `OnTick`, or Python ccxt/MetaAPI).
2. Implement the Order Execution Engine state machine: `PENDING -> EXECUTED -> SL/TP_HIT -> CLOSED`.
3. Wire the audit log to PostgreSQL (order ticket, timestamp, realized slippage).

**✅ Verify:** Static lot sizing and unbounded martingale are absent; every order logs ticket + slippage; exchange API keys have NO withdrawal permission.

---

## PHASE 5 — Validate (Anti-Overfitting SOP)
Run the 5-gate validation from blueprint §3 — **no live capital before all pass**:
1. In-Sample backtest (70%) — PF > 1.5, MaxDD < 15%, Sharpe > 1.2.
2. Out-of-Sample (30%) — degradation < 25%.
3. Walk-Forward analysis — consistent across regimes.
4. Paper/Demo — ≥ 30 days live data.
5. Incubation — micro/cent live capital (1–5%).

**✅ Verify:** All 5 gates documented with metrics; degradation within tolerance; no gate skipped.

---

## PHASE 6 — Operate & Verify
1. Deploy on low-latency VPS near broker server (< 5 ms ping).
2. Enable watchdog heartbeat (60 s) with auto-restart + emergency alert.
3. Complete the Pre-Live checklist (blueprint §5).

**✅ Verify:** Watchdog restarts a frozen terminal and alerts; pre-live checklist fully checked; `make audit` clean (no API keys/secrets in Git).
