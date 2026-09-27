# 🛡️ Aegis Forge

> **A secure starting point for your software project** — built-in enterprise security and AI coding guardrails, ready from day one.

[![DevSecOps CI Pipeline](https://github.com/mochrzlf/aegis-forge/actions/workflows/security.yml/badge.svg)](https://github.com/mochrzlf/aegis-forge/actions/workflows/security.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Protected by Gitleaks](https://img.shields.io/badge/Protected%20by-Gitleaks-red.svg)](.gitleaks.toml)
[![Security Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)

---

## 🏠 What Is Aegis Forge? (In Plain Words)

Imagine building a **house**:
- **Without Aegis Forge:** You buy an empty plot of land, dig foundations from scratch, install wiring and plumbing by hand, and hope your security alarms work. It takes weeks before you can even put up the first wall.
- **With Aegis Forge:** You start with a **model home on an earthquake-proof bunker foundation**. The foundation is already poured, electricity and plumbing are connected, and the security alarms are armed. On Day 1, you simply decorate the rooms and build your custom features.

**Aegis Forge is that foundation for software.** It provides pre-tested starter templates (**Web Apps**, **Mobile Apps**, and **Trading Bots**) with enterprise banking-grade security and strict guardrails for **AI Coding Agents** (Claude Code, Cursor, Hermes, Copilot) so they write clean, secure code without cutting corners.

> 🇮🇩 *Pengguna Bahasa Indonesia? Baca panduan lengkap dalam bahasa sehari-hari di [`docs/PANDUAN-AWAM.md`](docs/PANDUAN-AWAM.md).*

---

## 🚀 Getting Started: 7 Step-by-Step Instructions

This guide is designed for **complete beginners**. Follow these 7 steps in order:

<p align="center">
  <img src="docs/diagrams/quickstart-workflow.svg" alt="Aegis Forge 7-Step Development Journey" width="100%" />
</p>

---

### Step 1 — Get a Copy of the Template

Open your terminal (PowerShell on Windows, Terminal on Mac/Linux) and download the baseline:

```bash
git clone https://github.com/mochrzlf/aegis-forge.git
cd aegis-forge
```

> 💡 **Zero-Setup Alternative (VS Code):** Open the folder in **VS Code** and click **"Reopen in Container"** when prompted. All required tools (Docker, Python, Node, Git, Gitleaks) will be configured automatically.

---

### Step 2 — Run the Setup Wizard (`init-new-project`)

Run the automated interactive wizard to create your fresh project workspace:

```bash
# On Linux, macOS, or WSL:
bash scripts/init-new-project.sh

# On Windows (PowerShell):
pwsh scripts/init-new-project.ps1
```

#### 🧙‍♂️ What the Interactive Wizard Asks You:
1. **Project Name:** Enter your application name (e.g. `TokoKeren`, `PatientPortal`, or `GoldScalperEA`).
2. **Target Folder:** Specify where to create the project (press Enter for default: `../YourProjectName`).
3. **Domain Type:** Select the type of project:
   - `1) Web` (FastAPI, Express.js, Laravel, Go, or Next.js)
   - `2) Trading` (MetaTrader 5 EA & Algorithmic Trading)
   - `3) Mobile` (Android Kotlin or iOS Swift)
   - `4) Enterprise` (Multi-tier enterprise)
4. **Architecture Approach & Template Choice:**
   - **Pre-built Starter Skeletons (Recommended):** Choose a ready-to-run template with pre-wired code and automated tests (e.g. `web-app` for Python FastAPI, `web-app-express` for Node.js, `web-app-laravel` for PHP, `web-app-go` for Golang, `trading-ea`, `mobile-android`, or `mobile-ios`).
   - **Custom Stack Mix & Match:** Or pick your own combination of Frontend (Next.js/React/Vue), Backend (FastAPI/Express/Laravel/Go/NestJS), CSS, and Database, and choose whether to enforce Banking-Grade IAM.

#### ⚙️ What the Wizard Does Automatically (Behind the Scenes):
- ✅ Creates your clean project folder and replaces all project name placeholders.
- ✅ Initializes a fresh Git repository (`git init -b main`).
- ✅ Installs a **Git pre-commit security hook** to block accidental credential leaks.
- ✅ Generates unique, high-entropy cryptographic keys (`JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`, `ENCRYPTION_MASTER_KEY`) inside your `.env` file.
- ✅ **Automatically installs your chosen starter skeleton directly into the project** — so you never need to copy template files manually!
- ✅ **Generates `AI-AGENT-PROMPT.md` at your project root** — a tailored, ready-to-use instruction prompt you can immediately copy-paste into your AI agent.

---

### Step 3 — Describe Your App & Paste `AI-AGENT-PROMPT.md` into Your AI

Switch into your newly created project folder:

```bash
cd ../YourProjectName
```

> 🤖 **Zero Guesswork Prompting:**
> 1. Open the file **`AI-AGENT-PROMPT.md`** at your project root.
> 2. Fill in the section **`💡 IDE & FITUR APLIKASI YANG INGIN SAYA BUAT`** with a plain description of what you want to build (e.g. *"I want to build a family finance website with daily expense tracking, receipt photo uploads, monthly budgets, and summary charts"*).
> 3. Copy the entire prompt and paste it into your AI coding agent (Claude Code, Cursor, Windsurf, Copilot, or Hermes)!

#### 🎙️ What the AI Does Next (Interactive PRD Interview):
Upon receiving your prompt, the AI reads your app idea and automatically starts the **`prd-interviewer` skill**:
1. **Reads the Rules:** It loads `AGENTS.md` and enforces security policies (RTR, lockout, Maker-Checker, etc.).
2. **Conducts the PRD Interview:** It asks you at most **5 focused questions per round** to clarify personas, workflows, and edge cases, producing `docs/PRD.md` and `docs/PRD-detail.md`.
3. **Designs UI Tokens & Wireframes (`docs/ui-design.md`):** If your project has a Web or Mobile UI, it defines visual tokens (Tailwind) and screen layouts before coding.

---

### Step 4 — Break the Plan into Small Tasks

Instruct your AI to break the PRD into bite-sized, atomic work units:

> *"Use the `spec-to-tasks` skill. Convert `docs/PRD.md` and `docs/PRD-detail.md` into `docs/TASKS.md`. Ensure every task is small (XS/S/M) with clear dependencies and includes a `skeleton_hint` pointing to the file to edit."*

Now you have an exact, ordered roadmap (`docs/TASKS.md`). This keeps the AI focused on one small task at a time and prevents hallucinated code.

---

### Step 5 — Start the Stack (Ready to Run!)

Because the setup wizard in **Step 2** already copied your starter skeleton, your application is ready to start immediately:

```bash
# Launch database, cache, run migrations, and start the backend:
make first-run
```

- 🌐 **Backend API:** Live at `http://localhost:8000`
- 📑 **Interactive API Documentation:** Open `http://localhost:8000/docs` in your browser.
- 📬 **Local Test Mailbox (Mailpit):** View test emails at `http://localhost:8025`.

*(Building a decoupled frontend? Check the [Frontend Architecture Guide](docs/starter-skeletons.md#3-frontend-architecture-guide-decoupled-vs-fullstack) for connecting React/Next.js to your backend).*

---

### Step 6 — Build Features with Your AI Agent

Have your AI agent execute the tasks from `docs/TASKS.md` one by one:

> *"Read `docs/TASKS.md`. Let's implement Task 1. Follow the file indicated in `skeleton_hint`, adhere to the rules in `AGENTS.md`, and write the corresponding test."*

> 🛡️ **Pro Tip (Agent Rule Packs):** Install our pre-packaged guardrails directly into your AI tool:
> ```bash
> npx skills add mochrzlf/aegis-forge
> ```

---

### Step 7 — Check Security & Save Changes

Before saving your progress, verify that all tests pass and no secret keys were exposed:

```bash
# Run the automated security audit:
make audit

# Save your work:
git add .
git commit -m "feat: implement initial user registration"
```

> 🛡️ **Leak Protection:** If you accidentally leave a database password or API token in your code, the pre-commit hook will **automatically reject the commit** to protect your project.

---

## ⌨️ Common Daily Commands

| Command | What It Does (In Plain Words) |
|---|---|
| `make help` | Displays all available shortcut commands. |
| `make first-run` | Initial run: generates local `.env`, boots containers, and applies migrations. |
| `make up` | Starts all local containers (database, Redis, backend). |
| `make down` | Gracefully stops all local containers. |
| `make test` | Runs the full automated test suite. |
| `make audit` | Runs comprehensive security and secret-leak scans. |
| `make seed` | Seeds initial administrative users (`superadmin` and `checker`). |
| `make mock-api` | Starts a mock REST server at `http://localhost:4010` for testing. |

---

## 🗺️ Project Structure at a Glance

```
aegis-forge/
├── 📖 README.md                ← Main overview & beginner guide (you are here)
├── 📖 AGENTS.md                ← Permanent rulebook & working contract for AI agents
├── 🔧 SETUP.md                 ← Technical installation & environment reference
├── ⌨️ Makefile                 ← Shortcut commands for daily development
├── 🐳 docker-compose.yml       ← Local development services (Postgres, Redis, API)
│
├── 📁 docs/                    ← 📚 Complete documentation & specifications
│   ├── 📖 glossary.md          ← Plain-language glossary & everyday analogies
│   ├── 🧰 starter-skeletons.md  ← Domain maturity matrix & template details
│   ├── 💼 examples.md          ← Real-world case studies & TokoKeren walkthrough
│   ├── ❓ faq-troubleshooting.md← Frequently asked questions & problem solutions
│   ├── 🇮🇩 PANDUAN-AWAM.md      ← Full beginner guide in Indonesian
│   ├── 🌐 architecture.html    ← Interactive visual diagrams (Topology & IAM)
│   ├── 🏦 BANKING-IAM-GUIDE.md  ← 6 pillars of banking-grade Zero Trust IAM
│   ├── 🚀 vps-deployment-guide.md← Cloud VPS production deployment guide
│   └── 📁 blueprints/          ← Architectural blueprints per domain
│
├── 📁 templates/               ← 🏠 Runnable starter skeletons (Web, Mobile, Trading)
├── 📁 skills/                  ← 🛡️ Installable skill guardrails for AI agents
└── 📁 scripts/                 ← ⚙️ Automation scripts (init wizard, security check)
```

---

## 📚 Modular Documentation Index

For in-depth details on specific topics, refer to the dedicated documents:

- 📖 **[Plain-Language Glossary & Analogies](docs/glossary.md)** — Understand tech terms with simple analogies.
- 🧰 **[Starter Skeletons & Domain Maturity Matrix](docs/starter-skeletons.md)** — Deep dive into FastAPI, Express, Laravel, Go, MQL5 EA, and Mobile templates.
- 💼 **[Real-World Case Studies & Walkthrough](docs/examples.md)** — Detailed walkthrough of building an e-commerce store, clinic portal, or gold trading bot.
- ❓ **[FAQ & Troubleshooting Guide](docs/faq-troubleshooting.md)** — Solutions for common issues like Docker errors, port conflicts, or secret leak alerts.
- 🌐 **[Interactive Visual Architecture](docs/architecture.html)** — Explore visual diagrams for network topology, Zero Trust auth, and Maker-Checker workflows.
- 🏦 **[Banking-Grade IAM Guide](docs/BANKING-IAM-GUIDE.md)** — Technical reference for Refresh Token Rotation, JML Kill-Switches, and Dual Control.
- 🚀 **[VPS Production Deployment](docs/vps-deployment-guide.md)** — Provider-agnostic production deployment with Caddy auto-HTTPS.

---

## 📄 License & Contributing

- **License:** Licensed under the [Apache-2.0 License](LICENSE) — free for personal, commercial, and enterprise use.
- **Reporting Vulnerabilities:** Please see [SECURITY.md](SECURITY.md) for responsible disclosure procedures.
- **Contributing:** Read [CONTRIBUTING.md](CONTRIBUTING.md) to submit improvements or report issues.
