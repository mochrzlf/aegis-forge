# Task Breakdown — Agent-Ready Implementation Units
# [Product Name] — [Feature / Epic Name]

Produced from `docs/PRD.md` + `docs/PRD-detail.md`. Every task below is a
unit of work an AI coding agent (or human) can pick up in isolation. A task
that cannot be done without "figuring out the rest" is NOT agent-ready —
split it further.

> **Token-economy rule (non-negotiable):** reference the baseline by path
> (`docs/...`, `skills/...`) — never paste whole documents into a task.
> A task should give the agent enough to *find* context, not to *contain* it.

| | |
|---|---|
| **Product** | [Product Name] |
| **Source PRD** | `docs/PRD.md` v[x.y] |
| **Source Detail** | `docs/PRD-detail.md` v[x.y] |
| **Status** | Draft / Ready for Agent |
| **Owner** | [Name / Team] |

---

## Task T1: [Short imperative name, e.g. "Implement POST /auth/login endpoint"]

| Field | Value |
|---|---|
| **Traces to** | PRD Module F1 / User Story F1.1 (AC 1–5) |
| **Depends on** | None (or: T0 must be merged first) |
| **Type** | Backend / Frontend / DB-migration / Infra / Test |
| **Size** | XS (≪½ day) · S · M — anything L must be split |
| **Skeleton hint** | [`templates/web-app/` path to EDIT, or `new` if no skeleton file exists] |

### Objective
[One sentence: what will be true when this task is done.]

### Skeleton Hint
[Point at the EXISTING file in the starter skeleton (`templates/<domain>/`)
that this task should MODIFY, so the agent edits instead of generating from
scratch (token economy). Examples: `templates/web-app/backend/app/api/auth.py`
(extend) or `new module — no skeleton equivalent` (then justify why). Leave
blank only if the project is not built from a skeleton.]

### Files Touched
- `backend/src/auth/routes.py` — add `POST /auth/login`
- `backend/tests/auth/test_login.py` — new

### Context the Agent Needs (by reference, not by paste)
- `AGENTS.md` §3.1 — API envelope & error codes (MANDATORY)
- `docs/openapi.yaml` — add the endpoint contract here FIRST
- `skills/api-contract-envelope/SKILL.md` — envelope guardrail
- `skills/rbac-enforcement/SKILL.md` — if a role check is involved

### Definition of Done (verifiable)
1. [ ] Endpoint matches `docs/openapi.yaml` contract exactly (CI: Redocly lint).
2. [ ] Success uses standard envelope `{ status: "success", data: {...}, meta: null }`.
3. [ ] Errors use the fixed code set — no new codes without PRD change.
4. [ ] Refresh token ONLY in `HttpOnly; Secure; SameSite=Strict` cookie (never JSON body).
5. [ ] Unit tests cover AC 1–5; CI green.
6. [ ] No secrets/tokens logged; mutation recorded in `audit_logs` if applicable.

### Out of Scope (explicit)
- [e.g. Rate limiting — separate task T7. Do NOT add it here.]

### If Blocked
Escalate as `[OPEN QUESTION]` — do not guess requirements. Unspecified
security behavior defaults to the stricter baseline rule, and the deviation
MUST be flagged in the PR description.

---

## Task T2: [Short imperative name]

| Field | Value |
|---|---|
| **Traces to** | PRD Module F2 / User Story F2.1 (AC 1–4) |
| **Depends on** | T1 |
| **Type** | [Backend/Frontend/...] |
| **Size** | [XS/S/M] |

### Objective
[...]

### Files Touched
- [...]

### Context the Agent Needs
- [...]

### Definition of Done
1. [ ] ...

### Out of Scope
- [...]

---

## Execution Order & Parallelization

```text
T1 ──┬──> T2 ──> T4
     └──> T3 ──┘
```

- **Wave 1 (parallel):** T1
- **Wave 2 (parallel):** T2, T3
- **Wave 3:** T4 (needs both T2 and T3)

## Coverage Check (before handing to an agent)

- [ ] Every Module in `docs/PRD.md` maps to ≥ 1 task.
- [ ] Every User Story AC in `docs/PRD-detail.md` is covered by ≥ 1 DoD item.
- [ ] No task invents scope absent from the PRD (flag `[OPEN QUESTION]` instead).
- [ ] Security-critical ACs (token handling, anti-IDOR, audit logging, RTR)
      appear verbatim in the owning task's DoD — never weakened.
