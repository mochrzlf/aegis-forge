#!/usr/bin/env bash
set -e

# Ensure PATH includes ~/.local/bin so gitleaks/hermes is always found
export PATH="$HOME/.local/bin:$PATH"

# ==============================================================================
# AUTOMATED DEVSECOPS AUDIT SCRIPT
# ==============================================================================

MODE="$1"
EXIT_CODE=0

echo "🔍 Running Automated Security Audit..."

# 1. Check if .env is tracked by Git
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
    echo "❌ FATAL: .env file detected in Git staging/tracking!"
    echo "   Run: git rm --cached .env"
    EXIT_CODE=1
else
    echo "✅ .env Protection: OK (Not tracked by Git)"
fi

# 2. Check for dangerous credential files
SUSPICIOUS_FILES=$(find . -maxdepth 3 -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "id_rsa*" 2>/dev/null | grep -v "/node_modules/" || true)
if [ -n "$SUSPICIOUS_FILES" ]; then
    echo "⚠️  WARNING: Private key file(s) found:"
    echo "$SUSPICIOUS_FILES"
    EXIT_CODE=1
else
    echo "✅ Private Key Scan: OK (No sensitive private keys found)"
fi

# 3. Gitleaks scan if installed
if command -v gitleaks >/dev/null 2>&1; then
    if [ "$MODE" = "--staged" ]; then
        echo "🔍 Running Gitleaks protect on staged changes..."
        if ! gitleaks protect -v --staged; then
            echo "❌ Credentials or secrets detected in changes staged for commit!"
            EXIT_CODE=1
        else
            echo "✅ Gitleaks Pre-Commit Audit: Clean (No leaks detected)"
        fi
    else
        echo "🔍 Running Gitleaks full repository audit..."
        if ! gitleaks detect --verbose; then
            echo "❌ Credentials or secrets detected by Gitleaks!"
            EXIT_CODE=1
        else
            echo "✅ Gitleaks Repository Audit: Clean"
        fi
    fi
else
    echo "ℹ️  Gitleaks is not installed on the system. Install it for automated secret detection."
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 All security checks passed!"
else
    echo "❌ Security checks encountered issues! Operation aborted."
fi

exit $EXIT_CODE
