# Aegis Forge — Portable Agent Skills

This folder contains **portable Agent Skills** (`SKILL.md`, following the
[Agent Skills specification](https://agentskills.io/specification)) that package
the baseline's non-negotiable rules so any skills-compatible agent
(Claude Code, Codex, OpenCode, …) can load them dynamically.

> **Why skills, not just docs?** `AGENTS.md` is a working contract the agent is
> *asked to read*. A skill is a capability the agent *loads when relevant* —
> far harder to miss mid-session. The `docs/` documents remain the source of
> truth; skills are faithful summaries that point back to them.

## Shipped Skills

| Skill | Guards | Source of truth |
|---|---|---|
| [`quant-risk-guardian`](quant-risk-guardian/SKILL.md) | Hard SL, 1–2% dynamic lot sizing, 5% daily DD circuit breaker, 10% kill-switch, no-withdrawal API keys | `docs/security/trading-risk-policy.md` |
| [`adr-threat-model`](adr-threat-model/SKILL.md) | ADR format (metadata, status, sections) + complete STRIDE threat→control mapping, validator-compatible | `docs/adr/ADR-000-template.md`, `docs/adr/ADR-001-*.md`, `scripts/validate_adrs.py` |
| [`mobile-appsec`](mobile-appsec/SKILL.md) | Keystore/EncryptedSharedPreferences, SSL pinning, FLAG_SECURE, Play Integrity, biometric-gated ops | `docs/security/mobile-security-checklist.md` |
| [`api-contract-envelope`](api-contract-envelope/SKILL.md) | Standard success/error payload envelope, fixed error-code set, pagination `meta`, HTTP↔code mapping | `AGENTS.md` §3.1, `docs/openapi.yaml` |
| [`rbac-enforcement`](rbac-enforcement/SKILL.md) | Server-side role checks, IDOR/BOLA ownership predicates, maker-checker, JML kill-switch, immutable audit trail | `AGENTS.md` §3.2, `docs/security-access-matrix.md`, `docs/security-iam-policy.md` |

> **Coverage:** every scenario in `evals/scenarios/` now has a companion skill
> that enforces the rule being evaluated — what is tested is also taught.

## Installation

### Any skills-compatible agent (via `npx skills`)

```bash
npx skills add mochrzlf/aegis-forge
```

### Claude Code (manual)

Copy the skill folder(s) into your project's `.claude/skills/` directory:

```bash
cp -r skills/quant-risk-guardian /path/to/your-project/.claude/skills/
```

### Codex (manual)

Copy the skill folder(s) into your Codex skills path (typically `~/.codex/skills`).

### OpenCode (manual)

Clone into the OpenCode skills directory so the layout is
`~/.opencode/skills/aegis-forge/skills/<skill-name>/SKILL.md`:

```bash
git clone https://github.com/mochrzlf/aegis-forge.git ~/.opencode/skills/aegis-forge
```

Restart the agent after installing. Invoke by mentioning the skill, e.g.
*"Use quant-risk-guardian to review this MQL5 order module."*

## Maintenance Rules

1. **Docs are the source of truth.** When a policy/checklist changes, update
   the corresponding `SKILL.md` in the same PR.
2. **Skills stay domain-scoped and single-responsibility** — one guardrail set
   per skill, mirroring `docs/agent-playbooks/` conventions.
3. **No secrets, no environment specifics** inside skills — they are portable
   rule summaries, not configuration.
