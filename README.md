# Enterprise Baseline

A production-ready blueprint and scaffolding template for building secure **Web Applications**, **Mobile Apps (Android & iOS)**, and **Algorithmic Trading Systems (EAs)**.

[![DevSecOps CI Pipeline](https://github.com/mochrzlf/enterprise-baseline/actions/workflows/security.yml/badge.svg)](https://github.com/mochrzlf/enterprise-baseline/actions/workflows/security.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Protected by Gitleaks](https://img.shields.io/badge/Protected%20by-Gitleaks-red.svg)](.gitleaks.toml)
[![Security Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)

---

## Why This Exists

Starting a new software project usually means spending the first few days solving the exact same problems:
- Configuring authentication, token rotation, and secure cookies from scratch.
- Setting up database schemas with audit logging and access controls.
- Installing secret-detection hooks so API keys don't accidentally leak to Git.
- Establishing folder structures so the codebase doesn't turn into spaghetti as it grows.

This baseline solves that upfront. Whether you are building a SaaS portal, an Android mobile app, or an automated trading bot, all core architectural patterns, security checklists, and AI agent guardrails are ready on day one.

---

## Supported Domains

- **Web Applications & SaaS:** Next.js / React, strict HttpOnly cookie sessions (RFC 6749), CSRF/XSS defenses, and OpenAPI 3.0 contracts.
- **Mobile Applications (Android & iOS):** Clean Architecture, hardware-backed Android Keystore (`EncryptedSharedPreferences`), SSL Pinning, and screen privacy (`FLAG_SECURE`).
- **Algorithmic & EA Trading Systems:** Capital preservation doctrine, mandatory Hard Stop Losses, dynamic lot sizing (max 1-2% equity risk), and an autonomous 5% daily drawdown circuit breaker.
- **Enterprise Backend Core:** Role-Based Access Control (RBAC), Maker-Checker approval flows (Four-Eyes Principle), tamper-proof audit trails, and field-level encryption (AES-256-GCM).

---

## Step-by-Step Guide: From Idea to Production

### Step 1: Scaffold Your Project

Clone this repository and create a dedicated workspace for your project:

```bash
git clone https://github.com/mochrzlf/enterprise-baseline.git
cd enterprise-baseline

# Choose your project profile:
# For Web App:
make new NAME="PatientPortal" PATH="../PatientPortal" TYPE="web"

# For Mobile App (Android/iOS):
make new NAME="MobileWallet" PATH="../MobileWallet" TYPE="mobile"

# For Algorithmic Trading EA:
make new NAME="GoldScalperEA" PATH="../GoldScalperEA" TYPE="trading"

# For Fullstack Enterprise:
make new NAME="CoreEnterprise" PATH="../CoreEnterprise" TYPE="fullstack"
```

The scaffolding script will automatically:
1. Copy all blueprints, security policies, and configs to your new directory.
2. Replace all template placeholders with your project name.
3. Initialize a clean Git repository (`git init -b main`).
4. Activate the Git pre-commit hook with Gitleaks protection.
5. Generate unique, high-entropy cryptographic keys (JWT secrets & AES-256 master key) in your local `.env`.

---

### Step 2: Equip Your AI Agent with Recommended Skills

If you are using Hermes Agent or Claude Code, equip your agent with the skills detailed in [`docs/AI-AGENT-SKILLS.md`](docs/AI-AGENT-SKILLS.md):

```bash
# Clean, natural writing without AI cliches:
hermes skills install blader/humanizer

# Visual architecture and sequence diagrams:
hermes skills install skills-sh/diagram-design
```

---

### Step 3: Define Specifications Before Writing Code

Navigate to your new project and let your AI agent review the requirements:

```bash
cd ../YourProjectName
hermes
```

Prompt your AI agent:
> *"Read AGENTS.md. Draft docs/PRD.md and docs/PRD-detail.md for our project based on the domain blueprint in docs/blueprints/. Then perform a STRIDE threat analysis in docs/adr/ before writing application code."*

---

### Step 4: Test APIs Instantly (Mock Server)

For mobile and frontend development, you don't need to wait for the backend to be finished:

```bash
make mock-api
```
This launches a Stoplight Prism mock server at `http://localhost:4010` serving mock data directly from `docs/openapi.yaml`.

---

### Step 5: Verify Security and Commit

Before pushing any commit, the baseline ensures you are safe:

```bash
# Run comprehensive audit manually anytime:
make audit

# Normal git commits automatically trigger Gitleaks secret scanning:
git add .
git commit -m "feat: implement user registration flow"
```

---

## Directory Structure

```
Baseline/
├── AGENTS.md                   # AI Agent Operating Contract & Non-Negotiable Rules
├── README.md                   # Primary English documentation
├── SETUP.md                    # Technical setup & configuration manual
├── SECURITY.md                 # Vulnerability disclosure policy
├── LICENSE                     # Apache-2.0 License
├── Makefile                    # Unified task runner (audit, mock-api, up, down)
├── .env.example                # Hardened environment variable template
├── .gitattributes              # Line-ending normalization (LF)
├── .editorconfig               # Editor & IDE consistency rules
├── .gitleaks.toml              # Secret detection rules & template allowlists
├── docker-compose.yml          # PostgreSQL 16, Redis 7, Mailpit, & Prism Mock Server
├── docs/
│   ├── AI-AGENT-SKILLS.md      # Recommended AI agent skills matrix & installation
│   ├── PRD-template.md         # High-level product requirements template
│   ├── PRD-detail-template.md  # User stories & acceptance criteria template
│   ├── ui-design-template.md   # Design system & UI tokens guide
│   ├── schema-template.sql     # PostgreSQL schema (RBAC, triggers, audit logs)
│   ├── openapi-template.yaml   # REST API contract (OpenAPI 3.0)
│   ├── blueprints/             # Architecture blueprints (web, mobile, trading)
│   ├── security/               # Mobile security checklist & trading risk policy
│   ├── diagrams/               # Architecture & sequence diagrams (Mermaid)
│   └── adr/                    # Architecture Decision Records & STRIDE models
└── scripts/
    ├── init-new-project.sh     # Scaffolding automation script
    └── devsec-check.sh         # Security audit & secret scanner script
```

---

## Task Runner Commands (`Makefile`)

- `make help` : Display all available commands.
- `make audit` : Run full security audit (verify `.env`, private keys, and Gitleaks scan).
- `make mock-api` : Launch Prism Mock API Server at `http://localhost:4010`.
- `make up` : Start local development stack (PostgreSQL, Redis, Mailpit, Prism).
- `make down` : Stop all containers.
- `make hermes` : Launch Hermes AI Agent in the terminal.
- `make hermes-ui` : Launch Hermes Web Dashboard at `http://127.0.0.1:9119`.

---

## Built-In Security Standards

- **Pre-Commit Shield:** Blocks commits containing `.env` files, private keys, or API tokens before they enter Git history.
- **Hardware-Backed Mobile Storage:** Enforces Android Keystore instead of plain shared preferences.
- **Trading Circuit Breaker:** Automatically closes trades and halts the system if the daily floating loss hits 5%.
- **Tamper-Proof Audit Trail:** PostgreSQL triggers reject `UPDATE` and `DELETE` queries on the `audit_logs` table.
- **API Key Segregation:** Strictly prohibits withdrawal permissions on trading bot API keys.
