# AI Agent Skills Catalogue & Integration Guide

This guide defines the specialized skills and toolings required by autonomous AI coding agents (such as Hermes Agent, Claude Code, and Cursor) to design, build, and audit software across all domains supported by this baseline.

---

## 🧭 Overview

AI agents produce significantly higher-quality code when equipped with specialized domain skills rather than relying solely on raw LLM training data. In this baseline, skills enforce:
1. **Architectural Discipline:** Creating PRDs, Threat Models (STRIDE), and visual diagrams before touching code.
2. **Cybersecurity Rigor:** Continuous secret detection, SAST analysis, and cryptographic hygiene.
3. **Domain Correctness:** Adhering to mobile Keystore rules, web cookie security, and trading risk formulas.

---

## 📊 AI Agent Skills Matrix

| Domain | Skill Identifier | Installation / Source | Primary Capability |
|---|---|---|---|
| **Core** | `humanizer` | `hermes skills install blader/humanizer` | Strips AI cliches, buzzwords, and robotic phrasing from documentation and PRDs. |
| **Core** | `diagram-design` | `hermes skills install skills-sh/diagram-design` | Renders clean Mermaid, SVG, and visual architecture/sequence diagrams. |
| **Cybersecurity** | `security-audit` | Built-in via `scripts/devsec-check.sh` & Gitleaks | Scans staged code for hardcoded API keys, private keys, and `.env` leaks. |
| **Cybersecurity** | `semgrep-sast` | `.github/workflows/security.yml` | Scans for OWASP Top 10 vulnerabilities (SQLi, XSS, Broken Access Control). |
| **Web** | `modern-web-guidance` | Built-in / Modern Web Plugin | Best practices for Next.js App Router, Tailwind CSS, and WCAG accessibility. |
| **Mobile** | `mobile-appsec` | Custom Rules in `AGENTS.md` | Audits Android Keystore, SSL Pinning, and `FLAG_SECURE` screen protection. |
| **EA Trading** | `quant-risk-guardian` | Custom Rules in `AGENTS.md` | Enforces Hard Stop Loss, dynamic lot calculation, and the 5% daily drawdown circuit breaker. |

---

## 🛠️ Domain Skills Breakdown

### 1. Core Writing & Visual Architecture Skills

#### A. Humanizer (`blader/humanizer`)
- **Purpose:** Rewrites AI-generated documentation (PRDs, READMEs, architecture decisions) into natural, direct, and senior-engineer prose based on Wikipedia's *Signs of AI Writing* cleanup guidelines.
- **When to Invoke:** Whenever the AI agent writes or updates `docs/PRD.md`, `docs/PRD-detail.md`, or release notes.
- **Installation:**
  ```bash
  hermes skills install blader/humanizer
  ```

#### B. Diagram Design (`skills-sh/diagram-design`)
- **Purpose:** Generates visual system diagrams, token lifecycle sequences, and network topologies in Mermaid or standalone SVG format.
- **When to Invoke:** Before creating new API routes or modules, ensuring team alignment in `docs/diagrams/`.
- **Installation:**
  ```bash
  hermes skills install skills-sh/diagram-design
  ```

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
- **Dynamic Lot Sizing Formula:** Calculates position size based on a strict 1% to 2% equity risk parameter:
  $$\text{Lot Size} = \frac{\text{Account Equity} \times \text{Risk \%}}{\text{Stop Loss Points} \times \text{Tick Value}}$$
- **Autonomous Circuit Breaker:** Kills all open positions, cancels pending orders, and halts trading if the daily floating loss hits 5%.
- **API Key Segregation:** Prohibits trading agents from using exchange API keys with *Withdrawal* permissions enabled.

---

## 💡 How to Instruct Your AI Agent

When kicking off a task, reference these skills directly:

```text
"Hermes, read AGENTS.md. We are building a mobile application for user authentication.
First, consult docs/blueprints/mobile-application-blueprint.md and docs/security/mobile-security-checklist.md.
Draft the architecture diagram in docs/diagrams/ and apply blader/humanizer to docs/PRD.md so the text is clear and human.
Ensure Android Keystore storage is used for token caching."
```
