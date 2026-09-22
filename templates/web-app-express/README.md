# Aegis Forge — Web App Starter Skeleton (Express.js + TypeScript)

> **Enterprise-grade, security-hardened Express.js + TypeScript starter skeleton** adhering to the **Spec-First** and **Banking-Grade Zero Trust IAM** doctrines.

---

## 🛡️ Built-in Security Controls

| Pillar | Implementation | Technical Detail |
|---|---|---|
| **Auth + Token Rotation (RTR)** | JWT Access (15m) + Single-Use Refresh Token (7d) | Refresh token stored **exclusively** in `HttpOnly; Secure; SameSite=Strict` cookies. Replay reuse triggers immediate family-wide session revocation. |
| **Brute-Force & Lockout** | 5 failed attempts → 15-min lockout | Rejects brute-force attacks with `423 ACCOUNT_LOCKED` before executing expensive password hashing operations. Admin manual unlock endpoint included. |
| **JML Session Kill-Switch** | Instant session termination on status update | Moving user status to `suspended` or `terminated` revokes all active refresh tokens in a single scoped update. |
| **Maker-Checker / Dual Control** | Four-Eyes Principle | Maker cannot approve their own change request (`403 Forbidden`). Enforced both at service level and PostgreSQL DB check constraint (`maker_user_id <> checker_user_id`). |
| **Append-Only Audit Trail** | Immutable PostgreSQL trigger | Database trigger strictly prohibits `UPDATE` and `DELETE` queries on `audit_logs` table (returns SQL error `55000`). |
| **Rate Limiting** | Sliding window on Redis | Limits brute-force risk (e.g. 5 req/min on `/auth/login`, 10 req/min on `/auth/register`). Exceeded limits return `429 RATE_LIMITED` with `Retry-After`. |
| **Hardened Headers & CORS** | `helmet` + strict CORS | Defends against XSS, clickjacking, MIME-sniffing, and cross-origin abuse. |

---

## 🧰 Tech Stack
- **Runtime:** Node.js 20+ (LTS)
- **Framework:** Express.js + TypeScript 5
- **Database:** PostgreSQL 16 (`pg` pool)
- **Cache:** Redis 7 (sessions, rate limits)
- **Testing:** Vitest + Supertest (9 automated unit tests)
- **Containerization:** Docker Compose

---

## 🚀 Quick Start

```bash
# 1. Setup environment
cp .env.example .env

# 2. Start full stack in Docker (DB, Redis, API, Mailpit)
make first-run

# 3. Run unit tests
make test

# 4. Build TypeScript code
make build
```

Endpoints:
- API Server: `http://localhost:8000`
- Liveness Probe: `GET /health/live`
- Readiness Probe: `GET /health/ready`
- Mailpit Web UI: `http://localhost:8025`
