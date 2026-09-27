# ❓ FAQ & Troubleshooting Guide

> **Quick answers to common questions and step-by-step solutions to typical setup roadblocks.**

---

## 💡 1. Frequently Asked Questions (FAQ)

### ❓ Do I need to know how to code to use Aegis Forge?
**No.** Aegis Forge is specifically structured to collaborate with AI coding agents (Claude Code, Cursor, Copilot, Hermes). You describe your business goals, and the AI handles the implementation. Aegis Forge provides the "guardrails" and pre-built components to ensure the AI writes safe, production-grade software instead of messy or insecure code.

### ❓ How is Aegis Forge different from frameworks like Laravel or Next.js?
A framework is the **engine**. Aegis Forge is the **entire car assembly and road safety handbook** — it complements frameworks by providing:
- Pre-configured Zero Trust IAM (token rotation, lockout, Maker-Checker).
- Pre-wired database schemas and immutable audit trails.
- Git pre-commit security hooks to prevent password and API key leaks.
- Standardized workflows (`AGENTS.md`) so AI coding assistants don't hallucinate.

### ❓ Is Aegis Forge free?
**Yes.** Aegis Forge is licensed under **Apache-2.0**. You are free to use it for personal, commercial, and enterprise projects without any licensing fees.

### ❓ What if I only want to use one specific component?
That is completely supported! You can use the security checklists in `docs/security/`, install the AI skills from `skills/`, or copy an individual starter skeleton from `templates/` into your existing project.

### ❓ Is Aegis Forge overkill for a small hobby project?
If your project is a simple throwaway script or a static personal blog, Aegis Forge might be more structure than you need. However, if your application stores user passwords, processes financial transactions, or handles confidential data, Aegis Forge prevents costly security mistakes from Day 1.

---

## 🛠️ 2. Troubleshooting Roadblocks

### 1. 😰 `'make' command not found`
- **Windows:** You do not need `make`. You can run the PowerShell setup script:
  ```powershell
  pwsh scripts/init-new-project.ps1
  ```
  Or install Make via Chocolatey: `choco install make` or Scoop: `scoop install make`.
- **macOS:** Install Apple command-line tools: `xcode-select --install` or via Homebrew: `brew install make`.
- **Linux (Ubuntu/Debian):** Install standard build tools:
  ```bash
  sudo apt update && sudo apt install -y build-essential
  ```

---

### 2. 😰 `'git' command not found`
- Download and install Git from the official website: [git-scm.com](https://git-scm.com).
- On Windows, we recommend installing **Git for Windows**, which includes Git Bash.

---

### 3. 😰 Docker won't start or `Cannot connect to the Docker daemon`
1. Ensure **Docker Desktop** is installed and actively **running** (check for the whale icon in your system tray or menu bar).
2. If on Windows WSL2, open Docker Desktop Settings → **Resources** → **WSL Integration**, and toggle on your Ubuntu/Linux distribution.
3. Restart Docker Desktop if it is frozen.

---

### 4. 😰 Git commit rejected: `[Gitleaks] Secret detected!`
**Do not panic — this means the security alarm worked as intended!**
1. Review the terminal message to see which file and line triggered the alert.
2. If you accidentally typed a real password, API key, or token in a code file, remove it immediately.
3. Move the secret into your local `.env` file (which is git-ignored by default).
4. Stage the clean file and commit again:
   ```bash
   git add .
   git commit -m "feat: updated configuration safely"
   ```

---

### 5. 😰 `init-new-project` script permission denied or script fails
- **On Linux / Mac / WSL:** Give execution permission to the script:
  ```bash
  chmod +x scripts/init-new-project.sh
  bash scripts/init-new-project.sh
  ```
- **On Windows (PowerShell):** Ensure PowerShell allows running local scripts:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  pwsh scripts/init-new-project.ps1
  ```
- **Path Conflict:** Ensure the target folder (e.g. `../YourProject`) does not already exist before running the script.

---

### 6. 😰 Port Conflict: `port is already allocated (8000 or 5432)`
Another service on your computer is already using port 8000 (web) or 5432 (Postgres).
- Check what is running:
  - Linux/Mac: `sudo lsof -i :8000` or `sudo lsof -i :5432`
  - Windows: `netstat -ano | findstr :8000`
- Stop the existing container or process, or change the mapped port in `docker-compose.yml` (e.g. change `"8000:8000"` to `"8080:8000"`).

---

> 💡 **Next Steps:**
> - Return to the main guide: [README.md](../README.md).
> - Explore technical setup instructions: [SETUP.md](../SETUP.md).
