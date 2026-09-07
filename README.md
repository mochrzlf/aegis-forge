# Aegis Forge

> **A secure starting point for your software project** — ready from day one.

Aegis Forge is a **ready-to-use template** for building **Web apps**, **Mobile apps (Android & iOS)**, and **Algorithmic Trading Systems (EAs)** with enterprise-grade security — without setting everything up from scratch.

[![DevSecOps CI Pipeline](https://github.com/mochrzlf/aegis-forge/actions/workflows/security.yml/badge.svg)](https://github.com/mochrzlf/aegis-forge/actions/workflows/security.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Protected by Gitleaks](https://img.shields.io/badge/Protected%20by-Gitleaks-red.svg)](.gitleaks.toml)
[![Security Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)

---

## What Is Aegis Forge? (In Plain Words)

Imagine if you want to build a house. You *could* start from an empty lot — digging foundations, laying pipes, wiring electricity one by one. Or, you could start from a **model home whose foundation is already solid**, then just adjust the paint and furniture.

**Aegis Forge is that "model home" for software.** It is not a finished app — it is a **complete foundation** that already includes:
- 🔐 **Built-in security** — so passwords and user data don't leak.
- 📋 **Step-by-step guides** — for you and for AI assistants (like Claude/Cursor).
- ✅ **Quality checklists** — so nothing is missed before release.
- 🤖 **"Guardrails" for AI** — rules so AI that writes code doesn't make dangerous mistakes.

Just copy this foundation, give your project a name, and start building features.

---

## Who Is This For?

| If you are... | This template helps you... |
|---|---|
| 👤 **A beginner / non-programmer** | Start a project the right way without getting lost in technical setup. |
| 💻 **A developer** | Save days of initial setup (login, database, security). |
| 🤖 **An AI agent user** | Give your AI a "rulebook" so it produces safe, consistent code. |
| 📈 **A trader / quant** | Build a trading bot with automatic capital protection. |

---

## Why Does This Exist?

Starting a software project usually means spending the first few days solving the *exact same* problems over and over:
- Setting up a login system and session security from scratch.
- Setting up a database with activity logging (audit trail).
- Installing an "alarm" so secret keys (API keys) don't leak to the internet.
- Organizing folders so the code doesn't become messy as it grows.

This template solves all of that **upfront**. Whether you're building a SaaS portal, an Android app, or an automated trading bot — all core architecture patterns, security checklists, and AI agent rules are ready on day one.

---

## What Can You Build?

- 🌐 **Web Apps & SaaS** — secure login, protection from common attacks (XSS/CSRF), and clear API contracts.
- 📱 **Mobile Apps (Android & iOS)** — encrypted on-device storage, secure connections (SSL pinning), and screenshot-proof screens for sensitive data.
- 📈 **Algorithmic Trading Systems (EAs)** — capital protection rules, automatic loss limits, and an "emergency brake" that stops trading when daily losses hit a limit.
- 🏢 **Enterprise Backend** — role-based access control (RBAC), multi-step approval flows, tamper-proof audit trails, and advanced encryption.

---

## Getting Started: 5 Easy Steps

> 💡 **Easiest way:** open this folder in **VS Code**, then click **"Reopen in Container"** when prompted. All the tools you need will be installed automatically — no manual setup required.

### Step 1 — Create a Copy of Your Project

Download this template, then run one command to create a new project:

```bash
# Download the template
git clone https://github.com/mochrzlf/aegis-forge.git
cd aegis-forge
```

Then choose your project type:

```bash
# 🌐 For a Web App:
make new NAME="PatientPortal" PATH="../PatientPortal" TYPE="web"

# 📱 For a Mobile App:
make new NAME="MobileWallet" PATH="../MobileWallet" TYPE="mobile"

# 📈 For a Trading Bot:
make new NAME="GoldScalperEA" PATH="../GoldScalperEA" TYPE="trading"

# 🏢 For a Complete System (Web + Backend):
make new NAME="CoreEnterprise" PATH="../CoreEnterprise" TYPE="fullstack"
```

> 🪟 **On Windows without WSL?** Use the PowerShell version instead of `make new`:
> ```powershell
> pwsh scripts/init-new-project.ps1 "PatientPortal" "../PatientPortal" web
> ```

**What happens automatically:**
1. All guides & settings are copied to your new project folder.
2. Your project name is filled in everywhere it's needed.
3. Git is set up to track your changes.
4. A "security alarm" is installed (prevents secret keys from leaking).
5. Unique security keys are generated just for your project.

### Step 2 — Define Your Specs First (Important!)

Before writing any code, decide *what* you want to build. If you're using an AI agent, just give it this instruction:

> *"Read AGENTS.md. Draft docs/PRD.md and docs/PRD-detail.md for my project based on the blueprint in docs/blueprints/. Then run a STRIDE security analysis in docs/adr/ before writing application code."*

The AI will create planning documents and analyze security risks **before** it starts programming — just like an architect draws blueprints before building.

### Step 3 — Test APIs Without Waiting for the Backend

For mobile/frontend work, you don't need to wait for the backend to be finished:

```bash
make mock-api
```
This runs a "fake server" at `http://localhost:4010` that serves sample data based on your API design — so frontend work can happen in parallel.

### Step 4 — Build Your Features

Now just build. Your AI agent already has all the rules (via `AGENTS.md`), ready-to-use example prompts (in `docs/prompt-library.md`), and guided workflows (in `docs/agent-playbooks/`).

### Step 5 — Check Security & Save

Before saving (committing), make sure it's safe:

```bash
# Check security anytime:
make audit

# Every commit is automatically scanned for leaked secrets:
git add .
git commit -m "feat: add user registration feature"
```

Done! 🎉 Your project now stands on a secure foundation.

---

## Frequently Asked Questions (FAQ)

**❓ Do I need to know programming to use this?**
Not necessarily. This template is designed to work with AI agents (Claude, Cursor, Hermes, etc.). You describe what you want, the AI writes the code — this template makes sure the result is safe and clean.

**❓ How is this different from a framework like Laravel/Next.js?**
A framework is the "engine". Aegis Forge is the "rulebook + foundation" that *complements* your chosen framework — it focuses on security, quality, and a correct workflow.

**❓ Is it free?**
Yes. It's licensed under **Apache-2.0** — free for personal and commercial use.

**❓ What if I only need one part of it?**
That's fine! Each part (security, checklists, AI guides) can be used on its own. See the `docs/` folder.

---

## Common Commands

> `make` commands are shortcuts for common tasks. (Windows users can use Git Bash, WSL, or the equivalent commands — see `SETUP.md`.)

| Command | What it does (in plain words) |
|---|---|
| `make help` | Show all available commands. |
| `make new` | **Create a new project** from this template. |
| `make audit` | **Check security** — make sure no secrets are leaked. |
| `make up` | **Start** local services (database, etc.). |
| `make down` | **Stop** all local services. |
| `make mock-api` | Run a **fake API server** for testing at `http://localhost:4010`. |
| `make status` | See the status of running services. |

---

## Security That's Already Built In

You don't need to be a security expert — these protections are active from the start:

- 🛡️ **Leak Alarm:** Every time you save changes (commit), the system automatically scans — if a password or API key is accidentally left behind, the commit is **rejected**.
- 🔒 **Encrypted Mobile Storage:** On Android, sensitive data is stored in the device's secure vault (Keystore), not in a plain file that's easy to read.
- 🛑 **Trading Emergency Brake:** If the trading bot loses up to the daily limit, the system **automatically stops** to protect your capital.
- 📜 **Tamper-Proof Audit Trail:** Every important action is recorded in the database and **cannot be deleted or edited** — useful for audits and investigations.
- 🚫 **Restricted API Keys:** API keys for the trading bot are **forbidden** from having withdrawal permission — so even if they leak, your funds stay safe.

---

## Folder Structure (A Quick Map)

```
Baseline/
├── AGENTS.md                   # 📖 "Rulebook" for AI agents & developers
├── README.md                   # 📄 This file — the main guide
├── SETUP.md                    # 🔧 Detailed technical setup guide
├── CONTRIBUTING.md             # 🤝 How to contribute to this project
├── SECURITY.md                 # 🚨 How to report a security issue
├── Makefile                    # ⌨️  Collection of shortcut commands (make ...)
├── docker-compose.yml          # 🐳 Local services (database, cache, mock API)
├── .devcontainer/              # 📦 Ready-to-use environment (open in VS Code)
├── docs/                       # 📚 All guides, templates, & checklists
│   ├── blueprints/             #    🏗️  Architecture blueprints per project type
│   ├── agent-playbooks/        #    🤖 Guided step-by-step workflows for AI
│   ├── security/               #    🔐 Security checklists per domain
│   ├── adr/                    #    📝 Architecture decisions + risk analysis
│   └── ... (checklists, testing guides, deployment, etc.)
├── evals/                      # 🧪 Tests for AI output quality
└── scripts/                    # ⚙️  Automation scripts (create project, check security)
```

> 💡 **No need to memorize all of this.** The important ones: `README.md` (guide), `AGENTS.md` (AI rules), and the `docs/` folder (all documentation). The rest works behind the scenes.

---

## Full Documentation

| Topic | File | What it's for |
|---|---|---|
| 🚀 **Quick start** | `SETUP.md` | Step-by-step technical setup |
| 📖 **AI rules** | `AGENTS.md` | Working contract for AI agents |
| 🤖 **AI workflows** | `docs/agent-playbooks/` | Step-by-step guides per project type |
| 💬 **Ready prompts** | `docs/prompt-library.md` | Example instructions for AI |
| 🔐 **Security** | `docs/security/` | Security checklists per domain |
| 🧪 **Testing** | `docs/testing-strategy.md` | Overall testing strategy |
| 🚢 **Deployment** | `docs/deployment.md` | How to release to production |
| 🤝 **Contributing** | `CONTRIBUTING.md` | Commit & pull request rules |

---

## Need Help?

- 🐛 **Found a bug or have an idea?** Open a [GitHub Issue](https://github.com/mochrzlf/aegis-forge/issues).
- 🔐 **Found a security vulnerability?** Follow the guide in [SECURITY.md](SECURITY.md) (please don't open a public issue).
- 🤝 **Want to contribute?** Read [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

**Apache-2.0** — free to use for personal and commercial purposes. See [LICENSE](LICENSE).
