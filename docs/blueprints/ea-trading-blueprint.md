# Algorithmic & EA Trading System Architecture Blueprint

This document is the technical blueprint for designing, building, testing, and operating **Expert Advisors (EAs) & Algorithmic Trading Systems** (MQL5/MQL4, Python ccxt, MetaAPI, or FIX Protocol) adhering to institutional risk management standards.

---

## 🏛️ 1. Algorithmic Trading System Component Architecture

The algorithmic trading system decouples market analysis logic from order execution and risk controls:

```
[Market Data Ingestion Tier]
  ├── Real-time Tick Feed & Candlesticks (WebSocket / FIX Protocol / MQL OnTick)
  ├── News Calendar Filter (Economic High-Impact Event API)
  └── Market Depth & Spread Monitor
           │
           ▼
[Strategy & Quantitative Signal Engine]
  ├── Technical Indicators & Price Action Logic
  ├── Volatility Filters (ATR / Bollinger Bandwidth)
  └── Order Signals: BUY / SELL / CLOSE / MODIFY
           │
           ▼
[Pre-Trade Risk Management Gate (MANDATORY CONTROL)]
  ├── Daily Drawdown Validator (Verify whether max DD limit is reached)
  ├── Account Equity & Margin Check (Verify sufficient free margin)
  ├── Dynamic Lot Calculator (Calculate lot size based on % capital risk)
  ├── Spread & Slippage Filter (Abort if spread widens beyond tolerance)
  └── Maximum Simultaneous Exposure Check (Limit total open lots/trades)
           │
           ▼ (Forwarded only if all risk filters pass)
[Order Execution Engine]
  ├── Broker / Exchange Bridge (MetaTrader Trade Library / CCXT / FIX API)
  ├── Order Timeout & Re-quote Handler
  └── State Machine: PENDING -> EXECUTED -> SL/TP_HIT -> CLOSED
           │
           ▼
[Post-Trade & Observability Tier]
  ├── Trade Audit Log (Persisted to PostgreSQL with unique transaction IDs)
  ├── Emergency Circuit Breaker Watchdog (Heartbeat & Health Monitor)
  └── Real-time Notifications (Telegram Bot / Discord Webhook / Push Alerts)
```

---

## ⚖️ 2. Capital Preservation Doctrine & Risk Formulations

### 2.1 Dynamic Position Sizing (Dynamic Lot Calculation)
❌ **Strictly Prohibited:** Arbitrary static lot sizing (e.g., always 1.0 lot) or unbounded martingale multiplication strategies.  
✅ **Standard Lot Calculation Formula:**
Position sizing must be calculated dynamically based on the risk tolerance percentage of current account equity:

$$\text{Risk Amount (\$)} = \text{Account Equity} \times \text{Risk Percentage (e.g., 1\%)}$$

$$\text{Lot Size} = \frac{\text{Risk Amount (\textit{USD})}}{\text{Stop Loss Distance (Pips/Points)} \times \text{Tick Value per Lot}}$$

*Example Case:*
- Account Equity = \$10,000
- Risk per Trade = 1% (\$100)
- Stop Loss Distance = 50 pips
- Pip Value for EURUSD per 1.0 lot = \$10
- Resulting Lot Size = $\$100 / (50 \times \$10) = 0.20\text{ lot}$.

### 2.2 Emergency Circuit Breaker (Max Daily Drawdown Kill-Switch)
Every EA or trading bot must implement an autonomous emergency circuit breaker:
```text
If (Current_Equity <= Day_Start_Equity * (1 - Max_Daily_Drawdown_Limit%)):
    1. Immediately execute CloseAllPositions() at best available market price.
    2. Cancel all pending orders (CancelAllPendingOrders()).
    3. Disable trading permission flag (TradingEnabled = FALSE).
    4. Dispatch high-priority emergency alerts via Telegram & operator email.
    5. Lock the system until manual intervention or next session rollover.
```

### 2.3 API Key Permission Segregation & Hardening
When connecting trading bots to crypto exchanges (Binance, Bybit) or institutional broker APIs:
- **Permitted Permissions:** `Read Info (Query)`, `Spot Trading`, `Futures Trading`.
- **STRICTLY PROHIBITED PERMISSIONS:**  
  ❌ `Enable Withdrawals` (Fund Withdrawal).  
  *Rationale:* If the EA host server is compromised, attackers can never extract or drain trading capital from the exchange account!

---

## 🧪 3. Standard Operating Procedure (SOP) for Testing & Anti-Overfitting

Trading algorithms are prohibited from deploying with live capital before passing 5 validation gates:

| Testing Phase | Period & Dataset | Acceptance Criteria |
| :--- | :--- | :--- |
| **1. In-Sample Backtest** | 70% historical dataset (e.g., 2020-2023) | Profit Factor > 1.5, Max Drawdown < 15%, Sharpe Ratio > 1.2. |
| **2. Out-of-Sample Test** | 30% unseen historical dataset | Performance degradation < 25% relative to in-sample (guards against curve-fitting). |
| **3. Walk-Forward Analysis** | Rolling window optimization & testing | Consistent profitability across diverse market regimes (trending vs. ranging). |
| **4. Paper Trading / Demo** | Minimum 30 calendar days on live data | Realized slippage and execution latency align with model assumptions. |
| **5. Incubation (Micro/Cent)** | Live account with micro capital (1-5% planned capital) | Validates live broker execution, real-world spreads, and VPS stability. |

---

## 🖥️ 4. VPS Infrastructure & Watchdog Heartbeat

1. **Low-Latency VPS Hosting:**
   - Deployed within the data center in closest proximity to broker trade servers (e.g., Equinix LD4 London for Forex, or Tokyo/Virginia for Crypto).
   - Execution ping latency strictly sub-5 ms.
2. **Watchdog Heartbeat:**
   - Independent monitoring process emits a *ping heartbeat* every 60 seconds.
   - If the MT5 terminal or Python runtime hangs (*freezes*), the watchdog automatically restarts the process and dispatches an emergency notification to the operator.

---

## 📋 5. Pre-Live Trading Verification Checklist

- [ ] Automated Stop Loss is attached at order dispatch time (*never enter market without an SL*).
- [ ] *Max Daily Drawdown* circuit breaker is verified on a simulated environment.
- [ ] Spread filters and economic news filters (*Economic News Filter*) are active.
- [ ] *Withdrawal* permissions on all exchange API keys are 100% disabled.
- [ ] Audit database logs every order ticket, execution timestamp, and realized slippage.

---

## 🧰 6. Tool Selection Matrix (By Instrument & Use Case)

Not every trading tool serves the same purpose. Select based on **target instrument** and **role in the pipeline** — do not force a single tool to cover everything. This matrix reflects each project's license and scope constraints so that derived projects remain legally compliant and architecturally coherent.

### 6.1 Selection by Instrument

| Target Instrument | Primary Toolchain | License | Role | Notes |
|---|---|---|---|---|
| **Forex / CFD / Metals** (XAUUSD, EURUSD, dll) | **MQL5 + MT5 Strategy Tester + MetaAPI** | Proprietary (MetaQuotes) + MetaAPI SDK | Authoring EA, backtest, live execution | The ONLY path that produces a real MetaTrader EA (`.ex5`). This is the baseline's default trading stack. |
| **Crypto Spot / Futures** (BTC/USDT, dll) | **freqtrade** *or* your own `ccxt + vectorbt/backtrader` stack | freqtrade = **GPL-3.0** ⚠️ | End-to-end crypto algo: backtest, hyperopt, dry-run, live | Strong risk controls (stoploss, trailing, protections). GPL-3.0 = **reference/separate deployment only**, never copy code into Apache-2.0 derived projects. |
| **Multi-asset backtest / architecture reference** | **QuantConnect Lean** | **Apache-2.0** ✅ | Reference design for event-driven engine (data feeds, transaction handlers, risk, kill-switch) | Written in C#/.NET — **use as a design reference, not a dependency**. Does NOT author MetaTrader EAs. |
| **Alpha research + strategy export** | **Vibe-Trading** | **MIT** ✅ | Optional research workspace: backtesting (10 engines), Alpha Zoo, and strategy export incl. **MQL5** | Research-only by default (read-only, no custody). Optional companion for the research phase, not the execution core. |

### 6.2 Non-Negotiable Rules for External Tools

1. **License gate:** Only MIT / Apache-2.0 tools may be referenced as *recommended*. GPL/AGPL tools (freqtrade, FinceptTerminal) are for **learning or isolated deployment** — never copy their source into a derived project.
2. **No MetaTrader authoring outside MQL5:** None of the external tools above compile a MetaTrader EA. For Forex/CFD, always fall back to the MQL5 + MetaAPI stack defined in Section 1.
3. **Research vs Execution separation:** Tools like Vibe-Trading and Lean belong to the *research/backtest* tier. The *live execution* tier must remain the hardened, risk-gated pipeline from Sections 1–2 with the circuit breaker and API-key segregation intact.
4. **Capital preservation is non-transferable:** Adopting any external tool does NOT waive the Section 2 doctrine — Hard Stop Loss, 1–2% dynamic sizing, and the 5% daily drawdown kill-switch must still be enforced regardless of the tool.

### 6.3 Rejected / Not Recommended

| Tool | Reason |
|---|---|
| **FinceptTerminal** | Financial *data/analytics desktop terminal*, not a trading/bot framework. No MetaTrader/MQL support, and **AGPL-3.0** copyleft is incompatible with this Apache-2.0 baseline. Core algo/live features are locked behind paid tiers. |
