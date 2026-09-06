#!/usr/bin/env bash
set -e

# ==============================================================================
# UNIVERSAL MULTI-DOMAIN PROJECT SCAFFOLDING
# ==============================================================================

PROJECT_NAME="$1"
TARGET_DIR="$2"
PROJECT_TYPE="${3:-fullstack}"

if [ -z "$PROJECT_NAME" ] || [ -z "$TARGET_DIR" ]; then
    echo "Penggunaan: bash init-new-project.sh <NamaProject> <PathTujuan> [web|mobile|trading|fullstack]"
    echo "Contoh:"
    echo "  bash init-new-project.sh FinPortal /home/tpam_su/Project/FinPortal web"
    echo "  bash init-new-project.sh FinMobile /home/tpam_su/Project/FinMobile mobile"
    echo "  bash init-new-project.sh QuantEA   /home/tpam_su/Project/QuantEA trading"
    exit 1
fi

BASELINE_DIR="/home/tpam_su/Project/Baseline"

echo "=================================================================="
echo "🚀 Membuat Universal Project: $PROJECT_NAME"
echo "📁 Lokasi target: $TARGET_DIR"
echo "🏷️  Tipe Domain: ${PROJECT_TYPE^^}"
echo "=================================================================="

if [ -d "$TARGET_DIR" ]; then
    echo "⚠️  Direktori $TARGET_DIR sudah ada! Batalkan untuk mencegah penimpaan data."
    exit 1
fi

mkdir -p "$TARGET_DIR"

# Salin direktori & file dari Baseline
cp -r "$BASELINE_DIR/AGENTS.md" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/README.md" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/SETUP.md" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/SECURITY.md" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/LICENSE" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/Makefile" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.env.example" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.gitignore" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.gitattributes" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.editorconfig" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.gitleaks.toml" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/docker-compose.yml" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.github" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/docs" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/scripts" "$TARGET_DIR/"

# Salin template PRD menjadi PRD aktif
cp "$TARGET_DIR/docs/PRD-template.md" "$TARGET_DIR/docs/PRD.md"
cp "$TARGET_DIR/docs/PRD-detail-template.md" "$TARGET_DIR/docs/PRD-detail.md"
cp "$TARGET_DIR/docs/ui-design-template.md" "$TARGET_DIR/docs/ui-design.md"
cp "$TARGET_DIR/docs/schema-template.sql" "$TARGET_DIR/docs/schema.sql"
cp "$TARGET_DIR/docs/openapi-template.yaml" "$TARGET_DIR/docs/openapi.yaml"

# Ganti placeholder [PROJECT_NAME] di semua file teks
find "$TARGET_DIR" -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.sql" -o -name ".env.example" \) | while read -r file; do
    sed -i "s/\[PROJECT_NAME\]/$PROJECT_NAME/g" "$file"
done

# Inisialisasi Git Repository lokal jika belum ada
cd "$TARGET_DIR"
if [ ! -d ".git" ]; then
    git init -b main
    echo "✅ Git repository berhasil diinisialisasi."
fi

# Pasang Git Pre-Commit Security Hook
mkdir -p "$TARGET_DIR/.git/hooks"
cat << 'HOOK_EOF' > "$TARGET_DIR/.git/hooks/pre-commit"
#!/usr/bin/env bash
if [ -f "./scripts/devsec-check.sh" ]; then
    ./scripts/devsec-check.sh --staged
fi
HOOK_EOF
chmod +x "$TARGET_DIR/.git/hooks/pre-commit"
echo "🛡️  Git pre-commit security hook berhasil diaktifkan."

# Salin .env.example menjadi .env
cp .env.example .env

echo "=================================================================="
echo "✨ Project $PROJECT_NAME (${PROJECT_TYPE^^}) berhasil dibuat di $TARGET_DIR!"
echo "Langkah selanjutnya:"
echo "  1. cd $TARGET_DIR"
echo "  2. Buka Hermes Agent: ~/.local/bin/hermes"

if [ "$PROJECT_TYPE" = "mobile" ]; then
    echo "  3. Jalankan Mock API Server: make mock-api"
    echo "  4. Perintahkan Hermes: 'Baca AGENTS.md dan rancang Mobile App untuk $PROJECT_NAME mengacu pada docs/blueprints/mobile-application-blueprint.md dan docs/security/mobile-security-checklist.md'"
elif [ "$PROJECT_TYPE" = "trading" ]; then
    echo "  3. Perintahkan Hermes: 'Baca AGENTS.md dan rancang EA Trading System untuk $PROJECT_NAME mengacu pada docs/blueprints/ea-trading-blueprint.md dan docs/security/trading-risk-policy.md'"
elif [ "$PROJECT_TYPE" = "web" ]; then
    echo "  3. Perintahkan Hermes: 'Baca AGENTS.md dan rancang Web Application untuk $PROJECT_NAME mengacu pada docs/blueprints/web-application-blueprint.md'"
else
    echo "  3. Perintahkan Hermes: 'Baca AGENTS.md dan rancang spesifikasi lengkap untuk $PROJECT_NAME'"
fi
echo "=================================================================="
