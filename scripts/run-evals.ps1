<#
.SYNOPSIS
    Aegis Forge — Agent Evals guard & launcher (Windows / PowerShell).

.DESCRIPTION
    Interactive guard before running the promptfoo agent evals:
      1. Verifies promptfoo is reachable (via npx).
      2. Checks that a generic OpenAI-compatible provider is configured in the
         local .env (EVAL_API_BASE_URL, EVAL_MODEL, EVAL_API_KEY); if not,
         offers an interactive (masked) setup that persists them to .env
         (git-ignored, gitleaks-protected).
      3. Confirms paid API usage with the user before spending anything.
      4. Runs the per-scenario configs in evals/suites/ (one config per
         scenario -> clean 1:1 prompt-to-scenario pairing).

    API keys are NEVER written to the repo, the command line, or logs.
    The local .env file is excluded by .gitignore and scanned by gitleaks.

.EXAMPLE
    pwsh scripts/run-evals.ps1                      # guarded run, all suites
    pwsh scripts/run-evals.ps1 -Suite prd-interview # run one suite
    pwsh scripts/run-evals.ps1 -View                # run + open results viewer
#>
[CmdletBinding()]
param(
    # Run a single suite (file name without .yaml, e.g. "prd-interview").
    [string]$Suite,

    [switch]$View  # open `promptfoo view` after a successful eval run
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- Locate repo root (this script lives in scripts/) -------------------------
$RepoRoot  = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$EnvFile   = Join-Path $RepoRoot '.env'
$SuitesDir = Join-Path $RepoRoot 'evals/suites'

Write-Host ""
Write-Host "🛡️  Aegis Forge — Agent Evals Setup Check" -ForegroundColor Cyan
Write-Host ("─" * 60)

# --- Generic OpenAI-compatible provider (from the local .env) -----------------
# The evals call any OpenAI-compatible chat endpoint, described by three vars:
#   EVAL_API_BASE_URL  e.g. https://api.openai.com/v1  (or a local router)
#   EVAL_MODEL         the model id your endpoint serves
#   EVAL_API_KEY       your provider key (git-ignored .env only)

function Import-DotEnv {
    if (Test-Path $EnvFile) {
        foreach ($line in Get-Content $EnvFile) {
            if ($line -match '^\s*([A-Z0-9_]+)\s*=\s*"?([^"#]*)"?' -and $line -notmatch '^\s*#') {
                [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2].Trim(), 'Process')
            }
        }
    }
}
Import-DotEnv

function Get-EnvVal([string]$name) {
    return [Environment]::GetEnvironmentVariable($name, 'Process')
}

function Test-Configured {
    return -not [string]::IsNullOrWhiteSpace((Get-EnvVal 'EVAL_API_BASE_URL')) -and
           -not [string]::IsNullOrWhiteSpace((Get-EnvVal 'EVAL_MODEL')) -and
           -not [string]::IsNullOrWhiteSpace((Get-EnvVal 'EVAL_API_KEY'))
}

function Save-EnvVar([string]$name, [string]$value) {
    $entry = "$name=`"$value`""
    if (Test-Path $EnvFile) {
        $content = Get-Content $EnvFile -Raw
        if ($content -match "(?m)^#?\s*$([regex]::Escape($name))=") {
            $content = $content -replace "(?m)^#?\s*$([regex]::Escape($name))=.*$", $entry
        }
        else {
            $content = $content.TrimEnd() + "`n$entry"
        }
        Set-Content -Path $EnvFile -Value $content -NoNewline -Encoding utf8
    }
    else {
        Set-Content -Path $EnvFile -Value "# Local secrets — NEVER commit (protected by .gitignore + gitleaks)`n$entry`n" -Encoding utf8
    }
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
}

# --- Step 1: promptfoo reachable? ---------------------------------------------
Write-Host "🔍 Checking promptfoo (via npx)..." -ForegroundColor DarkGray
$null = Get-Command npx -ErrorAction SilentlyContinue
if (-not $?) {
    Write-Host "❌ npx not found. Install Node.js (LTS) first: https://nodejs.org" -ForegroundColor Red
    exit 1
}
Write-Host "✅ npx available — promptfoo will run as npx promptfoo@latest" -ForegroundColor Green

# --- Step 2: provider configured? ----------------------------------------------
if (Test-Configured) {
    Write-Host "✅ Provider configured: EVAL_MODEL=$(Get-EnvVal 'EVAL_MODEL') @ $(Get-EnvVal 'EVAL_API_BASE_URL') (key hidden)" -ForegroundColor Green
}
else {
    Write-Host "❌ Eval provider not configured (need EVAL_API_BASE_URL + EVAL_MODEL + EVAL_API_KEY)." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "These describe any OpenAI-compatible chat endpoint the evals will call."
    Write-Host "Examples: https://api.openai.com/v1 + gpt-4o-mini, or a local router."
    Write-Host ""

    $base = Read-Host "EVAL_API_BASE_URL (e.g. https://api.openai.com/v1)"
    if ([string]::IsNullOrWhiteSpace($base)) { Write-Host "❌ Base URL is required — aborted." -ForegroundColor Red; exit 1 }
    $model = Read-Host "EVAL_MODEL (model id your endpoint serves)"
    if ([string]::IsNullOrWhiteSpace($model)) { Write-Host "❌ Model is required — aborted." -ForegroundColor Red; exit 1 }

    # Masked input — the key is never echoed to the terminal.
    $secure = Read-Host "EVAL_API_KEY (input hidden)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    if ([string]::IsNullOrWhiteSpace($plain)) { Write-Host "❌ Empty key — aborted." -ForegroundColor Red; exit 1 }

    Save-EnvVar 'EVAL_API_BASE_URL' $base.Trim()
    Save-EnvVar 'EVAL_MODEL' $model.Trim()
    Save-EnvVar 'EVAL_API_KEY' $plain
    $plain = $null  # scrub from memory ASAP
    Write-Host "✅ Provider saved to local .env (git-ignored, gitleaks-protected)" -ForegroundColor Green
    Import-DotEnv
}

# --- Step 3: choose suites ------------------------------------------------------
$suites = Get-ChildItem -Path $SuitesDir -Filter '*.yaml' -ErrorAction SilentlyContinue |
          Sort-Object Name
if (-not $suites -or $suites.Count -eq 0) {
    Write-Host "❌ No suite configs found in evals/suites/." -ForegroundColor Red
    exit 1
}

$toRun = $suites
if (-not [string]::IsNullOrWhiteSpace($Suite)) {
    $toRun = $suites | Where-Object { $_.BaseName -eq $Suite }
    if (-not $toRun) {
        Write-Host "❌ Suite '$Suite' not found. Available:" -ForegroundColor Red
        $suites | ForEach-Object { Write-Host "   - $($_.BaseName)" }
        exit 1
    }
}

# --- Step 4: confirm paid API usage ---------------------------------------------
Write-Host ""
Write-Host "⚠️  This will call a PAID LLM API ($($toRun.Count) suite(s) × agent + judge calls)." -ForegroundColor Yellow
Write-Host "   Typical cost is small, but it is billed to YOUR provider account."
$go = Read-Host "Proceed with evals? [y/N]"
if ($go -notmatch '^(y|yes)$') {
    Write-Host "Cancelled. No API calls were made." -ForegroundColor DarkGray
    exit 0
}

# --- Step 5: run the evals ------------------------------------------------------
Write-Host ""
Write-Host "🚀 Running $($toRun.Count) suite(s)..." -ForegroundColor Cyan
Push-Location $RepoRoot
$failures = @()
try {
    foreach ($s in $toRun) {
        Write-Host "`n▶ $($s.BaseName)" -ForegroundColor Cyan
        & npx --yes promptfoo@latest eval -c "evals/suites/$($s.Name)" --no-cache
        if ($LASTEXITCODE -ne 0) { $failures += $s.BaseName }
    }
}
finally {
    Pop-Location
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "✅ All $($toRun.Count) suite(s) finished without harness errors." -ForegroundColor Green
    Write-Host "   (Scenario pass/fail reflects the MODEL under test — inspect with:)" -ForegroundColor DarkGray
    Write-Host "   npx promptfoo@latest view" -ForegroundColor DarkGray
    if ($View) { & npx --yes promptfoo@latest view }
    exit 0
}
else {
    Write-Host "⚠️  $($failures.Count) suite(s) exited non-zero (model assertions failed or API error):" -ForegroundColor Yellow
    $failures | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
    Write-Host "   Re-inspect a single suite: npx promptfoo@latest eval -c evals/suites/<name>.yaml --no-cache" -ForegroundColor DarkGray
    exit 1
}
