# Observability Standard

> **Purpose:** Define how services built from this baseline produce logs, metrics, and traces — with **anti-PII** logging and tamper-evident audit trails as first-class requirements. Follows [OpenTelemetry](https://opentelemetry.io) semantic conventions (referenced, not vendored).
>
> The four pillars from `AGENTS.md`: *"structured anti-PII logging, and tamper-proof audit trails."* This document makes that concrete.

---

## 1. The Three Signals + Audit

| Signal | Purpose | Tooling (per stack) |
|---|---|---|
| **Logs** | Discrete events; debugging & security forensics | JSON logger (pino / winston / structlog / logback) |
| **Metrics** | Aggregated trends; alerting | Prometheus-style RED metrics |
| **Traces** | Request flow across services | OpenTelemetry SDK + collector |
| **Audit Trail** | Who did what, when — compliance & SoD | Append-only DB table + immutable sink |

---

## 2. Structured Logging (JSON)

### 2.1 Required fields on every log line
```json
{
  "ts": "2026-09-07T10:15:30.123Z",
  "level": "info",
  "service": "auth-api",
  "env": "production",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "request_id": "req_01J...",
  "msg": "user login",
  "user_id": "u_123",
  "outcome": "success",
  "duration_ms": 42
}
```
- `trace_id` / `span_id` come from OpenTelemetry context; `request_id` is generated per inbound request and propagated to downstream calls (header `X-Request-ID`).
- Log levels used consistently: `debug` (dev only), `info`, `warn`, `error`. No `info`-level secrets.

### 2.2 Anti-PII & Redaction (MANDATORY)
- **Never log:** passwords, tokens (access/refresh/API keys), full card numbers, national IDs, session cookies, `ENCRYPTION_MASTER_KEY`, DB connection strings.
- **Redact by default:** email → `u***@domain.com`; phone → `+62****123`; IP → truncate last octet where feasible.
- Implement a **denylist redactor** (field names: `password`, `token`, `secret`, `authorization`, `cookie`, `api_key`, `ssn`, `card`) applied at the logger, not ad-hoc.
- Sampling/`debug` logging that could capture payloads must be **off in production**.

### 2.3 Security events that MUST be logged
Login success/failure, account lockout, password reset, privilege/role change, authorization failures (403), token reuse detection, circuit-breaker triggers (trading), Maker-Checker approvals/rejections.

---

## 3. Metrics (RED per endpoint)

Expose for **every** HTTP endpoint and background job:
- **Rate** — requests/sec (`http_requests_total{route,method,status}`).
- **Errors** — error ratio (`5xx`/`4xx` counts; separate them).
- **Duration** — latency histogram (`http_request_duration_seconds` p50/p95/p99).

Plus service-level: DB pool usage, queue depth/lag, cache hit ratio, circuit-breaker state (trading).

### Example alert rules (starting point)
| Alert | Condition | Severity |
|---|---|---|
| HighErrorRate | `5xx ratio > 2%` for 5m | SEV-2 |
| LatencyP99 | `p99 > 1s` for 10m on critical route | SEV-3 |
| AuthBruteForce | `login failures > 20/min` per account/IP | SEV-2 |
| TradingCircuitBreaker | state = TRIGGERED | SEV-1 |

---

## 4. Tracing (OpenTelemetry)

- Instrument inbound HTTP, outbound HTTP, DB calls, and queue publish/consume.
- Propagate context via W3C `traceparent` headers so a request is traceable across services.
- Use OpenTelemetry **semantic conventions** for attribute names (`http.method`, `http.route`, `db.system`, `db.statement` — but see redaction: **do not** record raw SQL with parameter values).
- Sample: 100% in dev, tail- or ratio-based (e.g., 10–25%) in prod with errors always kept.

---

## 5. Audit Trail (Tamper-Evident)

For sensitive operations (privileged actions, financial transactions, role changes, approvals):
- **Append-only table** — `INSERT`-only; no `UPDATE`/`DELETE` granted to the app role.
- **Chained integrity:** each row stores `prev_hash` = hash of previous row + `entry_hash` = hash(canonical row + prev_hash) → tampering breaks the chain and is detectable.
- Record: `actor_id`, `action`, `entity_type`, `entity_id`, `before`/`after` (JSON), `ip`, `user_agent`, `created_at`, `trace_id`.
- Periodically ship to an immutable sink (object-lock/WORM storage) for long-term retention.

---

## 6. Correlation & Request Flow

1. Edge generates/accepts `X-Request-ID`; create OTel span → `trace_id`.
2. Propagate `traceparent` + `X-Request-ID` to all downstream calls (HTTP, queue messages).
3. All logs/metrics/traces for that request share the same `trace_id` → one query reconstructs the full journey.

---

## 7. Minimal Setup Checklist

- [ ] JSON logger with request-id + trace context middleware installed.
- [ ] PII/secret **redactor** active and unit-tested (feed it a fake token, assert it is masked).
- [ ] RED metrics exposed at `/metrics` (or via OTLP).
- [ ] OTel tracing wired for HTTP + DB with context propagation.
- [ ] Audit table is `INSERT`-only with hash chaining; app role lacks `UPDATE/DELETE`.
- [ ] At least the 4 example alert rules configured.
- [ ] Verified: **no** password/token appears in any log line (manual spot-check + test).

> Treat "a secret appeared in logs" as a security incident → rotate per `docs/security/secrets-rotation.md` and review `docs/security/incident-response.md`.
