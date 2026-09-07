#!/usr/bin/env bash
# Aegis Forge — devcontainer post-create setup
# Runs once after the container is built. Keeps setup idempotent and non-fatal
# so a missing optional tool never breaks environment provisioning.
set -e

echo "=================================================================="
echo "🔧 Aegis Forge devcontainer — post-create setup"
echo "=================================================================="

# --- Python tooling (pre-commit + validators) -------------------------------
if command -v pip >/dev/null 2>&1; then
    echo "🐍 Installing Python tooling (pre-commit, PyYAML)..."
    pip install --quiet --upgrade pip
    pip install --quiet pre-commit pyyaml || echo "⚠️  pip tool install skipped"
else
    echo "ℹ️  pip not found; skipping Python tooling."
fi

# --- pre-commit framework hooks (optional layer on top of .git/hooks) -------
if command -v pre-commit >/dev/null 2>&1 && [ -f ".pre-commit-config.yaml" ]; then
    echo "🪝 Installing pre-commit framework hooks..."
    pre-commit install --allow-missing-config >/dev/null 2>&1 \
        && echo "   pre-commit hooks installed." \
        || echo "   (pre-commit install skipped — non-fatal)"
fi

# --- Node / web dependencies (only if a package.json exists) ----------------
if [ -f "package.json" ]; then
    echo "📦 Installing Node dependencies..."
    if [ -f "pnpm-lock.yaml" ] && command -v pnpm >/dev/null 2>&1; then
        pnpm install --frozen-lockfile || npm ci || npm install
    elif [ -f "package-lock.json" ]; then
        npm ci || npm install
    else
        npm install
    fi
else
    echo "ℹ️  No package.json yet — skipping Node dependency install."
fi

# --- Gitleaks (secret scanning) ---------------------------------------------
if ! command -v gitleaks >/dev/null 2>&1; then
    echo "🛡️  Installing gitleaks..."
    GITLEAKS_VERSION="8.24.3"
    ARCH="$(uname -m)"; [ "$ARCH" = "aarch64" ] && ARCH="arm64" || ARCH="x64"
    curl -sSfL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_${ARCH}.tar.gz" \
        | sudo tar -xz -C /usr/local/bin gitleaks 2>/dev/null \
        && echo "   gitleaks v${GITLEAKS_VERSION} installed." \
        || echo "   (gitleaks install skipped — non-fatal)"
fi

echo "=================================================================="
echo "✅ devcontainer ready. Next:"
echo "   • make up        # start postgres/redis/mailpit/prism"
echo "   • make mock-api  # start Prism mock API on :4010"
echo "=================================================================="
