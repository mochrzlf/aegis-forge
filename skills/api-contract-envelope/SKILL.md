---
name: api-contract-envelope
description: Enforces the aegis-forge standardized REST API response envelope on every endpoint. Use whenever writing, reviewing, or refactoring controllers, routes, handlers, serializers, or OpenAPI specs — in NestJS, FastAPI, Express, or any REST backend.
---

# API Contract Envelope Guardian

Every REST endpoint in an aegis-forge project MUST return the standardized
payload envelope — 100% compliance required, no exceptions. Source of truth:
`AGENTS.md` §3.1 and `docs/openapi.yaml` (the contract; this skill summarizes
the formatting rule).

## Mandatory Success Envelope

```json
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "per_page": 20, "total": 100 }
}
```

- `data` — the payload object (or array for collections).
- `meta` — **required on every list/collection endpoint** with `page`,
  `per_page`, `total`. Omit only for single-resource responses.

## Mandatory Error Envelope

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "User-friendly error message",
    "details": {}
  }
}
```

- `code` — MUST be one of the fixed set:
  `UNAUTHORIZED` | `FORBIDDEN` | `VALIDATION_ERROR` | `NOT_FOUND` | `INTERNAL_ERROR`
- `message` — human-readable, safe to display (never a stack trace).
- `details` — structured field errors when applicable (e.g.
  `{ "email": ["invalid format"] }`).

## HTTP Status ↔ Code Mapping

| HTTP | error.code |
|---|---|
| 400 / 422 | `VALIDATION_ERROR` |
| 401 | `UNAUTHORIZED` |
| 403 | `FORBIDDEN` |
| 404 | `NOT_FOUND` |
| 5xx | `INTERNAL_ERROR` |

## Rules for Agents

1. **Never** return bare payloads: `return user`, `return { status: "ok" }`,
   `return res.json(items)` are violations.
2. **Never** invent new error codes — extend `details`, not the code set.
3. List endpoints MUST include `meta` pagination even when results are empty
   (`total: 0`).
4. The `docs/openapi.yaml` contract defines these schemas — generated code,
   mock servers (Prism), and tests all assume them. Deviating breaks the mock
   server and the mobile/frontend clients that consume the contract.
5. Exceptions/unhandled errors must be funneled through a global error filter
   that emits the error envelope — never leak framework default HTML/stack
   pages.

## When Reviewing Code — Flag These Violations

- Mixed response shapes across endpoints (some enveloped, some raw)
- `res.status(200).json({ error: "..." })` — errors reported with 2xx status
- Paginated endpoints missing `meta.total`
- Error `message` containing SQL errors, stack traces, or internal paths
- Client-specific formats leaking in (`{ data: { attributes: ... } }` JSON:API
  style alongside the standard envelope)
