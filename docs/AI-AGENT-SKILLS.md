# AI Agent Skills Catalogue & Integration Guide

This guide defines the specialized skills and toolings required by autonomous AI coding agents (such as Hermes Agent, Claude Code, and Cursor) to design, build, and audit software across all domains supported by this baseline.

---

## 🧭 Overview

AI agents produce significantly higher-quality code when equipped with specialized domain skills rather than relying solely on raw LLM training data. In this baseline, skills enforce:
1. **Architectural Discipline:** Creating PRDs, Threat Models (STRIDE), and visual diagrams before touching code.
2. **Cybersecurity Rigor:** Continuous secret detection, SAST analysis, and cryptographic hygiene.
3. **Domain Correctness:** Adhering to mobile Keystore rules, web cookie security, and trading risk formulas.

---

## � Portable Skills Shipped with This Baseline

The `skills/` folder ships ready-to-install **Agent Skills** (`SKILL.md` format, per the [Agent Skills specification](https://agentskills.io/specification)) that package this baseline's most critical guardrails for any skills-compatible agent (Claude Code, Codex, OpenCode):

| Skill | Guards | Status |
|---|---|---|
| `skills/quant-risk-guardian` | Hard SL, 1–2% dynamic lot sizing, 5% daily DD circuit breaker, 10% kill-switch | ✅ Shipped |
| `skills/adr-threat-model` | ADR format + complete STRIDE threat→control mapping (validator-compatible) | ✅ Shipped |
| `skills/mobile-appsec` | Keystore storage, SSL pinning, `FLAG_SECURE`, Play Integrity, biometric gating | ✅ Shipped |

Install with `npx skills add mochrzlf/aegis-forge` or copy manually per agent — see `skills/README.md`. The custom-rule rows in the matrix below (`adr-threat-model`, `mobile-appsec`, `quant-risk-guardian`) describe the same guardrails as enforced via `AGENTS.md`; the shipped skills are their portable, installable form.

---

## �📊 AI Agent Skills Matrix

| Domain | Skill Identifier | Installation / Source | Primary Capability |
|---|---|---|---|
| **Core** | `humanizer` | `hermes skills install blader/humanizer` | Strips AI cliches, buzzwords, and robotic phrasing from documentation and PRDs. |
| **Core** | `diagram-design` | `hermes skills install skills-sh/diagram-design` | Renders clean Mermaid, SVG, and visual architecture/sequence diagrams. |
| **Core** | `openapi-designer` | `hermes skills install stoplight/spectral` | Lints and validates REST API specifications to ensure enterprise standardization. |
| **Core** | `ui-wireframer` | Built-in / Vercel v0 / Generative UI | Rapidly prototypes frontend components and wireframes before actual implementation. |
| **Core** | `adr-threat-model` | Custom Rules in `AGENTS.md` | Automates the drafting of Architecture Decision Records (ADRs) and STRIDE Threat Models. |
| **Cybersecurity** | `security-audit` | Built-in via `scripts/devsec-check.sh` & Gitleaks | Scans staged code for hardcoded API keys, private keys, and `.env` leaks. |
| **Cybersecurity** | `semgrep-sast` | `.github/workflows/security.yml` | Scans for OWASP Top 10 vulnerabilities (SQLi, XSS, Broken Access Control). |
| **Web** | `modern-web-guidance` | Built-in / Modern Web Plugin | Best practices for Next.js App Router, Tailwind CSS, and WCAG accessibility. |
| **Mobile** | `mobile-appsec` | Custom Rules in `AGENTS.md` | Audits Android Keystore, SSL Pinning, and `FLAG_SECURE` screen protection. |
| **EA Trading** | `quant-risk-guardian` | Custom Rules in `AGENTS.md` | Enforces Hard Stop Loss, dynamic lot calculation, and the 5% daily drawdown circuit breaker. |
| **EA Trading** | `freqtrade` | External — `github.com/freqtrade/freqtrade` (**GPL-3.0** ⚠️) | End-to-end **crypto** algo bot: backtest, hyperopt, dry-run, live. Reference/separate deploy only — never copy source into derived projects. |
| **EA Trading** | `quantconnect-lean` | External — `github.com/QuantConnect/Lean` (**Apache-2.0** ✅) | Reference architecture for event-driven engines (data feeds, risk, kill-switch). Design reference only; C#/.NET, does not author MetaTrader EAs. |
| **EA Trading** | `vibe-trading` | External — `github.com/HKUDS/Vibe-Trading` (**MIT** ✅) | Optional research workspace: 10 backtest engines, Alpha Zoo, strategy export incl. MQL5. Research-only companion, not the execution core. |

---

## 🛠️ Domain Skills Breakdown

### 1. Core Writing & Visual Architecture Skills

While `humanizer` and `diagram-design` serve as the foundation for clear documentation and visual blueprints, a complete enterprise agent should also possess the following expanded writing and design skills:

#### A. Humanizer (`blader/humanizer`)
- **Purpose:** Rewrites AI-generated documentation (PRDs, READMEs, architecture decisions) into natural, direct, and senior-engineer prose based on Wikipedia's *Signs of AI Writing* cleanup guidelines.
- **When to Invoke:** Whenever the AI agent writes or updates `docs/PRD.md`, `docs/PRD-detail.md`, or release notes.

#### B. Diagram Design (`skills-sh/diagram-design`)
- **Purpose:** Generates visual system diagrams, token lifecycle sequences, and network topologies in Mermaid or standalone SVG format.
- **When to Invoke:** Before creating new API routes, databases, or modules, ensuring team alignment in `docs/diagrams/`.

#### C. API Contract Designer (`stoplight/spectral` or similar)
- **Purpose:** Automatically validates `docs/openapi.yaml` against OpenAPI v3 rules (e.g., ensuring all endpoints have security definitions, error schemas, and pagination metadata).
- **When to Invoke:** During the backend design phase, strictly before any controller or router code is written.

#### D. UI Wireframer & Prototyping
- **Purpose:** Allows the AI Agent to render interactive UI mockups or HTML/Tailwind wireframes based on `docs/ui-design-template.md`.
- **When to Invoke:** During frontend PRD definition to validate user experience (UX) and component layout before locking the design.

#### E. ADR & Threat Modeling Generator
- **Purpose:** Automates the drafting of Architecture Decision Records (ADRs) and STRIDE Threat Models based on the proposed system architecture.
- **When to Invoke:** Prior to adopting a new technology, library, or security flow.

---

### 2. Cybersecurity & DevSecOps Skills

#### A. Secret Shield (`gitleaks` & `devsec-check`)
- **Purpose:** Intercepts every commit to ensure credentials, private keys, and environment variables never enter Git history.
- **Command:**
  ```bash
  make audit        # Full repository scan
  make audit-staged # Staged commit scan (pre-commit)
  ```

#### B. Static Application Security Testing (SAST)
- **Engine:** Semgrep & Trivy (automated in GitHub Actions).
- **Rulesets:** OWASP Top 10, CWE Top 25, and container dependency audits.

---

### 3. Web Engineering Skills

- **Cookie & Session Guardrails:** Enforces `HttpOnly; Secure; SameSite=Strict` cookie transport for refresh tokens (RFC 6749). Prohibits storing refresh tokens in client `localStorage`.
- **API Contract Adherence:** Verifies that all response payloads strictly match `docs/openapi.yaml` format.
- **Accessibility & Performance:** Enforces WCAG 2.1 AA contrast ratios and Core Web Vitals (LCP < 2.5s, INP < 200ms).

---

### 4. Mobile Engineering Skills (Android & iOS)

- **Hardware Keystore Verification:** Validates that mobile code uses `EncryptedSharedPreferences` backed by the **Android Keystore System** instead of plain `SharedPreferences`.
- **Network Security Configuration:** Verifies that `res/xml/network_security_config.xml` enforces HTTPS and public key pinning (SSL Pinning).
- **Screen Obfuscation:** Confirms that `FLAG_SECURE` is active on sensitive UI views.

---

### 5. Algorithmic & EA Trading Skills

- **Capital Preservation First:** Rejects any order dispatch that lacks a calculated **Hard Stop Loss (SL)**.
- **Dynamic Lot Sizing Formula:** Calculates position size based on a strict 1% to 2% equity risk parameter.
- **Autonomous Circuit Breaker:** Kills all open positions, cancels pending orders, and halts trading if the daily floating loss hits 5%.
- **API Key Segregation:** Prohibits trading agents from using exchange API keys with *Withdrawal* permissions enabled.

#### External Tooling (Optional — select by instrument, see `docs/blueprints/ea-trading-blueprint.md` §6)

- **freqtrade** (**GPL-3.0** ⚠️): Full-featured **crypto** trading bot (backtest, hyperopt, dry-run, live via ccxt). Use for crypto sub-domain research or isolated deployment only. Its GPL-3.0 copyleft means its source must **never** be copied into an Apache-2.0 derived project — reference or run it standalone.
- **QuantConnect Lean** (**Apache-2.0** ✅): Professional event-driven trading engine. Treat as an **architectural reference** for how to model data feeds, transaction handlers, and risk kill-switches. It is C#/.NET and does not produce MetaTrader EAs — do not add it as a project dependency.
- **Vibe-Trading** (**MIT** ✅): Natural-language finance research workspace with 10 backtest engines, an Alpha Zoo, and strategy export (including MQL5). Use as an **optional research-phase companion**; it is research-only (read-only, no custody) and is not the hardened execution core.

> ⚠️ **Boundary for all trading tools:** Adopting any external tool does not waive the Capital Preservation Doctrine — Hard SL, 1–2% dynamic sizing, and the 5% daily drawdown circuit breaker remain mandatory regardless of the tool used.

---

## 💡 How to Instruct Your AI Agent

When kicking off a task, reference these skills directly:

```text
"Read AGENTS.md. We are building a mobile application for user authentication.
First, consult docs/blueprints/mobile-application-blueprint.md and docs/security/mobile-security-checklist.md.
Draft the architecture diagram in docs/diagrams/ and apply humanizer to docs/PRD.md so the text is clear and human.
Validate the API design using OpenAPI standards, and ensure Android Keystore storage is used for token caching."
```
