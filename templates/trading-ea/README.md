# Aegis Forge — Trading EA & Algorithmic Trading Starter Skeleton

Institutional-grade, security-first quantitative trading starter skeleton adhering to the **Capital Preservation Doctrine**.

---

## 🏛️ Architecture Overview

This skeleton provides two complementary tiers:

1. **Native MQL5 Expert Advisor (`mql5/AegisRiskGuardianEA.mq5`)**:
   - Compiles directly in MetaEditor (MetaTrader 5).
   - Enforces pre-trade hard stop loss, max 1–2% dynamic equity sizing, and emergency daily drawdown circuit breaker.
   - Built-in spread & slippage protection.

2. **Python FastAPI Risk Guardian Bridge (`backend/`)**:
   - Independent REST API for quantitative models, machine learning signal engines, or exchange bots.
   - Centralizes risk calculation: dynamic lot sizing, drawdown monitoring, and API key permission verification (refuses startup if withdrawal permissions are detected).

---

## 🛡️ Core Guardrails Enforced

- **Hard Stop Loss Mandatory:** Zero unhedged positions or grid/martingale betting allowed. Every trade must have an initial SL.
- **Dynamic Lot Sizing:** Automatically calculates lot size based on `1.0%` (or user-configured ceiling up to `2.0%`) equity risk per trade.
- **Emergency Circuit Breaker:** If daily drawdown reaches `5.0%` of day-start equity, the system:
  1. Immediately closes all open positions.
  2. Cancels all pending orders.
  3. Halts new trading until session rollover or operator review.
- **API Key Segregation:** Rejects any exchange API key that contains `withdrawal` or `transfer_funds` permissions.

---

## 🚀 Getting Started

### 1. Running the Python Risk Guardian Bridge

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run test suite
pytest tests/ -v

# Start the bridge server
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Interactive documentation will be available at `http://localhost:8001/docs`.

### 2. Deploying the MQL5 EA in MetaTrader 5

1. Open MetaTrader 5 and press `F4` to open **MetaEditor**.
2. Copy `mql5/AegisRiskGuardianEA.mq5` into your terminal's `MQL5/Experts/` directory.
3. Open the file in MetaEditor and click **Compile** (`F7`).
4. Attach `AegisRiskGuardianEA` to any chart (e.g., EURUSD, XAUUSD).
5. Ensure **Allow Algo Trading** is enabled in MT5.
