# Web Application Playbook

> Follow the phases in order. Each phase is a **gate** — do not proceed until its verification checklist passes. Reference: `docs/blueprints/web-application-blueprint.md`.

---

## PHASE 0 — Context Load
1. Read `AGENTS.md` in full (non-negotiable rules, API response format, cookie/session rules).
2. Read `docs/blueprints/web-application-blueprint.md`.
3. Read `docs/frontend-checklist.md` and `docs/security-iam-policy.md`.

**✅ Verify:** You can state the required API success/error envelope and the cookie rule (`HttpOnly; Secure; SameSite=Strict`, no refresh token in `localStorage`).

---

## PHASE 1 — Specify
1. Draft `docs/PRD.md` from `docs/PRD-template.md` (problem, personas, success metrics).
2. Draft `docs/PRD-detail.md` from `docs/PRD-detail-template.md` (user stories + acceptance criteria per module).

**✅ Verify:** Every user story has at least one testable acceptance criterion. No story references an undefined endpoint or role.

---

## PHASE 2 — Threat Model
1. Create a new ADR in `docs/adr/` (next number) applying **STRIDE** per `docs/adr/ADR-001-Threat-Modeling-Standard.md`.
2. Cover: session hijacking, CSRF, XSS, broken access control (RBAC bypass), injection.

**✅ Verify:** Each STRIDE category has at least one identified threat + mitigation mapped to a control.

---

## PHASE 3 — Contract (API + DB)
1. Define/extend `docs/openapi.yaml` for every endpoint (request, success, error, security scheme, pagination).
2. Define/extend `docs/schema.sql` (tables, constraints, indexes, audit columns).
3. Validate: Redocly lint on `openapi.yaml`; sqlfluff parse on `schema.sql` (both run in pre-commit/CI).

**✅ Verify:** OpenAPI lints clean; every endpoint returns the standard envelope; schema parses in PostgreSQL dialect.

---

## PHASE 4 — Design
1. Produce `docs/ui-design.md` from `docs/ui-design-template.md` (design tokens: color, typography, spacing).
2. Optionally use the `ui-ux-pro-max` skill to generate the token set from the product brief.
3. Add any new flow diagrams to `docs/diagrams/` (Mermaid).

**✅ Verify:** Tokens cover color/typography/spacing; components reference tokens (no hardcoded ad-hoc values); WCAG 2.1 AA contrast is stated.

---

## PHASE 5 — Implement
1. Scaffold per blueprint stack (Next.js/React + Tailwind + shadcn; NestJS/FastAPI/Express backend).
2. Implement endpoints to match `openapi.yaml` **exactly**.
3. Implement auth with HttpOnly cookie sessions + refresh-token rotation.
4. Apply RBAC per `docs/security-access-matrix.md`.

**✅ Verify:** No endpoint deviates from contract; cookies are `HttpOnly; Secure; SameSite=Strict`; RBAC enforced server-side on every protected route.

---

## PHASE 6 — Verify
1. Unit/integration tests; contract test against `openapi.yaml`.
2. Run security audit (`make audit`) — Gitleaks clean.
3. Run the app against the Prism mock (`make mock-api`) for frontend isolation.

**✅ Verify:** Tests pass; no secrets detected; responses match contract; frontend checklist items addressed.
