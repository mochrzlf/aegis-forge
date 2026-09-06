# Enterprise Security & IAM Policy Blueprint
## Identity, Access, and Data Protection Security Standard

This document serves as the formal security architecture guideline for engineering teams and AI Agents when designing, implementing, and testing systems.

---

## 1. Identity & Authentication

1. **Password Policy (For Local Auth):**
   - Must use **Argon2id** (primary choice) or **bcrypt** (minimum cost factor 12) hashing algorithms.
   - Minimum 12 characters combining uppercase letters, lowercase letters, numbers, and symbols.
   - Enforce validation against common leaked password databases (*HaveIBeenPwned API check*).
2. **Session & Token Hygiene:**
   - **Access Token:** Ultra short-lived (maximum 15 minutes), stateless JWT containing claims: `sub` (User ID), `role`, and `jti` (unique JWT ID).
   - **Refresh Token:** Must be stored in the database as a SHA-256 hash.
   - **Transport Cookie:** Must be transmitted via `Set-Cookie` header with flags:
     `HttpOnly; Secure; SameSite=Strict; Path=/api/auth`.
   - STRICTLY FORBIDDEN to store authentication tokens in `localStorage` or `sessionStorage`.
3. **Refresh Token Rotation (RTR):**
   - Every refresh token exchange issues a new token pair and invalidates the previous token.
   - If an already revoked token is submitted, the system triggers a **Replay Detection Alert**, invalidates all descendant sessions, and logs the event to `audit_logs`.

---

## 2. Authorization & Access Control (Authorization & IAM)

1. **Principle of Least Privilege (PoLP):**
   - Users and services are granted only the absolute minimum permissions necessary to perform their assigned tasks.
2. **Role-Based Access Control (RBAC):**
   - Role Hierarchy:
     - `superadmin`: Global system management, security configuration, and auditing.
     - `admin`: Operational management and user reviews.
     - `support`: Limited read-only access for support tickets (sensitive data masked).
     - `member`: Standard user owning their own account data.
     - `guest`: Public read-only access.
3. **Prevention of IDOR (Insecure Direct Object Reference / BOLA):**
   - The server must not solely validate whether the `id` format is valid.
   - The server MUST validate that the requested resource `id` truly belongs to the authenticated user (`WHERE id = :id AND user_id = :currentUserId`).
4. **Step-Up Authentication:**
   - For critical actions (balance withdrawals, user role modifications, bulk data exports, account deletion), users must complete a re-authentication challenge (password re-entry, WhatsApp/Email OTP, or WebAuthn).

---

## 3. Threat Modeling (STRIDE) SOP

Every new endpoint creation or module addition must be preceded by a STRIDE evaluation:

| Threat Category | Evaluation Focus | Standard Mitigation |
|---|---|---|
| **S**poofing | Identity / session forgery | JWT signature validation, HMAC webhook verification |
| **T**ampering | Unauthorized data modification | Zod input validation, database constraints, parameterized queries |
| **R**epudiation | Action denial | Immutable logging to `audit_logs` (IP, UA, Timestamp) |
| **I**nformation Disclosure | Sensitive data leakage | PII masking, generic error messages, Field-Level Encryption |
| **D**enial of Service | Resource exhaustion | Redis rate limiter, mandatory pagination, payload size limits |
| **E**levation of Privilege | Permission escalation | Server-side role guards, Row-Level Security / IDOR checks |

Document evaluation results in `docs/adr/ADR-[NUM]-threat-model-[feature].md`.

---

## 4. Regulatory Compliance (Data Privacy Laws (e.g., GDPR))

1. **Data Processing Consent:**
   - Mandatory logging of timestamp and privacy policy version agreed to during onboarding (`consent_given_at`, `consent_policy_version`).
2. **Right to Erasure:**
   - Users have the right to request account deletion.
   - A 30-day grace period is provided (`deletion_requested_at`). After 30 days, a background worker performs *Permanent Hard Delete* or *Anonymization* on historical records.
3. **Data Portability:**
   - Provide account data archive download capabilities in a structured format (encrypted JSON/CSV).
4. **Third-Party Credential Encryption (Field-Level Encryption):**
   - Third-party tokens (Gmail, GitHub, Payment Gateway) must be encrypted at the column level using **AES-256-GCM**.
