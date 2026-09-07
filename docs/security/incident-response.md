# Incident Response Plan

> **Purpose:** A pragmatic, runbook-style procedure for handling security incidents (credential leak, breach, vulnerability exploitation, trading-system anomaly) in projects derived from this baseline. The goal is fast containment, clean evidence, and correct recovery — not blame.
>
> Related: `docs/security/secrets-rotation.md`, `SECURITY.md`, `docs/security/trading-risk-policy.md`.

---

## 1. Severity Levels

| Level | Definition | Examples | Response Time |
|---|---|---|---|
| **SEV-1 Critical** | Active compromise of credentials/data/funds; trading kill-switch event | Leaked production secret in Git; unauthorized withdrawal; EA circuit-breaker triggered | Immediate (< 15 min) |
| **SEV-2 High** | Exploitable vuln in prod; confirmed unauthorized access attempt | Auth bypass; RBAC escalation; PII exposure in logs | < 1 hour |
| **SEV-3 Medium** | Vuln found pre-prod; suspicious but unconfirmed activity | SAST CRITICAL finding; anomalous login pattern | < 1 business day |
| **SEV-4 Low** | Policy deviation, near-miss, hygiene issue | Missing security header; outdated dependency | Backlog / next sprint |

---

## 2. Phases (follow in order)

### Phase 1 — Detect & Triage
1. Record **when/how** the issue was detected and by what (Gitleaks, CI, monitoring, user report).
2. Assign a **severity** (table above) and a single **Incident Commander (IC)**.
3. Open a private channel/tracking issue (NOT public if it would aid an attacker).

### Phase 2 — Contain (stop the bleeding first)
- **Credential leak:** revoke/rotate the secret **immediately** (see `secrets-rotation.md`). Assume it is compromised even if "only for a minute".
- **Account/system compromise:** disable affected tokens/sessions/keys; isolate the host/service.
- **Trading anomaly:** trigger/verify the **circuit breaker** (close all, cancel pendings, disable trading) before investigating.
- Do NOT delete evidence while containing.

### Phase 3 — Eradicate & Recover
1. Remove the root cause (patch vuln, fix config, purge the secret from history if needed).
2. Restore from a known-good state; re-enable services in stages.
3. Confirm integrity (logs, audit trail, checksums) before declaring recovery.

### Phase 4 — Post-Incident
1. **Timeline:** reconstruct events from logs/audit trail.
2. **Blameless post-mortem:** what happened, why, and what control failed or was missing.
3. **Preventive actions:** new checklist item, eval scenario, ADR, or CI gate. Track to completion.
4. If the fix changes infra/schema/auth/workflow → write/update an **ADR**.

---

## 3. Scenario Quick-Reference

### 🔑 Secret committed to Git (SEV-1)
1. Rotate the secret at the provider **now** (revoke old).
2. Purge from history: `git filter-repo` / BFG, or rewrite + force-push (coordinate with team).
3. Audit access logs at the provider for misuse during the exposure window.
4. Verify Gitleaks pre-commit + CI are active so it can't recur silently.

### 📈 Trading circuit-breaker fired (SEV-1)
1. Confirm all positions closed & pendings cancelled; trading disabled.
2. Preserve equity/DD logs and order audit trail.
3. Investigate cause (data feed, strategy bug, broker issue) before re-enabling.
4. Re-enable only after the 5-gate validation re-passes.

### 🌐 Suspected web breach (SEV-1/2)
1. Rotate session-signing keys (invalidate all sessions → force re-login).
2. Revoke OAuth tokens; force re-consent where supported.
3. Review access logs for IDOR/enumeration; identify affected accounts.
4. Assess PII exposure → notify per GDPR/privacy obligations if required.

---

## 4. Roles & Contacts (fill in for your project)

| Role | Name | Contact |
|---|---|---|
| Incident Commander | | |
| Security Lead | | |
| On-call Engineer | | |
| Comms / Legal (GDPR) | | |

---

## 5. Ground Rules

- **Contain before you investigate.** Stop the loss first.
- **Never route secrets through chat/tickets** — reference them by name, rotate, don't paste.
- **One Incident Commander** owns decisions; others advise.
- **Document as you go** — memory is unreliable under pressure.
