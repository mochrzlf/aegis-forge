# 💼 Real-World Implementation Examples & Case Studies

> **Concrete scenarios showing how Aegis Forge is used in practice** — from online shops to medical portals and automated trading bots.

---

## 🎯 1. End-to-End Walkthrough: Building "TokoKeren" (E-Commerce Store)

This scenario demonstrates how a non-technical founder builds a secure online store from scratch using Aegis Forge and an AI Coding Agent (Claude Code, Cursor, or Hermes).

| Stage | Command or AI Prompt | What Actually Happens |
|---|---|---|
| **1. Initialize** | `bash scripts/init-new-project.sh`<br>*(Or `pwsh scripts/init-new-project.ps1` on Windows)* | • Name: `TokoKeren`<br>• Domain: `1) Web`<br>• Skeleton: `1) web-app (FastAPI)`<br>• The script creates `../TokoKeren/`, copies the FastAPI backend, configures unique secret keys, and activates git pre-commit alarms. |
| **2. Navigate** | `cd ../TokoKeren` | Switches into your new project directory. |
| **3. Plan Specs with AI** | **Prompt AI:**<br>_"Use the `prd-interviewer` skill. Read AGENTS.md, then interview me to draft `docs/PRD.md` and `docs/PRD-detail.md` for TokoKeren (product catalog, cart, checkout, payment webhooks, and buyer/admin roles)."_ | AI asks structured questions, confirms requirements, and writes unambiguous specs without hallucinating features. |
| **4. Design UI Mockups** | **Prompt AI:**<br>_"Read docs/ui-design-template.md and draft docs/ui-design.md with complete UI tokens (Tailwind), screen wireframes, and button states for TokoKeren."_ | AI defines the visual design system, colors, fonts, and wireframes before writing code. |
| **5. Break Down Tasks** | **Prompt AI:**<br>_"Use the `spec-to-tasks` skill. Turn `docs/PRD.md` into atomic tasks in `docs/TASKS.md` with explicit `skeleton_hint` for each."_ | AI creates manageable tasks (Task 1 to Task N), each referencing the exact file to edit. |
| **6. Start the Stack** | `make first-run` | Spins up PostgreSQL, Redis, executes database migrations, and launches FastAPI at `http://localhost:8000` (interactive API documentation live at `/docs`). |
| **7. Build Features with AI** | **Prompt AI:**<br>• *(Backend)* _"Execute Task 1 from `docs/TASKS.md`: Implement product catalog endpoints per skeleton_hint."_<br>• *(Frontend)* _"Scaffold a React + Tailwind frontend in `frontend/` following `docs/ui-design.md` and connecting to `http://localhost:8000`."_ | AI modifies the working backend code first, then scaffolds the decoupled web UI. |
| **8. Audit & Commit** | `make test && make audit`<br>`git add . && git commit -m "feat: complete product catalog"` | Automated unit and security tests pass. The pre-commit hook verifies no API keys or database credentials are leaked. |

---

## 🍜 2. Case Study: WhatsApp Food-Ordering Bot

- **Scenario:** A home-catering business wants a WhatsApp bot where customers can view the daily menu, place lunch orders, calculate total prices, and receive payment instructions.
- **How Aegis Forge Solves It:**
  - ✅ **Database Schema (`schema.sql`):** Pre-modeled tables for `menu_items`, `orders`, and `order_items`.
  - ✅ **Credential Security:** WhatsApp Cloud API tokens and LLM API keys are encrypted using AES-256 master keys in `.env`.
  - ✅ **Rate Limiting:** Prevents malicious users from spamming the WhatsApp webhook endpoint and driving up LLM API bills.
  - ✅ **Immutable Audit Trail:** Order history and status changes are permanently recorded and cannot be altered or falsified.
  - 🔨 **What You Add:** WhatsApp webhook handler, conversation logic, and payment gateway callback.

---

## 🏥 3. Case Study: Clinic Patient Portal

- **Scenario:** A healthcare clinic needs an online portal where patients can schedule doctor appointments, view lab test results, and update personal profiles.
- **How Aegis Forge Solves It:**
  - ✅ **Banking-Grade IAM & RBAC:** Enforces strict role separation between `superadmin` (clinic director), `admin` (receptionist), `doctor`, and `member` (patient).
  - ✅ **Anti-IDOR / BOLA:** Ensures Patient A cannot view Patient B's medical records by modifying the ID parameter in the URL.
  - ✅ **Account Lockout:** Locks accounts after 5 failed login attempts to stop brute-force password guessing.
  - ✅ **JML Kill-Switch:** Immediately revokes portal access when a staff member leaves the clinic.
  - 🔨 **What You Add:** Doctor scheduling logic, medical record upload handler, and appointment calendar UI.

---

## 📈 4. Case Study: Automated Gold Trading Bot (XAUUSD)

- **Scenario:** A quantitative trader wants an Expert Advisor (EA) running 24/5 on MetaTrader 5 (MT5) to scalp gold (XAUUSD) based on market volatility.
- **How Aegis Forge Solves It:**
  - ✅ **Mandatory Hard Stop Loss:** Orders cannot be placed without a predefined hard Stop Loss.
  - ✅ **Dynamic Lot Calculation:** Automatically calculates lot size so each trade risks no more than 1% of total equity.
  - ✅ **Emergency Circuit Breaker:** If daily floating loss reaches 5%, the system immediately liquidates all open positions, cancels pending orders, and stops trading until the next day.
  - ✅ **Restricted API Keys:** Broker API keys are forbidden from having withdrawal permissions.
  - 🔨 **What You Add:** Specific technical indicator rules (e.g. RSI divergence, Bollinger Band mean reversion).

---

> 💡 **Next Steps:**
> - Ready to start building? Follow the steps in [README.md](../README.md).
> - Encountered an issue? Check [docs/faq-troubleshooting.md](faq-troubleshooting.md).
