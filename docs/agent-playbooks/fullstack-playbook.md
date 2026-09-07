# Fullstack / Enterprise Playbook

> Use when a project spans web + backend + mobile, or when the domain is unclear. This playbook composes the domain playbooks and adds enterprise controls (RBAC, Maker-Checker, audit trails). Reference: `docs/security-iam-policy.md` + `docs/security-access-matrix.md`.

---

## PHASE 0 — Context Load
1. Read `AGENTS.md` in full.
2. Read the blueprint(s) for every surface in scope (web / mobile / trading).
3. Read `docs/security-iam-policy.md`, `docs/security-access-matrix.md`, and `docs/diagrams/system-architecture-universal.md`.

**✅ Verify:** You can name every surface in scope and which domain playbook governs each.

---

## PHASE 1 — Specify
1. Draft `docs/PRD.md` + `docs/PRD-detail.md`, explicitly mapping each module to its owning surface (web / mobile / backend / trading).
2. Identify cross-cutting concerns: auth, RBAC roles, audit logging, data privacy (GDPR).

**✅ Verify:** Every module has an owner surface; roles and entitlements enumerated (feeds the access matrix).

---

## PHASE 2 — Threat Model
1. New ADR in `docs/adr/` with STRIDE across all surfaces, PLUS enterprise threats: privilege escalation, SoD violation (maker == checker), audit-trail tampering, PII leakage in logs.

**✅ Verify:** RBAC, Maker-Checker (Four-Eyes), and tamper-proof audit controls are specified for sensitive operations.

---

## PHASE 3 — Contract (API + DB + IAM)
1. Define `docs/openapi.yaml` (all services) and `docs/schema.sql` (incl. audit tables, RBAC tables).
2. Finalize `docs/security-access-matrix.md` (entitlements + SoD) for the concrete roles.
3. Validate contracts (Redocly + sqlfluff via pre-commit/CI).

**✅ Verify:** Contracts lint clean; schema includes audit-trail + field-level encryption (AES-256-GCM) for sensitive columns; SoD enforced for privileged actions.

---

## PHASE 4 — Design
1. Produce `docs/ui-design.md` for each UI surface; add integration diagrams to `docs/diagrams/`.

**✅ Verify:** Each UI surface has tokens + at least one architecture/sequence diagram covering cross-service flows.

---

## PHASE 5 — Implement
1. Implement each surface per its domain playbook's Phase 5 (web auth cookies, mobile Keystore, trading risk gate).
2. Implement shared services: RBAC enforcement, Maker-Checker approval flow, structured anti-PII logging, immutable audit trail.

**✅ Verify:** Domain-specific rules hold per surface; privileged operations require a distinct approver; audit entries are append-only.

---

## PHASE 6 — Verify
1. Per-surface tests + end-to-end flow across services (use Prism mock for isolation).
2. `make audit` (Gitleaks) + confirm CI `security-audit` and `contract-validation` jobs pass.
3. Confirm no ADR-required change (infra/schema/auth/workflow) lacks an ADR.

**✅ Verify:** All surfaces verified per their domain playbook Phase 6; enterprise controls demonstrated; ADR coverage complete.
