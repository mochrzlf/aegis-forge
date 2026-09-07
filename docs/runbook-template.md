# Runbook — <Service / System Name>

> **How to use this template:** Copy this file to `docs/runbooks/<service>.md` for each deployable service and fill in every `<placeholder>`. A runbook is the **operational** companion to `docs/security/incident-response.md` (which defines the *process*); this document holds the *concrete technical steps* to operate and recover one specific service. Keep it accurate — an outdated runbook is worse than none.

| Field | Value |
|---|---|
| **Service** | `<name>` |
| **Owner / On-call** | `<team / handle>` |
| **Tier / SEV default** | `<e.g., Tier-1 / SEV-2>` |
| **Repo / Path** | `<link or path>` |
| **Environments** | `dev / staging / production` |
| **Last verified** | `<YYYY-MM-DD>` |

---

## 1. Overview
- **What it does:** `<one-paragraph description>`
- **Upstream dependencies:** `<DB / Redis / third-party APIs / other services>`
- **Downstream consumers:** `<who breaks if this goes down>`
- **SLOs:** availability `<99.9%>`; p95 latency `<300ms>` (see `docs/performance-budgets.md` §5)

---

## 2. Architecture (quick reference)
```
<ASCII diagram or link to docs/diagrams/ — components, ports, data flow>
```
- **Entry points:** `<URLs / ports / queues>`
- **Health endpoints:** `/healthz` (liveness), `/readyz` (readiness)
- **Dashboards:** `<link>` · **Logs:** `<link/query>` · **Traces:** `<link>`

---

## 3. Common Operations

### Start / Stop / Restart
```bash
# Local (compose)
docker compose up -d <service>
docker compose restart <service>
docker compose down

# Staging / Production
<orchestrator command — kubectl rollout restart, ecs update-service, etc.>
```

### Deploy / Rollback
```bash
# Deploy (promote immutable image)
<command / pipeline reference — see docs/deployment.md>

# Rollback to previous known-good digest
<command to redeploy previous image digest>
```

### View logs / exec / inspect
```bash
docker compose logs -f <service>
# prod: <kubectl logs / cloud logs query with trace_id filter>
```

---

## 4. Health Verification (after any change)
- [ ] `GET /healthz` returns `200`.
- [ ] `GET /readyz` returns `200` (deps reachable).
- [ ] Key user flow works (run the service's `@smoke` E2E path).
- [ ] No new errors in logs; RED metrics within normal band.
- [ ] Alerts are green / not firing.

---

## 5. Alerts & Response

> Map each alert to an action. Reference the alert rules in `docs/observability.md`. Classify severity per `docs/security/incident-response.md` (SEV-1..4) and page on-call for SEV-1/SEV-2.

| Alert | Likely cause | Immediate action | Escalate if |
|---|---|---|---|
| **HighErrorRate** | bad deploy / dep failure | check recent deploy → rollback if correlated | not resolved in 15 min |
| **HighLatency (p95)** | DB slow query / N+1 / resource sat. | check DB p95, scale, inspect slow traces | customer impact |
| **ServiceDown / readyz fail** | crash loop / dep unreachable | check logs, restart, verify deps (DB/redis) | restart doesn't recover |
| **TradingCircuitBreaker** *(trading only)* | risk limit breached | **SEV-1** — halt trading, follow risk policy (`docs/security/trading-risk-policy.md`) | immediately page on-call |
| **Cert/Secret expiring** | rotation overdue | rotate per `docs/security/secrets-rotation.md` | within 7 days of expiry |

---

## 6. Common Failure Scenarios & Playbooks

### 🔴 Database unreachable
1. Confirm: `docker compose ps` / DB health-check; connection string env.
2. Check DB resource limits (connections, disk).
3. If RDS/managed: check provider status page.
4. Mitigation: enable read-replica/failover; if prolonged, declare SEV per IR.

### 🔴 Third-party API outage (e.g., broker/MetaAPI, OAuth)
1. Confirm via provider status + failing traces.
2. Enable **circuit breaker** / serve degraded mode if designed.
3. Communicate per IR stakeholder template.

### 🔴 Disk / memory saturation
1. Identify consumer: `docker stats` / node metrics.
2. Clear safe temp data; scale up/out.
3. Add alert if recurring; consider data-retention policy.

### 🔴 Bad deploy (errors spike right after release)
1. **Rollback immediately** to previous digest (`docs/deployment.md` §4).
2. Verify health (§4). Open incident note + root-cause follow-up.

---

## 7. Data Recovery / Backup
- **Backups:** `<schedule, tool, retention>` · **Last restore test:** `<date>`
- **Restore steps:** `<how to restore DB / state>`
- **RPO / RTO:** `<recovery point / time objectives>`

---

## 8. Security & Access
- **Who can access prod:** `<roles>` · **How (break-glass):** `<procedure>`
- **Secrets location:** `<secret manager path>` — rotation per `docs/security/secrets-rotation.md`
- **Audit:** actions are logged to the tamper-evident audit trail (`docs/observability.md`).

---

## 9. Escalation & Contacts
| Role | Contact | When |
|---|---|---|
| Primary on-call | `<handle>` | first responder |
| Secondary / lead | `<handle>` | not ack in 15 min / SEV-1 |
| Security lead | `<handle>` | suspected breach / SEV-1 |
| Stakeholder comms | `<handle>` | customer-facing impact |

> Follow the communication cadence and post-incident review process in `docs/security/incident-response.md`.

---

## 10. Maintenance & Review
- [ ] Runbook **reviewed & re-verified quarterly** (update "Last verified").
- [ ] Updated after every incident (new scenario → new playbook entry).
- [ ] Drills/game-days run for Tier-1 services.
