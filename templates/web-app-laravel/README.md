# Aegis Forge — Web App Starter Skeleton (Laravel + PHP)

> **Enterprise-grade, security-hardened Laravel 11 starter skeleton** adhering to the **Spec-First** and **Banking-Grade Zero Trust IAM** doctrines.

---

## 🛡️ Built-in Security Controls

| Pillar | Implementation | Technical Detail |
|---|---|---|
| **Auth + Token Rotation (RTR)** | Refresh Token Rotation (7d) | Refresh token transmitted via `HttpOnly; Secure; SameSite=Strict` cookie (`/api/auth`). Replay of a revoked token triggers instant revocation of the entire token family. |
| **Brute-Force & Lockout** | 5 failed attempts → 15-min lockout | Rejects brute-force attempts with `423 ACCOUNT_LOCKED` before executing expensive password verification. Admin manual unlock endpoint included. |
| **JML Session Kill-Switch** | Instant session termination on status update | Moving user status to `suspended` or `terminated` revokes all active refresh tokens in a single scoped update. |
| **Maker-Checker / Dual Control** | Four-Eyes Principle | Maker cannot approve their own change request (`403 Forbidden`). Enforced both at controller level and database check constraint (`maker_user_id <> checker_user_id`). |
| **Append-Only Audit Trail** | Immutable audit logs | All mutations log immutable audit records into `audit_logs` table (user ID hash, actor role, IP hash, payload details). |
| **Security Headers & CORS** | `SecurityHeadersMiddleware` | Enforces HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, and Referrer-Policy. |

---

## 🧰 Tech Stack
- **Framework:** Laravel 11 (PHP 8.2 / 8.3 / 8.5)
- **Database:** PostgreSQL 16 (or in-memory SQLite for instant tests)
- **Web Server:** Nginx Alpine reverse proxy + PHP-FPM
- **Testing:** PHPUnit / Pest (10 automated unit & feature tests passing)
- **Containerization:** Docker Compose

---

## 🚀 Quick Start

```bash
# 1. Setup environment
cp backend/.env.example backend/.env

# 2. Start full stack in Docker (Postgres, Redis, PHP-FPM, Nginx, Mailpit)
make first-run

# 3. Run test suite
make test
```

Endpoints:
- API Server: `http://localhost:8000/api`
- Liveness Probe: `GET /api/health/live`
- Readiness Probe: `GET /api/health/ready`
- Mailpit Web UI: `http://localhost:8025`
