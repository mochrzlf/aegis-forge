# Evals — AI Agent Output Quality Harness

> **Purpose:** Measure — not assume — whether the AI agent's output actually obeys the baseline's non-negotiable rules (API envelope, cookie security, RBAC, trading risk gates, contract compliance). A scenario is a small task; a rubric scores the result.
>
> **Status:** Skeleton. Scenarios + rubrics are defined and ready; wire them to a runner (recommended: **promptfoo**, MIT) when you're ready to execute. See `docs/research/EXTERNAL-TOOLS.md` §4.

---

## Layout

```
evals/
├── README.md                 ← this file
├── promptfooconfig.yaml      ← reference config + run instructions
├── prompts/                  ← one .txt per scenario (the task text sent to the model)
│   └── web-auth-endpoint.txt
├── scenarios/                ← one YAML per scenario (description + assertions)
│   └── web-auth-endpoint.yaml
├── suites/                   ← one runnable promptfoo config per scenario (1 prompt ↔ 1 scenario)
│   └── web-auth-endpoint.yaml
└── rubrics/                  ← scoring criteria per scenario
    └── web-auth-endpoint.md
```

> **Why `suites/`?** A single promptfoo config with N prompts × M scenarios
> produces an N×M cross product (mismatched assertions). One config per
> scenario in `suites/` keeps each prompt paired 1:1 with its assertions.
> The provider is any OpenAI-compatible endpoint read from `.env`
> (`EVAL_API_BASE_URL`, `EVAL_MODEL`, `EVAL_API_KEY`).

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

**Recommended path — guarded launcher (interactive key setup + cost confirmation):**

```powershell
# Windows (PowerShell)
pwsh scripts/run-evals.ps1                      # guarded run, all suites
pwsh scripts/run-evals.ps1 -Suite prd-interview # run one suite
pwsh scripts/run-evals.ps1 -View                # run + open results viewer
```

```bash
# Linux / macOS / Git Bash / WSL
bash scripts/run-evals.sh                       # guarded run, all suites
bash scripts/run-evals.sh prd-interview         # run one suite
bash scripts/run-evals.sh --view                # run + open results viewer
```

The guard script:
1. verifies `npx` is available,
2. checks for a generic OpenAI-compatible provider in `.env` (`EVAL_API_BASE_URL` / `EVAL_MODEL` / `EVAL_API_KEY`) and, if missing, offers a **masked** interactive prompt that stores them in the local `.env` (git-ignored, gitleaks-protected) — keys are never echoed or committed,
3. asks for explicit confirmation before any **paid** API call,
4. runs the per-scenario configs in `evals/suites/`.

**Manual path (single scenario):**

```bash
# Set the provider in .env first (EVAL_API_BASE_URL / EVAL_MODEL / EVAL_API_KEY),
# or export them in your shell, then:
npx promptfoo@latest eval -c evals/suites/web-auth-endpoint.yaml --no-cache
npx promptfoo@latest view   # browse results
```

> The suites use promptfoo's generic `http` provider (not `openai:chat`) so the
> request body is explicit (`stream:false`) and the response transform is fixed
> — this avoids SSE-parsing failures against OpenAI-compatible routers that
> force streaming. See `evals/suites/` for the pattern.

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
