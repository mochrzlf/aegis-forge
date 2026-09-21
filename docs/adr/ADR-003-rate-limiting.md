# ADR-003: Rate Limiting on Authentication Endpoints

## Architecture Decision Record

| | |
|---|---|
| **ID** | ADR-003 |
| **Title** | Rate Limiting on Authentication Endpoints |
| **Status** | **ACCEPTED** |
| **Date** | 2026-09-21 |
| **Decided by** | Security Lead / Architecture |
| **Impacts** | Backend auth service, Redis cache layer, API consumers, CI smoke test |

---

## 1. Context & Problem Statement

The authentication surface of the web-app skeleton (`/auth/register`, `/auth/login`,
`/auth/refresh`) is open to anyone who can reach the service. Without throttling, an
unauthenticated attacker can:

1. **Guess credentials** at unlimited speed against `/auth/login` (credential stuffing).
2. **Enumerate or create accounts** at unlimited speed against `/auth/register`, which
   also costs one database write and one password hash (Argon2) per attempt — a cheap
   denial-of-service and resource-exhaustion vector.
3. **Flood `/auth/refresh`** to exhaust database connections.

`AGENTS.md` §3.2 requires brute-force defense, and the skeleton `README.md` already
stated that Redis was used as a "session/refresh-token store + rate limiter". That claim
was **false**: Redis was declared in configuration and used only by the `/healthz` ping.
This decision closes that gap and makes the claim true.

## 2. Alternatives Considered

* **Option A — Fixed-window counter per IP (`INCR` + `EXPIRE`):** Simplest to implement,
  but allows bursts of up to **2× the limit** at window boundaries (all requests at the
  end of one window plus the start of the next). **Rejected** for an auth surface where
  burst behaviour is exactly what an attacker exploits.
* **Option B — Add a dedicated library (`slowapi`, `fastapi-limiter`):** Provides
  decorators and annotations. **Rejected**: the codebase dependency gate prefers the
  stdlib and already-installed dependencies; the sliding-window logic is ~30 lines and
  Redis is already a declared dependency.
* **Option C — Sliding-window counter over a Redis sorted set, implemented locally:**
  Accurate to the request, no burst amplification, no new dependency, and the counting
  logic stays in-repo so it can be audited and unit-tested. **Chosen.**

## 3. Decision

Adopt **Option C**, formalised as follows.

**Algorithm** — every request records a member in a Redis sorted set scored by the
current Unix time. A single pipelined transaction trims expired members, inserts the new
one, sets a key TTL, and counts remaining members. More than `limit` members inside the
trailing `window` → the request is refused with `429 Too Many Requests`.

**Limits** (defaults in `backend/app/core/config.py`, overridable via environment):

| Endpoint | Identifier | Default limit | Rationale |
|---|---|---|---|
| `/auth/login` | account (email) | 10 / 60 s | Stops password guessing against one account |
| `/auth/login` | IP | 30 / 60 s | Stops the same guessing spread across many accounts |
| `/auth/register` | IP | 5 / 60 s | Open endpoint, no account required — tightest bound |
| `/auth/refresh` | IP | 60 / 60 s | Storm control; caller identity is unknown pre-validation |

**Client identification** — `client_ip()` prefers the first entry of `X-Forwarded-For`
and otherwise falls back to `request.client.host`.

**Error shape** — `429` with the standard error envelope and a new code `RATE_LIMITED`,
plus a `Retry-After` header. `RATE_LIMITED` is a skeleton-local extension of the baseline
envelope code set; it lets a caller distinguish "slow down" from "your input is invalid",
which `VALIDATION_ERROR` cannot express.

**Not covered by this decision** (deliberately, see §4): account lockout after repeated
*failed* credentials, the JML kill-switch, and Maker-Checker approvals are separate
controls tracked as Gelombang 1 items 1.2 and 1.4 in `docs/gap-analysis.md`.

## 4. Consequences

* **Positive:** the README claim about Redis-backed rate limiting becomes true; burst
  behaviour is bounded; the counting logic is pure and unit-testable; no dependency is
  added; every knob is environment-configurable.
* **Trade-off:** IP-based limits are coarse — a large NAT or a corporate proxy can pool
  many users behind one address, so per-IP bounds are deliberately looser than per-account
  bounds. Conversely, an attacker with a rotating IP farm defeats per-IP limits entirely;
  per-account limits remain the effective bound for credential stuffing.
* **Trust boundary:** `X-Forwarded-For` is attacker-controlled unless a trusted reverse
  proxy overwrites it. Deployments behind a proxy must configure that proxy to set the
  header itself; otherwise an attacker can rotate the header to evade throttling.

---

## 5. Security Threat Modeling (STRIDE)

| Threat | Description | Mitigation Strategy |
|---|---|---|
| **S**poofing | Attacker rotates `X-Forwarded-For` to appear as many clients | Header is only consulted for the first entry; deployments behind a proxy must overwrite it at the proxy (see §4 trust boundary). Per-account limits on `/auth/login` are unaffected by header spoofing |
| **T**ampering | Limiter state manipulated to reset a counter | Redis is an internal service on the compose network, not exposed; keys are server-generated (`rl:<scope>:<identifier>`), never derived from client input |
| **R**epudiation | Attacker denies having bombarded an endpoint | Refusals are observable via structured access logs; audit trail already exists for authenticated mutations (`docs/observability.md`) |
| **I**nformation Disclosure | 429 responses leak which accounts exist | Per-account throttling applies to `/auth/login` only, whose success/failure distinction already exists; refusal carries no account-existence signal beyond what a login attempt already reveals |
| **D**enial of Service | Flood of auth requests exhausts CPU (Argon2) and DB connections | This decision: bounded requests per window → bounded Argon2 and DB work. Complements, and is complemented by, account lockout (Gelombang 1 item 1.2) |
| **E**levation of Privilege | Throttling bypass used to reach a privileged path | All endpoints remain behind existing authn/RBAC checks; throttling never grants access, it only delays |

---

## 6. References

- `AGENTS.md` §3.2 (IAM Security & Privileged Access) · `docs/security-iam-policy.md`
- `docs/gap-analysis.md` Gelombang 1 item 1.1
- `templates/web-app/backend/app/core/ratelimit.py` (implementation)
- `templates/web-app/backend/tests/check_ratelimit.py` (runnable self-check)
- OWASP Cheat Sheets: Rate Limiting; Authentication Attack Prevention
