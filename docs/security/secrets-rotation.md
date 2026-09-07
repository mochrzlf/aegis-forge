# Secrets Rotation Guide

> **Purpose:** How to rotate every secret class used in this baseline quickly and safely — both on a schedule (hygiene) and immediately (on suspected compromise). Rotation is the #1 containment action in the Incident Response Plan.
>
> Rule of thumb: **when in doubt, rotate.** A rotated-but-uncompromised secret costs minutes; an un-rotated compromised secret costs a breach.

---

## 1. Rotation Cadence

| Trigger | Action |
|---|---|
| **Scheduled** | Rotate production secrets every **90 days** (or per your compliance policy). |
| **On suspicion/compromise** | Rotate **immediately**, then investigate (see `incident-response.md`). |
| **On personnel/vendor change** | Rotate any secret a departing person/vendor could access. |
| **On environment promotion** | Never reuse a dev/staging secret in production. |

---

## 2. Per-Secret Procedures

### 2.1 JWT Signing Secrets (`JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`)
1. Generate: `openssl rand -base64 48`.
2. Deploy the new secret **alongside** the old (support a grace window) if your stack allows key-ring/dual verification; otherwise schedule a brief maintenance window.
3. Remove the old secret → all existing tokens invalidate → users re-login.
> ⚠️ Rotating JWT secrets **logs out every active session**. Prefer low-traffic windows.

### 2.2 Field-Level Encryption Master Key (`ENCRYPTION_MASTER_KEY`, AES-256-GCM)
1. Generate: `openssl rand -hex 32`.
2. **Do NOT simply swap it** — existing ciphertext becomes unreadable. Use **key versioning**:
   - Keep old key as `..._KEY_v1`, add new as active `..._KEY_v2`.
   - New writes use v2; reads try active then fall back to v1.
   - Lazily re-encrypt (or run a migration) until v1 is unused, then retire v1.
> ⚠️ Never lose the old key before all data encrypted with it is re-encrypted.

### 2.3 Database Credentials (`DATABASE_URL`)
1. Create a new DB user / rotate the password via your provider.
2. Update the connection string in the secret store; rolling-restart the app so connections pick it up.
3. Revoke the old credential.

### 2.4 Redis (`REDIS_URL`)
1. Rotate the Redis password/ACL (or TLS credential for managed `rediss://`).
2. Update the secret store; rolling-restart. Old sessions in cache may flush — acceptable.

### 2.5 OAuth Client Secrets (`GOOGLE_CLIENT_SECRET`, etc.)
1. Rotate in the provider console (Google Cloud / IdP).
2. Update the secret store; rolling-restart. Existing user OAuth grants usually persist (they're tied to client ID, not secret), but verify.

### 2.6 Exchange / Broker API Keys (Trading)
1. Create a **new** API key with the **least-privilege** permissions: `Read` + `Trade` only — **never** `Withdraw`.
2. Update the secret store; restart the EA/bot.
3. Delete the old key at the exchange.
> ⚠️ Confirm the new key has withdrawal **disabled** before enabling live trading (see `trading-risk-policy.md`).

### 2.7 SSH / Deploy Keys
1. Generate a new keypair: `ssh-keygen -t ed25519`.
2. Add the new public key to the target; deploy and verify access.
3. Remove the old public key; securely delete the old private key.

---

## 3. Where Secrets Live (and don't)

| ✅ Allowed | ❌ Never |
|---|---|
| Local `.env` (git-ignored) | Committed to Git / `.env.example` |
| Secret manager (Doppler, Vault, AWS/GCP/Azure KMS, GitHub Secrets for CI) | Chat, tickets, screenshots, logs |
| CI/CD protected variables | Source code / config committed to repo |

- `.env.example` must only ever contain **placeholders** like `[REPLACE_WITH_...]`.
- Gitleaks (pre-commit + CI) is the safety net — do not bypass it.

---

## 4. Rotation Checklist

- [ ] New secret generated with sufficient entropy (≥32 bytes for keys).
- [ ] Secret stored in the secret manager / `.env` (not committed).
- [ ] App redeployed/restarted and health-checked against the new secret.
- [ ] Old secret revoked **after** the new one is verified working.
- [ ] Access/audit logs reviewed for misuse during any exposure window.
- [ ] Rotation recorded (date, secret name, operator) in the ops log.

> If the rotation follows a suspected compromise, link the incident ticket and complete the post-incident steps in `incident-response.md`.
