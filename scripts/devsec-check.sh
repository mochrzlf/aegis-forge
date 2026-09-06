#!/usr/bin/env bash
set -e

# ==============================================================================
# AUTOMATED DEVSECOPS PRE-FLIGHT AUDIT
# ==============================================================================

echo "🔍 Menjalankan Automated Security Pre-flight Check..."

EXIT_CODE=0

# 1. Periksa apakah .env ter-track oleh Git
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
    echo "❌ FATAL: File .env terdeteksi berada di dalam staging/tracking Git!"
    echo "   Jalankan: git rm --cached .env"
    EXIT_CODE=1
else
    echo "✅ Proteksi .env: OK (Tidak ter-track Git)"
fi

# 2. Periksa apakah ada file kredensial berbahaya
SUSPICIOUS_FILES=$(find . -maxdepth 3 -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "id_rsa*" 2>/dev/null | grep -v "/node_modules/" || true)
if [ -n "$SUSPICIOUS_FILES" ]; then
    echo "⚠️  PERINGATAN: Ditemukan file kunci privat:"
    echo "$SUSPICIOUS_FILES"
    EXIT_CODE=1
else
    echo "✅ Private Key Scan: OK (Tidak ada private key sensitif)"
fi

# 3. Gitleaks scan jika terpasang
if command -v gitleaks >/dev/null 2>&1; then
    echo "🔍 Menjalankan Gitleaks audit..."
    if ! gitleaks detect --no-git --source . --verbose; then
        echo "❌ Kredensial atau secret terdeteksi oleh Gitleaks!"
        EXIT_CODE=1
    else
        echo "✅ Gitleaks Secret Audit: Clean"
    fi
else
    echo "ℹ️  Gitleaks belum terpasang di sistem. Pasang untuk deteksi secret otomatis."
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 Semua pemeriksaan keamanan dasar lolos!"
else
    echo "❌ Pemeriksaan keamanan menemukan masalah! Harap perbaiki sebelum melanjutkan."
fi

exit $EXIT_CODE
