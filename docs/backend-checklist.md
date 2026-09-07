# Backend Quality Assurance (QA) Checklist

> **Scope:** The backend/service-side counterpart to `docs/frontend-checklist.md`. Every API/service built from this baseline must satisfy these before release. Mark ✅ / ❌ / N/A and record evidence.
>
> Companion docs: `docs/openapi.yaml`, `docs/schema.sql`, `docs/observability.md`, `docs/migrations.md`, `docs/security/web-security-checklist.md`.

---

## 1. API Contract Compliance
- [ ] Every endpoint matches `docs/openapi.yaml` **exactly** (paths, methods, request/response schemas).
- [ ] Standard envelope on all responses: success `{ "success": true, "data", "meta"? }`; error `{ "success": false, "error": { "code", "message" } }`.
- [ ] List endpoints paginate via `meta { page, per_page, total }`.
- [ ] Correct HTTP semantics: verbs, status codes (`200/201/204`, `400/401/403/404/409/422/429/500`), and idempotency where applicable.
- [ ] API versioned (`/api/v1/...`) or version strategy documented; no silent breaking changes.

## 2. Data Layer & Integrity
- [ ] Schema matches `docs/schema.sql`; constraints (FK, UNIQUE, CHECK, NOT NULL) enforced at the DB, not only in app code.
- [ ] Indexes exist for foreign keys and hot query paths; no N+1 queries on list endpoints.
- [ ] **All queries parameterized** — no string-concatenated SQL (see web-security-checklist §3).
- [ ] Migrations are versioned, reversible, and applied via tooling — never hand-edited prod DB (see `docs/migrations.md`).
- [ ] Audit columns (`created_at`, `updated_at`) present; sensitive tables have an append-only audit trail.

## 3. Authentication & Authorization
- [ ] AuthN via HttpOnly cookie session / verified JWT per `docs/adr/ADR-002-auth-token-strategy.md`.
- [ ] **Server-side authorization on every protected route** (RBAC per `docs/security-access-matrix.md`); object-level (IDOR) checks.
- [ ] Privileged actions enforce Maker-Checker where required.
- [ ] Token validation checks signature, expiry, issuer/audience; rejects `alg=none`.

## 4. Validation, Errors & Rate Limiting
- [ ] Input validated at the boundary (schema/DTO validation) — type, length, format, allow-lists.
- [ ] Errors are consistent, machine-readable, and leak **no** internals (no stack trace / SQL / paths).
- [ ] Rate limiting on public + auth endpoints (login stricter); `429` with `Retry-After`.
- [ ] Request size limits + timeouts configured (slow-loris / large-payload defense).

## 5. Performance & Reliability
- [ ] Health/readiness endpoints (`/healthz`, `/readyz`) for orchestration.
- [ ] DB connection pooling configured (`DATABASE_POOL_MIN/MAX`); no unbounded connections.
- [ ] Blocking/expensive work offloaded to a queue (Redis Streams / BullMQ) — not on the request path.
- [ ] Graceful shutdown (drain connections, finish in-flight requests).
- [ ] Caching strategy (Redis) for hot read paths with sane TTLs; cache-invalidation documented.

## 6. Observability (see `docs/observability.md`)
- [ ] **Structured logs** (JSON) with correlation/request IDs propagated across calls.
- [ ] **No PII / credentials / tokens in logs** — redaction applied.
- [ ] Metrics exposed (RED: Rate, Errors, Duration) for each endpoint.
- [ ] Tracing/instrumentation hooks present (OpenTelemetry) for cross-service flows.

## 7. Security & Secrets
- [ ] Security headers set (CSP, nosniff, frame-ancestors, Referrer/Permissions-Policy).
- [ ] CORS restrictive (explicit origins; not `*` with credentials).
- [ ] Secrets from env/secret manager — never hardcoded; Gitleaks clean.
- [ ] Field-level encryption (AES-256-GCM) for sensitive columns.
- [ ] Dependencies pass `dependency-review` (no new HIGH+ vulns); Trivy FS scan clean.

## 8. Testing & Ops
- [ ] Unit tests for business logic; integration tests for endpoints (against real DB/test container).
- [ ] Contract test against `docs/openapi.yaml` (e.g., Schemathesis) passes.
- [ ] Test coverage on auth, authorization, and payment/risk paths specifically (not just happy path).
- [ ] Runbook entry exists for the service (deploy, rollback, on-call).

---

## Sign-off

| Role | Name | Date | Result |
|---|---|---|---|
| Backend Lead | | | ☐ Pass ☐ Fail |
| Security Lead | | | ☐ Pass ☐ Fail |

> Any **❌** on *Contract Compliance*, *AuthZ*, *Injection*, or *Secrets* is a **release blocker**.
