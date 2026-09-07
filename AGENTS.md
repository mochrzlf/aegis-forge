# AGENTS.md — Universal Multi-Domain Aegis Forge

> **CRITICAL FOR AI AGENTS (Hermes / Claude / Cursor / LLM) & DEVELOPERS:**
> This file is automatically read at the beginning of every development session.
> It serves as the **permanent working contract & single source of truth** for all derived projects:
> - 🌐 **Web Applications & SaaS Platforms**
> - 📱 **Mobile Applications (Android & iOS)**
> - 📈 **Algorithmic & EA Trading Systems**
> - 🏢 **Enterprise Backend Services & Data Infrastructure**
> 
> Read this entire document before writing or modifying a single line of code.

---

## 🎯 1. Project Philosophy & Reference Standards

Every project derived from this baseline MUST uphold four universal pillars:
1. **Product-Driven & Specification-First:** Every line of code must refer to specifications in the `docs/` folder (PRD, OpenAPI, UI tokens, or Trading Strategy Sheet).
2. **Secure-by-Design & Zero Trust:** Implement Zero Trust, Principle of Least Privilege (PoLP), Threat Modeling (STRIDE), and automated secrets protection.
3. **Rigid Risk Management:** For financial/trading systems specifically, capital preservation and drawdown risk limits are absolute priorities above profit generation.
4. **High Polish & Observability:** Responsive and accessible interfaces, structured anti-PII logging, and tamper-proof audit trails.

### Mandatory Reference Documents:
| Document | Description |
|---|---|
| `docs/PRD.md` | Product summary, problem statement, personas, and success metrics |
| `docs/PRD-detail.md` | User Stories & Acceptance Criteria (AC) per module |
| `docs/ui-design.md` | Design System, color tokens, typography, and screen mockups |
| `docs/openapi.yaml` | REST API Contract — 100% compliance REQUIRED |
| `docs/schema.sql` | PostgreSQL database schema & integrity constraints |
| `docs/security-iam-policy.md` | IAM and RBAC security standards, and Data Privacy compliance (e.g., GDPR) |
| `docs/security-access-matrix.md` | Entitlement Matrix, Segregation of Duties (SoD), & Maker-Checker |
| `docs/blueprints/` | Domain-specific architectural blueprints (Web, Mobile, EA Trading) |
| `docs/security/` | Domain-specific security checklists (Mobile AppSec, Trading Risk Policy) |
| `docs/diagrams/` | Visual architecture diagrams, authentication sequences, and execution flows |
| `docs/adr/` | Architecture Decision Records & STRIDE Threat Modeling |
| `docs/agent-playbooks/` | Gated, step-by-step workflows per domain — follow BEFORE writing code |
| `docs/prompt-library.md` | Tested copy-paste prompts per phase & domain |
| `docs/backend-checklist.md` | Backend/service QA checklist (contract, data, authz, observability) |
| `docs/observability.md` | Structured anti-PII logging, RED metrics, tracing, tamper-evident audit |
| `docs/migrations.md` | Versioned, reversible, zero-downtime DB migration standard |
| `docs/design-tokens.md` | Single-source design-token pipeline → Web/Tailwind, Compose, SwiftUI, Flutter |
| `docs/frontend-testing.md` | Frontend testing standard (Vitest, Testing Library, axe-core, Playwright) |
| `docs/performance-budgets.md` | Core Web Vitals + bundle-size budgets, enforced in CI |
| `docs/deployment.md` | Environment promotion, deploy strategies, secrets, rollback standard |
| `docs/runbook-template.md` | Per-service operational runbook (start/stop, alerts, recovery) |
| `docs/testing-strategy.md` | Unified cross-domain testing strategy, coverage & quality gates |
| `docs/research/EXTERNAL-TOOLS.md` | Adoption register for all external tools/skills (verdict, license, constraints) |
| `evals/` | Agent output-quality harness (scenarios + rubrics) |

---

## 🏗️ 2. Standard Tech Stack per Domain

AI Agents must adopt the following standardized stack according to the project domain:

```
[Web Applications]
Frontend  : Next.js (App Router) / React / Vue + TypeScript + Tailwind CSS
UI Kit    : Radix UI / shadcn/ui primitives + Lucide Icons
Backend   : NestJS / FastAPI / Express + TypeScript / Python

[Mobile Applications]
Android   : Kotlin (Jetpack Compose) / Clean Architecture + Coroutines / Flow
Cross-Plat: Flutter (Dart) / React Native (TypeScript)
Security  : Android Keystore, EncryptedSharedPreferences, SSL Pinning, FLAG_SECURE

[EA & Quantitative Trading Systems]
MetaTrader: MQL5 / MQL4 (Expert Advisors, Custom Indicators, Scripts)
Python    : Python 3.11+ (ccxt, pandas, numpy, backtrader / vectorbt, MetaAPI)
Protocols : FIX Protocol (4.4/5.0), low-latency WebSocket, REST API
Messaging : Redis Streams / BullMQ for order queues and tick streaming

[Core Infrastructure & Shared Services]
Database  : PostgreSQL 16+ (RBAC, Triggers, Kill-Switch, AES-256 FLE)
Caching   : Redis 7+ (Session Store, Rate Limiter, Market Data Cache)
Testing   : Vitest / Jest / PyTest / JUnit5 / MT5 Strategy Tester
Mocking   : Stoplight Prism (Mock API Server on port 4010)
DevSecOps : Gitleaks, Semgrep SAST, Trivy, Git Pre-Commit Hooks
```

---

## ⚖️ 3. Universal Core Non-Negotiable Rules

### 3.1 API Contract & Response Formatting
All REST API endpoints MUST return a standardized payload structure:
```json
// SUCCESS
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "per_page": 20, "total": 100 }
}

// ERROR
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED" | "FORBIDDEN" | "VALIDATION_ERROR" | "NOT_FOUND" | "INTERNAL_ERROR",
    "message": "User-friendly error message",
    "details": {}
  }
}
```

### 3.2 IAM Security & Privileged Access
1. **Role-Based Access Control (RBAC) & Maker-Checker:**
   - Critical actions (role promotion, fund withdrawals, limit adjustments, trading parameter execution) MUST enforce the Four-Eyes principle (`maker_user_id <> checker_user_id`).
   - JML Kill-Switch: Updating user status to `terminated` or `suspended` must immediately revoke all active tokens and sessions.
2. **IDOR / BOLA Prevention:**
   - Every data modification query must verify resource ownership: `WHERE id = :id AND user_id = :currentUserId`.
3. **Immutable Audit Trail:**
   - All data mutations must be logged to the `audit_logs` table, protected by anti-tamper triggers (strict prohibition of `UPDATE` and `DELETE`).
4. **Data Privacy Laws (e.g., GDPR) & Secret Leak Prevention:**
   - STRICTLY FORBIDDEN to log personally identifiable information (PII), passwords, card numbers, or account balances to console logs.
   - STRICTLY FORBIDDEN to commit `.env` files, `.jks` keystores, or secret tokens to Git.

### 3.3 Automated Threat Modeling (STRIDE)
- Before writing code for any new module, endpoint, or trading strategy, a **STRIDE** analysis (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) must be documented under `docs/adr/`.

---

## 🚀 4. Domain-Specific Execution Engine Modules

### 4.1 🌐 Web Application Engine
1. **Cookie Transport Security:** Refresh tokens MUST be sent via `Set-Cookie` with the attributes: `HttpOnly; Secure; SameSite=Strict; Path=/api/auth`. Returning refresh tokens in JSON response bodies for storage in `localStorage` is strictly forbidden.
2. **Security Headers:** Apply Helmet.js (strict CSP, HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff).
3. **Core Web Vitals:** Ensure responsive component rendering, image optimization (WebP/AVIF), and LCP < 2.5s.

### 4.2 📱 Mobile Application Engine (Android & iOS)
1. **Hardware Keystore Storage:**
   - ❌ STRICTLY FORBIDDEN to store tokens, passwords, or biometric data in plaintext `SharedPreferences` / `NSUserDefaults`.
   - ✅ MUST use **Android Keystore System** + `EncryptedSharedPreferences` (or `flutter_secure_storage` / `react-native-keychain`).
2. **SSL / Certificate Pinning:**
   - Must include `network_security_config.xml` configuration to pin backend server public SSL certificate hashes to prevent Man-in-the-Middle (MitM) attacks.
3. **Screen Protection (`FLAG_SECURE`):**
   - Screens displaying financial data, OTPs, balances, or personal identity must be protected with `FLAG_SECURE` to block screenshots and screen recording.
4. **Anti-Tampering & Minification:**
   - MUST enable **R8 / ProGuard** to minify and obfuscate production code.

### 4.3 📈 Algorithmic & EA Trading Engine
1. **Capital Preservation Doctrine:**
   - ❌ STRICTLY FORBIDDEN to execute trading orders without a mathematically calculated **Hard Stop Loss (SL)**.
   - ❌ STRICTLY FORBIDDEN to use pure martingale strategies (unlimited lot doubling) that risk *Margin Call / Account Wipeout*.
2. **Dynamic Position Sizing:**
   - Lot sizes MUST be calculated dynamically based on capital risk percentage per trade (maximum **1% to 2% of Equity**), accounting for Stop Loss distance and the instrument's tick/pip value.
3. **Emergency Circuit Breaker (Max Daily Drawdown Kill-Switch):**
   - The EA must periodically monitor daily floating drawdown.
   - If *Daily Drawdown* reaches the tolerance limit (e.g., **5% Equity**), the system must:
     1. Close all open positions (*Emergency Close All*).
     2. Cancel all pending orders.
     3. Activate an automatic *trading pause* until the next market day rollover.
     4. Dispatch emergency alerts (Telegram / Discord / Email).
4. **API Key Permission Segregation:**
   - Exchange API keys (e.g., Binance, Bybit, IBKR) MUST ONLY have **Read Info** and **Spot/Futures Trading** permissions.
   - ❌ **STRICTLY FORBIDDEN TO ENABLE WITHDRAWAL PERMISSIONS** on API keys used by the EA/Algorithm.
5. **Slippage Tolerance & Spread Filter:**
   - The EA must validate spreads prior to execution. Abort orders if the spread widens beyond reasonable limits (e.g., during high-impact news releases such as NFP, CPI, FOMC).
6. **Mandatory Testing Cycle (Anti-Overfitting SOP):**
   - Prior to live account deployment, algorithms must pass through 5 validation gates:
     `In-Sample Backtest (70% data) -> Out-of-Sample Test (30% data) -> Walk-Forward Analysis -> Demo / Paper Trading (Min. 30 days) -> Low-Risk Live Account (Cent/Micro)`.

---

## 🧪 5. Testing Requirements

Every new feature implementation must pass a comprehensive testing suite:
1. **Unit Tests (Business Logic):** Validate financial calculations, authorization flows, and state transitions.
2. **Boundary & Negative Tests:** Invalid input, negative values, numeric overflow, missing headers.
3. **Security Tests:**
   - Access without token (must return 401 Unauthorized).
   - Access with unauthorized role (must return 403 Forbidden).
   - IDOR probe against other users (must return 403 or 404).
4. **Domain-Specific Tests:**
   - Mobile: Offline caching tests and token expiry refresh flow.
   - Trading: Extreme slippage simulations, margin call scenarios, and circuit breaker triggers.

---

## 📋 6. AI Agent Execution Workflow

When a user assigns a task:
1. **Identify Domain:** Determine project domain (`Web`, `Mobile`, `EA Trading`, or `Fullstack`).
2. **Consult Blueprint:** Refer to the relevant architecture document in `docs/blueprints/`.
3. **Evaluate Threats & Risks:** Perform STRIDE analysis (for applications) or a *Risk Breakdown* (for trading EAs) in `docs/adr/`.
4. **Visualize Architecture:** Create or update visual diagrams in `docs/diagrams/` before writing complex code.
5. **Implement Code:** Write clean, modular code adhering to layered architecture (*Clean Architecture*) with tests.
6. **Verify Security:** Run `make audit` and unit tests before reporting that the work is complete.
