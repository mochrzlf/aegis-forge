<#
.SYNOPSIS
    Universal Multi-Domain Project Scaffolding (PowerShell / native Windows).

.DESCRIPTION
    PowerShell parity of scripts/init-new-project.sh. Copies the Aegis Forge
    baseline into a new target directory, personalises placeholders, generates
    unique cryptographic keys, initialises Git, and enables security hooks —
    with NO dependency on bash, WSL, or openssl.

.PARAMETER ProjectName
    Name of the new project (replaces [PROJECT_NAME] placeholders).

.PARAMETER TargetPath
    Destination directory (must not already exist).

.PARAMETER Type
    Domain type: web | mobile | trading | fullstack (default: fullstack).

.EXAMPLE
    pwsh scripts/init-new-project.ps1 -ProjectName FinPortal -TargetPath ..\FinPortal -Type web
    .\scripts\init-new-project.ps1 QuantEA ..\QuantEA trading
#>
[CmdletBinding(PositionalBinding = $true)]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$ProjectName,

    [Parameter(Mandatory = $false, Position = 1)]
    [string]$TargetPath,

    [Parameter(Mandatory = $false, Position = 2)]
    [ValidateSet('web', 'mobile', 'trading', 'enterprise', 'fullstack')]
    [string]$Type
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- Interactive Wizard fallback if parameters are omitted ---
if (-not $ProjectName) {
    Write-Host "=================================================================="
    Write-Host "🛡️  Aegis Forge — Interactive Project Setup Wizard"
    Write-Host "=================================================================="
    do {
        $ProjectName = Read-Host "🏷️  Masukkan nama proyek (contoh: TokoKeren)"
    } while (-not $ProjectName)
}

if (-not $TargetPath) {
    $defaultTarget = "..\$ProjectName"
    $inputTarget = Read-Host "📁 Lokasi folder tujuan (default: $defaultTarget)"
    $TargetPath = if ($inputTarget) { $inputTarget } else { $defaultTarget }
}

if (-not $Type) {
    Write-Host ""
    Write-Host "🌐 Pilih domain proyek:"
    Write-Host "   1) Web        (FastAPI / Express / Next.js) [Default]"
    Write-Host "   2) Trading    (Algorithmic Trading & EA MT5)"
    Write-Host "   3) Mobile     (Android Kotlin)"
    Write-Host "   4) Enterprise (Multi-tier enterprise)"
    $domainPick = Read-Host "Pilihan domain [1-4] (default: 1)"
    switch ($domainPick) {
        '2'     { $Type = 'trading' }
        '3'     { $Type = 'mobile' }
        '4'     { $Type = 'enterprise' }
        default { $Type = 'web' }
    }
}

# Dynamically detect baseline directory (works across any host/user environment)
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaselineDir = Split-Path -Parent $ScriptDir

Write-Host "=================================================================="
Write-Host "🚀 Creating Universal Project: $ProjectName"
Write-Host "📁 Target directory: $TargetPath"
Write-Host "🏷️  Domain Type: $($Type.ToUpper())"
Write-Host "=================================================================="

if (Test-Path $TargetPath) {
    Write-Host "⚠️  Directory $TargetPath already exists! Aborting to prevent overwriting data."
    exit 1
}

New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null

# --- Copy baseline directories & files (skip missing, like the bash `|| true`)
$items = @(
    'AGENTS.md', 'README.md', 'SETUP.md', 'SECURITY.md',
    'LICENSE', 'Makefile', '.env.example', '.gitignore', '.gitattributes',
    '.editorconfig', '.gitleaks.toml', '.pre-commit-config.yaml',
    'docker-compose.yml', '.github', 'docs', 'scripts', 'evals', '.devcontainer'
)
foreach ($item in $items) {
    $src = Join-Path $BaselineDir $item
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $TargetPath -Recurse -Force
    }
}

# --- Copy PRD templates into active project documents
$templateMap = @{
    'docs/PRD-template.md'         = 'docs/PRD.md'
    'docs/PRD-detail-template.md'  = 'docs/PRD-detail.md'
    'docs/ui-design-template.md'   = 'docs/ui-design.md'
}
foreach ($src in $templateMap.Keys) {
    $srcFull  = Join-Path $TargetPath $src
    $destFull = Join-Path $TargetPath $templateMap[$src]
    if (Test-Path $srcFull) { Copy-Item $srcFull $destFull -Force }
}

# --- Remove internal baseline maintenance files from downstream project
$internalGapFile = Join-Path $TargetPath 'docs/gap-analysis.md'
if (Test-Path $internalGapFile) { Remove-Item $internalGapFile -Force }

# --- Replace [PROJECT_NAME] placeholder across all text files
$textExt = '.md', '.yaml', '.yml', '.sql', '.example'
Get-ChildItem -Path $TargetPath -Recurse -File | Where-Object {
    $textExt -contains $_.Extension -or $_.Name -eq '.env.example'
} | ForEach-Object {
    (Get-Content $_.FullName -Raw) -replace [regex]::Escape('[PROJECT_NAME]'), $ProjectName |
        Set-Content $_.FullName -NoNewline -Encoding UTF8
}

# --- Helper: generate cryptographically secure random strings (no openssl) ---
function New-SecureBase64 ([int]$bytes = 48) {
    $buf = New-Object byte[] $bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($buf)
    return [Convert]::ToBase64String($buf)
}
function New-SecureHex ([int]$bytes = 32) {
    $buf = New-Object byte[] $bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($buf)
    return ($buf | ForEach-Object { $_.ToString('x2') }) -join ''
}

# --- Copy .env.example to .env and inject unique cryptographic keys
$envExample = Join-Path $TargetPath '.env.example'
$envFile    = Join-Path $TargetPath '.env'
if (Test-Path $envExample) {
    Copy-Item $envExample $envFile -Force
    $env = Get-Content $envFile -Raw
    $env = $env -replace 'JWT_ACCESS_SECRET="[^"]*"',  ('JWT_ACCESS_SECRET="'  + (New-SecureBase64 48) + '"')
    $env = $env -replace 'JWT_REFRESH_SECRET="[^"]*"', ('JWT_REFRESH_SECRET="' + (New-SecureBase64 48) + '"')
    $env = $env -replace 'ENCRYPTION_MASTER_KEY="[^"]*"', ('ENCRYPTION_MASTER_KEY="' + (New-SecureHex 32) + '"')
    Set-Content $envFile $env -NoNewline -Encoding UTF8
    Write-Host "🔑 Secure cryptographic keys (JWT & AES-256 FLE) successfully generated in .env."
}

# --- Interactive: optionally copy a runnable starter skeleton
# Copies templates/<choice>/ into the project so it runs without a manual `cp`.
$SkeletonChoice = ''
$IsCustomStack = $false
$CustomFe = 'None'
$CustomBe = 'FastAPI (Python)'
$CustomCss = 'Tailwind CSS'
$CustomDb = 'PostgreSQL'
$BankingIam = 'yes'

if ($Type -eq 'web') {
    Write-Host ""
    Write-Host "🏗️  Pilih Pendekatan Arsitektur (Architecture Approach):"
    Write-Host "   1) Template Siap Pakai (Pre-built Starter Skeletons — pre-wired code & tests)"
    Write-Host "   2) Custom Stack Mix & Match (Pilih sendiri Frontend, Backend, CSS, dan Database)"
    Write-Host "   0) Kanvas Kosong (Hanya spesifikasi, guardrails, & dokumen)"
    $approachPick = Read-Host "Pilihan pendekatan [1/2/0] (default: 1)"
    if ([string]::IsNullOrWhiteSpace($approachPick)) { $approachPick = '1' }

    if ($approachPick -eq '2') {
        $IsCustomStack = $true
        Write-Host ""
        Write-Host "🎨 [1/5] Pilih Frontend Framework:"
        Write-Host "   1) Next.js (React 19, App Router) [Recommended]"
        Write-Host "   2) React (Vite + TypeScript)"
        Write-Host "   3) Vue 3 (Vite / Nuxt)"
        Write-Host "   4) SvelteKit"
        Write-Host "   5) None (Headless / API Only)"
        Write-Host "   6) Lainnya (Ketik sendiri)"
        $fePick = Read-Host "Pilihan Frontend [1-6] (default: 1)"
        switch ($fePick) {
            '2'     { $CustomFe = 'React (Vite + TypeScript)' }
            '3'     { $CustomFe = 'Vue 3 (Vite / Nuxt)' }
            '4'     { $CustomFe = 'SvelteKit' }
            '5'     { $CustomFe = 'None (API Only)' }
            '6'     { $CustomFe = Read-Host "Masukkan nama frontend framework" }
            default { $CustomFe = 'Next.js (React 19, App Router)' }
        }

        Write-Host ""
        Write-Host "⚙️  [2/5] Pilih Backend Framework:"
        Write-Host "   1) FastAPI (Python) [Recommended]"
        Write-Host "   2) Express.js (Node.js / TypeScript)"
        Write-Host "   3) Laravel 11 (PHP)"
        Write-Host "   4) Go (Gin / Fiber)"
        Write-Host "   5) NestJS (TypeScript)"
        Write-Host "   6) Spring Boot (Java)"
        Write-Host "   7) None / BaaS (Supabase / Firebase)"
        Write-Host "   8) Lainnya (Ketik sendiri)"
        $bePick = Read-Host "Pilihan Backend [1-8] (default: 1)"
        $suggestedSkel = ''
        switch ($bePick) {
            '2'     { $CustomBe = 'Express.js (TypeScript)'; $suggestedSkel = 'web-app-express' }
            '3'     { $CustomBe = 'Laravel 11 (PHP)'; $suggestedSkel = 'web-app-laravel' }
            '4'     { $CustomBe = 'Go (Gin / Fiber)' }
            '5'     { $CustomBe = 'NestJS (TypeScript)' }
            '6'     { $CustomBe = 'Spring Boot (Java)' }
            '7'     { $CustomBe = 'None / BaaS (Supabase / Firebase)' }
            '8'     { $CustomBe = Read-Host "Masukkan nama backend framework" }
            default { $CustomBe = 'FastAPI (Python)'; $suggestedSkel = 'web-app' }
        }

        Write-Host ""
        Write-Host "💅 [3/5] Pilih CSS / UI Styling:"
        Write-Host "   1) Tailwind CSS [Recommended]"
        Write-Host "   2) Tailwind CSS + Shadcn UI"
        Write-Host "   3) Bootstrap"
        Write-Host "   4) Vanilla CSS / CSS Modules"
        Write-Host "   5) None (Headless / API Only)"
        Write-Host "   6) Lainnya (Ketik sendiri)"
        $cssPick = Read-Host "Pilihan CSS [1-6] (default: 1)"
        switch ($cssPick) {
            '2'     { $CustomCss = 'Tailwind CSS + Shadcn UI' }
            '3'     { $CustomCss = 'Bootstrap' }
            '4'     { $CustomCss = 'Vanilla CSS / CSS Modules' }
            '5'     { $CustomCss = 'None (Headless / API Only)' }
            '6'     { $CustomCss = Read-Host "Masukkan nama CSS framework" }
            default { $CustomCss = 'Tailwind CSS' }
        }

        Write-Host ""
        Write-Host "🗄️  [4/5] Pilih Database:"
        Write-Host "   1) PostgreSQL [Recommended]"
        Write-Host "   2) MySQL / MariaDB"
        Write-Host "   3) SQLite (Local / Embedded)"
        Write-Host "   4) MongoDB (Document NoSQL)"
        Write-Host "   5) Redis (In-Memory / Cache)"
        Write-Host "   6) None"
        Write-Host "   7) Lainnya (Ketik sendiri)"
        $dbPick = Read-Host "Pilihan Database [1-7] (default: 1)"
        switch ($dbPick) {
            '2'     { $CustomDb = 'MySQL / MariaDB' }
            '3'     { $CustomDb = 'SQLite' }
            '4'     { $CustomDb = 'MongoDB' }
            '5'     { $CustomDb = 'Redis' }
            '6'     { $CustomDb = 'None' }
            '7'     { $CustomDb = Read-Host "Masukkan nama database" }
            default { $CustomDb = 'PostgreSQL' }
        }

        Write-Host ""
        Write-Host "🏦 [5/5] Standar Keamanan Perbankan (Banking-Grade Zero Trust IAM):"
        Write-Host "   Karakteristik: RTR token rotation di cookie HttpOnly, deteksi replay, lockout 5x,"
        Write-Host "   JML kill-switch instan, Maker-Checker Dual Control, dan immutable audit trail."
        Write-Host "   1) Ya (Recommended) — AI Agent akan dipandu men-setting standar perbankan"
        Write-Host "   2) Tidak — Standar Startup / MVP Fleksibel (Relaxed Auth & Simple Roles)"
        $iamPick = Read-Host "Terapkan standar perbankan? [1/2] (default: 1)"
        if ($iamPick -eq '2') {
            $BankingIam = 'no'
        } else {
            $BankingIam = 'yes'
        }

        if ($suggestedSkel) {
            Write-Host ""
            $copyBePick = Read-Host "💡 Aegis Forge memiliki starter skeleton backend siap pakai untuk '$CustomBe'. Pasang sebagai pondasi di folder 'backend/'? [Y/n] (default: Y)"
            if ([string]::IsNullOrWhiteSpace($copyBePick) -or $copyBePick -match '^[Yy]$') {
                $SkeletonChoice = $suggestedSkel
            }
        }
    } elseif ($approachPick -eq '0') {
        $SkeletonChoice = ''
    } else {
        Write-Host ""
        Write-Host "🏠 Starter skeleton (optional) — runnable code with security pre-wired."
        Write-Host "   Choose one to copy into your project, or skip to start from a blank canvas:"
        Write-Host "   1) web-app (default)   FastAPI + Postgres + Redis (Python)"
        Write-Host "   2) web-app-express     Express.js + TypeScript + Postgres + Redis (Node.js)"
        Write-Host "   3) web-app-laravel     Laravel 11 + Postgres + Redis (PHP)"
        Write-Host "   4) nextjs-supabase     Next.js + Supabase — full website with a UI"
        Write-Host "   0) skip                no skeleton — I'll build from scratch"
        $pick = Read-Host "Select skeleton [1/2/3/4/0] (default: 1)"
        switch ($pick) {
            '2'      { $SkeletonChoice = 'web-app-express' }
            '3'      { $SkeletonChoice = 'web-app-laravel' }
            '4'      { $SkeletonChoice = 'web-app-nextjs-supabase' }
            '0'      { $SkeletonChoice = '' }
            default  { $SkeletonChoice = 'web-app' }
        }
    }
} elseif ($Type -eq 'trading') {
    Write-Host ""
    Write-Host "🏠 Starter skeleton (optional) — quantitative trading with risk guardrails."
    Write-Host "   1) trading-ea (default) FastAPI Risk Guardian bridge + MQL5 EA template"
    Write-Host "   0) skip                 no skeleton — I'll build from scratch"
    $pick = Read-Host "Select skeleton [1/0] (default: 1)"
    switch ($pick) {
        '0'      { $SkeletonChoice = '' }
        default  { $SkeletonChoice = 'trading-ea' }
    }
} elseif ($Type -eq 'mobile') {
    Write-Host ""
    Write-Host "🏠 Starter skeleton (optional) — mobile app with Keystore & SSL pinning."
    Write-Host "   1) mobile-android (default) Kotlin Native with Keystore, SSL Pinning, & FLAG_SECURE"
    Write-Host "   0) skip                     no skeleton — I'll build from scratch"
    $pick = Read-Host "Select skeleton [1/0] (default: 1)"
    switch ($pick) {
        '0'      { $SkeletonChoice = '' }
        default  { $SkeletonChoice = 'mobile-android' }
    }
}

if ($SkeletonChoice) {
    $skelSrc = Join-Path $BaselineDir "templates/$SkeletonChoice"
    if (Test-Path $skelSrc) {
        Write-Host "📦 Copying skeleton 'templates/$SkeletonChoice' into the project..."
        Copy-Item -Path (Join-Path $skelSrc '*') -Destination $TargetPath -Recurse -Force
        # Copy dotfiles too (Copy-Item '*' misses hidden files like .github, .env.example)
        Get-ChildItem -Path $skelSrc -Force | Where-Object { $_.Name -like '.*' } | ForEach-Object {
            Copy-Item -Path $_.FullName -Destination $TargetPath -Recurse -Force
        }
        Write-Host "✅ Skeleton applied successfully."
    } else {
        Write-Host "⚠️  Skeleton 'templates/$SkeletonChoice' not found in baseline — skipping."
    }
} else {
    Write-Host "⏭️  No skeleton selected — starting from a blank canvas."
}

# --- If Custom Stack was selected, generate Custom Stack Spec & AI Agent Prompt ---
if ($IsCustomStack) {
    # 1. Generate docs/CUSTOM-STACK.md
    $iamLabel = if ($BankingIam -eq 'yes') { 'Active (Enforced)' } else { 'Standard / MVP Startup (Relaxed)' }
    $customStackMd = @"
# 🛠️ Custom Architecture Specification: $ProjectName

> Document generated automatically by Aegis Forge Setup Wizard.
> Single source of truth for tech stack and architectural conventions.

## 📐 Selected Technology Stack
- **Frontend Framework:** $CustomFe
- **Backend Framework:** $CustomBe
- **CSS / UI Styling:** $CustomCss
- **Database:** $CustomDb
- **Banking-Grade IAM Standard:** $iamLabel

## 🏗️ Architectural Topology
- **Frontend Layer:** Located in ``frontend/`` (or decoupled SPA/SSR client).
- **Backend Layer:** Located in ``backend/`` exposing REST/GraphQL endpoints adhering to ``docs/openapi.yaml``.
- **Database Layer:** Configured per ``docs/schema.sql`` and environment variables in ``.env``.
- **Security Guidance:** Detailed requirements defined in ``docs/BANKING-IAM-GUIDE.md`` and ``docs/security-iam-policy.md``.
"@
    Set-Content (Join-Path $TargetPath 'docs/CUSTOM-STACK.md') $customStackMd -Encoding UTF8

    # 2. If frontend is chosen, scaffold frontend README if not exists
    $feDir = Join-Path $TargetPath 'frontend'
    if ($CustomFe -ne 'None (API Only)' -and -not (Test-Path $feDir)) {
        New-Item -ItemType Directory -Path $feDir -Force | Out-Null
        $feReadme = @"
# Frontend Application: $ProjectName

This directory holds the frontend codebase for **$ProjectName**.

- **Framework:** $CustomFe
- **Styling:** $CustomCss

### Setup Instructions for AI Agent:
1. Initialize the frontend project in this folder using standard CLI tools (e.g. ``npx create-next-app@latest .`` or ``npm create vite@latest .``).
2. Integrate styling library ($CustomCss).
3. Connect API calls to backend server (``http://localhost:8000``) using standard cookie-based authentication.
"@
        Set-Content (Join-Path $feDir 'README.md') $feReadme -Encoding UTF8
    }

    # 3. Generate AI-AGENT-PROMPT.md at project root
    $bankingStatusText = if ($BankingIam -eq 'yes') { 'AKTIF (Wajib Banking-Grade Zero Trust IAM)' } else { 'STANDAR STARTUP (MVP Fleksibel)' }
    $bankingGuideLine = if ($BankingIam -eq 'yes') { "   - ``docs/BANKING-IAM-GUIDE.md`` (panduan implementasi 6 pilar keamanan perbankan)" } else { "" }
    $securityPolicyBlock = if ($BankingIam -eq 'yes') {
@"
   PROYEK INI WAJIB MEMATUHI STANDAR KEAMANAN PERBANKAN (Banking-Grade Zero Trust IAM):
   - Auth & RTR: Gunakan Refresh Token Rotation (RTR). Simpan refresh token HANYA di cookie HttpOnly; Secure; SameSite=Strict. Deteksi Replay Attack (jika token lama dipakai ulang, revoke seluruh keluarga token session tersebut seketika). Dilarang simpan JWT di localStorage.
   - Account Lockout (ADR-004): 5x gagal login berturut-turut WAJIB mengunci akun selama 15 menit (HTTP 423 Locked) SEBELUM komputasi hash password berat (anti-DoS). Sediakan endpoint admin unlock manual.
   - JML Session Kill-Switch (ADR-005): Saat user berstatus 'suspended' atau 'terminated', batalkan semua sesi aktif & token dalam transaksi atomik yang sama. Admin dilarang men-suspend diri sendiri.
   - Maker-Checker / Dual Control (ADR-006): Aksi mutasi berisiko tinggi (promosi role, transfer dana, approval sistem) wajib Four-Eyes Principle. Maker dilarang menyetujui tiket buatannya sendiri (enforce di logic & database check constraint: maker_id <> checker_id).
   - Immutable Audit Trail: Tabel audit_logs wajib append-only (cegah UPDATE & DELETE via DB trigger). Hash identifier untuk cegah kebocoran PII.
   - Security Headers & Rate Limiting: Pasang security headers (HSTS, CSP, X-Frame-Options: DENY) dan sliding-window rate limit pada endpoint auth.
"@
    } else {
@"
   PROYEK INI MENGGUNAKAN STANDAR STARTUP / MVP FLEKSIBEL:
   - Gunakan autentikasi token / session standar dengan hashing password bcrypt/argon2.
   - RBAC sederhana (admin vs regular user).
   - Fokus pada kecepatan deliver fitur sesuai PRD dengan tetap menjaga sanitasi input dan proteksi OWASP dasar.
"@
    }

    $aiPromptMd = @"
# 🤖 Prompt Instruksi untuk AI Coding Agent ($ProjectName)

> **PETUNJUK UNTUK DEVELOPER:**
> Buka AI Agent Anda (Claude Code, Hermes, Cursor, Windsurf, Copilot, dll.), lalu salin dan kirimkan prompt di bawah ini pada giliran pertama Anda.

```text
Halo AI Agent! Saya baru saja menginisialisasi proyek baru bernama $ProjectName menggunakan Aegis Forge Baseline.

Berikut adalah spesifikasi arsitektur yang saya pilih:
- 🎨 Frontend Framework: $CustomFe
- ⚙️ Backend Framework: $CustomBe
- 💅 CSS / UI Framework: $CustomCss
- 🗄️ Database: $CustomDb
- 🏦 Standar Keamanan Perbankan: $bankingStatusText

TUGAS DAN ATURAN WAJIB ANDA:
1. DOKUMEN WAJIB BACA:
   - ``AGENTS.md`` (kontrak kerja single source of truth)
   - ``docs/CUSTOM-STACK.md`` (spesifikasi arsitektur pilihan user)
   - ``docs/PRD.md`` & ``docs/PRD-detail.md`` (kebutuhan produk)
   - ``docs/security-iam-policy.md`` & ``docs/security-access-matrix.md``
$bankingGuideLine

2. KEBIJAKAN KEAMANAN & IMPLEMENTASI:
$securityPolicyBlock

3. ALUR KERJA (SPEC-FIRST):
   - JANGAN langsung menulis kode implementasi secara acak!
   - Step 1: Wawancarai saya atau konfirmasi spesifikasi di ``docs/PRD.md`` dan ``docs/PRD-detail.md``.
   - Step 2: Breakdown modul menjadi unit tugas di ``docs/TASKS.md``.
   - Step 3: Setup struktur folder (misal ``frontend/`` dan ``backend/``) sesuai arsitektur di atas.
   - Step 4: Tulis kode teruji dan verifikasi dengan unit test otomatis.

Mohon konfirmasi pemahaman Anda terhadap arsitektur dan aturan di atas sebelum kita mulai!
```
"@
    Set-Content (Join-Path $TargetPath 'AI-AGENT-PROMPT.md') $aiPromptMd -Encoding UTF8
}

# --- Initialise local Git repository
Push-Location $TargetPath
try {
    if (-not (Test-Path '.git')) {
        git init -b main | Out-Null
        Write-Host "✅ Git repository successfully initialized."
    }

    # --- Git pre-commit security hook (bash shim; runs under Git Bash on Windows)
    $hooksDir = Join-Path (Get-Location) '.git/hooks'
    New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
    $hook = @'
#!/usr/bin/env bash
if [ -f "./scripts/devsec-check.sh" ]; then
    ./scripts/devsec-check.sh --staged
fi
'@
    Set-Content (Join-Path $hooksDir 'pre-commit') $hook -Encoding ASCII
    Write-Host "🛡️  Git pre-commit security hook successfully enabled."

    # --- Optional: install pre-commit framework hook (non-fatal if unavailable)
    if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
        pre-commit install --allow-missing-config 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-Host "🪝 pre-commit framework hook installed (.pre-commit-config.yaml)." }
        else { Write-Host "ℹ️  pre-commit detected but hook install was skipped." }
    } else {
        Write-Host "ℹ️  'pre-commit' not installed. Run 'pip install pre-commit; pre-commit install'"
        Write-Host "    inside the project to enable extended hygiene/lint checks (optional)."
    }
}
finally {
    Pop-Location
}

Write-Host "=================================================================="
Write-Host "✨ Project $ProjectName ($($Type.ToUpper())) successfully created at $TargetPath!"
Write-Host "Next steps:"
Write-Host "  1. cd $TargetPath"
Write-Host "  2. Open your preferred AI Coding Agent (Hermes, Claude, Cursor, etc.)"
switch ($Type) {
    'mobile'  {
        Write-Host "  3. Run Mock API Server: docker compose up -d prism"
        Write-Host "  4. Instruct: 'Read AGENTS.md and design Mobile App for $ProjectName referring to docs/blueprints/mobile-application-blueprint.md and docs/security/mobile-security-checklist.md'"
    }
    'trading' {
        Write-Host "  3. Instruct: 'Read AGENTS.md and design EA Trading System for $ProjectName referring to docs/blueprints/ea-trading-blueprint.md and docs/security/trading-risk-policy.md'"
    }
    'web'     {
        if ($IsCustomStack) {
            $iamText = if ($BankingIam -eq 'yes') { 'Banking-Grade Zero Trust IAM (Aktif)' } else { 'Standar Startup MVP Fleksibel' }
            Write-Host "  3. Stack: $CustomFe + $CustomBe + $CustomCss + $CustomDb"
            Write-Host "  4. Keamanan: $iamText"
            Write-Host "  5. Buka file AI-AGENT-PROMPT.md, salin prompt-nya, dan kirimkan ke AI Agent Anda untuk mulai men-setting proyek!"
        } elseif ($SkeletonChoice) {
            Write-Host "  3. Start the skeleton: make first-run   (app → http://localhost:8000 or :3000)"
            Write-Host "  4. Instruct agent: 'Use prd-interviewer for docs/PRD.md, then spec-to-tasks for docs/TASKS.md — EDIT the skeleton files per skeleton_hint (do not generate from scratch).'"
        } else {
            Write-Host "  3. Instruct: 'Read AGENTS.md and design Web Application for $ProjectName referring to docs/blueprints/web-application-blueprint.md'"
        }
    }
    default   {
        Write-Host "  3. Instruct: 'Read AGENTS.md and design complete specifications for $ProjectName'"
    }
}
Write-Host "=================================================================="
