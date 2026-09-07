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
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ProjectName,

    [Parameter(Mandatory = $true, Position = 1)]
    [string]$TargetPath,

    [Parameter(Mandatory = $false, Position = 2)]
    [ValidateSet('web', 'mobile', 'trading', 'fullstack')]
    [string]$Type = 'fullstack'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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
    'AGENTS.md', 'README.md', 'README.id.md', 'SETUP.md', 'SECURITY.md',
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
    'docs/schema-template.sql'     = 'docs/schema.sql'
    'docs/openapi-template.yaml'   = 'docs/openapi.yaml'
}
foreach ($src in $templateMap.Keys) {
    $srcFull  = Join-Path $TargetPath $src
    $destFull = Join-Path $TargetPath $templateMap[$src]
    if (Test-Path $srcFull) { Copy-Item $srcFull $destFull -Force }
}

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
        Write-Host "  3. Instruct: 'Read AGENTS.md and design Web Application for $ProjectName referring to docs/blueprints/web-application-blueprint.md'"
    }
    default   {
        Write-Host "  3. Instruct: 'Read AGENTS.md and design complete specifications for $ProjectName'"
    }
}
Write-Host "=================================================================="
