#!/usr/bin/env bash
# ==============================================================================
# Aegis Forge — Agent Evals guard & launcher (Linux / macOS / Git Bash / WSL)
#
# Interactive guard before running the promptfoo agent evals:
#   1. Verifies npx is available.
#   2. Checks that a generic OpenAI-compatible provider is configured in the
#      local .env (EVAL_API_BASE_URL, EVAL_MODEL, EVAL_API_KEY); if not, offers
#      an interactive (masked) setup that persists them to .env (git-ignored,
#      gitleaks-protected).
#   3. Confirms paid API usage with the user before spending anything.
#   4. Runs the per-scenario configs in evals/suites/ (one config per scenario
#      -> clean 1:1 prompt-to-scenario pairing).
#
# API keys are NEVER written to the repo, the command line, or logs.
#
# Usage:
#   bash scripts/run-evals.sh                      # guarded run, all suites
#   bash scripts/run-evals.sh prd-interview        # run one suite
#   bash scripts/run-evals.sh --view               # run + open results viewer
#   bash scripts/run-evals.sh prd-interview --view # one suite + viewer
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"
SUITES_DIR="$REPO_ROOT/evals/suites"
SUITE=""
VIEW=""

for arg in "$@"; do
    case "$arg" in
        --view) VIEW="--view" ;;
        *)      SUITE="$arg" ;;
    esac
done

echo ""
echo "🛡️  Aegis Forge — Agent Evals Setup Check"
echo "────────────────────────────────────────────────────────────"

# --- Load provider vars already present in the local .env ----------------------
if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source <(grep -E '^[A-Z0-9_]+=' "$ENV_FILE" | grep -v '^\s*#') || true
    set +a
fi

save_env() {
    # save_env NAME VALUE — upsert a variable into .env and export it.
    local name="$1" value="$2"
    if [[ -f "$ENV_FILE" ]] && grep -qE "^#?\s*$name=" "$ENV_FILE"; then
        sed -i.bak -E "s|^#?\s*$name=.*|$name=\"$value\"|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
    else
        [[ -f "$ENV_FILE" ]] || printf '# Local secrets — NEVER commit (protected by .gitignore + gitleaks)\n' > "$ENV_FILE"
        printf '%s="%s"\n' "$name" "$value" >> "$ENV_FILE"
    fi
    export "$name=$value"
}

# --- Step 1: npx available? ------------------------------------------------------
if ! command -v npx >/dev/null 2>&1; then
    echo "❌ npx not found. Install Node.js (LTS) first: https://nodejs.org"
    exit 1
fi
echo "✅ npx available — promptfoo will run as npx promptfoo@latest"

# --- Step 2: provider configured? --------------------------------------------------
if [[ -n "${EVAL_API_BASE_URL:-}" && -n "${EVAL_MODEL:-}" && -n "${EVAL_API_KEY:-}" ]]; then
    echo "✅ Provider configured: EVAL_MODEL=$EVAL_MODEL @ $EVAL_API_BASE_URL (key hidden)"
else
    echo "❌ Eval provider not configured (need EVAL_API_BASE_URL + EVAL_MODEL + EVAL_API_KEY)."
    echo ""
    echo "These describe any OpenAI-compatible chat endpoint the evals will call."
    echo "Examples: https://api.openai.com/v1 + gpt-4o-mini, or a local router."
    echo ""
    read -r -p "EVAL_API_BASE_URL (e.g. https://api.openai.com/v1): " base
    [[ -n "$base" ]] || { echo "❌ Base URL is required — aborted."; exit 1; }
    read -r -p "EVAL_MODEL (model id your endpoint serves): " model
    [[ -n "$model" ]] || { echo "❌ Model is required — aborted."; exit 1; }
    read -r -s -p "EVAL_API_KEY (input hidden): " api_key
    echo ""
    [[ -n "$api_key" ]] || { echo "❌ Empty key — aborted."; exit 1; }

    save_env "EVAL_API_BASE_URL" "$base"
    save_env "EVAL_MODEL" "$model"
    save_env "EVAL_API_KEY" "$api_key"
    unset api_key  # scrub from memory ASAP
    echo "✅ Provider saved to local .env (git-ignored, gitleaks-protected)"
fi

# --- Step 3: choose suites ---------------------------------------------------------
mapfile -t all_suites < <(find "$SUITES_DIR" -maxdepth 1 -name '*.yaml' -printf '%f\n' 2>/dev/null | sort)
if [[ ${#all_suites[@]} -eq 0 ]]; then
    echo "❌ No suite configs found in evals/suites/."
    exit 1
fi

to_run=("${all_suites[@]}")
if [[ -n "$SUITE" ]]; then
    to_run=()
    for f in "${all_suites[@]}"; do
        [[ "${f%.yaml}" == "$SUITE" ]] && to_run=("$f")
    done
    if [[ ${#to_run[@]} -eq 0 ]]; then
        echo "❌ Suite '$SUITE' not found. Available:"
        for f in "${all_suites[@]}"; do echo "   - ${f%.yaml}"; done
        exit 1
    fi
fi

# --- Step 4: confirm paid API usage ---------------------------------------------------
echo ""
echo "⚠️  This will call a PAID LLM API (${#to_run[@]} suite(s) × agent + judge calls)."
echo "   Typical cost is small, but it is billed to YOUR provider account."
read -r -p "Proceed with evals? [y/N] " go
if [[ ! "$go" =~ ^[yY]([eE][sS])?$ ]]; then
    echo "Cancelled. No API calls were made."
    exit 0
fi

# --- Step 5: run the evals -------------------------------------------------------------
echo ""
echo "🚀 Running ${#to_run[@]} suite(s)..."
cd "$REPO_ROOT"
failures=()
for f in "${to_run[@]}"; do
    name="${f%.yaml}"
    echo ""
    echo "▶ $name"
    if ! npx --yes promptfoo@latest eval -c "evals/suites/$f" --no-cache; then
        failures+=("$name")
    fi
done

echo ""
if [[ ${#failures[@]} -eq 0 ]]; then
    echo "✅ All ${#to_run[@]} suite(s) finished without harness errors."
    echo "   (Scenario pass/fail reflects the MODEL under test — inspect with:)"
    echo "   npx promptfoo@latest view"
    if [[ "$VIEW" == "--view" ]]; then
        npx --yes promptfoo@latest view
    fi
    exit 0
else
    echo "⚠️  ${#failures[@]} suite(s) exited non-zero (model assertions failed or API error):"
    for n in "${failures[@]}"; do echo "   - $n"; done
    echo "   Re-inspect a single suite: npx promptfoo@latest eval -c evals/suites/<name>.yaml --no-cache"
    exit 1
fi
