# ADR-005: JML Kill-Switch — Account Status Suspends All Live Sessions

## Architecture Decision Record

| | |
|---|---|
| **ID** | ADR-005 |
| **Title** | JML Kill-Switch: account status change suspends all live sessions |
| **Status** | **ACCEPTED** |
| **Date** | 2026-09-21 |
| **Decided by** | Security Lead / Architecture |
| **Impacts** | User lifecycle, admin endpoints, session revocation, audit trail |

---

## 1. Context & Problem Statement

`User.status` exists in the schema (`active` / `suspended` / `terminated`) but the
skeleton never acted on it: a suspended user could keep refreshing tokens and keep
calling protected routes indefinitely, because nothing connected the status column to
session state.

`AGENTS.md` §3.2.1 (the Joiner-Mover-Leaver rule) is explicit: moving a user to
`suspended` or `terminated` must *immediately* revoke all active tokens and sessions.
In workforce terms, this is the day-one and day-last control — an account that has left
the organisation, or is suspected of compromise, must lose access at once, not at the
next token expiry. The gap analysis (item 1.3) calls this the signature capability of
the IAM background; leaving it unwired makes the doctrine untrustworthy.

## 2. Alternatives Considered

* **Option A — Revoke lazily at request time by checking `User.status` in the auth
  dependency:** Adds a database read to every authenticated call. **Rejected**: it taxes
  every request for an event that is rare, and a stateless access token still cannot be
  recalled this way without that lookup.
* **Option B — Blocklist of revoked access-token IDs in Redis:** Strongest possible
  revocation (access tokens too, not just refresh tokens). **Rejected for now**: it makes
  every authenticated request depend on cache availability and reintroduces a stateful
  check the stateless JWT was chosen to avoid. Tracked in §4 as the upgrade path.
* **Option C — Eager revocation of live refresh tokens at the moment of suspension:**
  One UPDATE scoped to the user, executed exactly when the status changes. **Chosen**:
  immediate effect for sessions, no per-request cost, and it composes with the existing
  RTR machinery (revoked tokens are already rejected and, on replay, cascade-revoke).

## 3. Decision

Adopt **Option C**, formalised as follows.

**Trigger** — `PUT /api/v1/users/{user_id}/status`, admin-only via `require_roles("admin")`.
The body accepts `active` / `suspended` / `terminated` plus an optional human `reason`
(bounded to 256 characters, so the audit record stays readable and cannot be abused as
an unbounded text dump).

**Effect** — a transition into `suspended` or `terminated` executes
`revoke_all_refresh_tokens(user_id)`: a single bulk UPDATE setting `revoked_at = now()`
on every refresh token of that user that is not already revoked. Every further `/refresh`
with one of those tokens fails; because the RTR path treats a revoked token as replay,
any attempt also cascade-revokes whatever sessions remained. The transition is also
combined with clearing any login lockout (ADR-004), so a suspended account is not left
with a lock artefact that could confuse a later reactivation.

**Blast radius** — the UPDATE is scoped by `user_id` *and* `revoked_at IS NULL` in the
WHERE clause, so it can never touch another user's tokens, and re-running it is a no-op
(verified in `tests/check_killswitch.py`, including the cross-user isolation case).

**Guard** — an admin may not suspend or terminate their own account. Without this, one
mis-click can remove the only administrative access in the system, and there is no other
admin to restore it. The request fails with `422 VALIDATION_ERROR` and a message that
says so plainly, rather than a generic error.

**Audit** — every transition writes `audit_logs` with `action =
user.status.<previous>_to_<new>`, the actor, the resource, and either the admin's reason
or an auto-generated statement of the transition. The log row is written in the same
transaction as the status change and the revocation, so the audit record and the effect
cannot diverge.

**No schema migration** — `User.status`, `RefreshToken.revoked_at`, and `audit_logs`
already exist from `0001_init`; the kill-switch wires existing columns together. This is
why the item is cheap now: the data model was right, only the behaviour was missing.

## 4. Consequences

* **Positive:** suspension takes effect within one request for all sessions; no
  per-request cost; idempotent; self-service lockout recovery is blocked for admins; the
  whole transition is one audited transaction.
* **Limitation — access tokens remain valid until expiry (≤15 minutes):** a stateless JWT
  cannot be recalled without a blocklist; the access token is short-lived by design
  (ADR-002). The session cannot be extended, so exposure is bounded and closes fast.
  Option B above is the upgrade path when that bound is too loose for a deployment.
* **Limitation — single-admin self-service:** the self-suspend guard prevents the obvious
  footgun but is not Maker-Checker; dual control for status changes arrives with the
  `approval_requests` mechanism in gap item 1.4, and this endpoint is the natural first
  consumer of it.
* **Operational:** reactivating a user (`suspended` → `active`) restores the ability to
  log in but does not re-issue any token — sessions were revoked, not paused. A
  reactivated user must authenticate again. That is deliberate: a restored account
---

## 5. Security Threat Modeling (STRIDE)

| Threat | Description | Mitigation Strategy |
|---|---|---|
| **S**poofing | Non-admin suspends a user to cause a denial of service, or spoofs an admin identity | `require_roles("admin")` is enforced server-side on every call; no client-supplied role is trusted |
| **T**ampering | Attacker edits another user's status, or widens the revocation to other users | Endpoint is admin-only; the revocation UPDATE is scoped `WHERE user_id = :id AND revoked_at IS NULL` — the ownership predicate at the data layer, so it cannot cross users; isolation is covered by `tests/check_killswitch.py` |
| **R**epudiation | "Nobody suspended me" / "I did not approve this suspension" | Every transition writes `audit_logs` in the same transaction, naming the actor, the from/to states, and the reason; the table is append-only by trigger, so it cannot be rewritten |
| **I**nformation Disclosure | The `reason` field leaks other users' data, or status responses leak account existence | `reason` is bounded to 256 characters; the endpoint returns 404 for unknown users (existence is not disclosed); audit text records the transition, not credentials or PII |
| **D**enial of Service | An attacker suspends admins to lock out administration | Self-suspension is explicitly rejected with 422; the guard is documented in ADR-005 §3 so reviewers can audit it |
| **E**levation of Privilege | A member escalates to admin, or a terminated account keeps calling protected routes | Role is read from the verified access token, not the request; refresh tokens of the terminated user are revoked at the moment of termination, so the session cannot be extended past the current access token's 15-minute life |

---

## 6. References

- `AGENTS.md` §3.2.1 (JML kill-switch) · `docs/security-iam-policy.md`
- `docs/gap-analysis.md` Gelombang 1 item 1.3 (this), 1.2 (lockout — different mechanism)
- `docs/adr/ADR-002-auth-token-strategy.md` (short-lived access tokens, RTR)
- `docs/adr/ADR-004-account-lockout.md` (transient lock; deliberately not `User.status`)
- `templates/web-app/backend/app/repositories/__init__.py` (`revoke_all_refresh_tokens`)
- `templates/web-app/backend/app/api/users.py` (`PUT /users/{id}/status`)
- `templates/web-app/backend/tests/check_killswitch.py` (runnable self-check)
- OWASP / NIST SP 800-53 AC-2 (Account Management) — session termination on status change

  should not silently inherit sessions that were revoked for cause.
