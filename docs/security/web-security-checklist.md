# Web Application Security Checklist

> **Scope:** Security controls every web/SaaS project derived from this baseline must satisfy before launch. Adapted from the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org) and the OWASP Top 10 (2021) — cited, not copied. Mark each item ✅ / ❌ / N/A and record evidence.
>
> Companion docs: `docs/security-iam-policy.md`, `docs/security-access-matrix.md`, `docs/frontend-checklist.md`.

---

## 1. Transport & Session
- [ ] **HTTPS enforced everywhere** (HSTS `max-age ≥ 31536000; includeSubDomains; preload`). No plaintext HTTP endpoints.
- [ ] **Cookies:** `HttpOnly; Secure; SameSite=Strict` on session/refresh cookies. No refresh token in `localStorage` / `sessionStorage` / readable response body.
- [ ] Access token short-lived (~15 min); refresh token rotated on each use; old refresh tokens invalidated (reuse detection).
- [ ] Logout invalidates the session server-side, not just client-side.
- [ ] Session IDs are cryptographically random (≥128 bits) and regenerated after login/privilege change.

## 2. Authentication & Account Security
- [ ] Passwords hashed with **Argon2id** or **bcrypt** (cost tuned); never MD5/SHA1/plain.
- [ ] Credential-stuffing & brute-force protection: per-account + per-IP **rate limiting** and progressive lockout/backoff on login.
- [ ] MFA available (TOTP/WebAuthn) and enforced for privileged roles.
- [ ] Password reset uses single-use, time-limited, random tokens; no user-enumeration via reset/login responses (identical wording + timing).
- [ ] OAuth/OIDC: `state` + `nonce` validated; PKCE for public clients; redirect URIs strictly allow-listed.

## 3. Input, Output & Injection (OWASP A03)
- [ ] **SQL:** parameterized queries / ORM bindings only — no string concatenation of user input into SQL.
- [ ] **XSS:** output encoding per context (HTML/attribute/JS/URL); framework auto-escaping not disabled (`dangerouslySetInnerHTML`/`v-html` audited and sanitized).
- [ ] **CSP** header set (`default-src 'self'`, no `unsafe-inline` for scripts unless strictly necessary with nonce/hash).
- [ ] **Command/Path/LDAP/SSRF:** no shell-out with user input; file paths validated against allow-list; outbound requests to user-supplied URLs restricted (SSRF guard).
- [ ] File uploads: type/size validated, content sniffed, stored outside webroot, served with `Content-Disposition: attachment` + `X-Content-Type-Options: nosniff`.

## 4. Access Control (OWASP A01)
- [ ] **Server-side authorization on every request** — never rely on hidden UI. (See `evals` scenario `rbac-enforcement`.)
- [ ] Deny by default; least-privilege roles per `docs/security-access-matrix.md`.
- [ ] **IDOR/BOLA:** object-level checks — a user can only access their own records (verify `user_id` from session, not from request).
- [ ] Privileged actions require **Maker-Checker** approval where mandated; role derived from verified JWT/session, not client-supplied data.
- [ ] CORS is restrictive (explicit origins, not `*` with credentials).

## 5. Security Headers & Browser Defenses
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY` (or CSP `frame-ancestors 'none'`) — clickjacking defense.
- [ ] `Referrer-Policy: strict-origin-when-cross-origin` (or stricter).
- [ ] `Permissions-Policy` disables unused powerful features (camera, mic, geolocation) unless needed.
- [ ] **CSRF:** anti-CSRF token on state-changing requests when using cookie auth (or verify `SameSite=Strict` + custom-header pattern).

## 6. Data Protection & Privacy (OWASP A02)
- [ ] Sensitive fields encrypted at rest with **AES-256-GCM** (field-level) per `docs/security-iam-policy.md`; keys managed outside the DB.
- [ ] PII minimized; classification documented; GDPR data-subject rights (export/erase) supported.
- [ ] Secrets never in code, Git history, or logs (Gitleaks enforced in pre-commit + CI).
- [ ] DB backups encrypted; access to backups restricted and audited.

## 7. Logging, Monitoring & Error Handling (OWASP A09)
- [ ] **Structured logs** with correlation/request IDs; security events (login, lockout, privilege change, failed authz) logged.
- [ ] **No PII/credentials/tokens in logs** — redaction applied (see `docs/observability.md` if present).
- [ ] Audit trail is append-only/tamper-evident for sensitive operations.
- [ ] Errors return the standard envelope; **no stack traces, SQL, or internal paths** leaked to clients.
- [ ] Alerting on suspicious patterns (brute force, privilege escalation attempts).

## 8. Dependencies, Configuration & Supply Chain (OWASP A06/A05)
- [ ] Dependencies pinned; `dependency-review` CI gate passes (no known HIGH+ vulns introduced).
- [ ] Trivy FS scan clean of CRITICAL/HIGH; Semgrep SAST findings triaged.
- [ ] Default credentials removed; debug modes off in production; admin consoles not publicly exposed.
- [ ] Security-relevant config (cookie flags, CSP, CORS) verified per environment (dev/staging/prod).

---

## Sign-off

| Role | Name | Date | Result |
|---|---|---|---|
| Security Lead | | | ☐ Pass ☐ Fail |
| Backend Lead | | | ☐ Pass ☐ Fail |

> Any **❌** on a *Transport & Session*, *Access Control*, or *Injection* item is a **launch blocker**.
