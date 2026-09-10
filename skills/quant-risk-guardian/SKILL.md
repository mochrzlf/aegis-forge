---
name: quant-risk-guardian
description: Enforces the aegis-forge Capital Preservation Doctrine for any trading or EA (Expert Advisor) code. Use whenever writing, reviewing, or modifying MQL5/MQL4, Python (ccxt/backtrader/vectorbt), or FIX-protocol trading logic — order dispatch, position sizing, drawdown handling, or broker/exchange API integration.
---

# Quant Risk Guardian

Mandatory risk standard for all trading bots, EAs, and quantitative algorithms.
Source of truth: `docs/security/trading-risk-policy.md` (this skill summarizes it; the policy document governs on conflict).

## Core Principle

**Capital preservation first.** The objective is Risk of Ruin = 0% across all
market regimes — not short-term profit maximization. Any output that violates
the thresholds below is defective by definition, no matter how profitable it looks.

## Non-Negotiable Rules (enforce on every artifact)

1. **Hard Stop Loss required.** Reject/refuse any order dispatch that lacks a
   calculated SL. No "mental stop", no SL-less grid/martingale recovery logic.
2. **Risk per trade: 1.0%–2.0% of total equity.** Position size MUST be derived
   from a dynamic lot formula: `lot = (equity × risk%) / (SL_distance × tick_value)`.
   Fixed-lot sizing is a violation.
3. **Daily drawdown circuit breaker at 5.0%** of the day-start balance
   (00:00 GMT). On breach: close ALL positions, cancel ALL pending orders,
   set `TRADING_HALTED = TRUE`, send an emergency alert, and log to the audit DB.
4. **Total drawdown kill-switch at 10.0%** of high-watermark equity:
   full EA deactivation + mandatory manual architecture review before re-enable.
5. **Exposure cap: max 3 concurrent positions per currency pair** — reject new
   signals beyond that.
6. **Spread guard: reject execution if spread > 2.5× its normal average**
   (news-widening protection).
7. **News blackout: no new positions 15 min before/after high-impact releases**
   (NFP, CPI, FOMC/ECB rate decisions). Pre-existing positions must have a
   verified SL before the window opens.

## API Key Hardening (broker/exchange integrations)

- Allowed permissions ONLY: read account info, order create, order cancel.
- ❌ **WITHDRAWAL / fund-extraction permission is strictly prohibited.**
- API keys MUST be IP-whitelisted to the authorized VPS static IPs.
- Secrets never in source code — environment variables / secrets manager only.

## When Reviewing Existing Code — Flag These Violations

- `OrderSend` / `createOrder` calls without an SL parameter
- Constant `Lots = 0.1` style fixed sizing
- Drawdown checks only at bar close instead of per-tick equity monitoring
- Circuit breaker that logs but does not actually halt new orders
- Exchange keys with withdrawal scope, or keys embedded in source

## Audit Trail

Every executed order must log structured data (ticket ID, client order ID,
symbol, direction, lots, SL/TP, equity at entry, risk% used) to the tamper-proof
audit store — never to plain console with PII or balances in cleartext beyond
what the schema allows.
