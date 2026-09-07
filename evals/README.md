# Evals — AI Agent Output Quality Harness

> **Purpose:** Measure — not assume — whether the AI agent's output actually obeys the baseline's non-negotiable rules (API envelope, cookie security, RBAC, trading risk gates, contract compliance). A scenario is a small task; a rubric scores the result.
>
> **Status:** Skeleton. Scenarios + rubrics are defined and ready; wire them to a runner (recommended: **promptfoo**, MIT) when you're ready to execute. See `docs/research/EXTERNAL-TOOLS.md` §4.

---

## Layout

```
evals/
├── README.md                 ← this file
├── promptfooconfig.yaml      ← runner config (promptfoo) — optional until runner is chosen
├── scenarios/                ← one YAML per task the agent must perform
│   └── web-auth-endpoint.yaml
└── rubrics/                  ← scoring criteria per scenario
    └── web-auth-endpoint.md
```

---

## How It Works

1. **Scenario** (`scenarios/*.yaml`): a self-contained task (prompt + context + expected artifacts).
2. **Rubric** (`rubrics/*.md`): pass/fail + weighted criteria the output is judged against (e.g., "refresh token is NOT in localStorage").
3. **Runner**: executes the scenario against the agent, then scores the output against the rubric (LLM-as-judge and/or deterministic assertions).

### Two scoring modes (use both where possible)
- **Deterministic assertions** — cheap, objective: "output contains `SameSite=Strict`", "OpenAPI has `securitySchemes`", "no `localStorage.setItem.*refresh`".
- **LLM-as-judge** — for qualitative rubric items: "is the STRIDE mitigation concrete and mapped to a control?"

---

## Run (once a runner is adopted)

```bash
# Recommended runner (MIT): https://github.com/promptfoo/promptfoo
npx promptfoo@latest eval -c evals/promptfooconfig.yaml
npx promptfoo@latest view   # browse results
```

> The provided `promptfooconfig.yaml` is a ready-to-adapt template. Fill in your provider/model and point `tests` at `scenarios/*.yaml`.

---

## Adding a New Eval

1. Create `scenarios/<name>.yaml` — prompt, any seed files, and `assert` (deterministic checks).
2. Create `rubrics/<name>.md` — the human-readable criteria (used for LLM-as-judge).
3. Keep each scenario **small and single-responsibility** (mirrors the prompt library's single-task rule).

### Scenario naming
`<domain>-<capability>` → e.g. `web-auth-endpoint`, `mobile-token-storage`, `trading-risk-gate`, `api-contract-envelope`.

---

## Baseline Eval Suite (target coverage)

| # | Scenario | Verifies | Domain |
|---|---|---|---|
| 1 | `web-auth-endpoint` | HttpOnly cookie, no localStorage refresh token, API envelope | 🌐 |
| 2 | `mobile-token-storage` | Keystore/EncryptedSharedPreferences, no plain SharedPreferences | 📱 |
| 3 | `trading-risk-gate` | Dynamic lot (1-2%), Hard SL present, 5% DD kill-switch | 📈 |
| 4 | `api-contract-envelope` | Standard success/error payload, pagination meta | 🔧 |
| 5 | `rbac-enforcement` | Server-side role check per access matrix | 🏢 |
| 6 | `stride-adr-quality` | STRIDE ADR has threat→control mapping | 🔧 |

Start with #1 (provided as a worked example). Add the rest incrementally.
