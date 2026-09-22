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

### 🤖 The Real Problem: Why AI Coding Agents Need Guardrails

Modern AI coding agents (Claude Code, Cursor, Copilot, Hermes) write code at blistering speed. But when asked to build an application from scratch on a blank canvas, **AI agents are notoriously careless with security**:

- 🔓 **Fragile Authentication:** They frequently dump raw JWT tokens into browser `localStorage` (trivially vulnerable to XSS credential theft).
- 🚪 **Missing Rate Limits:** They omit brute-force defenses, leaving login endpoints vulnerable to automated credential stuffing.
- 🕳️ **Broken Access Controls:** They forget object-level authorization checks, creating Insecure Direct Object References (IDOR).
- 💥 **Reckless Trading Algorithms:** If asked to write a trading bot, they often author unhedged grid or martingale algorithms that inevitably liquidate user accounts on market volatility.
- 🌀 **Hallucinated Scope:** Without an immutable technical contract, they drift from requirements and invent speculative abstractions.

### 🛡️ How Aegis Forge Solves It (The "Earthquake-Proof Bunker" Analogy)

Think of building software like constructing a building:
- **Hiring an AI agent without Aegis Forge** is like giving a power tool to an eager worker on an empty plot with no blueprint. They might throw up walls in record time, but the foundation is cracked, the plumbing leaks, and the front door has no lock.
- **Aegis Forge is the earthquake-proof bunker foundation.** It provides:
  1. ⚡ **An "Electric Fence" for AI Agents (`AGENTS.md` + Spec-First):** AI tools are strictly pinned to verified contracts (`docs/openapi.yaml`, PRD, STRIDE threat models). They are prevented from hallucinating or cutting security corners.
  2. 🏦 **Enterprise Banking-Grade IAM from Day One:** Zero Trust session management, Refresh Token Rotation (RTR) with replay detection, JML session kill-switches, database-enforced Maker-Checker dual control, and automated lockout.
  3. 🧱 **Pre-Tested Starter Skeletons:** You never start from zero. The core FastAPI backend, Android Kotlin module, and MQL5 EA trading engine are already built, runtime-verified, and protected by automated CI test suites.

**Aegis Forge solves all of this upfront.** Whether you're building a SaaS portal, an Android app, or an automated trading bot — all core architecture patterns, security checklists, and AI agent rules are ready on day one.

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
- **A runnable starter skeleton** (`templates/web-app/` or `templates/web-app-nextjs-supabase/`) — login, database & security already working; you just add features
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

## 🚀 Getting Started: 7 Easy Steps

> 💡 **Easiest way:** open this folder in **VS Code**, then click **"Reopen in Container"** when prompted. All the tools you need will be installed automatically — no manual setup required.

### Step 1 — Get a Copy of the Template

Open a **terminal** (PowerShell on Windows, Terminal on Mac/Linux), then:

```bash
# Download the template
git clone https://github.com/mochrzlf/aegis-forge.git
cd aegis-forge
```

### Step 2 — Create Your New Project

You can run the setup wizard interactively (recommended) or pass arguments directly:

```bash
# 🧙‍♂️ Interactive Setup Wizard (asks you questions step-by-step):
bash scripts/init-new-project.sh

# Or run directly with arguments:
# 🌐 For a Web App:
bash scripts/init-new-project.sh "YourProjectName" "../YourProjectName" web

# 📱 For a Mobile App:
bash scripts/init-new-project.sh "YourProjectName" "../YourProjectName" mobile

# 📈 For a Trading Bot:
bash scripts/init-new-project.sh "YourProjectName" "../YourProjectName" trading
```

> 🪟 **On Windows (PowerShell)?** Use the `.ps1` version instead:
> ```powershell
> # Interactive Wizard:
> pwsh scripts/init-new-project.ps1
> 
> # Or directly with arguments:
> pwsh scripts/init-new-project.ps1 "YourProjectName" "../YourProjectName" web
> ```

> 💡 **What the Wizard lets you choose:**
> 1. **Pre-built Templates:** FastAPI (Python), Express.js (TypeScript), Laravel 11 (PHP), Next.js + Supabase, MT5 EA Trading, or Android Kotlin.
> 2. **Custom Stack Mix & Match:** Pick your own Frontend (Next.js, React Vite, Vue, SvelteKit), Backend (FastAPI, Express, Laravel, Go, NestJS, Spring Boot), CSS (Tailwind, Shadcn, Bootstrap), and Database (Postgres, MySQL, SQLite, Mongo, Redis).
> 3. **Banking-Grade Security Choice:** Choose whether to enforce enterprise banking IAM standards (RTR, lockout, JML kill-switch, Maker-Checker, immutable audit log). If yes, the wizard generates `AI-AGENT-PROMPT.md` for your AI Agent to configure the rules into your custom stack!

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

> *"Use the prd-interviewer skill. Read AGENTS.md, then draft docs/PRD.md and docs/PRD-detail.md for my project based on the blueprint in docs/blueprints/ — interview me first. Then run a STRIDE security analysis in docs/adr/ before writing application code."*

The AI will create planning documents and analyze security risks **before** it starts programming — just like an architect draws blueprints before building.

### Step 4 — Break the Plan into Tasks

Don't let the AI start coding from a one-page idea. Have it turn the PRD into a list of small, ordered tasks first:

> *"Use the spec-to-tasks skill. Break docs/PRD.md into docs/TASKS.md — atomic tasks with dependencies and a skeleton_hint for each."*

The result is `docs/TASKS.md`: bite-sized tasks the AI (or you) can finish one at a time — each pointing at the exact file to edit. This keeps the AI on-track and prevents "hallucinated" big-bang code.

### Step 5 — Start from a Ready-Made Skeleton (Don't Start from Zero)

This is the biggest time-saver. Aegis Forge ships **runnable starter skeletons** in `templates/` — the login, database, and security are **already working**. You copy one and your AI *edits* it, instead of writing everything from scratch.

### 📊 Domain Maturity Matrix

| Domain | Blueprint Specification | Starter Skeleton | CI & Test Verification | Maturity Status |
|---|---|---|---|---|
| **Web (FastAPI Backend)** | ✅ `docs/blueprints/web-application-blueprint.md` | ✅ `templates/web-app/` | ✅ Docker Compose smoke test + 20 Pytest unit tests | **Production-Ready Core** (Python) |
| **Web (Express.js Backend)** | ✅ `docs/blueprints/web-application-blueprint.md` | ✅ `templates/web-app-express/` | ✅ Docker Compose + 9 Vitest unit tests | **Production-Ready Core** (TypeScript) |
| **Web (Laravel Backend)** | ✅ `docs/blueprints/web-application-blueprint.md` | ✅ `templates/web-app-laravel/` | ✅ Docker Compose + 10 PHPUnit feature tests | **Production-Ready Core** (PHP) |
| **Trading EA & Quantitative** | ✅ `docs/blueprints/ea-trading-blueprint.md` | ✅ `templates/trading-ea/` (MQL5 + FastAPI bridge) | ✅ 6 Pytest unit tests (Risk Guardian & Sizing) | **Code-Backed Starter** |
| **Mobile (Android Kotlin)** | ✅ `docs/blueprints/mobile-application-blueprint.md` | ✅ `templates/mobile-android/` (Keystore + Pinning) | ✅ Architecture verified (Clean Arch + AppSec) | **Code-Backed Starter** |
| **Web (Next.js + Supabase)** | ✅ `docs/blueprints/web-application-blueprint.md` | ⚠️ `templates/web-app-nextjs-supabase/` | ⚠️ Manual verification | **Reference Only** (trades strictness for UI speed) |

### 🧰 Available Starter Skeletons

| Skeleton | Best for | What's inside |
|---|---|---|
| **`templates/web-app/`** ⭐ default | A secure backend/API (Python) | FastAPI + Postgres + Redis. Login (RTR), RBAC/anti-IDOR, lockout, JML kill-switch, Maker-Checker, MFA/TOTP, audit trail — **CI smoke-tested & Pytest verified (20 tests)**. |
| **`templates/web-app-express/`** | A secure backend/API (TypeScript) | Express.js + Postgres + Redis. Login (RTR), lockout, JML kill-switch, Maker-Checker DB constraint, audit trigger — **Vitest verified (9 tests)**. |
| **`templates/web-app-laravel/`** | A secure backend/API (PHP) | Laravel 11 + Postgres + Redis. Login (RTR), lockout, JML kill-switch, Maker-Checker DB constraint, audit trail — **PHPUnit verified (10 tests)**. |
| **`templates/trading-ea/`** | Algo trading & Expert Advisors | FastAPI Risk Guardian bridge + native MQL5 EA template (`AegisRiskGuardianEA.mq5`). Dynamic lot sizing (1-2%), hard SL, 5% drawdown circuit breaker — **Pytest verified (6 tests)**. |
| **`templates/mobile-android/`** | Secure native Android app | Kotlin Native with Android Keystore `SecureStorage` (AES256-GCM), `network_security_config.xml` (SSL Pinning), `FLAG_SECURE` screen protection, and ProGuard/R8 rules. |
| **`templates/web-app-nextjs-supabase/`** | Fast website with UI | Next.js + Supabase. Pages, login, dashboard (RLS). Reference-only alternative. |

Copy a skeleton into your project and run it:

```bash
# Example: secure backend skeleton
cp -r templates/web-app/* .
make first-run     # copies .env, builds, runs migrations → app live at localhost:8000
```

> 🖥️ **Where does the Frontend UI go? (Option A vs. Option B)**
>
> The default skeleton (`templates/web-app/`) is an **API-first / Headless Backend** (FastAPI + Postgres + Redis). Right after `make first-run`, you have:
> - Interactive API documentation at `http://localhost:8000/docs` (Swagger UI)
> - Mailpit web client at `http://localhost:8025` (simulated inbox for password reset & verify emails)
>
> **When and where do you create your frontend (React, Vite, Next.js, or Vue)?**
> - **In Step 3 (Define Specs):** Define your UI mockups, screens, and design tokens in `docs/ui-design.md` and `docs/PRD.md`.
> - **In Step 6 (Build Features):** Ask your AI agent:
>   > *"Scaffold a frontend in `frontend/` using React + Vite + Tailwind CSS that connects to our FastAPI backend at `http://localhost:8000`."*
>
> *(Prefer a skeleton with a pre-built web UI from day one? Choose `2) web-app-nextjs-supabase` in Step 2).*

> 💡 Your AI's tasks in `TASKS.md` already say *which skeleton file to edit* (the `skeleton_hint`) — so it modifies existing safe code instead of generating new code from nothing.

### Step 6 — Build Your Features

Now just build. Your AI agent already has all the rules (via `AGENTS.md`), ready-to-use example prompts (in `docs/prompt-library.md`), and guided workflows (in `docs/agent-playbooks/`).

> 🛡️ **Want the strongest AI compliance?** Install the ready-made "rule packs" directly into your AI agent — so the rules load automatically instead of hoping the AI reads them:
> ```bash
> npx skills add mochrzlf/aegis-forge
> ```
> These cover trading risk limits, security checklists, API standards, and more. See the [`skills/`](skills/) folder for details.

> 🧪 **Want proof your AI follows the rules?** The `evals/` folder can *measure* it — run `pwsh scripts/run-evals.ps1` (Windows) or `bash scripts/run-evals.sh` (Linux/Mac) with your own AI API key. See [`evals/`](evals/) for details.

### Step 7 — Check Security & Save

Before saving (committing), make sure it's safe:

```bash
# Check security anytime:
make audit

# Every commit is automatically scanned for leaked secrets:
git add .
git commit -m "feat: add user registration feature"
```

**Done!** 🎉 Your project now stands on a secure foundation.

### 🎯 Concrete Walkthrough: Building an E-Commerce Store ("TokoKeren")

Here is exactly how the 7 steps look in practice when building an online store:

| Stage | Command / Prompt | What Happens |
|---|---|---|
| **1. Initialize (Step 2)** | `bash scripts/init-new-project.sh TokoKeren ../TokoKeren web`<br>*(Select `1` for FastAPI)* | Generates `../TokoKeren/` with pre-wired IAM, unique `.env` crypto keys, gitleaks pre-commit hooks, and starter code. |
| **2. Navigate** | `cd ../TokoKeren` | Enter your new project workspace. |
| **3. Plan Specs (Step 3)** | Prompt AI: *"Use the `prd-interviewer` skill to interview me and draft `docs/PRD.md` for TokoKeren (product catalog, cart, checkout, payment webhooks, and buyer/admin roles)."* | AI interviews you and creates an airtight requirement spec without hallucinating scope. |
| **4. Break Tasks (Step 4)** | Prompt AI: *"Use the `spec-to-tasks` skill to turn `docs/PRD.md` into atomic tasks in `docs/TASKS.md` with explicit `skeleton_hint`."* | AI generates manageable tasks, each pointing to the exact skeleton file to edit. |
| **5. Start Stack (Step 5)** | `make first-run` | Starts PostgreSQL, Redis, runs DB migrations, and launches FastAPI at `http://localhost:8000` (docs at `/docs`). |
| **6. Build Backend & UI (Step 6)** | Prompt AI:<br>• *(Backend)* *"Execute Task 1 from `docs/TASKS.md`: Implement product catalog endpoints per skeleton_hint."*<br>• *(Frontend UI - Option A)* *"Scaffold a web frontend in `frontend/` using Vite + React + Tailwind CSS that connects to `http://localhost:8000`."* | AI edits existing safe backend code first, then scaffolds the decoupled web UI. |
| **7. Verify & Save (Step 7)** | `make test && make audit`<br>`git add . && git commit -m "feat: add product catalog"` | Runs 20+ automated tests, scans for leaked secrets, and commits cleanly. |

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
│   ├── schema.sql              ← Your active database schema (OK to edit)
│   ├── openapi.yaml            ← Your active API contract
│   └── prompt-library.md       ← 💬 Ready-to-use AI prompts
│
├── 📁 evals/                   ← 🧪 Tests for AI output quality
├── 📁 skills/                  ← 🛡️ Installable "rule packs" for AI agents
├── 📁 templates/               ← 🏠 Runnable starter skeletons (copy & run!)
│   ├── web-app/                ←   FastAPI + Postgres + Redis (secure backend)
│   └── web-app-nextjs-supabase/←   Next.js + Supabase (full website + UI)
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
- ✅ `schema.sql` → design `menu`, `orders`, `order_items` tables
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
