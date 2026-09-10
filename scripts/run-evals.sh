#!/usr/bin/env bash
# ==============================================================================
# Aegis Forge — Agent Evals guard & launcher (Linux / macOS / Git Bash / WSL)
#
# Interactive guard before running the promptfoo agent evals:
#   1. Verifies npx is available.
#   2. Checks that an LLM provider API key is configured; if not, offers an
#      interactive (masked) setup that persists the key to the local .env
#      file (git-ignored, gitleaks-protected).
#   3. Confirms paid API usage with the user before spending anything.
#   4. Runs: npx promptfoo@latest eval -c evals/promptfooconfig.yaml
#
# API keys are NEVER written to the repo, the command line, or logs.
#
# Usage:
#   bash scripts/run-evals.sh           # run evals
#   bash scripts/run-evals.sh --view    # also open the results viewer
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"
CONFIG="$REPO_ROOT/evals/promptfooconfig.yaml"
VIEW="${1:-}"

echo ""
echo "🛡️  Aegis Forge — Agent Evals Setup Check"
echo "────────────────────────────────────────────────────────────"

# --- Load provider keys already present in the local .env ---------------------
if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source <(grep -E '^[A-Z0-9_]+=' "$ENV_FILE" | grep -v '^\s*#') || true
    set +a
fi

# --- Step 1: npx available? ----------------------------------------------------
if ! command -v npx >/dev/null 2>&1; then
    echo "❌ npx not found. Install Node.js (LTS) first: https://nodejs.org"
    exit 1
fi
echo "✅ npx available — promptfoo will run as npx promptfoo@latest"

# --- Step 2: API key configured? ----------------------------------------------
KEY_VAR=""
for var in OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY; do
    val="${!var:-}"
    if [[ -n "$val" && "$val" != *REPLACE* ]]; then
        KEY_VAR="$var"
        break
    fi
done

if [[ -n "$KEY_VAR" ]]; then
    echo "✅ Provider key detected: $KEY_VAR (value hidden)"
else
    echo "❌ No LLM provider API key found (checked: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)"
    echo ""
    echo "Choose your provider:"
    echo "  1) OpenAI     (OPENAI_API_KEY)"
    echo "  2) Anthropic  (ANTHROPIC_API_KEY)"
    echo "  3) Google     (GOOGLE_API_KEY)"
    echo "  q) Cancel"
    read -r -p "Selection: " choice
    case "$choice" in
        1) KEY_VAR="OPENAI_API_KEY" ;;
        2) KEY_VAR="ANTHROPIC_API_KEY" ;;
        3) KEY_VAR="GOOGLE_API_KEY" ;;
        *) echo "Cancelled. No changes made."; exit 0 ;;
    esac

    # Masked input — the key is never echoed to the terminal.
    read -r -s -p "Paste your API key (input hidden): " api_key
    echo ""
    if [[ -z "$api_key" ]]; then
        echo "❌ Empty key — aborted."
        exit 1
    fi

    entry="$KEY_VAR=\"$api_key\""
    if [[ -f "$ENV_FILE" ]]; then
        if grep -qE "^#?\s*$KEY_VAR=" "$ENV_FILE"; then
            # Replace existing (possibly commented-out) line in place.
            sed -i.bak -E "s|^#?\s*$KEY_VAR=.*|$entry|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
        else
            printf '\n# LLM / AGENT EVALS (added by run-evals.sh, %s)\n%s\n' \
                "$(date +%F)" "$entry" >> "$ENV_FILE"
        fi
    else
        printf '# Local secrets — NEVER commit (protected by .gitignore + gitleaks)\n%s\n' \
            "$entry" > "$ENV_FILE"
    fi
    unset api_key  # scrub from memory ASAP
    echo "✅ Key saved to local .env (git-ignored, gitleaks-protected)"
    export "$KEY_VAR=<set>"
fi

# --- Step 3: confirm paid API usage --------------------------------------------
echo ""
echo "⚠️  This will call a PAID LLM API (6 scenarios × agent + judge calls)."
echo "   Typical cost is small, but it is billed to YOUR provider account."
read -r -p "Proceed with evals? [y/N] " go
if [[ ! "$go" =~ ^[yY]([eE][sS])?$ ]]; then
    echo "Cancelled. No API calls were made."
    exit 0
fi

# --- Step 4: run the evals ------------------------------------------------------
echo ""
echo "🚀 Running promptfoo evals..."
cd "$REPO_ROOT"
if npx --yes promptfoo@latest eval -c "$CONFIG"; then
    echo ""
    echo "✅ Evals finished. Browse results with:"
    echo "   npx promptfoo@latest view"
    if [[ "$VIEW" == "--view" ]]; then
        npx --yes promptfoo@latest view
    fi
else
    code=$?
    echo ""
    echo "❌ promptfoo exited with code $code — see output above."
    exit "$code"
fi
