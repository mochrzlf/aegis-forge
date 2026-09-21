# ADR-004: Temporary Account Lockout After Failed Logins

## Architecture Decision Record

| | |
|---|---|
| **ID** | ADR-004 |
| **Title** | Temporary Account Lockout After Failed Logins |
| **Status** | **ACCEPTED** |
| **Date** | 2026-09-21 |
| **Decided by** | Security Lead / Architecture |
| **Impacts** | Backend login flow, admin user-management endpoint, Redis cache layer, audit trail |

---

## 1. Context & Problem Statement

`ADR-003` bounds request *volume* per identifier. It does not, by itself, stop a
patient attacker who stays under the volume limit and guesses passwords over hours.

The doctrine layer (`AGENTS.md` §3.2, `docs/security-iam-policy.md`) expects repeated
failed authentication to disable the account temporarily. Without it, the only cost of
guessing is time, and an account with a weak password is eventually taken. The gap
analysis (item 1.2) records this control as missing.

## 2. Alternatives Considered

* **Option A — Lock by mutating `User.status` to `suspended`:** Persistent and visible in
  the database. **Rejected for the automatic case**: a transient lockout (wrong password
  5 times) must self-heal without an admin. It also collides with the JML kill-switch
  (gap item 1.3), which uses `suspended` as a *deliberate, durable* state and must not be
  conflated with a self-clearing nuisance lock.
* **Option B — A `login_failures` table with a cleanup job:** Durable, queryable, and
  heavier: a new migration, a new model, and a scheduled reaper for expired locks.
  **Rejected**: the failure-tracking horizon is minutes, so durability buys nothing and
  the reaper is a new failure mode.
* **Option C — Redis failure counter + self-expiring lock key:** No migration, no reaper,
  no new dependency; a lock clears itself when its TTL elapses. **Chosen.**

## 3. Decision

Adopt **Option C**, formalised as follows.

**State** — two Redis keys per account email: `fails:<email>` (INCR counter) and
`lock:<email>` (presence key with TTL). Emails are normalised to lowercase before use.

**Failure accounting** — only a genuine credential failure (`AuthError("UNAUTHORIZED")`)
increments the counter. A non-active account (FORBIDDEN), a malformed request, or a
locked response must not — penalising those would let an attacker lock *other* users out
by probing their status. A failure increments the counter and, when the counter reaches
the threshold, sets the lock with `NX` (set-once) so the audit event fires exactly once.

**Window semantics** — the counter gets its TTL on the *first* increment only. Each
subsequent failure does not refresh it, so an attacker cannot avoid the threshold by
spacing attempts just inside a rolling window; N failures inside any 900-second span
still locks the account.

**Defaults** (`backend/app/core/config.py`, environment-overridable):

| Setting | Default | Meaning |
|---|---|---|
| `LOCKOUT_MAX_FAILURES` | 5 | Failed logins before the account locks |
| `LOCKOUT_SECONDS` | 900 | Lock duration, also the failure-tracking horizon (15 minutes) |

**Response** — a locked account is refused with `423 Locked` and envelope code `LOCKED`
before any password is hashed or compared, so the Argon2 cost is not spent on an account
that cannot succeed. `LOCKED` is a skeleton-local extension of the baseline envelope code
set, paired with `RATE_LIMITED` from ADR-003.

**Audit** — every lock and unlock is written to the append-only `audit_logs`:
`user.locked` (actor `null`, resource `auth:lockout:<sha256-16>` — the email is hashed
because it is PII and must never be logged) and `user.unlock` (actor = the admin).

**Manual recovery** — `POST /api/v1/users/{user_id}/unlock` (admin role only) clears both
keys and writes `user.unlock`. Because lifting a lock removes a protective control, the
endpoint is a state-changing, audit-logged action rather than a silent one.

## 4. Consequences

* **Positive:** guessing now has a hard ceiling per 15-minute window and the account is
  unreachable while locked; no migration, no scheduled job, no new dependency; manual
  unlock is available and accountable; locks expire without intervention.
* **Trade-off — self-inflicted DoS:** an attacker who knows an email can lock that account
  on purpose by submitting bad credentials. This is accepted: the lock is short (15 min),
  self-clearing, and an admin can lift it immediately. The volume limiter (ADR-003)
  already throttles the flood needed to do this at scale.
* **Trade-off — data locality:** lock state lives in Redis, so it is per-instance
  ephemeral; if Redis restarts, in-flight failure counters are lost. Acceptable for a
  15-minute security control, and shared with the rate limiter.
* **Interaction with JML:** this mechanism never writes `User.status`; the kill-switch
  remains the only path to durable suspension, keeping the two controls separable in
  audit and recovery.

---

## 5. Security Threat Modeling (STRIDE)

| Threat | Description | Mitigation Strategy |
|---|---|---|
| **S**poofing | Attacker locks a victim's account by submitting bad credentials as them | Short, self-clearing lock; volume limiter (ADR-003) throttles the flood; admin `unlock` restores access immediately and is audit-logged |
| **T**ampering | Attacker clears their own lock directly | Keys live in Redis on the internal compose network, not exposed; the unlock endpoint requires the `admin` role and is audit-logged; keys are server-generated from the email, never from client input |
| **R**epudiation | "I was never locked / nobody unlocked me" | Both events are written to the append-only `audit_logs` (trigger blocks UPDATE/DELETE); `user.locked` and `user.unlock` name the actor where one is known |
| **I**nformation Disclosure | Lock state or audit records leak account emails | Audit references use a 16-char SHA-256 prefix of the email (`_hash_email`); raw email is never written to logs or audit text |
| **D**enial of Service | Lock mechanism itself used to disable accounts at scale | Per-IP volume limiting on `/auth/login` bounds the request volume needed; lock is 15 minutes and admin-clearable; the pre-check returns 423 without spending Argon2 CPU, so lock traffic stays cheap |
| **E**levation of Privilege | Non-admin unlocks an account, or lock bypass grants access | Unlock requires `require_roles("admin")` server-side (not a client claim); locked accounts are refused before credential comparison, so no authn path is reachable while locked |

---

## 6. References

- `AGENTS.md` §3.2 · `docs/security-iam-policy.md` · `docs/security-access-matrix.md`
- `docs/gap-analysis.md` Gelombang 1 items 1.2 (this) and 1.3 (JML kill-switch, kept separate)
- `docs/adr/ADR-003-rate-limiting.md` (companion: bounds volume; this bounds failures)
- `templates/web-app/backend/app/core/lockout.py` (implementation)
- `templates/web-app/backend/tests/check_lockout.py` (runnable self-check)
- OWASP Cheat Sheet: Authentication Attack Prevention

**Not covered** (deliberately): durable suspension and token revocation — the JML
kill-switch — remain gap item 1.3 and are intentionally kept distinct from this transient
mechanism.
