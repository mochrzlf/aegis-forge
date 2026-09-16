# Aegis Forge — Web App Starter Skeleton (FastAPI + Postgres + Redis)

> **Runnable starter template** (`templates/web-app/`). Copy this folder into a
> new project (or wire it into `init-new-project`) and the four AGENTS.md
> pillars are already satisfied from commit zero: Specification-First,
> Secure-by-Design, Risk Management, Observability.
>
> **Verification status:** ✅ runtime-verified 2026-09-16 (`docker compose up`
> + smoke test: register → login → anti-IDOR 404 → RBAC 403 → RTR rotation →
> replay-detection revokes all sessions → append-only audit trigger blocks
> UPDATE/DELETE). See "Smoke test" below.

## What is pre-wired (the non-negotiables, already implemented)

| Pillar | Implementation | Where |
|---|---|---|
| **Auth + RTR** | Access token (15 min) + Refresh Token Rotation; refresh token ONLY in `HttpOnly; Secure; SameSite=Strict` cookie (never JSON body); reuse/replay → revoke descendant sessions + audit incident | `backend/app/api/auth.py`, `backend/app/core/security.py`, `backend/app/services/auth_service.py` |
| **RBAC / anti-IDOR** | Server-side role check dependency + ownership predicate on every mutation | `backend/app/core/deps.py`, `backend/app/repositories/__init__.py` |
| **Audit trail** | Append-only `audit_logs` (DB trigger blocks UPDATE/DELETE) written on every mutation | `backend/app/models/__init__.py`, `backend/app/services/audit_service.py`, `backend/alembic/versions/0001_init.py` |
| **Secrets** | All config from env (pydantic-settings); nothing hardcoded | `backend/app/core/config.py`, `.env.example` |
| **API envelope** | `{success, data, meta}` / `{success, error:{code,message}}` on every response | `backend/app/core/envelope.py` |
| **Token economy** | Code is minimal, layered; agents extend by editing, not regenerating | throughout |
| **Observability** | Structured JSON logs, no PII; `/healthz` + `/readyz` | `backend/app/core/logging.py`, `backend/app/api/health.py` |

## Stack
- **FastAPI** (Python 3.11+) — async API
- **PostgreSQL 16** — SQLAlchemy 2.0 async + Alembic migrations
- **Redis 7** — session/refresh-token store + rate limiter
- **Docker Compose** — api + db + cache, one command up
- **CI (GitHub Actions)** — gitleaks, semgrep, trivy, redocly (mirrors baseline)

## Layout
```
web-app/
├── docker-compose.yml
├── .env.example
├── README.md                 ← this file
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/env.py
│   ├── alembic/versions/0001_init.py
│   └── app/
│       ├── main.py
│       ├── core/        (config, security, envelope, deps, logging)
│       ├── models/      (user, refresh_token, audit_log)
│       ├── schemas/     (pydantic DTOs)
│       ├── repositories/(data access + ownership predicates)
│       ├── services/    (auth_service, audit_service)
│       └── api/         (auth, users, health routers)
└── .github/workflows/security.yml
```

## Quick start
```bash
cp .env.example .env          # fill POSTGRES_PASSWORD + JWT_SECRET
docker compose up --build
# API: http://localhost:8000  | docs: http://localhost:8000/docs
```

### Makefile (cross-platform task runner)
```bash
make first-run   # copy .env (if missing) + build + up + migrate — idempotent
make dev         # start db + cache + api
make audit       # gitleaks + semgrep + trivy (needs those tools installed)
make check       # audit + tests — gate before opening a PR
make down        # stop;  make clean  # stop + delete volumes
```
(On Windows without `make`, run the equivalent `docker compose` commands —
see each recipe.)

### Smoke test (after `up`) — verified 2026-09-16
```bash
# register (sets refresh cookie) -> login -> access a protected route
curl -X POST localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.co","password":"a-very-long-password"}' -c jar
# use the returned access_token for:
curl localhost:8000/api/v1/users/me -H "Authorization: Bearer <access_token>"
# refresh rotates the token (cookie -> cookie)
curl -X POST localhost:8000/api/v1/auth/refresh -b jar -c jar
# reuse the OLD refresh token -> 401 + ALL sessions revoked (RTR replay defense)
```

> **Verified:** `docker compose up` + the flow above passed end-to-end —
> including anti-IDOR (404), RBAC (403), RTR rotation, replay-detection
> (revokes all user sessions), and the append-only `audit_logs` trigger
> (UPDATE/DELETE → `ERROR: audit_logs is append-only`).

## How to extend (token-economy rule)
1. Add a PRD via the `prd-interviewer` skill → `docs/PRD.md`.
2. Break it into tasks via `spec-to-tasks` → `docs/TASKS.md`.
3. Each task = **edit existing files / add one module**, never regenerate the
   scaffold. Security ACs (RTR, anti-IDOR, audit) are already wired — do NOT
   weaken them; extend the pattern in `app/api/users.py` for new resources.

## Out of scope (deliberately)
- No frontend (backend-only per decision).
- No example CRUD feature beyond auth + a minimal protected `users` resource
  (to demonstrate anti-IDOR). Add features via TASKS.md.
- No OAuth/social login — email+password only in this skeleton (see ADR-002).
