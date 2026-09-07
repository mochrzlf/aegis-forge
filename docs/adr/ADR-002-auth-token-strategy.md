# ADR-002: Authentication & Token Strategy (Cookie vs Bearer, Rotation)

## Architecture Decision Record

| | |
|---|---|
| **ID** | ADR-002 |
| **Title** | Authentication & Token Strategy (Cookie vs Bearer, Rotation) |
| **Status** | **ACCEPTED** |
| **Date** | 2026-09-07 |
| **Decided by** | Security Lead / Architecture |
| **Impacts** | Web frontend, Mobile apps, Backend auth service, Session store (Redis), IAM |

---

## 1. Context & Problem Statement

Every derived project needs a single, coherent strategy for issuing, transporting, refreshing, and revoking authentication tokens across **web browsers** and **mobile apps**, while honoring the baseline's Zero-Trust and OWASP rules (no refresh token readable by JavaScript, CSRF defense, token-theft containment).

The open questions:
1. Where do tokens live on each client type (cookie vs `localStorage` vs secure enclave)?
2. How are short-lived access tokens refreshed without forcing re-login?
3. How is a stolen refresh token detected and neutralized?

## 2. Alternatives Considered

* **Option A — Access token only, long-lived, in `localStorage`:** Simple, but a long-lived token readable by JS is catastrophic on XSS; no revocation. **Rejected.**
* **Option B — Refresh token in `localStorage`, access token in memory:** Common SPA pattern but violates the baseline rule that refresh tokens must never be JS-readable. **Rejected.**
* **Option C — Split by client:** Web uses **HttpOnly cookie** (refresh) + short-lived access token; Mobile uses **hardware-backed secure storage** (Keystore/Keychain) + short-lived access token. Both with refresh-token rotation + reuse detection. **Chosen.**

## 3. Decision

Adopt **Option C**, formalized as follows:

**Lifetimes**
- Access token: **15 minutes** (`JWT_ACCESS_EXPIRY=15m`).
- Refresh token: **30 days** (`JWT_REFRESH_EXPIRY=30d`), rotated on every use.

**Web (browser)**
- Refresh token → `HttpOnly; Secure; SameSite=Strict` **cookie**, scoped to the auth path. Never in `localStorage`/response body.
- Access token → kept in memory (or short-lived cookie); sent as `Authorization: Bearer`.
- CSRF: anti-CSRF token (or custom-header requirement) on state-changing requests, because cookie auth is CSRF-exposed.

**Mobile (Android/iOS)**
- Tokens → `EncryptedSharedPreferences` (Android Keystore) / Keychain (iOS). Sent as `Authorization: Bearer`.
- Bearer tokens (not cookies) are used, so CSRF does not apply; HTTPS + SSL pinning mandatory.

**Rotation & Reuse Detection**
- Every refresh issues a **new** refresh token and **invalidates the old** (one-time use).
- Token families tracked (Redis): if an **already-rotated** refresh token is presented → treat as theft → **revoke the entire family** and force re-login + security log/alert.

**Revocation**
- Logout revokes the refresh token server-side.
- Rotating `JWT_*_SECRET` invalidates all sessions (see `docs/security/secrets-rotation.md`).

## 4. Consequences

* **Positive:** XSS cannot steal a refresh token on web; stolen refresh tokens are detected and killed via rotation/reuse detection; mobile tokens are hardware-protected; CSRF is explicitly addressed; aligns with OWASP and the eval scenarios (`web-auth-endpoint`, `mobile-token-storage`, `rbac-enforcement`).
* **Trade-off:** Requires a server-side session/token store (Redis) and rotation bookkeeping → more moving parts than stateless-only JWT. Logout-all (secret rotation) forces mass re-login. CSRF token handling adds frontend complexity on web.

---

## 5. Security Threat Modeling (STRIDE)

| Threat | Description | Mitigation Strategy |
|---|---|---|
| **S**poofing | Forged/stolen token used to impersonate a user | Short-lived access tokens; signature + `iss`/`aud` validation; reject `alg=none`; hardware-backed storage on mobile |
| **T**ampering | Token/claims modified client-side | Signed JWT (asymmetric or strong HMAC); server verifies signature on every request; no client-trusted role claims |
| **R**epudiation | User denies authenticated actions | Append-only audit trail of auth + privileged events (`docs/observability.md`) |
| **I**nformation Disclosure | Token leaked via JS, logs, or storage | HttpOnly cookie; never log tokens (PII redactor); Keystore/Keychain; no refresh token in `localStorage` |
| **D**enial of Service | Login/refresh endpoint brute-forced or flooded | Rate limiting + lockout on auth endpoints; `429` + `Retry-After`; reused-token family revocation |
| **E**levation of Privilege | Stolen refresh token exchanged for higher privileges | Refresh-token rotation + reuse detection revokes family; server-side RBAC on every request; Maker-Checker for privileged actions |

---

## 6. References

- `docs/security/web-security-checklist.md` §1–2 · `docs/security/mobile-security-checklist.md`
- `docs/diagrams/mobile-auth-sequence.md` · `docs/security/secrets-rotation.md`
- `evals/scenarios/web-auth-endpoint.yaml`, `evals/scenarios/mobile-token-storage.yaml`
- OWASP Cheat Sheets: Session Management, JSON Web Token, CSRF
