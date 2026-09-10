# Multi-Domain Project Setup & Initialization Guide

This document provides step-by-step instructions for creating a new project using the **Universal Aegis Forge** (Web, Mobile, EA Trading, or Fullstack).

---

## 1. Create a New Project Instance by Domain

> **Zero-setup option (recommended):** open this baseline in the provided **Dev Container** (`.devcontainer/`) via VS Code *"Reopen in Container"* or GitHub Codespaces. Python, Node, Docker, gitleaks, and pre-commit come pre-installed and version-pinned — no manual toolchain setup required.

Use the `make new` command or the automated script (two equivalent variants):

**Bash (Linux / macOS / Git Bash / WSL):**
```bash
# Option 1: Web Application / SaaS Project
bash scripts/init-new-project.sh "MyWebApp" "../MyWebApp" web

# Option 2: Mobile Application Project (Android / iOS)
bash scripts/init-new-project.sh "MyMobileApp" "../MyMobileApp" mobile

# Option 3: EA / Algorithmic Trading Project
bash scripts/init-new-project.sh "MyTradingEA" "../MyTradingEA" trading

# Option 4: Fullstack Enterprise Project (Default)
bash scripts/init-new-project.sh "MyFullstack" "../MyFullstack" fullstack
```

**PowerShell (native Windows — no bash/WSL/openssl required):**
```powershell
# Web Application / SaaS Project
pwsh scripts/init-new-project.ps1 "MyWebApp" "../MyWebApp" web

# Mobile Application Project (Android / iOS)
pwsh scripts/init-new-project.ps1 "MyMobileApp" "../MyMobileApp" mobile

# EA / Algorithmic Trading Project
pwsh scripts/init-new-project.ps1 "MyTradingEA" "../MyTradingEA" trading

# Fullstack Enterprise Project (Default)
pwsh scripts/init-new-project.ps1 "MyFullstack" "../MyFullstack" fullstack
```

Both scripts are functionally identical and will automatically:
1. Copy the entire baseline structure (`AGENTS.md`, `docs/blueprints/`, `docs/security/`, `docs/diagrams/`, `Makefile`, `.env.example`, `.gitignore`, `.gitattributes`, `.gitleaks.toml`, `.devcontainer/`).
2. Replace the placeholder `[PROJECT_NAME]` with your project's name.
3. Initialize a new Git repository (`git init -b main`).
4. Install and enable the **Git Pre-Commit Security Hook** (`.git/hooks/pre-commit`) to block leaks of `.env` files, private key files, Android keystores, and secret tokens via Gitleaks.
5. Prepare a local `.env` file with unique encryption & JWT keys generated automatically (via OpenSSL in bash, or .NET crypto in PowerShell).

---

## 2. Configure Credentials & Environment (.env)

Navigate into the new project directory:
```bash
cd ../YourProjectName
```
Open the `.env` file and generate secure cryptographic keys:
- Generate JWT Secret: `openssl rand -base64 48`
- Generate Encryption Master Key: `openssl rand -hex 32`
- Adjust database or API key configurations according to your project domain.

---

## 3. Domain-Specific Workflows

### 🌐 A. If You Are Building a Web Project:
1. Refer to the blueprint in `docs/blueprints/web-application-blueprint.md`.
2. Prompt Hermes Agent:
   > *"Hermes, please design docs/PRD.md and docs/ui-design.md for this web application using Zustand for state management and HttpOnly session cookies."*

### 📱 B. If You Are Building a Mobile Project (Android/iOS):
1. Refer to the blueprint in `docs/blueprints/mobile-application-blueprint.md` and the checklist in `docs/security/mobile-security-checklist.md`.
2. Launch the instant Mock API Server:
   ```bash
   make mock-api
   ```
   *(Access `http://localhost:4010` or `http://10.0.2.2:4010` in an Android emulator to immediately test API requests & responses).*
3. Prompt Hermes Agent:
   > *"Hermes, please design an Android Jetpack Compose application following Clean Architecture and store tokens in EncryptedSharedPreferences (Android Keystore)."*

### 📈 C. If You Are Building an EA / Algorithmic Trading Project:
1. Refer to the blueprint in `docs/blueprints/ea-trading-blueprint.md` and the risk policy in `docs/security/trading-risk-policy.md`.
2. Prompt Hermes Agent:
   > *"Hermes, please design an EA Trading architecture for XAUUSD/EURUSD instruments with Hard Stop Loss rules, dynamic lot sizing capped at 1% capital risk, and a Circuit Breaker triggered when daily drawdown reaches 5%."*

---

## 4. Running Security Audits Anytime

The pre-commit hook security checks run automatically whenever you execute `git commit`. You can also trigger a manual audit at any time:
```bash
make audit
# or
devsec-check
```

---

## 4b. (Optional) Running Agent Output-Quality Evals

The `evals/` harness measures whether your AI agent's output obeys the baseline's non-negotiable rules (API envelope, cookie security, RBAC, trading risk gates). It needs an LLM provider API key (billed to **your own** provider account).

Use the interactive guard script — it checks prerequisites, helps you store the key safely in the local `.env` (git-ignored, gitleaks-protected), and confirms before any paid API call:

**PowerShell (Windows):**
```powershell
pwsh scripts/run-evals.ps1          # guarded run
pwsh scripts/run-evals.ps1 -View    # run + open results viewer
```

**Bash (Linux / macOS / Git Bash / WSL):**
```bash
bash scripts/run-evals.sh           # guarded run
bash scripts/run-evals.sh --view    # run + open results viewer
```

Alternatively, set the key manually (any one of `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`) in your shell or `.env`, then run `npx promptfoo@latest eval -c evals/promptfooconfig.yaml` directly. See `evals/README.md` for details.

---

## 5. (Recommended) Enable the Pre-Commit Framework

Beyond the built-in security hook, the baseline ships a `.pre-commit-config.yaml`
that adds file hygiene checks, ShellCheck, YAML lint, **OpenAPI contract
validation**, and **PostgreSQL schema linting** — the same checks enforced in CI:

```bash
pip install pre-commit
pre-commit install        # one-time, per repository clone
pre-commit run --all-files # manual full audit
```

The scaffolding script installs this hook automatically when `pre-commit` is
already available on your machine. Both hooks coexist: the framework hook runs
first, then the Gitleaks-based security hook.

---

## 6. Branch Protection & CODEOWNERS (Recommended)

The baseline ships `.github/CODEOWNERS`, which routes review of security-sensitive
paths to designated owners. For this to actually *enforce* anything, enable branch
protection on `main` in your repository settings:

**GitHub → Settings → Branches → Add rule for `main`:**
- ✅ Require a pull request before merging (no direct pushes).
- ✅ **Require review from Code Owners** (enforces `.github/CODEOWNERS`).
- ✅ Require status checks to pass → select: `Security & SAST Scans`,
  `API Contract & Schema Validation`, `Dependency Review (PR Gate)`,
  `Scorecard supply-chain security`, `Validate ADR format & STRIDE completeness`.
- ✅ Require conversation resolution before merging.
- ✅ (Recommended) Require linear history & block force pushes.

Then edit `.github/CODEOWNERS` and replace the `@org/...` placeholder handles with
your real GitHub users/teams (`@you`, `@your-org/security`, etc.).

> **Segregation of Duties:** with CODEOWNERS + "require code owner review", a
> change to `docs/security/`, CI workflows, or the DB schema *cannot* be merged
> by a single person — it needs the owning lead's approval. This mirrors the
> Maker-Checker principle already used elsewhere in the baseline.

---

## 7. Command Shortcut Summary

| Shortcut | Description |
| :--- | :--- |
| `make help` | Display all available Makefile commands |
| `make audit` | Run comprehensive Gitleaks & secret detection security audit |
| `make mock-api` | Start Prism Mock API server (port 4010) |
| `make up` | Start local Docker Compose services |
| `make down` | Stop local Docker Compose services |
| `make hermes` | Open Hermes AI Agent in terminal |
| `make hermes-ui` | Launch Hermes Web Dashboard in background (port 9119) |
| `new-project` | Terminal alias shortcut to initialize a new project |
| `goto-baseline` | Navigate directly to the Baseline directory |
