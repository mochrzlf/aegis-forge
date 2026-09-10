# 🛡️ Aegis Forge

> **A secure starting point for your software project** — ready from day one.

**Aegis Forge** is a ready-to-use **template** for building **Web apps**, **Mobile apps (Android & iOS)**, and **Algorithmic Trading bots** with **enterprise-grade security** — without setting everything up from scratch.

[![DevSecOps CI Pipeline](https://github.com/mochrzlf/aegis-forge/actions/workflows/security.yml/badge.svg)](https://github.com/mochrzlf/aegis-forge/actions/workflows/security.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Protected by Gitleaks](https://img.shields.io/badge/Protected%20by-Gitleaks-red.svg)](.gitleaks.toml)
[![Security Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)

---

## 🌍 For Everyone — Beginners & Professionals Alike

This guide is written so that **anyone** can understand it — whether you've never written a line of code, or you're a seasoned engineer. If you can use WhatsApp and a word processor, you can follow along.

| If you are... | Aegis Forge helps you... |
|---|---|
| 👤 **A complete beginner** | Start a project the *right way* without getting lost in technical setup. |
| 💻 **A developer** | Skip days of initial setup (login, database, security) — it's already done. |
| 🤖 **An AI agent user** | Give your AI (Claude, Cursor, etc.) a "rulebook" so it writes safe, consistent code. |
| 📈 **A trader / quant** | Build a trading bot with automatic capital protection built in. |
| 🏢 **An enterprise team** | Enforce RBAC, audit trails, and segregation of duties from day one. |

---

## 🏠 What Is Aegis Forge? (In Plain Words)

Imagine you want to build a **house**. You have two options:

| The Old Way (Without Aegis Forge) | The New Way (With Aegis Forge) |
|---|---|
| Buy an empty plot of land | Buy a **model home with a rock-solid foundation** |
| Dig the foundation yourself | Foundation is already poured |
| Install plumbing & wiring yourself | Plumbing & electricity already connected |
| Install the security alarm yourself | Alarm already armed |
| **Month 1:** finally starting the walls | **Day 1:** just picking paint & furniture |

**Aegis Forge is that "model home" for software.** It's not a finished app — it's a **complete foundation** that already includes:

- 🔐 **Built-in security** — so passwords & user data don't leak.
- 📋 **Step-by-step guides** — for you *and* for AI assistants (Claude, Cursor, etc.).
- ✅ **Quality checklists** — so nothing is missed before release.
- 🤖 **"Guardrails" for AI** — rules so AI that writes code doesn't make dangerous mistakes.

Just copy this foundation, give your project a name, and start building features.

---

## ❓ Why Does This Exist?

Every time someone starts a software project, they spend the **first few days** solving the **exact same problems** over and over:

1. **"How do I build a secure login system?"** — passwords must be encrypted, sessions must expire, etc.
2. **"How do I record who did what?"** (audit trail) — critical for investigations when things go wrong.
3. **"How do I stop API keys from leaking to the internet?"** — one small mistake = data stolen.
4. **"How do I organize folders so code doesn't become a mess as it grows?"**

**Aegis Forge solves all of this *upfront*.** Whether you're building a SaaS portal, an Android app, or an automated trading bot — all core architecture patterns, security checklists, and AI agent rules are ready on day one.

---

## 📖 Glossary — Plain-Language Terms

Before going further, here are the key terms explained with everyday analogies.

### Basic Terms

| Term | What It Really Means | Everyday Analogy |
|---|---|---|
| **Template / Baseline** | A master copy you can duplicate | Like a **photocopy of a blank form** — you just fill it in |
| **Repository (repo)** | Where all project files live | Like a **binder** holding every project document |
| **Clone** | Copying a repo from the internet to your computer | Like **downloading** all files to your laptop |
| **Commit** | Saving changes (with a note about what changed) | Like **"Save" + writing the date & a note** |
| **Framework** | The "engine" that runs your app | Like a **car engine** — Aegis Forge is the "body + driving rules" |

### Security Terms

| Term | What It Really Means | Everyday Analogy |
|---|---|---|
| **API Key** | A secret key to access third-party services | Like a **house key** — don't let it fall into the wrong hands |
| **Encryption** | Scrambling data so it can't be read without a key | Like **writing a letter in secret code** |
| **Audit Trail** | A record of who did what, when | Like a **CCTV + guest book** that can't be erased |
| **RBAC** | Rules about who can access what (based on role) | Like **office access cards** — managers can open the server room, staff can't |
| **Secrets** | Sensitive data (passwords, API keys, etc.) | Like your **ATM PIN** — never write it where others can see |

### AI & Development Terms

| Term | What It Really Means | Everyday Analogy |
|---|---|---|
| **AI Agent** | AI that can write code (Claude, Cursor, etc.) | Like a **personal assistant** that types for you |
| **PRD** | A document describing "what to build" | Like a **house blueprint** before construction |
| **OpenAPI** | A contract for "how the app communicates" | Like a **restaurant menu** — a list of what can be ordered |
| **Schema (Database)** | The table structure for storing data | Like a **filing cabinet** — where each document is stored |
| **CI/CD** | Automatically checking & testing code on every change | Like **factory quality control** — every product is inspected before shipping |

---

## 🎯 What Can You Build?

Aegis Forge supports **4 main project types**:

### 🌐 A. Web Apps & SaaS
**Examples:** Clinic information system, customer portal, business dashboard, online store.

**Already prepared for you:**
- Secure login (encrypted passwords, auto-expiring sessions)
- Protection from common attacks (XSS, CSRF — hackers can't inject malicious code)
- A clear "API contract" (frontend & backend never misunderstand each other)

### 📱 B. Mobile Apps (Android & iPhone)
**Examples:** E-wallet, attendance app, health app.

**Already prepared for you:**
- Sensitive data stored in the **device's secure vault** (Android Keystore) — not in an easy-to-read plain file
- Secure connections (SSL Pinning — prevents eavesdropping)
- Screenshot-proof screens for sensitive data (`FLAG_SECURE`)

### 📈 C. Algorithmic Trading Bots (EAs)
**Examples:** Forex/gold trading bot on MetaTrader, crypto bot.

**Already prepared for you:**
- **Automatic emergency brake** — if losses hit the daily limit, the bot STOPS itself
- Risk limit per trade (max 1% of capital)
- Trading API keys are **forbidden from having withdrawal permission** — funds stay safe even if the key leaks

### 🏢 D. Enterprise Backend Systems
**Examples:** Core company systems, multi-branch platforms.

**Already prepared for you:**
- Layered access control (RBAC — who can access what)
- Multi-level approvals (Maker-Checker — no single person can act alone)
- Tamper-proof audit trail (can't be deleted or edited)

---

## 🚀 Getting Started: 5 Easy Steps

> 💡 **Easiest way:** open this folder in **VS Code**, then click **"Reopen in Container"** when prompted. All the tools you need will be installed automatically — no manual setup required.

### Step 1 — Get a Copy of the Template

Open a **terminal** (PowerShell on Windows, Terminal on Mac/Linux), then:

```bash
# Download the template
git clone https://github.com/mochrzlf/aegis-forge.git
cd aegis-forge
```

### Step 2 — Create Your New Project

Choose **one** command based on the type of project you want:

```bash
# 🌐 For a Web App:
bash scripts/init-new-project.sh "YourProjectName" "../YourProjectName" web

# 📱 For a Mobile App:
bash scripts/init-new-project.sh "YourProjectName" "../YourProjectName" mobile

# 📈 For a Trading Bot:
bash scripts/init-new-project.sh "YourProjectName" "../YourProjectName" trading

# 🏢 For a Complete System (Web + Backend):
bash scripts/init-new-project.sh "YourProjectName" "../YourProjectName" fullstack
```

> 🪟 **On Windows (PowerShell)?** Use the `.ps1` version instead:
> ```powershell
> pwsh scripts/init-new-project.ps1 "YourProjectName" "../YourProjectName" web
> ```

> 💡 Replace `"YourProjectName"` with your actual project name. Examples: `"WartegBot"`, `"PatientPortal"`, `"GoldScalperEA"`

**What happens automatically** (you don't have to do anything):
1. ✅ All guides & settings are copied to your new project folder.
2. ✅ Your project name is filled in everywhere it's needed.
3. ✅ Git is set up to track your changes.
4. ✅ A "security alarm" is installed (prevents secret keys from leaking).
5. ✅ Unique security keys are generated just for your project.

### Step 3 — Define Your Specs First (Important!)

> ⚠️ **Don't write code yet!** First decide *what* you want to build.

If you're using an AI agent (Claude, Cursor, etc.), give it this instruction:

> *"Read AGENTS.md. Draft docs/PRD.md and docs/PRD-detail.md for my project based on the blueprint in docs/blueprints/. Then run a STRIDE security analysis in docs/adr/ before writing application code."*

The AI will create planning documents and analyze security risks **before** it starts programming — just like an architect draws blueprints before building.

### Step 4 — Build Your Features

Now just build. Your AI agent already has all the rules (via `AGENTS.md`), ready-to-use example prompts (in `docs/prompt-library.md`), and guided workflows (in `docs/agent-playbooks/`).

> 🛡️ **Want the strongest AI compliance?** Install the ready-made "rule packs" directly into your AI agent — so the rules load automatically instead of hoping the AI reads them:
> ```bash
> npx skills add mochrzlf/aegis-forge
> ```
> These cover trading risk limits, security checklists, API standards, and more. See the [`skills/`](skills/) folder for details.

> 🧪 **Want proof your AI follows the rules?** The `evals/` folder can *measure* it — run `pwsh scripts/run-evals.ps1` (Windows) or `bash scripts/run-evals.sh` (Linux/Mac) with your own AI API key. See [`evals/`](evals/) for details.

### Step 5 — Check Security & Save

Before saving (committing), make sure it's safe:

```bash
# Check security anytime:
make audit

# Every commit is automatically scanned for leaked secrets:
git add .
git commit -m "feat: add user registration feature"
```

**Done!** 🎉 Your project now stands on a secure foundation.

---

## 🔐 Security That's Already Built In

You **don't need to be a security expert** — these protections are active from the start:

- 🛡️ **Leak Alarm (Gitleaks):** Every time you save changes (`git commit`), the system automatically scans. If a password or API key is accidentally left behind, the commit is **rejected**.
- 🔒 **Encrypted Mobile Storage:** On Android, sensitive data is stored in the device's secure vault (Keystore), not in a plain file that's easy to read.
- 🛑 **Trading Emergency Brake:** If the trading bot loses up to the daily limit (e.g., 5% of capital), the system **automatically stops** to protect your funds.
- 📜 **Tamper-Proof Audit Trail:** Every important action is recorded in the database and **cannot be deleted or edited** — useful for audits and investigations.
- 🚫 **Restricted Trading API Keys:** API keys for the trading bot are **forbidden** from having withdrawal permission — so even if they leak, your funds stay safe.

---

## 🗺️ Folder Structure (A Quick Map)

```
aegis-forge/
│
├── 📖 README.md                ← MAIN GUIDE (you are here)
├── 🔧 SETUP.md                 ← Detailed technical setup
├── 📖 AGENTS.md                ← "Rulebook" for AI agents & developers
├── 🤝 CONTRIBUTING.md          ← How to contribute
├── 🚨 SECURITY.md              ← How to report a security issue
├── ⌨️ Makefile                 ← Collection of shortcut commands
├── 🐳 docker-compose.yml       ← Local services (database, cache, mock API)
│
├── 📁 docs/                    ← 📚 ALL GUIDES & TEMPLATES
│   ├── 📁 blueprints/          ← 🏗️ Architecture blueprints per project type
│   ├── 📁 agent-playbooks/     ← 🤖 Step-by-step workflows for AI
│   ├── 📁 security/            ← 🔐 Security checklists per domain
│   ├── 📁 adr/                 ← 📝 Architecture decisions + risk analysis
│   ├── 📁 diagrams/            ← 🎨 Visual architecture diagrams
│   │
│   ├── PRD-template.md         ← Template "what to build"
│   ├── schema-template.sql     ← Database template (DON'T edit!)
│   ├── schema.sql              ← Your active database schema (OK to edit)
│   ├── openapi-template.yaml   ← API contract template
│   ├── openapi.yaml            ← Your active API contract
│   └── prompt-library.md       ← 💬 Ready-to-use AI prompts
│
├── 📁 evals/                   ← 🧪 Tests for AI output quality
├── 📁 skills/                  ← 🛡️ Installable "rule packs" for AI agents
└── 📁 scripts/                 ← ⚙️ Automation scripts
    ├── init-new-project.sh     ← Create project (Linux/Mac)
    ├── init-new-project.ps1    ← Create project (Windows)
    ├── run-evals.sh            ← Test AI rule compliance (Linux/Mac)
    ├── run-evals.ps1           ← Test AI rule compliance (Windows)
    └── devsec-check.sh         ← Manual security check
```

> 💡 **No need to memorize all of this.** The important ones: `README.md` (guide), `AGENTS.md` (AI rules), and the `docs/` folder (all documentation). The rest works behind the scenes.

### Files You'll Edit Often

| File | Purpose | When to Edit |
|---|---|---|
| `docs/PRD.md` | What you want to build | At project start |
| `docs/schema.sql` | Database structure | When adding tables (menu, orders, etc.) |
| `docs/openapi.yaml` | API contract | When adding endpoints |
| `docs/ui-design.md` | UI/UX design | When designing screens |

### Files You Should NOT Edit

| File | Why Not |
|---|---|
| `*-template.*` (all templates) | These are the master copies — edit them and you lose your clean reference |
| `AGENTS.md` | This is the AI's work contract — changing it can break AI behavior |
| `.github/workflows/` | This is automated CI — changing it without understanding can break security |

---

## ⌨️ Common Commands

| Command | What it does (in plain words) |
|---|---|
| `make help` | Show all available commands. |
| `make new` | **Create a new project** from this template. |
| `make audit` | **Check security** — make sure no secrets are leaked. |
| `make up` | **Start** local services (database, etc.). |
| `make down` | **Stop** all local services. |
| `make mock-api` | Run a **fake API server** for testing at `http://localhost:4010`. |
| `make status` | See the status of running services. |

> 🪟 **Windows without `make`?** Use the PowerShell equivalents — see `SETUP.md`.

---

## 💼 Real-World Examples

### 🍜 Example 1: WhatsApp Food-Ordering Bot
**Need:** You sell food in your apartment building. Customers chat on WhatsApp; a bot replies automatically (menu, selection, total price), then forwards the order to you.

**How Aegis Forge helps:**
- ✅ `schema-template.sql` → design `menu`, `orders`, `order_items` tables
- ✅ Security baseline → store WhatsApp & LLM API keys **encrypted**
- ✅ `AGENTS.md` → AI writes code safely
- ✅ Audit trail → order history can't be manipulated
- 🔨 You add: WhatsApp connector, LLM integration, conversation logic

### 🏥 Example 2: Clinic Patient Portal
**Need:** A clinic wants patients to register online, view doctor schedules, and receive reminders.

**How Aegis Forge helps:**
- ✅ All web features (secure login, RBAC for admin/doctor/patient, audit trail for medical records)
- 🔨 You add: clinic business logic (booking, scheduling, notifications)

### 📈 Example 3: Gold Trading Bot
**Need:** A trader wants a bot that auto-trades XAUUSD with capital protection.

**How Aegis Forge helps:**
- ✅ Circuit breaker (emergency brake), 1% risk limit per trade, API key with no withdrawal permission
- 🔨 You add: specific trading strategy (indicators, entry/exit rules)

---

## ❓ Frequently Asked Questions (FAQ)

**❓ Do I need to know programming to use this?**
Not necessarily. This template is designed to work with AI agents (Claude, Cursor, Hermes, etc.). You describe what you want, the AI writes the code — this template makes sure the result is safe and clean.

**❓ How is this different from a framework like Laravel/Next.js?**
A framework is the **"engine"**. Aegis Forge is the **"rulebook + foundation"** that *complements* your chosen framework — it focuses on security, quality, and a correct workflow.

**❓ Is it free?**
Yes. It's licensed under **Apache-2.0** — free for personal and commercial use.

**❓ What if I only need one part of it?**
That's fine! Each part (security, checklists, AI guides) can be used on its own. See the `docs/` folder.

**❓ Is Aegis Forge overkill for a small, simple project?**
It can be. Aegis Forge is designed for projects that take security seriously (involving user data, money, or transactions). For a toy/experimental project, it might be too heavy. But for a real business — highly recommended.

---

## 🔧 Troubleshooting

<details>
<summary><b>😰 "make" command not found</b></summary>

- **Windows:** Use the PowerShell version — `pwsh scripts/init-new-project.ps1 ...`
- **Mac:** Install via `brew install make`
- **Linux:** Install via `sudo apt install make` (Ubuntu/Debian)
</details>

<details>
<summary><b>😰 "git" command not found</b></summary>

Install Git from [git-scm.com](https://git-scm.com)
</details>

<details>
<summary><b>😰 Docker won't start</b></summary>

1. Make sure Docker Desktop is installed and **running** (icon in system tray)
2. Try restarting Docker Desktop
3. If it still fails, you can skip Docker — it's not required to get started
</details>

<details>
<summary><b>😰 Commit rejected ("secret detected")</b></summary>

**Don't panic — this is the security feature working!**
1. Find the file containing the secret (usually `.env` or a config file)
2. Remove the secret from that file
3. Move it to a `.env` file that's already git-ignored
4. Commit again
</details>

<details>
<summary><b>😰 init-new-project script fails</b></summary>

1. Make sure you're running it from inside the `aegis-forge` folder
2. Make sure the target path (`../YourProject`) doesn't already exist
3. **Windows:** ensure PowerShell execution policy allows scripts:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
</details>

---

## 📚 Full Documentation

| Topic | File | What it's for |
|---|---|---|
| 🚀 **Quick start** | `SETUP.md` | Step-by-step technical setup |
| 📖 **AI rules** | `AGENTS.md` | Working contract for AI agents |
| 🤖 **AI workflows** | `docs/agent-playbooks/` | Step-by-step guides per project type |
| �️ **AI rule packs** | `skills/` | Installable guardrails for AI agents |
| 🧪 **AI quality tests** | `evals/` | Measure whether AI output follows the rules |
| �💬 **Ready prompts** | `docs/prompt-library.md` | Example instructions for AI |
| 🔐 **Security** | `docs/security/` | Security checklists per domain |
| 🧪 **Testing** | `docs/testing-strategy.md` | Overall testing strategy |
| 🚢 **Deployment** | `docs/deployment.md` | How to release to production |
| 🤝 **Contributing** | `CONTRIBUTING.md` | Commit & pull request rules |

---

## 🆘 Need Help?

- 🐛 **Found a bug or have an idea?** Open a [GitHub Issue](https://github.com/mochrzlf/aegis-forge/issues).
- 🔐 **Found a security vulnerability?** Follow the guide in [SECURITY.md](SECURITY.md) (please don't open a public issue).
- 🤝 **Want to contribute?** Read [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

**Apache-2.0** — free to use for personal and commercial purposes. See [LICENSE](LICENSE).

---

> 💡 **Remember:** You don't need to understand everything at once. Start small, learn as you go. Aegis Forge is designed to **keep you on the right track**, even when you don't know all the answers yet.
