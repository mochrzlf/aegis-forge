# Security Access Matrix & Segregation of Duties (SoD)
## Enterprise IAM Governance & Entitlement Standard
### Enterprise Banking Standard Control Blueprint

| | |
|---|---|
| **Document** | Security Access Matrix & Access Governance Policy |
| **Classification** | Internal Confidential — Security Baseline |
| **Core Principles** | Least Privilege (PoLP), Segregation of Duties (SoD), Dual Control (Maker-Checker) |
| **Lifecycle** | Joiner, Mover, Leaver (JML) Automation |

---

## 1. Role Hierarchy

| Role | Access Level | Description & Responsibility Boundaries |
|---|:---:|---|
| `superadmin` | Level 0 | Emergency break-glass / root infrastructure account. Strictly forbidden for daily operational activities. |
| `admin` | Level 1 | Operational system administrator. Manages general configurations; prohibited from mutating financial data. |
| `support` | Level 2 | Customer support / helpdesk. Limited Read-Only access with masked PII data. |
| `member` | Level 3 | Standard user / customer / client. Access restricted exclusively to self-owned resources (Ownership Bound). |
| `guest` | Level 4 | Unauthenticated public user. Restricted to public endpoints only. |

---

## 2. Security Access Matrix (Entitlement Table)

| Module / Resource | Action / Endpoint | `superadmin` | `admin` | `support` | `member` | `guest` | Security Control Notes |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| **Authentication** | Login / Refresh / Logout | ✅ | ✅ | ✅ | ✅ | ✅ | Rate limited (max 5 req/min) |
| **User Personal Data** | Read Own Profile | ✅ | ✅ | ✅ | ✅ | ❌ | Row-Level Ownership Bound |
| **User Personal Data** | Read Other Profile | ✅ | ✅ | 👁️ (Masked) | ❌ | ❌ | Support can only view the last 4 digits of phone/email |
| **Role Management** | Promote / Demote Role | 🔒 **Dual** | 🔒 **Dual** | ❌ | ❌ | ❌ | **Mandatory Maker-Checker** |
| **Financial Mutation** | Request Transaction / Withdrawal | ❌ | ❌ | ❌ | ✅ | ❌ | Step-Up MFA / Challenge Token |
| **Financial Mutation** | Approve Commission Payout | 🔒 **Dual** | 🔒 **Dual** | ❌ | ❌ | ❌ | **Maker prohibited from approving own request** |
| **System & Config** | Edit Security Parameters | 🔒 **Dual** | ❌ | ❌ | ❌ | ❌ | Mandatory audit log & dual authorization |
| **Audit Trail** | Read Audit Logs | ✅ | ✅ | ❌ | ❌ | ❌ | Read-Only (Auditor / Security Officer) |
| **Audit Trail** | Modify / Delete Audit Logs | ⛔ **FORBIDDEN** | ⛔ **FORBIDDEN** | ⛔ | ⛔ | ⛔ | **Immutable Append-Only** (Trigger Protected) |
| **Account Lifecycle** | Suspend / Terminate User | 🔒 **Dual** | 🔒 **Dual** | ❌ | ❌ | ❌ | Triggers Instant Session Kill-Switch |
| **Data Portability** | Request Erasure (Data Privacy Laws (e.g., GDPR)) | ✅ | ❌ | ❌ | ✅ (Own) | ❌ | 30-day grace period |

*Legend: ✅ Allowed | ❌ Denied (403 Forbidden) | 👁️ Limited Read-Only | 🔒 **Dual** Mandatory Maker-Checker Flow*

---

## 3. Segregation of Duties (SoD) Rules — Anti-Fraud & Dual Control

To prevent abuse of authority (internal fraud or compromised administrator accounts):

### SoD Rule 1: Separation of Maker and Checker (Four-Eyes Principle)
- An administrator who initiates a request (*Maker*) for user role changes, mass withdrawals, or system limit changes is **STRICTLY PROHIBITED** from approving (*Checker*) their own request.
- The database enforces: `CHECK (maker_user_id <> checker_user_id)`.

### SoD Rule 2: Separation of Developer vs. Auditor
- Application developer/engineer accounts must not have direct access to modify audit logs.
- The `audit_logs` table is protected by anti-tamper database triggers that reject `UPDATE` and `DELETE` commands.

---

## 4. Identity Lifecycle (JML: Joiner, Mover, Leaver)

### A. Joiner (New Employee / User)
1. Account is created with `active` status and default role `member` (Principle of Least Privilege).
2. Mandatory privacy policy consent acceptance (`consent_given_at`).
3. Email or OAuth identity verification required before session activation.

### B. Mover (Department / Role Change)
1. Role changes trigger an entry in the `approval_requests` table.
2. Previous sessions are forcefully terminated upon new role approval to prevent *privilege creep* (accumulation of legacy permissions).

### C. Leaver (Terminated / Resigned / Suspended) — *Instant Access Kill-Switch*
1. As soon as a user's status is changed to `terminated` or `suspended`:
   - Database triggers automatically revoke all tokens in `refresh_tokens` (`revoked_at = NOW()`).
   - Redis sessions are immediately purged.
   - The user is instantly logged out across all devices.

### D. Dormancy (Inactive Accounts)
- Accounts without login activity for **90 consecutive days** are automatically locked to `dormant` status and require identity re-verification for reactivation.

---

## 5. Privileged Access & Break-Glass Protocol (CyberArk PAM Standard)

1. **Emergency Break-Glass Account:**
   - A local emergency superadmin account stored in an encrypted vault is provisioned for disaster recovery scenarios (*DRP / SSO Outage*).
2. **Instant Alerting:**
   - Whenever a privileged or break-glass account logs in, the system automatically dispatches an emergency alert to the Security Operations Center (SOC) / Admin Telegram channel.
3. **Session Timebox:**
   - Privileged sessions are time-boxed to a maximum of 2 hours and require submitting an access justification (*Ticket / Incident ID*).

---

## 6. Periodic Access Reconciliation Checklist (User Access Review - UAR)

Every quarter (3 months), execute the following reconciliation checklist:
- [ ] Pull list of users with `active` status and reconcile against current employment records.
- [ ] Verify that no `terminated` accounts retain active sessions or tokens.
- [ ] Review all accounts holding `admin` or `superadmin` roles (verify continued necessity).
- [ ] Verify Maker-Checker transaction logs in the `approval_requests` table.
- [ ] Export audit evidence using the `scripts/devsec-check.sh` script.
