---
name: rbac-enforcement
description: Enforces aegis-forge server-side authorization — RBAC per access matrix, IDOR/BOLA prevention, maker-checker for critical actions, JML kill-switch, and immutable audit trails. Use whenever writing or reviewing any endpoint, service, or query that touches protected resources, roles, or privileged operations.
---

# RBAC Enforcement Guardian

Broken Access Control is OWASP #1 — and invisible until exploited. Every data
mutation in an aegis-forge project MUST pass server-side authorization.
Source of truth: `AGENTS.md` §3.2, `docs/security-access-matrix.md`
(entitlement matrix + Segregation of Duties), `docs/security-iam-policy.md`.

## Non-Negotiable Rules

### 1. Server-Side Role Checks — Always
- Every protected endpoint verifies the caller's role **on the server**
  against the access matrix. Hiding buttons in the UI is NOT authorization.
- Deny by default: no role match → `403 FORBIDDEN` (standard error envelope).

### 2. IDOR / BOLA Prevention
- Every data modification query MUST verify resource ownership:
  `WHERE id = :id AND user_id = :currentUserId`.
- Never trust client-supplied user/tenant IDs — always derive identity from
  the authenticated session/token.

### 3. Maker-Checker (Four-Eyes) for Critical Actions
- Role promotion, fund withdrawals, limit adjustments, and trading-parameter
  execution require a distinct approver: `maker_user_id <> checker_user_id`
  enforced **in the database/service layer**, not by convention.
- Self-approval must be impossible — this mirrors the repo's own branch
  protection (authors cannot approve their own PRs).

### 4. JML Kill-Switch (Joiner-Mover-Leaver)
- Setting a user's status to `terminated` or `suspended` MUST immediately
  revoke all active tokens and sessions — same transaction or guaranteed
  immediate cascade, never a delayed batch job.

### 5. Immutable Audit Trail
- All data mutations log to `audit_logs` (actor, action, resource, timestamp,
  before/after). The table is protected by anti-tamper triggers:
  **UPDATE and DELETE are strictly prohibited.**
- ❌ Never log PII, passwords, card numbers, or account balances.

## When Reviewing Code — Flag These Violations

- Role checks only in frontend code (`if (user.role === 'admin')` in React)
- Queries by ID without an ownership predicate (`findById(req.params.id)`
  then mutate)
- Approver fields that accept the maker's own ID
- Session/token rows still active after user suspension
- Audit writes that are updateable/deletable, or missing for a mutation path
- Mass-assignment of role/permission fields from request bodies
  (`User.update(req.body)` with `role` inside)

## Reference: Standard Error Responses

Authorization failures use the standard envelope (`api-contract-envelope`):
`401 UNAUTHORIZED` (no/expired session), `403 FORBIDDEN` (insufficient role
or not the resource owner) — never disclose whether the resource exists for
non-owners when the matrix requires concealment.
