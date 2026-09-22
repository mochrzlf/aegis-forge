#!/usr/bin/env bash
set -e

# ==============================================================================
# UNIVERSAL MULTI-DOMAIN PROJECT SCAFFOLDING
# ==============================================================================

PROJECT_NAME="$1"
TARGET_DIR="$2"
PROJECT_TYPE="${3}"

# --- Interactive Wizard fallback if arguments are missing ---
if [ -z "$PROJECT_NAME" ]; then
    echo "=================================================================="
    echo "🛡️  Aegis Forge — Interactive Project Setup Wizard"
    echo "=================================================================="
    read -r -p "🏷️  Masukkan nama proyek (contoh: TokoKeren): " PROJECT_NAME
    while [ -z "$PROJECT_NAME" ]; do
        read -r -p "⚠️  Nama proyek tidak boleh kosong. Masukkan nama: " PROJECT_NAME
    done
fi

if [ -z "$TARGET_DIR" ]; then
    DEFAULT_TARGET="../$PROJECT_NAME"
    read -r -p "📁 Lokasi folder tujuan (default: $DEFAULT_TARGET): " TARGET_DIR
    TARGET_DIR="${TARGET_DIR:-$DEFAULT_TARGET}"
fi

if [ -z "$PROJECT_TYPE" ]; then
    echo ""
    echo "🌐 Pilih domain proyek:"
    echo "   1) Web        (FastAPI / Express / Next.js) [Default]"
    echo "   2) Trading    (Algorithmic Trading & EA MT5)"
    echo "   3) Mobile     (Android Kotlin)"
    echo "   4) Enterprise (Multi-tier enterprise)"
    read -r -p "Pilihan domain [1-4] (default: 1): " DOMAIN_PICK
    case "$DOMAIN_PICK" in
        2) PROJECT_TYPE="trading" ;;
        3) PROJECT_TYPE="mobile" ;;
        4) PROJECT_TYPE="enterprise" ;;
        *) PROJECT_TYPE="web" ;;
    esac
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

# Remove internal baseline maintenance files from downstream project
rm -f "$TARGET_DIR/docs/gap-analysis.md"

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

# --- Interactive: optionally copy a runnable starter skeleton
# --- Interactive: optionally copy a runnable starter skeleton
# Copies templates/<choice>/ into the project so it runs without a manual `cp`
SKELETON_CHOICE=""
IS_CUSTOM_STACK=false
CUSTOM_FE="None"
CUSTOM_BE="FastAPI (Python)"
CUSTOM_CSS="Tailwind CSS"
CUSTOM_DB="PostgreSQL"
BANKING_IAM="yes"

if [ "$PROJECT_TYPE" = "web" ]; then
    echo ""
    echo "🏗️  Pilih Pendekatan Arsitektur (Architecture Approach):"
    echo "   1) Template Siap Pakai (Pre-built Starter Skeletons — pre-wired code & tests)"
    echo "   2) Custom Stack Mix & Match (Pilih sendiri Frontend, Backend, CSS, dan Database)"
    echo "   0) Kanvas Kosong (Hanya spesifikasi, guardrails, & dokumen)"
    read -r -p "Pilihan pendekatan [1/2/0] (default: 1): " APPROACH_PICK
    APPROACH_PICK="${APPROACH_PICK:-1}"

    if [ "$APPROACH_PICK" = "2" ]; then
        IS_CUSTOM_STACK=true
        echo ""
        echo "🎨 [1/5] Pilih Frontend Framework:"
        echo "   1) Next.js (React 19, App Router) [Recommended]"
        echo "   2) React (Vite + TypeScript)"
        echo "   3) Vue 3 (Vite / Nuxt)"
        echo "   4) SvelteKit"
        echo "   5) None (Headless / API Only)"
        echo "   6) Lainnya (Ketik sendiri)"
        read -r -p "Pilihan Frontend [1-6] (default: 1): " FE_PICK
        case "$FE_PICK" in
            2) CUSTOM_FE="React (Vite + TypeScript)" ;;
            3) CUSTOM_FE="Vue 3 (Vite / Nuxt)" ;;
            4) CUSTOM_FE="SvelteKit" ;;
            5) CUSTOM_FE="None (API Only)" ;;
            6) read -r -p "Masukkan nama frontend framework: " CUSTOM_FE ;;
            *) CUSTOM_FE="Next.js (React 19, App Router)" ;;
        esac

        echo ""
        echo "⚙️  [2/5] Pilih Backend Framework:"
        echo "   1) FastAPI (Python) [Recommended]"
        echo "   2) Express.js (Node.js / TypeScript)"
        echo "   3) Laravel 11 (PHP)"
        echo "   4) Go (Gin / Fiber)"
        echo "   5) NestJS (TypeScript)"
        echo "   6) Spring Boot (Java)"
        echo "   7) None / BaaS (Supabase / Firebase)"
        echo "   8) Lainnya (Ketik sendiri)"
        read -r -p "Pilihan Backend [1-8] (default: 1): " BE_PICK
        SUGGESTED_SKEL=""
        case "$BE_PICK" in
            2) CUSTOM_BE="Express.js (TypeScript)"; SUGGESTED_SKEL="web-app-express" ;;
            3) CUSTOM_BE="Laravel 11 (PHP)"; SUGGESTED_SKEL="web-app-laravel" ;;
            4) CUSTOM_BE="Go (Gin / Fiber)" ;;
            5) CUSTOM_BE="NestJS (TypeScript)" ;;
            6) CUSTOM_BE="Spring Boot (Java)" ;;
            7) CUSTOM_BE="None / BaaS (Supabase / Firebase)" ;;
            8) read -r -p "Masukkan nama backend framework: " CUSTOM_BE ;;
            *) CUSTOM_BE="FastAPI (Python)"; SUGGESTED_SKEL="web-app" ;;
        esac

        echo ""
        echo "💅 [3/5] Pilih CSS / UI Styling:"
        echo "   1) Tailwind CSS [Recommended]"
        echo "   2) Tailwind CSS + Shadcn UI"
        echo "   3) Bootstrap"
        echo "   4) Vanilla CSS / CSS Modules"
        echo "   5) None (Headless / API Only)"
        echo "   6) Lainnya (Ketik sendiri)"
        read -r -p "Pilihan CSS [1-6] (default: 1): " CSS_PICK
        case "$CSS_PICK" in
            2) CUSTOM_CSS="Tailwind CSS + Shadcn UI" ;;
            3) CUSTOM_CSS="Bootstrap" ;;
            4) CUSTOM_CSS="Vanilla CSS / CSS Modules" ;;
            5) CUSTOM_CSS="None (Headless / API Only)" ;;
            6) read -r -p "Masukkan nama CSS framework: " CUSTOM_CSS ;;
            *) CUSTOM_CSS="Tailwind CSS" ;;
        esac

        echo ""
        echo "🗄️  [4/5] Pilih Database:"
        echo "   1) PostgreSQL [Recommended]"
        echo "   2) MySQL / MariaDB"
        echo "   3) SQLite (Local / Embedded)"
        echo "   4) MongoDB (Document NoSQL)"
        echo "   5) Redis (In-Memory / Cache)"
        echo "   6) None"
        echo "   7) Lainnya (Ketik sendiri)"
        read -r -p "Pilihan Database [1-7] (default: 1): " DB_PICK
        case "$DB_PICK" in
            2) CUSTOM_DB="MySQL / MariaDB" ;;
            3) CUSTOM_DB="SQLite" ;;
            4) CUSTOM_DB="MongoDB" ;;
            5) CUSTOM_DB="Redis" ;;
            6) CUSTOM_DB="None" ;;
            7) read -r -p "Masukkan nama database: " CUSTOM_DB ;;
            *) CUSTOM_DB="PostgreSQL" ;;
        esac

        echo ""
        echo "🏦 [5/5] Standar Keamanan Perbankan (Banking-Grade Zero Trust IAM):"
        echo "   Karakteristik: RTR token rotation di cookie HttpOnly, deteksi replay, lockout 5x,"
        echo "   JML kill-switch instan, Maker-Checker Dual Control, dan immutable audit trail."
        echo "   1) Ya (Recommended) — AI Agent akan dipandu men-setting standar perbankan"
        echo "   2) Tidak — Standar Startup / MVP Fleksibel (Relaxed Auth & Simple Roles)"
        read -r -p "Terapkan standar perbankan? [1/2] (default: 1): " IAM_PICK
        case "$IAM_PICK" in
            2) BANKING_IAM="no" ;;
            *) BANKING_IAM="yes" ;;
        esac

        if [ -n "$SUGGESTED_SKEL" ]; then
            echo ""
            read -r -p "💡 Aegis Forge memiliki starter skeleton backend siap pakai untuk '$CUSTOM_BE'. Pasang sebagai pondasi di folder 'backend/'? [Y/n]: " COPY_BE_PICK
            COPY_BE_PICK="${COPY_BE_PICK:-y}"
            if [[ "$COPY_BE_PICK" =~ ^[Yy]$ ]]; then
                SKELETON_CHOICE="$SUGGESTED_SKEL"
            fi
        fi

    elif [ "$APPROACH_PICK" = "0" ]; then
        SKELETON_CHOICE=""
    else
        echo ""
        echo "🏠 Pilih Template Starter Skeleton:"
        echo "   1) web-app (default)   FastAPI + Postgres + Redis (Python)"
        echo "   2) web-app-express     Express.js + TypeScript + Postgres + Redis (Node.js)"
        echo "   3) web-app-laravel     Laravel 11 + Postgres + Redis (PHP)"
        echo "   4) nextjs-supabase     Next.js + Supabase — full website with a UI"
        echo "   0) skip                no skeleton — I'll build from scratch"
        read -r -p "Select skeleton [1/2/3/4/0] (default: 1): " pick
        case "$pick" in
            2)  SKELETON_CHOICE="web-app-express" ;;
            3)  SKELETON_CHOICE="web-app-laravel" ;;
            4)  SKELETON_CHOICE="web-app-nextjs-supabase" ;;
            0)  SKELETON_CHOICE="" ;;
            *)  SKELETON_CHOICE="web-app" ;;
        esac
    fi
elif [ "$PROJECT_TYPE" = "trading" ]; then
    echo ""
    echo "🏠 Starter skeleton (optional) — quantitative trading with risk guardrails."
    echo "   1) trading-ea (default) FastAPI Risk Guardian bridge + MQL5 EA template"
    echo "   0) skip                 no skeleton — I'll build from scratch"
    read -r -p "Select skeleton [1/0] (default: 1): " pick
    case "$pick" in
        0)  SKELETON_CHOICE="" ;;
        *)  SKELETON_CHOICE="trading-ea" ;;
    esac
elif [ "$PROJECT_TYPE" = "mobile" ]; then
    echo ""
    echo "🏠 Starter skeleton (optional) — mobile app with Keystore & SSL pinning."
    echo "   1) mobile-android (default) Kotlin Native with Keystore, SSL Pinning, & FLAG_SECURE"
    echo "   0) skip                     no skeleton — I'll build from scratch"
    read -r -p "Select skeleton [1/0] (default: 1): " pick
    case "$pick" in
        0)  SKELETON_CHOICE="" ;;
        *)  SKELETON_CHOICE="mobile-android" ;;
    esac
fi

if [ -n "$SKELETON_CHOICE" ]; then
    SKEL_SRC="$BASELINE_DIR/templates/$SKELETON_CHOICE"
    if [ -d "$SKEL_SRC" ]; then
        echo "📦 Copying skeleton 'templates/$SKELETON_CHOICE' into the project..."
        cp -a "$SKEL_SRC/." "$TARGET_DIR/"
        echo "✅ Skeleton applied successfully."
    else
        echo "⚠️  Skeleton 'templates/$SKELETON_CHOICE' not found in baseline — skipping."
    fi
else
    echo "⏭️  No skeleton selected — starting from a blank canvas."
fi

# --- If Custom Stack was selected, generate Custom Stack Spec & AI Agent Prompt ---
if [ "$IS_CUSTOM_STACK" = true ]; then
    # 1. Generate docs/CUSTOM-STACK.md
    cat << EOF > "$TARGET_DIR/docs/CUSTOM-STACK.md"
# 🛠️ Custom Architecture Specification: $PROJECT_NAME

> Document generated automatically by Aegis Forge Setup Wizard.
> Single source of truth for tech stack and architectural conventions.

## 📐 Selected Technology Stack
- **Frontend Framework:** $CUSTOM_FE
- **Backend Framework:** $CUSTOM_BE
- **CSS / UI Styling:** $CUSTOM_CSS
- **Database:** $CUSTOM_DB
- **Banking-Grade IAM Standard:** $([ "$BANKING_IAM" = "yes" ] && echo "Active (Enforced)" || echo "Standard / MVP Startup (Relaxed)")

## 🏗️ Architectural Topology
- **Frontend Layer:** Located in \`frontend/\` (or decoupled SPA/SSR client).
- **Backend Layer:** Located in \`backend/\` exposing REST/GraphQL endpoints adhering to \`docs/openapi.yaml\`.
- **Database Layer:** Configured per \`docs/schema.sql\` and environment variables in \`.env\`.
- **Security Guidance:** Detailed requirements defined in \`docs/BANKING-IAM-GUIDE.md\` and \`docs/security-iam-policy.md\`.
EOF

    # 2. If frontend is chosen, scaffold frontend README if not exists
    if [ "$CUSTOM_FE" != "None (API Only)" ] && [ ! -d "$TARGET_DIR/frontend" ]; then
        mkdir -p "$TARGET_DIR/frontend"
        cat << EOF > "$TARGET_DIR/frontend/README.md"
# Frontend Application: $PROJECT_NAME

This directory holds the frontend codebase for **$PROJECT_NAME**.

- **Framework:** $CUSTOM_FE
- **Styling:** $CUSTOM_CSS

### Setup Instructions for AI Agent:
1. Initialize the frontend project in this folder using standard CLI tools (e.g. \`npx create-next-app@latest .\` or \`npm create vite@latest .\`).
2. Integrate styling library ($CUSTOM_CSS).
3. Connect API calls to backend server (\`http://localhost:8000\`) using standard cookie-based authentication.
EOF
    fi

    # 3. Generate AI-AGENT-PROMPT.md at project root
    cat << EOF > "$TARGET_DIR/AI-AGENT-PROMPT.md"
# 🤖 Prompt Instruksi untuk AI Coding Agent ($PROJECT_NAME)

> **PETUNJUK UNTUK DEVELOPER:**
> Buka AI Agent Anda (Claude Code, Hermes, Cursor, Windsurf, Copilot, dll.), lalu salin dan kirimkan prompt di bawah ini pada giliran pertama Anda.

\`\`\`text
Halo AI Agent! Saya baru saja menginisialisasi proyek baru bernama $PROJECT_NAME menggunakan Aegis Forge Baseline.

Berikut adalah spesifikasi arsitektur yang saya pilih:
- 🎨 Frontend Framework: $CUSTOM_FE
- ⚙️ Backend Framework: $CUSTOM_BE
- 💅 CSS / UI Framework: $CUSTOM_CSS
- 🗄️ Database: $CUSTOM_DB
- 🏦 Standar Keamanan Perbankan: $([ "$BANKING_IAM" = "yes" ] && echo "AKTIF (Wajib Banking-Grade Zero Trust IAM)" || echo "STANDAR STARTUP (MVP Fleksibel)")

TUGAS DAN ATURAN WAJIB ANDA:
1. DOKUMEN WAJIB BACA:
   - \`AGENTS.md\` (kontrak kerja single source of truth)
   - \`docs/CUSTOM-STACK.md\` (spesifikasi arsitektur pilihan user)
   - \`docs/PRD.md\` & \`docs/PRD-detail.md\` (kebutuhan produk)
   - \`docs/security-iam-policy.md\` & \`docs/security-access-matrix.md\`
   $([ "$BANKING_IAM" = "yes" ] && echo "   - \`docs/BANKING-IAM-GUIDE.md\` (panduan implementasi 6 pilar keamanan perbankan)")

2. KEBIJAKAN KEAMANAN & IMPLEMENTASI:
$([ "$BANKING_IAM" = "yes" ] && cat << 'SEC_PROMPT_EOF'
   PROYEK INI WAJIB MEMATUHI STANDAR KEAMANAN PERBANKAN (Banking-Grade Zero Trust IAM):
   - Role-Based Access Control (RBAC) & Anti-IDOR: Enforce server-side role check pada tiap endpoint (superadmin, admin, support, member, guest) dan pastikan kepemilikan resource (Ownership Bound: WHERE id = :id AND user_id = :current_user_id) untuk mengeliminasi celah IDOR/BOLA.
   - Auth & RTR: Gunakan Refresh Token Rotation (RTR). Simpan refresh token HANYA di cookie HttpOnly; Secure; SameSite=Strict. Deteksi Replay Attack (jika token lama dipakai ulang, revoke seluruh keluarga token session tersebut seketika). Dilarang simpan JWT di localStorage.
   - Account Lockout (ADR-004): 5x gagal login berturut-turut WAJIB mengunci akun selama 15 menit (HTTP 423 Locked) SEBELUM komputasi hash password berat (anti-DoS). Sediakan endpoint admin unlock manual.
   - JML Session Kill-Switch (ADR-005): Saat user berstatus 'suspended' atau 'terminated', batalkan semua sesi aktif & token dalam transaksi atomik yang sama. Admin dilarang men-suspend diri sendiri.
   - Maker-Checker / Dual Control (ADR-006): Aksi mutasi berisiko tinggi (promosi role, transfer dana, approval sistem) wajib Four-Eyes Principle. Maker dilarang menyetujui tiket buatannya sendiri (enforce di logic & database check constraint: maker_id <> checker_id).
   - Immutable Audit Trail: Tabel audit_logs wajib append-only (cegah UPDATE & DELETE via DB trigger). Hash identifier untuk cegah kebocoran PII.
   - Security Headers & Rate Limiting: Pasang security headers (HSTS, CSP, X-Frame-Options: DENY) dan sliding-window rate limit pada endpoint auth.
SEC_PROMPT_EOF
)
$([ "$BANKING_IAM" != "yes" ] && cat << 'SEC_PROMPT_EOF'
   PROYEK INI MENGGUNAKAN STANDAR STARTUP / MVP FLEKSIBEL:
   - Gunakan autentikasi token / session standar dengan hashing password bcrypt/argon2.
   - RBAC sederhana (admin vs regular user).
   - Fokus pada kecepatan deliver fitur sesuai PRD dengan tetap menjaga sanitasi input dan proteksi OWASP dasar.
SEC_PROMPT_EOF
)

3. ALUR KERJA (SPEC-FIRST):
   - JANGAN langsung menulis kode implementasi secara acak!
   - Step 1: Wawancarai saya atau konfirmasi spesifikasi di \`docs/PRD.md\` dan \`docs/PRD-detail.md\`.
   - Step 2: Breakdown modul menjadi unit tugas di \`docs/TASKS.md\`.
   - Step 3: Setup struktur folder (misal \`frontend/\` dan \`backend/\`) sesuai arsitektur di atas.
   - Step 4: Tulis kode teruji dan verifikasi dengan unit test otomatis.

Mohon konfirmasi pemahaman Anda terhadap arsitektur dan aturan di atas sebelum kita mulai!
\`\`\`
EOF
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
    if [ "$IS_CUSTOM_STACK" = true ]; then
        echo "  3. Stack: $CUSTOM_FE + $CUSTOM_BE + $CUSTOM_CSS + $CUSTOM_DB"
        echo "  4. Keamanan: $([ "$BANKING_IAM" = "yes" ] && echo "Banking-Grade Zero Trust IAM (Aktif)" || echo "Standar Startup MVP Fleksibel")"
        echo "  5. Buka file AI-AGENT-PROMPT.md, salin prompt-nya, dan kirimkan ke AI Agent Anda untuk mulai men-setting proyek!"
    elif [ -n "$SKELETON_CHOICE" ]; then
        echo "  3. Start the skeleton: make first-run   (app → http://localhost:8000 or :3000)"
        echo "  4. Instruct agent: 'Use prd-interviewer for docs/PRD.md, then spec-to-tasks for docs/TASKS.md — EDIT the skeleton files per skeleton_hint (do not generate from scratch).'"
    else
        echo "  3. Instruct: 'Read AGENTS.md and design Web Application for $PROJECT_NAME referring to docs/blueprints/web-application-blueprint.md'"
    fi
else
    echo "  3. Instruct: 'Read AGENTS.md and design complete specifications for $PROJECT_NAME'"
fi
echo "=================================================================="
