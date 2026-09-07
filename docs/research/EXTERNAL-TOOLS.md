# External Tools & Research — Adoption Register

> **Purpose:** Single source of truth for every external repository, tool, or skill evaluated for the Aegis Forge baseline. Each entry records the verdict, license, role, and constraints so that AI agents and humans make consistent, legally compliant adoption decisions.
>
> **How to read this:** A tool is only **Adopted** if it passes all four gates in §2. Anything **Rejected** lists its disqualifying reason so it is not re-evaluated repeatedly.

---

## 1. Adoption Verdict Legend

| Verdict | Meaning |
|---|---|
| ✅ **Adopted — Recommended** | Referenced in docs as an optional, recommended tool. Safe to suggest to derived projects. |
| 🔗 **Adopted — Reference Only** | Used as an architectural/design reference or for isolated deployment. Never a hard dependency, never copy source into derived projects. |
| 🧪 **Experimental** | Under evaluation. May be suggested with caveats; not yet part of the standard toolkit. |
| ❌ **Rejected** | Evaluated and disqualified. Reason recorded; do not re-propose without new evidence. |

---

## 2. The Four Adoption Gates (Non-Negotiable)

Every external tool MUST pass all four before being marked *Adopted — Recommended*:

1. **License Gate** — Only permissive licenses (**MIT, Apache-2.0, BSD**) may be *recommended*. **GPL/AGPL/SSPL** tools are at most *Reference Only* (learn from, or run standalone/isolated) and their source must never be copied into an Apache-2.0 derived project.
2. **Maintenance Gate** — Actively maintained (commits within ~6 months, responsive issues), or stable/mature enough that low activity is acceptable.
3. **Dependency Gate** — Adopted as *optional/recommended*, never a hard requirement for a scaffolded project. The baseline must stay portable without it.
4. **Zero-Trust Gate** — Any tool touching credentials, CI, or execution must support version pinning and run with least privilege. Network-facing or broker/exchange-connected tools get extra scrutiny.

---

## 3. Register by Domain

### 3.1 Core / Cross-Domain

| Tool | Verdict | License | Role in Baseline | Constraints / Notes |
|---|---|---|---|---|
| **blader/humanizer** | ✅ Adopted — Recommended | Check upstream | Strips AI cliches from PRDs/docs (humanizer skill). | Already in README Step 2 & skills matrix. |
| **skills-sh/diagram-design** | ✅ Adopted — Recommended | Check upstream | Mermaid/SVG architecture & sequence diagrams. | Already in README Step 2 & skills matrix. |
| **Gitleaks** | ✅ Adopted — Core | MIT | Secret detection (pre-commit + CI). | Core, not optional. Pinned in `.pre-commit-config.yaml`. |
| **Semgrep** | ✅ Adopted — Core | LGPL-2.1 (engine) / rules various | SAST (OWASP Top 10, CWE 25) in CI. | Runs via CLI in CI (the old `returntocorp/semgrep-action` is archived — do not use). |
| **Trivy** | ✅ Adopted — Core | Apache-2.0 | Filesystem/dependency vulnerability scanning, SARIF. | Pinned action version (`trivy-action@0.33.1`). |
| **Stoplight Prism** | ✅ Adopted — Core | Apache-2.0 | Mock API server from `docs/openapi.yaml` (port 4010). | Already in docker-compose. |
| **Redocly CLI** | ✅ Adopted — Core | MIT | OpenAPI lint/validation (pre-commit + CI). | Validates API contract before backend code. |
| **sqlfluff** | ✅ Adopted — Core | MIT | PostgreSQL schema lint (pre-commit). | `--dialect postgres`. |

### 3.2 Frontend / UI-UX

| Tool | Verdict | License | Role in Baseline | Constraints / Notes |
|---|---|---|---|---|
| **nextlevelbuilder/ui-ux-pro-max-skill** | ✅ Adopted — Recommended | MIT ✅ | Design intelligence: ~79 UI styles, 192 palettes, 73 font pairings, design-system/token generator. | Fills the UI/UX gap; aligns with web/mobile stacks (React/Next/Tailwind/Compose/SwiftUI). Needs Python 3 + Node on dev machine. Recommend per-domain (web/mobile), NOT for trading. |
| **amzn/style-dictionary** | 🧪 Experimental | Apache-2.0 ✅ | Design-tokens pipeline (tokens → Tailwind/CSS/Compose/Swift). | Candidate for Phase 4 (Frontend & Design System). Verify before adopting. |
| **storybookjs/storybook** | 🧪 Experimental | MIT ✅ | Component workshop + a11y addon. | Candidate for Phase 4 frontend testing standard. |
| **dequelabs/axe-core** | 🧪 Experimental | MPL-2.0 ✅ | Accessibility testing engine. | Pair with frontend QA checklist; MPL-2.0 is weak copyleft (file-level) — acceptable as a test dependency. |

### 3.3 Backend / API / Data

| Tool | Verdict | License | Role in Baseline | Constraints / Notes |
|---|---|---|---|---|
| **schemathesis/schemathesis** | 🧪 Experimental | MIT ✅ | Property-based API testing driven by `docs/openapi.yaml`. | Strong fit for contract testing (Phase 6). Verify before adopting. |
| **pact-foundation/pact** | 🧪 Experimental | Apache-2.0 ✅ | Contract testing (consumer-driven). | Alternative/complement to Schemathesis for Phase 6. |
| **pressly/goose / flyway / golang-migrate / Alembic** | 🧪 Experimental | Varies (MIT/BSD/Apache) | Schema migration standards. | Pick per stack in `docs/migrations.md` (Phase 3). Do not adopt all — document a decision. |
| **OpenTelemetry (spec + semconv)** | ✅ Adopted — Reference | Apache-2.0 ✅ | Naming/semantic conventions for `docs/observability.md`. | Reference the standard; language SDKs chosen per project. |

### 3.4 EA / Algorithmic Trading

| Tool | Verdict | License | Role in Baseline | Constraints / Notes |
|---|---|---|---|---|
| **MQL5 + MT5 Strategy Tester + MetaAPI** | ✅ Adopted — Core (trading) | Proprietary (MetaQuotes) + MetaAPI SDK | Default stack for Forex/CFD EAs. | The ONLY path that compiles a real MetaTrader EA (`.ex5`). Already the baseline's trading stack. |
| **freqtrade/freqtrade** | 🔗 Adopted — Reference Only | **GPL-3.0** ⚠️ | End-to-end **crypto** bot: backtest, hyperopt, dry-run, live (ccxt). Matches baseline's Python/ccxt stack. | **Crypto-only**; no MetaTrader. GPL-3.0 → learn from it or deploy standalone; NEVER copy source into an Apache-2.0 derived project. |
| **QuantConnect/Lean** | 🔗 Adopted — Reference Only | **Apache-2.0** ✅ | Reference architecture for event-driven engine (data feeds, transaction handlers, risk, kill-switch). | C#/.NET — design reference, NOT a dependency. Does NOT author MetaTrader EAs. Safe to adapt patterns (permissive license). |
| **HKUDS/Vibe-Trading** | 🔗 Adopted — Reference Only | **MIT** ✅ | Optional research workspace: 10 backtest engines, Alpha Zoo (462 alphas), strategy export incl. MQL5. | Research-only (read-only, no custody). Heavy optional companion for the research phase — not the execution core. Keep the lean baseline stack for execution. |

### 3.5 Rejected

| Tool | Verdict | Reason Disqualified |
|---|---|---|
| **Fincept-Corporation/FinceptTerminal** | ❌ Rejected | Financial data/analytics **desktop terminal**, not a trading/bot framework. No MetaTrader/MQL support. **AGPL-3.0** strong copyleft is incompatible with this Apache-2.0 baseline. Core algo/live features locked behind paid tiers. Do not re-propose. |
| **returntocorp/semgrep-action** | ❌ Rejected | GitHub Action is **archived/deprecated**. Replaced by running Semgrep via its official CLI in CI. |

---

## 4. Pending Evaluation Backlog (Roadmap Phases)

These were shortlisted but not yet verified. Evaluate against the Four Gates before adopting.

| Phase | Candidate | Purpose | Status |
|---|---|---|---|
| 1 — Agent Enablement | `promptfoo/promptfoo` | Eval harness for agent output quality | 🧪 To verify |
| 1 — Agent Enablement | `github/awesome-copilot` | Prompt/instruction library source | 🧪 To verify |
| 1 — Agent Enablement | `anthropics/skills` | SKILL.md structure reference | 🧪 To verify |
| 1 — Agent Enablement | `modelcontextprotocol/servers` | MCP servers (filesystem, git, postgres) | 🧪 To verify |
| 2 — Security | `ossf/scorecard` | OpenSSF security posture scoring | 🧪 To verify |
| 2 — Security | `anchore/sbom-action` / `syft` | SBOM generation | 🧪 To verify |
| 2 — Security | `OWASP/CheatSheetSeries` | Basis for `web-security-checklist.md` | ✅ Adopt as reference (cite, don't copy wholesale) |
| 2 — Security | `OWASP/owasp-masvs` | Mobile security standard reference | ✅ Adopt as reference |
| 5 — DevOps | `devcontainers/templates` | Dev container templates | 🧪 To verify |

---

## 5. Maintenance Rules for This Register

1. **One entry, one row.** Do not scatter tool decisions across README/blueprints — link back here instead.
2. **Record rejections.** A rejected tool with a documented reason saves future re-evaluation effort.
3. **Re-check on version bumps.** If a Recommended tool changes license or goes unmaintained, move it to Rejected or Reference Only immediately.
4. **License changes win.** A tool's current license at time of use governs; re-verify before each major adoption.
