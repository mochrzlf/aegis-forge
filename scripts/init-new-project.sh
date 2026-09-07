#!/usr/bin/env bash
set -e

# ==============================================================================
# UNIVERSAL MULTI-DOMAIN PROJECT SCAFFOLDING
# ==============================================================================

PROJECT_NAME="$1"
TARGET_DIR="$2"
PROJECT_TYPE="${3:-fullstack}"

if [ -z "$PROJECT_NAME" ] || [ -z "$TARGET_DIR" ]; then
    echo "Usage: bash init-new-project.sh <ProjectName> <TargetPath> [web|mobile|trading|fullstack]"
    echo "Examples:"
    echo "  bash init-new-project.sh FinPortal ../FinPortal web"
    echo "  bash init-new-project.sh FinMobile ../FinMobile mobile"
    echo "  bash init-new-project.sh QuantEA   ../QuantEA trading"
    exit 1
fi

# Dynamically detect baseline directory (works across any host/user environment)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASELINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================================="
echo "🚀 Creating Universal Project: $PROJECT_NAME"
echo "📁 Target directory: $TARGET_DIR"
echo "🏷️  Domain Type: ${PROJECT_TYPE^^}"
echo "=================================================================="

if [ -d "$TARGET_DIR" ]; then
    echo "⚠️  Directory $TARGET_DIR already exists! Aborting to prevent overwriting data."
    exit 1
fi

mkdir -p "$TARGET_DIR"

# Copy baseline directories & files
cp -r "$BASELINE_DIR/AGENTS.md" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/README.md" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/README.id.md" "$TARGET_DIR/" 2>/dev/null || true
cp -r "$BASELINE_DIR/SETUP.md" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/SECURITY.md" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/LICENSE" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/Makefile" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.env.example" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.gitignore" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.gitattributes" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.editorconfig" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.gitleaks.toml" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.pre-commit-config.yaml" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/docker-compose.yml" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/.github" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/docs" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/scripts" "$TARGET_DIR/"
cp -r "$BASELINE_DIR/evals" "$TARGET_DIR/" 2>/dev/null || true

# Copy PRD templates into active project documents
cp "$TARGET_DIR/docs/PRD-template.md" "$TARGET_DIR/docs/PRD.md"
cp "$TARGET_DIR/docs/PRD-detail-template.md" "$TARGET_DIR/docs/PRD-detail.md"
cp "$TARGET_DIR/docs/ui-design-template.md" "$TARGET_DIR/docs/ui-design.md"
cp "$TARGET_DIR/docs/schema-template.sql" "$TARGET_DIR/docs/schema.sql"
cp "$TARGET_DIR/docs/openapi-template.yaml" "$TARGET_DIR/docs/openapi.yaml"

# Replace [PROJECT_NAME] placeholder across all text files
find "$TARGET_DIR" -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.sql" -o -name ".env.example" \) | while read -r file; do
    sed -i "s/\[PROJECT_NAME\]/$PROJECT_NAME/g" "$file"
done

# Initialize local Git repository if not already present
cd "$TARGET_DIR"
if [ ! -d ".git" ]; then
    git init -b main
    echo "✅ Git repository successfully initialized."
fi

# Install Git Pre-Commit Security Hook
mkdir -p "$TARGET_DIR/.git/hooks"
cat << 'HOOK_EOF' > "$TARGET_DIR/.git/hooks/pre-commit"
#!/usr/bin/env bash
if [ -f "./scripts/devsec-check.sh" ]; then
    ./scripts/devsec-check.sh --staged
fi
HOOK_EOF
chmod +x "$TARGET_DIR/.git/hooks/pre-commit"
echo "🛡️  Git pre-commit security hook successfully enabled."

# Optionally install the pre-commit framework hook (adds hygiene, lint,
# and contract-validation layers on top of the security hook above).
# Non-fatal: skipped silently if the tool is not installed on this machine.
if command -v pre-commit >/dev/null 2>&1; then
    (cd "$TARGET_DIR" && pre-commit install --allow-missing-config >/dev/null 2>&1) \
        && echo "🪝 pre-commit framework hook installed (.pre-commit-config.yaml)." \
        || echo "ℹ️  pre-commit framework detected but hook install was skipped."
else
    echo "ℹ️  'pre-commit' not installed. Run 'pip install pre-commit && pre-commit install'"
    echo "    inside the project to enable extended hygiene/lint checks (optional)."
fi

# Copy .env.example to .env
cp .env.example .env

# Automatically generate secure unique cryptographic keys for the new project
if command -v openssl >/dev/null 2>&1; then
    RAND_JWT_ACCESS=$(openssl rand -base64 48 | tr -d '\n\r')
    RAND_JWT_REFRESH=$(openssl rand -base64 48 | tr -d '\n\r')
    RAND_ENC_KEY=$(openssl rand -hex 32 | tr -d '\n\r')
    
    sed -i "s|JWT_ACCESS_SECRET=\".*\"|JWT_ACCESS_SECRET=\"$RAND_JWT_ACCESS\"|g" .env
    sed -i "s|JWT_REFRESH_SECRET=\".*\"|JWT_REFRESH_SECRET=\"$RAND_JWT_REFRESH\"|g" .env
    sed -i "s|ENCRYPTION_MASTER_KEY=\".*\"|ENCRYPTION_MASTER_KEY=\"$RAND_ENC_KEY\"|g" .env
    echo "🔑 Secure cryptographic keys (JWT & AES-256 FLE) successfully generated in .env."
fi

echo "=================================================================="
echo "✨ Project $PROJECT_NAME (${PROJECT_TYPE^^}) successfully created at $TARGET_DIR!"
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. Open your preferred AI Coding Agent (Hermes, Claude, Cursor, etc.)"

if [ "$PROJECT_TYPE" = "mobile" ]; then
    echo "  3. Run Mock API Server: make mock-api"
    echo "  4. Instruct: 'Read AGENTS.md and design Mobile App for $PROJECT_NAME referring to docs/blueprints/mobile-application-blueprint.md and docs/security/mobile-security-checklist.md'"
elif [ "$PROJECT_TYPE" = "trading" ]; then
    echo "  3. Instruct: 'Read AGENTS.md and design EA Trading System for $PROJECT_NAME referring to docs/blueprints/ea-trading-blueprint.md and docs/security/trading-risk-policy.md'"
elif [ "$PROJECT_TYPE" = "web" ]; then
    echo "  3. Instruct: 'Read AGENTS.md and design Web Application for $PROJECT_NAME referring to docs/blueprints/web-application-blueprint.md'"
else
    echo "  3. Instruct: 'Read AGENTS.md and design complete specifications for $PROJECT_NAME'"
fi
echo "=================================================================="
