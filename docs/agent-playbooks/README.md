# Agent Playbooks

> **What this is:** Deterministic, step-by-step workflows that turn `AGENTS.md` from *passive rules* into *active procedure*. Each playbook tells the AI agent (or human) exactly **what to do, in what order, and how to verify each step** before moving on.
>
> **How to use:** At session start, the agent reads `AGENTS.md`, then opens the playbook matching the project domain (`TYPE=web|mobile|trading|fullstack`). Follow the steps in order. Do NOT skip a gate — a step is only "done" when its verification checklist passes.

---

## Available Playbooks

| Playbook | Domain | When to Use |
|---|---|---|
| [`web-app-playbook.md`](web-app-playbook.md) | 🌐 Web / SaaS | New web application or significant web feature. |
| [`mobile-app-playbook.md`](mobile-app-playbook.md) | 📱 Mobile (Android/iOS) | New mobile app or significant mobile feature. |
| [`trading-ea-playbook.md`](trading-ea-playbook.md) | 📈 EA / Algo Trading | New EA, strategy, or trading-bot change. |
| [`fullstack-playbook.md`](fullstack-playbook.md) | 🏢 Fullstack / Enterprise | Combined web+backend+mobile or unsure. |

---

## The Universal Pipeline (All Playbooks Follow This)

Every playbook is a domain-specialized version of the same gated pipeline. **Specification first, code last.**

```
PHASE 0  Context Load      → Read AGENTS.md + domain blueprint + security checklist
PHASE 1  Specify           → PRD.md + PRD-detail.md (user stories + acceptance criteria)
PHASE 2  Threat Model      → STRIDE analysis in docs/adr/ (new ADR)
PHASE 3  Contract          → openapi.yaml (API) + schema.sql (DB) — linted & validated
PHASE 4  Design            → ui-design.md (tokens, mockups) + diagrams/
PHASE 5  Implement         → Code that 100% matches the contracts above
PHASE 6  Verify            → Tests + security audit + contract compliance check
```

### Gate Discipline
- A **gate** between phases means: you may not proceed until the phase's artifacts exist AND pass their verification checklist.
- If a later phase reveals a contract problem, **go back and fix the contract first**, then re-run the affected phases. Never patch code to diverge from the spec silently.
- Any change to infrastructure, schema, auth flow, or workflow **requires a new ADR** (see `docs/adr/`).

---

## Playbook Authoring Rules (for contributors)

1. Steps must be **imperative and atomic** ("Draft X", "Validate Y") — not vague goals.
2. Every phase ends with a **verification checklist** the agent can self-evaluate.
3. Reference concrete files/paths, not concepts.
4. Keep domain constraints (security, risk) **inline in the steps**, not buried in appendices.
