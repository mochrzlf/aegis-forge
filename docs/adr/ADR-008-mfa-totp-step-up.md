# ADR-008: MFA / TOTP Step-Up

## Architecture Decision Record

| | |
|---|---|
| **ID** | ADR-008 |
| **Title** | TOTP second factor + short-lived step-up token for critical actions |
| **Status** | **ACCEPTED** |
| **Date** | 2026-09-22 |
| **Decided by** | Security Lead / Architecture |
| **Impacts** | `users.mfa_secret`, `users.mfa_enabled`, `mfa_backup_codes` table (migration `0004_mfa.py`), `app/services/mfa_service.py` (new), `app/services/auth_service.py` (login split), `app/api/auth.py` (5 endpoints), `app/api/users.py` (`DELETE /users/me`), `app/core/security.py` (step-up token), `app/core/deps.py` (`require_step_up`), `app/core/config.py`, `requirements.txt` (pyotp), `docs/schema.sql` §1/§9 |

Implements gap item `docs/gap-analysis.md` 1.6 — the last item of Gelombang 1.
Two halves: a TOTP second factor on the account, and a *step-up* token that
proves the second factor was freshly passed.

---

## 1. Context / Problem

`docs/security-iam-policy.md` §41 requires step-up re-authentication for
sensitive actions: balance withdrawal, role modification, bulk export, and
account deletion. A long-lived bearer token is not enough there — a hijacked
session must not be able to delete the account it belongs to. The skeleton had
no second factor at all, so neither half existed.

TOTP (RFC 6238) is the choice: it is a proof-of-possession factor that works
without a network path to the user, and no vendor is involved. `pyotp` is the
single new dependency of this gelombang, sanctioned by gap-analysis rule 5
(stdlib-first, one exception per gelombang, recorded in the gap-analysis row
1.6).

---

## 2. Decision

### 2.1 Data layer

Migration `alembic/versions/0004_mfa.py`:

- `users.mfa_secret` (VARCHAR 64, nullable) — the TOTP seed. Two-phase on
  purpose: enrollment writes it, activation turns the flag on only after a
  valid code proves the authenticator app is set up. An orphan secret that was
  never confirmed protects nothing and enables nothing.
- `users.mfa_enabled` (BOOLEAN NOT NULL, default FALSE) — the login-time
  switch; `mfa_secret` may exist without it.
- `mfa_backup_codes` stores **only** `code_hash = sha256(raw_code)`, with
  `used_at` as the single-use marker — exactly the bearer-secret pattern of
  `refresh_tokens` (ADR-002) and `auth_tokens` (ADR-007). A leaked table row is
  worthless; the raw code is shown once, at activation, and never persisted.

### 2.2 Anti-replay for TOTP codes

A TOTP value stays valid for about 90 s (pyotp accepts the current window plus
its neighbours), so "verified" cannot mean "used". A code that verifies is
marked in Redis under `totp_used:{user}:{digest}` with `SET NX` and a 90 s TTL —
the first presentation wins, any later one inside the same window is refused as
replay. The window, not the token, is what locks the code.

### 2.3 Login flow

Login is split so the two factors cannot drift on what "valid credentials"
means:

- `authenticate` verifies password + account state (shared precondition).
- An MFA-enabled account answers **202** with a refresh cookie set and *no*
  access token — a half-authenticated session that can do nothing but finish
  the challenge. The client completes it at `POST /auth/login/totp`, which
  validates the pending refresh token and the code, then rotates to a full
  pair. A failed second factor clears the cookie: the client re-authenticates
  from `/auth/login`, so an attacker who intercepts the challenge cannot brute
  force it with a live access token already in hand.
- `complete_mfa_login` refuses a revoked or expired pending token, and a
  non-MFA account cannot complete the flow at all (FORBIDDEN).

### 2.4 Step-up token

`POST /auth/step-up` trades a TOTP or backup code for a short-lived JWT
claiming `step_up: true`, expiring in `MFA_STEP_UP_TOKEN_MINUTES` (5). It is a
separate token, not a scope on the access token: it carries no extra
entitlement, only freshness, and its minutes-scale lifetime means a captured
step-up token cannot be banked. `require_step_up` in `app/core/deps.py` decodes
the bearer and requires the claim — an ordinary access token is rejected with
401. The first consumer is `DELETE /users/me`: the account is set to
`terminated`, every session is revoked (the JML kill-switch, ADR-005, applies
to self-termination too), the lockout counter is cleared, and
`user.self_deleted` is audited.

### 2.5 Frontend

No frontend ships in the skeleton — QR-code scan, manual secret entry, and
backup-code display are consumer responsibilities, the same boundary drawn in
ADR-001 through ADR-007. The API contract is complete: `/auth/mfa/enroll`
returns the secret and `otpauth://` URI needed to render both.

---

## 3. Consequences

Positive: the second factor is self-contained, offline-capable, and adds no
vendor. Step-up freshness is minutes-scoped, so a stolen access token still
cannot delete an account. Backup codes give a recovery path that does not
require weakening the factor (one-time, hashed), and disabling MFA requires a
live code — weakening an account is never free.

Residual risk, accepted deliberately: **`mfa_secret` is stored as plaintext.**
TOTP seeds are symmetric — the server must recompute codes, so they cannot be
hashed. With PostgreSQL 16 AES-256 field-level encryption (AGENTS.md §3.1) not
yet wired up, a read-only database leak would bypass the second factor for
every account. That is why this ADR lands *after* the RBAC and audit layers of
ADR-004/005/006: `audit_logs` is append-only with UPDATE/DELETE blocked at the
DB, so the leak scenario needs a broader compromise than reading a table.
Upgrade path: encrypt `mfa_secret` with FLE as soon as the secrets
infrastructure exists, behind the same envelope, with a migration re-writing
existing secrets.

Other costs: `pyotp` is a new runtime dependency (the only one sanctioned this
gelombang; `cryptography` is deliberately *not* pulled in — JWT already
provides HMAC). Used backup-code rows accumulate; like `auth_tokens` there is
no sweep job — add one when table growth is measured, not before. Rate limits
are per-IP (`RATE_LIMIT_MFA_IP`, 10/window) across the TOTP endpoints; a
per-account count would misfire on shared egress IPs.

---

## 4. STRIDE Threat Model

| Threat | Vector | Mitigation in this change |
|---|---|---|
| **S**poofing | Attacker submits someone else's TOTP code | The seed is a 32-char base32 secret, shown only at enrollment and never logged; backup codes are looked up by hash, so a DB read yields nothing usable; the step-up token is bound to `sub` and signed with the JWT secret |
| **T**ampering | Attacker flips `mfa_enabled` off, or replays a code | `mfa_enabled` only flips inside `activate`/`disable`, both requiring a live code; replayed TOTP is refused by the Redis `SET NX` marker for the whole validity window; backup codes are single-use via `used_at` |
| **R**epudiation | User denies disabling MFA, deleting the account, or completing a login | Every transition writes `audit_logs` — `user.mfa.enrolled/activated/disabled`, `user.mfa.step_up` (detail records which factor), `user.login_mfa_challenge`, `user.mfa.login_failed`, `user.login`, `user.self_deleted` with the session-revocation count |
| **I**nformation Disclosure | Attacker harvests secrets or probes backup codes | Only hashes of backup codes are stored; the TOTP secret appears in a response body exactly once (enrollment) and is never emailed or logged; MFA-off accounts verify nothing, so a probe learns no code state; all verification failures answer one identical `Invalid TOTP code` |
| **D**enial of Service | Brute force the 6-digit space, or flood step-up | ADR-003 limits at `RATE_LIMIT_MFA_IP` per IP across all TOTP endpoints; 10^6 codes at 10/window is not guessable; backup-code guessing costs a DB query per attempt (TOTP is tried first, the common case) |
| **E**levation of Privilege | Attacker uses a step-up token as an access token, or vice versa | The step-up token carries no extra claim beyond freshness and still needs the role it names; `require_step_up` rejects any token lacking `step_up`, so a plain access token cannot reach `DELETE /users/me`; it expires in minutes, so it cannot be hoarded after a legitimate step-up |

---

## 5. Verification

Runnable self-check — `templates/web-app/backend/tests/check_mfa.py`
(in-memory SQLite via `Base.metadata.create_all`, real service logic and real
UPDATE/SELECT predicates, fake Redis for the anti-replay store, no HTTP):

1. Enrollment returns a secret and an `otpauth://` URI, and does **not** enable
   MFA
2. Activation with a wrong code is refused and changes nothing
3. Activation with the right code enables MFA and issues 10 unique backup
   codes, all stored hashed, all unused
4. A TOTP code verifies once; the same code is refused inside its window
5. A backup code is accepted once and refused on reuse
6. An MFA-off account verifies nothing, even with a valid code
7. Disabling requires a live code and clears the secret, the flag, and the
   remaining codes
8. A half-authenticated login issues exactly one pending token and no access
   token; a wrong code is refused; a correct one rotates the refresh token and
   issues an access token
9. A consumed pending token is refused on replay; a non-MFA account cannot
   complete the MFA flow at all
10. A step-up token carries the `step_up` claim; an access token does not
11. No raw backup code and no raw secret appears in any audit row

39/39 pass. The full chain was also exercised over HTTP with FastAPI's TestClient
against SQLite + a fake Redis (throwaway, not committed): enroll → activate →
login 202 → login/totp → step-up → `DELETE /users/me` terminating the account,
plus the negative cases — wrong activation code (401), re-enroll while active
(409), a step-up attempt with a plain access token (401), a step-up attempt
without MFA (403), and a replayed TOTP code refused after login/totp consumed
it in the same window. 17/17 pass.

Still not covered offline: the PostgreSQL `mfa_backup_codes` schema itself
(SQLite has no CITEXT/UUID but enforces the constraints the checks exercise),
the real Redis anti-replay store and rate limits, and the `Secure`/`SameSite`
cookie attributes of the half-authenticated login (the TestClient does not
enforce them). Docker is unavailable in this environment, so those remain
pending the compose smoke test named in ADR-003 §5.


