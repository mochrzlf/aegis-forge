#!/usr/bin/env bash
set -e

# ==============================================================================
# SCRIPT SCAFFOLDING PROJECT BARU DARI BASELINE
# ==============================================================================

PROJECT_NAME="$1"
TARGET_DIR="$2"

if [ -z "$PROJECT_NAME" ] || [ -z "$TARGET_DIR" ]; then
    echo "Penggunaan: bash init-new-project.sh <NamaProject> <PathTujuan>"
    echo "Contoh: bash init-new-project.sh KlinikAccess /home/tpam_su/Project/KlinikAccess"
    exit 1
fi

BASELINE_DIR="/home/tpam_su/Project/Baseline"

echo "=================================================================="
echo "🚀 Membuat project baru: $PROJECT_NAME"
echo "📁 Lokasi target: $TARGET_DIR"
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
cp -r "$BASELINE_DIR/.env.example" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.gitignore" "$TARGET_DIR/"
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

# Ganti placeholder [PROJECT_NAME] di semua file
find "$TARGET_DIR" -type f -name "*.md" -o -name "*.yaml" -o -name "*.sql" -o -name ".env.example" | while read -r file; do
    sed -i "s/\[PROJECT_NAME\]/$PROJECT_NAME/g" "$file"
done

# Inisialisasi Git Repository lokal jika belum ada
cd "$TARGET_DIR"
if [ ! -d ".git" ]; then
    git init -b main
    echo "✅ Git repository berhasil diinisialisasi."
fi

# Salin .env.example menjadi .env
cp .env.example .env

echo "=================================================================="
echo "✨ Project $PROJECT_NAME berhasil dibuat di $TARGET_DIR!"
echo "Langkah selanjutnya:"
echo "  1. cd $TARGET_DIR"
echo "  2. Buka Hermes Agent: ~/.local/bin/hermes"
echo "  3. Perintahkan Hermes: 'Baca AGENTS.md dan rancang PRD untuk $PROJECT_NAME'"
echo "=================================================================="
