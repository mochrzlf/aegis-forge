# Aegis Forge — Go (Golang) Starter Skeleton

> **High-performance, enterprise-grade Go backend starter** adhering to the **Banking IAM Zero Trust Standard**.
> Ultra-low memory footprint (~15 MB RAM) with microsecond latency.

---

## 🛡️ Built-in Security Controls

| Pillar | Implementation | Technical Detail |
|---|---|---|
| **Token Rotation (RTR)** | `internal/modules/auth/` | Single-use refresh token with unique `jti` and `family_id`. Transports strictly via `HttpOnly; Secure; SameSite=Strict; Path=/api/auth` cookie. Replay detection revokes all session family members immediately. |
| **Account Lockout (Anti-DoS)** | `internal/modules/auth/` | 5 consecutive failed login attempts locks account for 15 minutes (`HTTP 423 Locked`). Lockout check precedes bcrypt hash computation to neutralize CPU exhaustion attacks. |
| **JML Session Kill-Switch** | `internal/modules/users/` | Updating user status to `suspended` or `terminated` immediately revokes all active refresh tokens in a database transaction. Anti-self-suspend guard prevents root admin lockouts. |
| **Maker-Checker (Four-Eyes)** | `internal/modules/approvals/` | Dual control enforced at both service layer and PostgreSQL table constraint: `CONSTRAINT chk_maker_not_checker CHECK (maker_user_id <> checker_user_id)`. |
| **Immutable Audit Trail** | `internal/core/audit.go` | PostgreSQL trigger `fn_prevent_audit_mutation` strictly blocks `UPDATE` and `DELETE` on `audit_logs` at the database engine level. |
| **Security Headers & Limiter** | `internal/middleware/` | HSTS (2 years preload), X-Frame-Options: DENY, X-Content-Type-Options: nosniff, CSP, and Redis sliding-window rate limiting (100 req/min). |

---

## 🚀 Quick Start

### 1. Start Services via Docker Compose
```bash
make first-run
```
App will be running at:
- **API Base:** `http://localhost:8000`
- **Health Live:** `http://localhost:8000/health/live`
- **Health Ready:** `http://localhost:8000/health/ready`

### 2. Seed Initial Admin & Checker
```bash
make seed
```

### 3. Run Unit Tests
```bash
make test
```
Runs the full Go test suite:
- `TestRateLimiter`
- `TestMakerCannotBeChecker`
- `TestFourEyesPrincipleLogic`
- `TestAntiSelfSuspendRule`
- `TestPasswordHashingAndVerification`
- `TestLockoutThresholdCalculation`
- `TestJWTAccessTokenLifecycle`
- `TestTokenHashIntegrity`
