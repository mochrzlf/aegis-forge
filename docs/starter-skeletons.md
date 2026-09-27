# 🧰 Starter Skeletons & Domain Maturity Matrix

> **Pre-tested, runnable starter code for every domain** — login, database, and security are already built and verified by automated test suites.

When you initialize a new project with `bash scripts/init-new-project.sh`, you don't start from an empty text file. You can automatically install one of these pre-built foundations.

---

## 📊 1. Domain Maturity Matrix

| Domain | Blueprint | Starter Skeleton | Automated Verification | Maturity Status |
|---|---|---|---|---|
| **Web (FastAPI)** | `docs/blueprints/web-application-blueprint.md` | `templates/web-app/` | ✅ Docker Compose + 20 Pytest unit & security tests | **Production-Ready Core** (Python) |
| **Web (Express.js)** | `docs/blueprints/web-application-blueprint.md` | `templates/web-app-express/` | ✅ Docker Compose + 9 Vitest unit tests | **Production-Ready Core** (TypeScript) |
| **Web (Laravel 11)** | `docs/blueprints/web-application-blueprint.md` | `templates/web-app-laravel/` | ✅ Docker Compose + 10 PHPUnit feature tests | **Production-Ready Core** (PHP) |
| **Web (Go Chi)** | `docs/blueprints/web-application-blueprint.md` | `templates/web-app-go/` | ✅ Docker Compose + 8 Go unit tests (~15MB RAM) | **Production-Ready Core** (Golang) |
| **Trading EA & Quant** | `docs/blueprints/ea-trading-blueprint.md` | `templates/trading-ea/` | ✅ 6 Pytest tests (Risk Guardian, Sizing & Circuit Breaker) | **Code-Backed Starter** (MQL5 + Python) |
| **Mobile (Android)** | `docs/blueprints/mobile-application-blueprint.md` | `templates/mobile-android/` | ✅ Android Keystore, SSL Pinning, FLAG_SECURE verified | **Code-Backed Starter** (Kotlin Native) |
| **Mobile (iOS)** | `docs/blueprints/mobile-application-blueprint.md` | `templates/mobile-ios/` | ✅ Apple Keychain, SSL Pinning, App Switcher blur verified | **Code-Backed Starter** (Swift / SwiftUI) |
| **Web (Next.js + Supabase)**| `docs/blueprints/web-application-blueprint.md` | `templates/web-app-nextjs-supabase/` | ⚠️ Manual verification (trades strictness for UI speed) | **Reference Only** (Fullstack Next.js) |

---

## 🏠 2. Detailed Breakdown of Skeletons

### 1. `templates/web-app/` (FastAPI Python) ⭐ *Recommended Default*
- **Technology:** FastAPI, Python 3.11+, PostgreSQL 16, Redis 7.
- **Key Capabilities:**
  - Refresh Token Rotation (RTR) stored in `HttpOnly; Secure; SameSite=Strict` cookies.
  - Replay attack detection: revokes entire session family if a used token is presented.
  - Role-Based Access Control (5 tiers: `superadmin`, `admin`, `support`, `member`, `guest`).
  - Account lockout after 5 consecutive failed attempts (15-min freeze).
  - JML session kill-switch (revokes all active sessions on user termination/suspension).
  - Maker-Checker dual control constraint on sensitive endpoints.
  - MFA / TOTP step-up authentication.
  - Tamper-proof append-only `audit_logs` table.
- **Testing:** 20 Pytest test suites passing in CI.

### 2. `templates/web-app-express/` (Express.js TypeScript)
- **Technology:** Node.js, Express.js, TypeScript, PostgreSQL, Redis.
- **Key Capabilities:**
  - TypeScript strict typing across controllers, services, and middlewares.
  - Cookie-based RTR token lifecycle and anti-IDOR resource ownership binding.
  - Database-level Maker-Checker constraint (`maker_id <> checker_id`).
  - Automated database triggers preventing `UPDATE` and `DELETE` on audit trails.
- **Testing:** 9 Vitest test suites.

### 3. `templates/web-app-laravel/` (Laravel 11 PHP)
- **Technology:** Laravel 11, PHP 8.3, PostgreSQL, Redis, Nginx.
- **Key Capabilities:**
  - Clean service-repository pattern with Form Request validation.
  - Eloquent model observers creating immutable audit records.
  - Database migrations for Maker-Checker tickets and account lockouts.
- **Testing:** 10 PHPUnit feature tests.

### 4. `templates/web-app-go/` (Go Chi)
- **Technology:** Golang 1.22+, Chi Router, pgx/v5, Redis client.
- **Key Capabilities:**
  - Ultra-high throughput and minimal memory footprint (~15MB RAM idle).
  - Native cryptographic password hashing and strict HTTP middleware stack.
  - Server-side role validation and ownership guards.
- **Testing:** 8 Go test suites.

### 5. `templates/trading-ea/` (Algorithmic Trading & MT5)
- **Technology:** MQL5 native Expert Advisor (`AegisRiskGuardianEA.mq5`) + Python FastAPI Risk Bridge.
- **Key Capabilities:**
  - Capital Preservation Doctrine: mandatory Hard Stop Loss on every ticket.
  - Dynamic position sizing: automatically computes lot size to risk exactly 1% to 2% of equity.
  - Emergency Circuit Breaker: triggers immediate emergency close-all and trading halt if daily floating drawdown hits 5%.
  - Zero-withdrawal permission guard on exchange/broker API keys.
- **Testing:** 6 Pytest unit tests for sizing algorithms and circuit breakers.

### 6. `templates/mobile-android/` (Android Kotlin)
- **Technology:** Kotlin Native, Jetpack Compose, Android Keystore System.
- **Key Capabilities:**
  - AES-256-GCM hardware-backed token storage via `EncryptedSharedPreferences`.
  - SSL / SPKI SHA-256 certificate pinning in `network_security_config.xml`.
  - `FLAG_SECURE` window protection preventing screenshots and recent-apps leaks.
  - Production R8/ProGuard obfuscation rules.

### 7. `templates/mobile-ios/` (iOS Swift)
- **Technology:** Swift 5.9+, SwiftUI, Apple Keychain Services.
- **Key Capabilities:**
  - Secure token storage using `kSecAttrAccessibleThisDeviceOnly`.
  - URLSession SPKI SSL Pinning delegate.
  - Privacy Shield: automatic screen blur when app enters background / App Switcher.
  - Anti-jailbreak environment verification heuristics.

### 8. `templates/web-app-nextjs-supabase/` (Reference Fullstack)
- **Technology:** Next.js 14 (App Router), React, Supabase Auth, PostgreSQL RLS.
- **Usage Note:** Provided for developers who want an all-in-one UI + database prototype in minutes. Note that it delegates auth and storage to Supabase, which deviates slightly from our self-hosted Zero Trust baseline.

---

## 🖥️ 3. Frontend Architecture Guide: Decoupled vs Fullstack

The web backend skeletons (`web-app`, `web-app-express`, `web-app-laravel`, `web-app-go`) are **Headless API Backends**. They run your database and API server at `http://localhost:8000`.

### How Does the Frontend UI Fit In?

```
┌───────────────────────────────────────┐
│     Frontend Client (Browser/App)     │
│   React / Next.js / Vue + Tailwind    │
│           (in frontend/)              │
└──────────────────┬────────────────────┘
                   │
                   │ HTTP Requests (with credentials: "include")
                   │ HttpOnly Auth Cookies
                   ▼
┌───────────────────────────────────────┐
│     Aegis Forge Headless Backend      │
│  FastAPI / Express / Laravel / Go     │
│       (at localhost:8000/api)         │
└──────────────────┬────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
   PostgreSQL 16         Redis 7
   (Data & Audit)     (Rate Limits)
```

1. **Step 1 — Design Specs First:** Your UI screens, wireframes, and color tokens are planned in `docs/ui-design.md`.
2. **Step 2 — Prompt Your AI Agent:** When backend endpoints are in place, instruct your AI coding agent:
   > *"Scaffold a frontend in `frontend/` using [React Vite / Next.js / Vue] with Tailwind CSS. Follow the design tokens in `docs/ui-design.md` and connect API calls to our backend at `http://localhost:8000` using cookie credentials."*
3. **Alternative Option:** If you prefer an all-in-one UI template on Day 1 without separating frontend and backend, select `nextjs-supabase` during project initialization.

---

> 💡 **Next Steps:**
> - Return to the main setup guide: [README.md](../README.md).
> - Explore real-world implementation examples: [docs/examples.md](examples.md).
