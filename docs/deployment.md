# Deployment Standard

> **Purpose:** Define how code moves safely from a developer's machine to production — environment promotion, deployment strategies, secrets handling, and rollback — so every derived project deploys the **same, auditable way** instead of improvising.
>
> Scope: this baseline ships a local `docker-compose.yml` for dev. This document is the standard for turning that into staging & production deployments (compose-based hosts, or Kubernetes/ECS/etc.).

---

## 1. Environments & Promotion

| Env | Purpose | Source of truth | Data | Approval |
|---|---|---|---|---|
| **dev** | Local feature work | feature branch | synthetic/seed | none |
| **staging** | Pre-prod validation, contract & E2E | `main` (auto-deploy) | anonymized/synthetic | CI green |
| **production** | Live users | tagged release (`v*`) | real | **manual approval** |

**Promotion is one-directional:** `dev → staging → production`. Never deploy to prod from a feature branch, and never "hot-patch" prod directly — fix forward through the pipeline.

**Golden rule:** the **same immutable artifact** (container image, tagged by digest/semver) is promoted across environments — you do **not** rebuild per environment. Only **configuration** (env vars/secrets) changes per env.

---

## 2. Build Once, Promote (artifact flow)

```
commit → CI build → run tests/security gates → build image :v1.2.3 (+ :sha)
        → push to registry → deploy to STAGING (auto)
        → smoke/E2E vs staging → ✅
        → promote SAME image :v1.2.3 to PRODUCTION (manual approval)
```
- Tag images with **semver + git SHA**; never deploy `latest` to prod.
- Generate and attach an **SBOM** (already produced by the `sbom` CI job).
- Record the deployed digest in the release notes / audit trail.

---

## 3. Deployment Strategies

Choose per service risk profile; document the choice in the service's runbook.

| Strategy | How | Pros | Cons | Use when |
|---|---|---|---|---|
| **Rolling** | Replace instances gradually | Simple, no extra infra | Mixed versions briefly | Stateless web/API, tolerant of brief skew |
| **Blue/Green** | Run two identical stacks; switch traffic | Instant rollback, zero-downtime | 2× infra cost, DB migration care | Critical user-facing services |
| **Canary** | Route small % of traffic to new version, ramp up | Early blast-radius limit | Needs traffic-splitting + metrics | High-risk changes, ML/trading logic |

> **Database + zero-downtime:** pair any strategy with the **Expand–Migrate–Contract** migration pattern (`docs/migrations.md`) so old and new app versions can coexist during rollout.

---

## 4. Health Checks, Readiness & Rollback

Every deployable service MUST expose:
- **`/healthz`** (liveness) — process is up.
- **`/readyz`** (readiness) — can serve traffic (DB/redis reachable). Load balancers route only to ready instances.

**Automated rollback triggers (abort + revert to previous version) when, post-deploy:**
- `/readyz` fails for N consecutive checks, **or**
- error rate > threshold (e.g., >1% 5xx for 2 min), **or**
- p95 latency breaches budget (see `docs/performance-budgets.md` §5).

**Manual rollback = redeploy the previous known-good image digest** (fast, because artifacts are immutable). Follow with a post-incident note per `docs/security/incident-response.md`.

---

## 5. Configuration & Secrets per Environment

- **12-factor:** config lives in **environment variables**, not in code or committed files.
- **`.env` is dev-only.** Staging/prod secrets come from a **secret manager** (e.g., Doppler, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) — never committed, never in CI logs.
- **Rotate** secrets per `docs/security/secrets-rotation.md`; key rotation must not require redeploying app code.
- Mark CI/CD secret variables as **masked + protected**; restrict prod deploy credentials to the release pipeline (least privilege).

---

## 6. Infrastructure as Code & Change Control

- Define infra declaratively (compose for small hosts; Terraform/Helm/Bicep for cloud/K8s). **No snowflake servers** configured by hand.
- All infra changes go through **PR + review** like application code (CODEOWNERS routes workflows/infra to `@org/devops-lead`).
- **Branch protection** (`SETUP.md` §6) + required status checks gate what reaches `main`, and only `main`/tags deploy.

---

## 7. CI/CD Pipeline Gates (minimum)

A change may reach production only after **all** gates pass:

- [ ] **Build** succeeds; image tagged (semver + SHA), SBOM generated.
- [ ] **Tests** green: unit + component + `@smoke` E2E (`docs/frontend-testing.md`).
- [ ] **Security** green: gitleaks, Semgrep, Trivy, dependency-review (no high/critical).
- [ ] **Contract** valid: OpenAPI lint + schema parse (`security.yml` `contract-validation` job).
- [ ] **Migrations** reviewed: reversible, zero-downtime-safe (`docs/migrations.md`).
- [ ] **Deployed to staging** and smoke-tested before prod approval.
- [ ] **Prod deploy requires manual approval** (protected environment).

---

## 8. Observability on Deploy

- Emit a **deploy event** (version, SHA, env, timestamp) to your monitoring/audit log so metrics/traces can be correlated to releases (`docs/observability.md`).
- Watch RED metrics + alerts after each deploy; a firing **SEV-1** alert (e.g., trading circuit-breaker) triggers the IR process.
- Keep release notes linking version → changes → deployed digest.

---

## 9. Pre-Production Deploy Checklist

- [ ] Same immutable image promoted (not rebuilt) from staging.
- [ ] DB migrations applied via Expand–Migrate–Contract; backward-compatible.
- [ ] Secrets sourced from secret manager; none in code/logs.
- [ ] `/healthz` + `/readyz` configured and wired to the load balancer.
- [ ] Rollback plan confirmed (previous digest identified).
- [ ] Dashboards/alerts visible; deploy event emitted.
- [ ] Manual approval recorded.
