# ADR-006: Maker-Checker (Four-Eyes) Approval Workflow

**Status:** Accepted — implemented in `templates/web-app`
**Date:** 2026-09-22
**Gap item:** `docs/gap-analysis.md` 1.4
**Supersedes / extends:** ADR-005 §4, which named `PUT /users/{id}/status` as the
natural first consumer of this mechanism

---

## 1. Context

`AGENTS.md` §3.2.1 requires the four-eyes principle for critical actions: the
person who *requests* a privileged change must not be the person who *executes*
it. `docs/security-access-matrix.md` §4.B additionally requires that a role
change on approval "forcefully terminate previous sessions" to prevent privilege
creep — a user promoted to `admin` must not keep using a token minted while they
were a `member`.

The `approval_requests` table was described in `docs/schema.sql` §2 and referenced
by `security-access-matrix.md` §6, but it did not exist in the runnable skeleton.
`alembic/versions/0001_init.py` created only `users`, `refresh_tokens`, and
`audit_logs`. The gap-analysis row 1.4 called this out: a security-control
document that cites a table the application never creates is a documentation
claim with no implementation behind it.

---

## 2. Decision

Introduce the table and a first consumer — **role promotion** — with the
maker/checker separation enforced at **three** independent layers, so that no
single defect lets one person both request and execute a change.

### 2.1 Data layer

New migration `alembic/versions/0002_approval_requests.py`:

```sql
CHECK (maker_user_id <> checker_user_id)   -- chk_maker_checker_different
CHECK (status IN ('pending', 'approved', 'rejected'))
```

The CHECK constraint is deliberately the last line of defence. The service checks
first and returns a clean `403 FORBIDDEN`, but if any future caller bypasses the
service, or a hand-written SQL path is added, the database itself rejects the
self-approval. `checker_user_id` is nullable and `NULL <> NULL` is not `TRUE`, so
the constraint permits a freshly created request that has no checker yet.

A partial index on `(status, expires_at)` supports the pending queue lookup, and
`maker_user_id` is indexed for the "requests I filed" query.

### 2.2 Service layer

`app/services/approval_service.py`:

- `request_role_change()` — the maker proposes a change; nothing is applied. The
  request is created `pending` with a 72-hour expiry.
- `decide_role_change()` — a checker approves or rejects. On approval the role
  change and the session revocation run in the **same transaction** as the status
  flip, so an approved request can never be recorded without its effect taking
  hold (or vice versa).

Two service-level guards exist independently of the constraint:

1. **Self-targeting is refused outright.** `maker_user_id == target_user_id`
   returns `VALIDATION_ERROR`. A second approver would still be required, so this
   is not a four-eyes bypass — but recording your own promotion request as a
   legitimate workflow is a conflict of interest the skeleton refuses to model.
2. **One pending request per target + action.** A second open approval for the
   same promotion returns `CONFLICT`. Two pending requests race; whichever checker
   acts second would find the role already changed and either double-apply or
   confuse the audit trail.


### 2.3 Session revocation on approval

Reuses `revoke_all_refresh_tokens()` from ADR-005's kill-switch work. The
privilege-creep guard required by `security-access-matrix.md` §4.B.2 is therefore
the same tested predicate, applied to a different trigger.

### 2.4 API layer

`app/api/approvals.py` — all routes admin-only via the existing `require_roles`
guard:

| Method | Path | Role |
|---|---|---|
| `POST` | `/api/v1/approvals/role-change` | Maker: propose a promotion |
| `POST` | `/api/v1/approvals/{id}/approve` | Checker: apply it |
| `POST` | `/api/v1/approvals/{id}/reject` | Checker: refuse it |
| `GET` | `/api/v1/approvals` | List the pending queue |

### 2.5 Expiry handling

A pending request older than 72 hours is not silently honoured. Attempting to
decide one auto-closes it as `rejected` with the reason `Expired with no
decision`, audits `approval.expired`, and returns `VALIDATION_ERROR`. Closing the
row rather than deleting it keeps the history — an auditor can see that a request
was filed and never acted on.

---

## 3. Consequences

**Positive.** The four-eyes requirement is now a runnable guarantee rather than a
documented intention. The audit chain is complete per request:
`approval.requested` → `approval.approved` / `approval.rejected` /
`approval.expired`, each carrying the maker and checker IDs. The privilege-creep
guard means a promoted user is forced to re-authenticate under their new role.

**Negative / trade-offs.** A single-admin deployment cannot complete a promotion:
the maker and checker must be different accounts. That is the intended control,
but it does change the operational shape of the smallest possible deployment. The
duplicate-request guard means a rejected promotion requires a *new* request
rather than re-opening the old one — deliberate, since re-opening would let a
checker's earlier refusal be reversed without a fresh maker request.

**Envelope extension.** `CONFLICT` (`409`) is added to `app/core/envelope.py` for
the duplicate-pending and already-decided cases. As with `RATE_LIMITED` and
`LOCKED` from ADR-003/004, this is a skeleton-local extension of the baseline
envelope, documented here rather than silently added. Callers can now distinguish
"the state machine refused you" from "your input was malformed".

---

## 4. STRIDE Threat Model

| Threat | Vector | Mitigation in this change |
|---|---|---|
| **S**poofing | Attacker forges a checker identity | Checker must hold a valid admin access token (`require_roles`); `checker_user_id` is taken from the token subject, never from the request body |
| **T**ampering | Attacker alters a pending request's payload | `payload` is written once at creation and never updated; `audit_logs` is append-only by trigger (`0001_init.py`); role mutation happens only inside `decide_role_change` on a row fetched by ID |
| **R**epudiation | Maker or checker denies acting | Every transition writes `audit_logs` with the acting user's ID (`actor_user_id`), the `approval:{id}` resource, and the before/after role in `detail` |
| **I**nformation disclosure | Non-admin reads the approval queue | All four endpoints are admin-only; the response never returns passwords, hashes, or PII beyond the target's user ID, which the caller (an admin) can already see |
| **D**enial of service | Flood of approval requests | Rate limiting from ADR-003 applies to all routes through the same `/auth`-style guard pattern; the duplicate-request guard bounds pending rows per target to one |
| **E**levation of privilege | **The core threat** — one person promotes themselves | Three layers: service refuses self-target and self-check; `require_roles("admin")` gates every endpoint; DB `CHECK (maker_user_id <> checker_user_id)` rejects the write itself. A compromised admin token alone cannot complete a promotion |

---

## 5. Verification

Runnable self-check — `templates/web-app/backend/tests/check_approvals.py`
(in-memory SQLite, exercising the real service logic and UPDATE predicates, no
mocking of the decision path):

1. A request for another user is created `pending`
2. Self-targeting refused
3. Duplicate pending request refused
4. Maker-as-checker refused
5. Checker approval applies the role **and** revokes both live sessions
6. A second decision on the same request refused, not re-applied
7. An expired request is auto-closed, not applied
8. Rejection records its reason and leaves the role untouched
9. The audit chain contains all four `approval.*` actions

All pass. Not covered offline: the PostgreSQL CHECK constraint itself (SQLite
enforces CHECK constraints too, but the production constraint is the one that
matters) and the real Redis-backed rate limiter in front of these endpoints.
Docker is unavailable in this environment; both remain pending the compose smoke
test named in ADR-003 §5.
