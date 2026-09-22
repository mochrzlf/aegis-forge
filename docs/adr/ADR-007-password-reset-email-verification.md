# ADR-007: Password Reset + Email Verification Tokens

## Architecture Decision Record

| | |
|---|---|
| **ID** | ADR-007 |
| **Title** | Single-use hashed tokens for password reset and email verification |
| **Status** | **ACCEPTED** |
| **Date** | 2026-09-22 |
| **Decided by** | Security Lead / Architecture |
| **Impacts** | `auth_tokens` table, `users.email_verified_at`, `app/services/auth_service.py`, `app/api/auth.py`, `app/core/mailer.py` (new), `app/core/security.py`, `app/core/config.py`, `docker-compose.yml` (Mailpit) |

Implements gap item `docs/gap-analysis.md` 1.5. Reuses the opaque-hash token
storage of ADR-002 and the blast-radius session revocation of ADR-005/006.

---

## 1. Context / Problem

`docs/security-iam-policy.md` treats credential recovery as part of the account
lifecycle, and `AGENTS.md` §3.2 forbids logging PII. The skeleton had neither
flow: a user who forgot a password had no recovery path, and nothing ever
attested that an address actually belonged to the account holder. Both are
listed as missing in gap-analysis row 1.5.

The hard part is not "send a link" — it is sending a link that cannot be turned
against the user. A recovery link is a *password equivalent* that arrives over
an untrusted channel (email), so the design has to assume the link may be
leaked, guessed, or replayed, and that the endpoint handing it out is
unauthenticated and therefore open to probing.

---

## 2. Decision

One token table, two purposes, one set of rules.

### 2.1 Data layer

Migration `alembic/versions/0003_auth_tokens.py`:

- `auth_tokens` stores **only** `token_hash = sha256(raw_token)`. The raw token
  exists in memory for one request and in one email; it is never written to the
  database, never logged, and never returned in an API response body.
- `purpose` is constrained by `CHECK (purpose IN ('password_reset',
  'email_verification'))` — a token of one kind can never be redeemed as the
  other, at the data layer.
- `consumed_at` is the single-use marker. Redemption sets it; a token with a
  non-null `consumed_at` is refused.
- `users.email_verified_at` (timestamp, NULL = unverified) records verification
  state on the user, mirroring `docs/schema.sql` §1. A timestamp, not a boolean,
  because "when was this verified" is the compliance-relevant fact.

### 2.2 Service layer

`app/services/auth_service.py` — `request_password_reset` /
`confirm_password_reset` / `request_email_verification` /
`confirm_email_verification`, over a shared validator `_claim_auth_token`.

Deliberate rules:

1. **Unknown address is not an error.** `request_password_reset` returns `None`
   and the endpoint still answers 200 with the identical body. Distinguishing
   "sent" from "no such account" would make the endpoint an account-enumeration
   oracle — the single cheapest thing an attacker learns from a reset flow.
2. **All failure modes look alike.** No-such-token, already-consumed, and
   expired all answer `UNAUTHORIZED / "Invalid link"`. A guesser learns nothing
   about which links might still be live.
3. **Failed redemption consumes nothing.** An expired or invalid token is left
   untouched, so a legitimate user's link survives a probe.
4. **Reset revokes sessions.** `confirm_password_reset` rehashes the password
   and calls `revoke_all_refresh_tokens` in the same transaction. A browser tab
   hijacked before the reset must not keep working on the old credentials — the
   same blast-radius rule as the JML kill-switch (ADR-005) and role promotion
   (ADR-006).
5. **Suspended accounts cannot reset.** A suspended account is under JML
   control; letting it rotate its own password would hand control back.
6. **SQLite-normalised expiry.** `expires_at` is coerced to tz-aware before
   comparison, so the check is well-defined on either driver (same fix as
   ADR-006).

### 2.3 Mail — no new dependency

`app/core/mailer.py` uses the stdlib `email` + `smtplib` stack, wrapped in
`asyncio.to_thread` so a slow or unreachable relay cannot stall an auth request.
Delivery is added to `templates/web-app/docker-compose.yml` as a Mailpit relay
(the same image the root compose already ships for this purpose). No runtime
dependency is added to `requirements.txt`.

Delivery failures are **logged and swallowed**: the caller still answers 200. A
mail outage must not become a signal about which addresses exist. The recipient
address and the link itself never reach the logs (PII discipline, AGENTS.md
§3.2.4). An empty `SMTP_HOST` disables sending outright without breaking the
endpoints.

### 2.4 Endpoints and rate limiting

Four routes under `/auth`, each behind ADR-003 limits:

| Endpoint | Auth | Limit per minute |
|---|---|---|
| `POST /auth/password-reset/request` | none | 5 per IP, 3 per address |
| `POST /auth/password-reset/confirm` | none | 10 per IP |
| `POST /auth/email-verification/request` | access token | 5 per IP |
| `POST /auth/email-verification/confirm` | none | 10 per IP |

The request endpoints are unauthenticated and carry the tightest bounds, plus a
per-address bound so one mailbox cannot be flooded with links. Registration
issues a verification link automatically.

**Login is not gated on `email_verified_at`.** Verification is an attestation of
address ownership, not a session prerequisite: blocking login would collide with
the lockout (ADR-004) and JML (ADR-005) flows, which are the authority on
whether an account may authenticate. A deployment that wants verified-only
logins adds the check in `login()`; the schema already supports it.

---

## 3. Decision / Consequences

**Positive.** Recovery exists end to end and is safe by construction: hashed
storage means a DB leak yields no usable links; single-use means a replayed link
is dead; the anti-enumeration contract means the flow cannot be mined for
accounts. Reset is consistent with the rest of the security model — a successful
reset invalidates every live session, so credentials and sessions never
disagree. No new dependency; the transport is replaceable without touching the
token logic.

**Negative / trade-offs.** Email is now in the trust path: if the mailbox is
compromised, the attacker holds a password equivalent for 30 minutes — the TTL
is short for exactly this reason, and it is the operator's job to keep it short.
Links are bearer tokens, so they must never be logged; the mailer enforces this,
but any future proxy/CDN in front must be configured to strip them from access
logs too. The 200-always request endpoint makes genuine "the mail never
arrived" failures invisible to the user, which is the price of not leaking
account existence — operators watch the audit trail
(`user.password_reset_requested`) for volume anomalies instead. Token rows
accumulate until consumed or expired; there is no cleanup job, matching how the
skeleton treats every other Redis/DB state. Add a sweep when table growth is
measured, not before.

---

## 4. STRIDE Threat Model

| Threat | Vector | Mitigation in this change |
|---|---|---|
| **S**poofing | Attacker requests a reset for someone else's account | Request answers 200 identically for known and unknown addresses; the link is emailed to the account's registered address only, never returned in the response body; redemption requires the raw token, which exists only in that mailbox |
| **T**ampering | Attacker alters a token row or submits a forged/expired link | Only `token_hash` is stored, so a stolen row is worthless; `consumed_at` and `expires_at` are server-side and tz-normalised; the password write happens only inside `confirm_password_reset` on a row fetched by hash + purpose |
| **R**epudiation | User denies changing their password | Every transition writes `audit_logs` — `user.password_reset_requested` (resource carries the email fingerprint, never the raw address) and `user.password_reset` with the session-revocation count; same for `user.email_verification_requested` / `user.email_verified` |
| **I**nformation Disclosure | Attacker harvests emails or live links | Unknown address → no row, no error; all redemption failures return one identical message; the raw token is never persisted or logged; the mailer logs the subject only, never the recipient or the link |
| **D**enial of Service | Flood of reset requests / link guessing | ADR-003 limits: 5/min per IP + 3/min per address on request, 10/min per IP on confirm; tokens are 48-byte `secrets.token_urlsafe`, so guessing is infeasible within any rate budget; suspended accounts cannot reset |
| **E**levation of Privilege | Attacker uses a verification link to act as another user | `purpose` CHECK at the DB and a purpose filter in the query mean a verification token can never be redeemed as a reset token; verification writes only `email_verified_at` and grants nothing; session revocation on reset prevents a stale hijacked session from surviving |

---

## 5. Verification

Runnable self-check — `templates/web-app/backend/tests/check_reset_verify.py`
(in-memory SQLite via `Base.metadata.create_all`, real service logic and real
UPDATE predicates, no mocking, no SMTP):

1. A reset token is stored hashed — the raw value appears nowhere in the DB row
2. An unknown address creates no token and raises no error
3. Confirm sets the new password (verified with `verify_password`) and consumes
   the token
4. A replayed token is refused
5. An expired token is refused and left unconsumed, password unchanged
6. A successful reset revokes both live sessions (and ignores the already-revoked one)
7. A suspended account cannot redeem a reset token
8. Email verification sets `email_verified_at` and its token is single-use
9. Re-requesting verification for a verified account is refused
10. A verification token cannot be redeemed as a reset token
11. The audit chain contains all four actions and no raw address or raw token
    appears in any audit row

All pass. Not covered offline: the PostgreSQL `purpose` CHECK constraint itself
(SQLite enforces CHECK constraints too, but the production constraint is the one
that matters), the real Mailpit relay (SMTP is disabled by default in the
self-check), and the Redis-backed rate limits in front of these endpoints.
Docker is unavailable in this environment; all three remain pending the compose
smoke test named in ADR-003 §5.