# 🏦 Banking-Grade Zero Trust IAM Implementation Guide for AI Agents

> **SINGLE SOURCE OF TRUTH FOR AI CODING AGENTS (Hermes, Claude Code, Cursor, Windsurf, Copilot, etc.)**
> When the project specifies **Banking-Grade Security Standard = YES**, the AI Agent **MUST** implement and enforce the following six non-negotiable security controls in the chosen architecture and codebase.

---

## 🛡️ 1. Refresh Token Rotation (RTR) & Replay Attack Revocation
- **Access Token:** Short-lived JWT (maximum 15 minutes), stateless, containing `sub` (User ID), `role`, and `jti` (unique UUID).
- **Refresh Token:** Long-lived (7 days), stored in the database ONLY as a cryptographically secure hash (`SHA-256`).
- **Transport Security:** Refresh token must ONLY be transmitted via HTTP headers using:
  `Set-Cookie: refreshToken=...; HttpOnly; Secure; SameSite=Strict; Path=/api/auth`
  *Never allow tokens to be stored in browser `localStorage` or `sessionStorage`.*
- **Replay Detection:**
  Each refresh token belongs to a `family_id` (UUID). When a refresh token is exchanged, it is marked as `is_revoked = true` and a new token in the same family is issued.
  **Trigger:** If an incoming refresh request uses an *already revoked* token, the server detects a **Replay Attack** (token theft). The server MUST immediately invalidate and revoke **ALL tokens within that family**, terminate the session, and write an incident record to `audit_logs`.

---

## 🔒 2. Brute-Force Defense & Sliding-Window Account Lockout (ADR-004)
- **Failure Threshold:** 5 consecutive failed login attempts.
- **Lockout Duration:** 15 minutes (`locked_until = now() + 15 minutes`).
- **Response Code:** `423 Locked` (Error Code: `ACCOUNT_LOCKED`).
- **Early Rejection Rule:** The system must check if the account is currently locked **before** computing expensive password hashes (bcrypt/Argon2id) to prevent Denial of Service (DoS) attacks on server CPU.
- **Admin Unlock Mechanism:** Sediakan endpoint khusus administrator terautentikasi (`POST /api/users/{id}/unlock`) untuk mereset counter gagal dan membuka kunci akun secara manual.

---

## ⚡ 3. Joiner-Mover-Leaver (JML) Instant Session Kill-Switch (ADR-005)
- **Account State Change:** When a user transitions to `suspended` or `terminated` status:
  1. The user record is updated in the database.
  2. All active refresh tokens, session records, and cached tokens belonging to that user must be **revoked immediately in the same database transaction**.
- **Self-Suspension Guard:** An administrator is strictly prohibited from suspending or terminating their own account (`400 INVALID_ACTION`).
- **Auth Guard:** All authenticated endpoints must verify user status (`active`). If `suspended` or `terminated`, immediately return `403 ACCOUNT_DISABLED`.

---

## 👁️ 4. Segregation of Duties & Dual Control / Maker-Checker (ADR-006)
- **Four-Eyes Principle:** Sensitive and high-risk state mutations (e.g. promoting user roles to admin, financial disbursements, security parameter adjustments, account deactivations) CANNOT be executed directly by a single individual.
- **Workflow:**
  1. **Maker:** Creates a change request (`status = pending`, `maker_user_id = requester_id`).
  2. **Checker:** A different authorized user reviews and approves/rejects the request (`checker_user_id = reviewer_id`).
- **Strict Enforcement Rule:** The Maker is strictly forbidden from reviewing or approving their own request (`403 FORBIDDEN`).
- **Database Hard Constraint:** Enforce this rule at the database level with a check constraint:
  ```sql
  CONSTRAINT chk_maker_not_checker CHECK (maker_user_id <> checker_user_id)
  ```

---

## 📜 5. Tamper-Proof & Append-Only Audit Trail
- **Immutable Table:** The `audit_logs` table must be strictly **append-only**.
- **Database Trigger:** Prohibit `UPDATE` and `DELETE` operations via database triggers or row-level permissions (SQL state `55000` / Exception).
- **Anti-PII Logging:**
  - Do NOT store plaintext passwords, sensitive personal data, or full authorization tokens.
  - Store identity as an anonymized or SHA-256 hashed identifier (`hash_id` or `user_id`).
  - Record: `user_id`, `actor_role`, `action`, `resource_type`, `resource_id`, `ip_address`, `user_agent`, `status`, and `metadata` (JSON).

---

## 🌐 6. Hardened Security Headers & Context-Aware Rate Limiting
- **Security Headers:**
  - `Content-Security-Policy: default-src 'self'`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Rate Limiting:**
  - Public authentication endpoints (`/login`, `/register`, `/password-reset`): Max 5–10 requests per minute per IP.
  - Sliding-window algorithm backed by Redis or memory cache. Return `429 Too Many Requests` when exceeded.

---

## 🤖 Instructions for the AI Agent Setting up This Project
1. **Understand the Chosen Stack:** Refer to `docs/CUSTOM-STACK.md` for the user's selected Frontend, Backend, CSS, and Database.
2. **Setup Modules:** Organize code into clean layers (Routes/Controllers, Business Logic/Services, Data Access/ORM, Middleware, Security).
3. **Implement Security First:** Wire up the 6 banking controls above before implementing general business features.
4. **Automated Verification:** Write unit tests asserting:
   - Lockout on the 5th failed login attempt (`423`).
   - Token family revocation on token replay.
   - Maker cannot approve own request (`403`).
   - JML status update immediately kills sessions.
