# Prompt Library

> **Purpose:** Tested, copy-paste prompts for each development phase, per domain. These are starting points — fill in `[PLACEHOLDERS]` and adapt. They are written to enforce the gated pipeline in `docs/agent-playbooks/`.
>
> **Convention:** Every prompt begins by anchoring the agent to `AGENTS.md` and the relevant playbook/blueprint, then states a single, verifiable task. Never ask for code before the specification phases are done.

---

## How to Use

1. Pick the row matching your **domain** and **phase**.
2. Replace `[PROJECT_NAME]`, `[INSTRUMENT]`, etc.
3. Run phases **in order** — a Phase N prompt assumes Phase N-1 artifacts already exist.

Legend: 🌐 Web · 📱 Mobile · 📈 Trading · 🏢 Fullstack · 🔧 Any

---

## PHASE 1 — Specify

| Domain | Prompt |
|---|---|
| 🔧 Kickoff | `Read AGENTS.md, then open the playbook at docs/agent-playbooks/[DOMAIN]-playbook.md. Draft docs/PRD.md and docs/PRD-detail.md for [PROJECT_NAME] from docs/PRD-template.md and docs/PRD-detail-template.md, based on docs/blueprints/[BLUEPRINT]. Every user story needs at least one testable acceptance criterion. Do not write any code yet.` |
| 📈 Strategy | `Read AGENTS.md and docs/security/trading-risk-policy.md. Draft a Strategy Specification for [INSTRUMENT] on timeframe [TF]: entry/exit rules, session/news filters, risk-per-trade (1-2%), max daily drawdown (5%), and max simultaneous exposure. Make every rule machine-translatable. Confirm the toolchain via docs/blueprints/ea-trading-blueprint.md §6.1.` |

## PHASE 2 — Threat Model

| Domain | Prompt |
|---|---|
| 🔧 STRIDE | `Following docs/adr/ADR-001-Threat-Modeling-Standard.md, create a new ADR (next number) performing a STRIDE threat analysis for [PROJECT_NAME]. Cover [DOMAIN-SPECIFIC THREATS]. Map each threat to a concrete control. Output only the ADR file.` |
| 🌐 Web threats | `...STRIDE for the web app: session hijacking, CSRF, XSS, broken access control (RBAC bypass), injection. Reference docs/security-iam-policy.md for controls.` |
| 📱 Mobile threats | `...STRIDE for the mobile app: token theft from insecure storage, MITM without SSL pinning, screenshot/shoulder-surfing, rooted device, insecure deep links. Reference docs/security/mobile-security-checklist.md.` |
| 📈 Trading threats | `...STRIDE for the trading system: API-key compromise (withdrawal permission), runaway/martingale logic, execution without a Hard Stop Loss, data-feed failure, VPS/runtime hang. Reference docs/security/trading-risk-policy.md.` |

## PHASE 3 — Contract

| Domain | Prompt |
|---|---|
| 🔧 API | `Design/extend docs/openapi.yaml for the endpoints implied by docs/PRD-detail.md. Every endpoint must use the standard success/error envelope, declare a security scheme, and paginate list endpoints. Lint it (Redocly) until clean. Do not write controllers yet.` |
| 🔧 DB | `Design/extend docs/schema.sql for the entities in docs/PRD-detail.md. Include constraints, indexes, and audit columns (created_at/updated_at). Validate it parses under the PostgreSQL dialect. Do not write migrations yet.` |
| 📱 Mobile contract | `Design docs/openapi.yaml for the backend endpoints the app consumes, matching the token lifecycle in docs/diagrams/mobile-auth-sequence.md. Then confirm the app can run against the Prism mock (make mock-api, port 4010).` |

## PHASE 4 — Design

| Domain | Prompt |
|---|---|
| 🌐/📱 Tokens | `Produce docs/ui-design.md from docs/ui-design-template.md for [PROJECT_NAME]. Use the ui-ux-pro-max skill to generate the design-token set (color palette, typography pairing, spacing scale) from the product type in docs/PRD.md. Components must reference tokens — no hardcoded values. State WCAG 2.1 AA contrast compliance.` |
| 🌐/📱 Diagram | `Add a Mermaid diagram to docs/diagrams/ showing [FLOW: e.g. auth token lifecycle / order execution]. Keep it consistent with docs/diagrams/system-architecture-universal.md.` |

## PHASE 5 — Implement

| Domain | Prompt |
|---|---|
| 🌐 Web build | `Implement the Next.js/React frontend and [NestJS/FastAPI/Express] backend exactly matching docs/openapi.yaml. Auth uses HttpOnly Secure SameSite=Strict cookie sessions with refresh-token rotation; never store refresh tokens in localStorage. Enforce RBAC per docs/security-access-matrix.md on the server side.` |
| 📱 Mobile build | `Implement the app with Clean Architecture ([Kotlin+Compose / Flutter / React Native]). Store tokens in EncryptedSharedPreferences (Android Keystore) / Keychain (iOS), enforce HTTPS + SSL pinning, and apply FLAG_SECURE on sensitive screens. Build against the mock API first.` |
| 📈 Trading build | `Implement the strategy from the Strategy Spec in [MQL5 / Python ccxt+MetaAPI]. MANDATORY: every order passes the Pre-Trade Risk Gate (dynamic lot 1-2%, spread/margin/exposure checks) and attaches a Hard Stop Loss; implement the 5% daily-drawdown circuit breaker; log every order ticket + slippage to PostgreSQL. No static lots, no unbounded martingale, no withdrawal-enabled API keys.` |

## PHASE 6 — Verify

| Domain | Prompt |
|---|---|
| 🔧 Review | `Review the implementation against docs/openapi.yaml and docs/schema.sql for 100% contract compliance, and against the domain security checklist. List every deviation with file:line. Then run make audit and report the result.` |
| 📈 Validate | `Run the 5-gate anti-overfitting validation from docs/blueprints/ea-trading-blueprint.md §3 (In-Sample, Out-of-Sample, Walk-Forward, Paper, Incubation). Report the acceptance metrics per gate and flag any gate that fails. Do not proceed to live capital unless all pass.` |

---

## Maintenance Rules

1. A prompt is only added here after it has produced a correct artifact at least once.
2. Keep prompts **single-task**; chain them via phases rather than writing one giant prompt.
3. If a prompt repeatedly produces contract violations, tighten its verification clause — don't just re-run it.
