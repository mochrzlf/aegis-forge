# Multi-Domain Project Setup & Initialization Guide

This document provides step-by-step instructions for creating a new project using the **Universal Aegis Forge** (Web, Mobile, EA Trading, or Fullstack).

---

## 1. Create a New Project Instance by Domain

Use the `make new` command or automated script:

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

The script will automatically:
1. Copy the entire baseline structure (`AGENTS.md`, `docs/blueprints/`, `docs/security/`, `docs/diagrams/`, `Makefile`, `.env.example`, `.gitignore`, `.gitattributes`, `.gitleaks.toml`).
2. Replace the placeholder `[PROJECT_NAME]` with your project's name.
3. Initialize a new Git repository (`git init -b main`).
4. Install and enable the **Git Pre-Commit Security Hook** (`.git/hooks/pre-commit`) to block leaks of `.env` files, private key files, Android keystores, and secret tokens via Gitleaks.
5. Prepare a local `.env` file with unique encryption & JWT keys generated automatically via OpenSSL.

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
  `Scorecard supply-chain security`.
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
