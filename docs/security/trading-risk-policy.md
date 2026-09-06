# Institutional Trading Risk Management Policy

This policy is a mandatory risk standard (*Mandatory Risk Policy*) governing all trading bots, Expert Advisors (EAs), and quantitative algorithms developed using this Baseline.

---

## 🛑 1. Core Principle: Capital Preservation First

The primary objective of an algorithmic trading system is not short-term profit maximization, but **preserving capital resilience against bankruptcy (*Risk of Ruin = 0%*)** across all market regimes (extreme conditions, range-bound/sideways, or liquidity crises).

---

## 📊 2. Mandatory Risk Parameter Thresholds

| Risk Parameter | Maximum Permitted Threshold | Automated System Action |
| :--- | :--- | :--- |
| **Maximum Risk per Trade** | **1.0% to 2.0%** of total Equity | Dynamic lot sizing; reject order if risk exceeds 2%. |
| **Maximum Daily Drawdown** | **5.0%** of day start balance (00:00 GMT) | **Circuit Breaker:** Close all positions, cancel pending orders, lock trading for the day. |
| **Maximum Total Drawdown** | **10.0%** of High Watermark Equity | **Hard Kill-Switch:** Total EA deactivation; mandatory manual architecture review. |
| **Maximum Open Exposure** | **3 Concurrent Positions** per currency pair | Reject new signals until an existing position is closed. |
| **Maximum Spread Tolerance** | **2.5x** normal average spread | Reject order execution (prevents spread widening during news releases). |

---

## ⚡ 3. Circuit Breaker & Emergency Kill-Switch Protocol

Every EA must implement an autonomous circuit breaker function (*Autonomous Circuit Breaker*):

```
┌────────────────────────────────────────────────────────┐
│               PER-TICK EQUITY MONITORING               │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
          Is Floating Loss >= 5% of Today's Equity?
             ├─── NO  ──> Resume Normal Operations
             │
             └─── YES (RISK THRESHOLD BREACHED)
                    │
                    ▼
          ┌──────────────────────────────────────────────┐
          │     🚨 CIRCUIT BREAKER EXECUTION ACTIVE      │
          ├──────────────────────────────────────────────┤
          │ 1. Call OrderCloseAll() for all positions    │
          │ 2. Call OrderCancelAll() for pending orders  │
          │ 3. Set GlobalVariable: TRADING_HALTED = TRUE │
          │ 4. Send emergency alert (Telegram/SMS/API)   │
          │ 5. Record alert log in PostgreSQL DB         │
          └──────────────────────────────────────────────┘
```

---

## 🔐 4. API Key Hardening & Permission Segregation

For institutional broker or crypto exchange integrations via REST/WebSocket/FIX:

1. **Principle of Least Privilege (PoLP):**
   - Permitted Permissions: **Read Account Info**, **Order Create**, **Order Cancel**.
   - ❌ **STRICTLY PROHIBITED PERMISSION: WITHDRAWAL / FUND EXTRACTION.**
2. **Mandatory IP Whitelisting:**
   - API keys must be locked (*IP whitelisted*) strictly to the static IP addresses of authorized VPS trading servers.
3. **API Key Storage:**
   - Never store API secrets in source code. Environment variables injected via a secure secrets manager are required.

---

## 📰 5. High-Impact Economic News Blackout Filter

The system must suspend opening new positions during critical time windows:
- **15 minutes before** high-impact news releases (NFP, CPI, FOMC/ECB Interest Rate Decisions).
- **15 minutes after** news releases, until spread volatility normalizes within standard ranges.
- Existing open positions must have verified, valid Stop Loss orders in place prior to the news window commencement.

---

## 📝 6. Audit Logging & Forensic Reconciliation

Every executed order must log structured audit data to the logging database:
- **Ticket ID & Client Order ID**
- **Execution Timestamp (Millisecond Precision)**
- **Requested Price vs. Actual Execution Price (Slippage Calculation)**
- **Spread Value at Execution**
- **Risk Percentage & Stop Loss / Take Profit Values**
