---
name: spec-to-tasks
description: Converts a finished PRD + PRD-detail into agent-ready atomic tasks following docs/TASK-template.md. Use whenever asked to break a spec, PRD, or feature into tasks/steps/implementation units for a coding agent. Enforces traceability (every task traces to a PRD module + AC), token economy (reference docs by path, never paste), and a confirmation gate before writing.
---

# Spec → Tasks

A PRD without a task breakdown forces the coding agent to plan AND execute
in one shot — the #1 cause of blown context, half-implemented features, and
invented scope. This skill produces `docs/TASKS.md`: atomic, traceable,
agent-ready tasks. Source of truth for the output format:
`docs/TASK-template.md`. Output that does not follow it is defective.

## Prerequisites (check FIRST — refuse politely if missing)

1. `docs/PRD.md` exists and is not a skeleton of placeholders.
2. `docs/PRD-detail.md` exists with real user stories + acceptance criteria.

If either is missing or still full of `[brackets]`, stop and tell the user
to finish the PRD first — recommend the **prd-interviewer** skill. Never
invent PRD content to fill the gap: that re-creates the hallucinated-
requirements problem one level down.

## Process

### Step 1 — Inventory (read, don't guess)
Read `docs/PRD.md` (modules, IAM matrix, NFRs) and `docs/PRD-detail.md`
(stories + ACs). List: every module F#, every story, every AC, every
security-critical AC (token handling, RTR, anti-IDOR, audit logging).

### Step 2 — Draft the task graph
For each module, propose tasks. Rules:

- **Atomic:** one task = one type of work, ≤ a handful of files, size XS/S/M.
  Anything that feels like "L" must be split and you must say why.
- **Traceable:** every task names its Module F# + Story + AC numbers. A task
  with no trace is invented scope — delete it or mark `[OPEN QUESTION]`.
- **Dependencies explicit:** state `Depends on` honestly. Parallelizable
  tasks must not secretly depend on each other.
- **Security ACs travel:** any story whose ACs mention token/RTR/anti-IDOR/
  audit must have those ACs copied VERBATIM into the owning task's
  Definition of Done. Never soften them to "make auth work".
- **Context by reference:** the "Context the Agent Needs" field lists paths
  (`AGENTS.md` §, `docs/...`, `skills/...`). NEVER paste document contents
  into the task — token economy is a baseline requirement.
- **Skeleton hint is mandatory when a starter skeleton exists** (`templates/`
  has the project's domain): each task names the EXISTING skeleton file to
  EDIT (e.g. `templates/web-app/backend/app/api/auth.py`) so the agent
  modifies rather than generates from scratch. If no skeleton file covers the
  task, write `new` and justify why the skeleton doesn't cover it.
- **Out of Scope is mandatory:** every task states what it will NOT do, so
  the agent doesn't gold-plate.

### Step 3 — Confirmation gate (mandatory)
Before writing `docs/TASKS.md`:

1. Present the task list: ID, name, traces-to, size, depends-on.
2. Present the coverage check: modules → tasks mapping, and any PRD area
   with NO task (either say why it's deferred, or add a task).
3. Ask: "Is this breakdown correct? Any task to split, merge, or drop?"
4. Only after an affirmative answer, write the file.

### Step 4 — Write
Follow `docs/TASK-template.md` section-for-section. Save to `docs/TASKS.md`.
End with the Execution Order (waves) + Coverage Check filled in truthfully.

## Anti-Patterns to Refuse

- Writing tasks from a PRD that doesn't exist yet
- One giant task per module ("T1: implement auth") — that is a module, not a task
- Pasting entire PRD sections into task context (token blow-up)
- Dropping security ACs from DoD because "the PRD already says them" —
  the coding agent reads the TASK, not the PRD
- Silent dependencies between "parallel" tasks
- Inventing tasks for features the PRD never specified — mark
  `[OPEN QUESTION]` and ask instead
