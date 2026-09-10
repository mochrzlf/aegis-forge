<#
.SYNOPSIS
    Aegis Forge — Agent Evals guard & launcher (Windows / PowerShell).

.DESCRIPTION
    Interactive guard before running the promptfoo agent evals:
      1. Verifies promptfoo is reachable (via npx).
      2. Checks that an LLM provider API key is configured; if not, offers
         an interactive (masked) setup that persists the key to the local
         .env file (git-ignored, gitleaks-protected).
      3. Confirms paid API usage with the user before spending anything.
      4. Runs: npx promptfoo@latest eval -c evals/promptfooconfig.yaml

    API keys are NEVER written to the repo, the command line, or logs.
    The local .env file is excluded by .gitignore and scanned by gitleaks.

.EXAMPLE
    pwsh scripts/run-evals.ps1
    pwsh scripts/run-evals.ps1 -View   # open results viewer afterwards
#>
[CmdletBinding()]
param(
    [switch]$View  # open `promptfoo view` after a successful eval run
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- Locate repo root (this script lives in scripts/) -------------------------
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$EnvFile  = Join-Path $RepoRoot '.env'
$Config   = Join-Path $RepoRoot 'evals/promptfooconfig.yaml'

Write-Host ""
Write-Host "🛡️  Aegis Forge — Agent Evals Setup Check" -ForegroundColor Cyan
Write-Host ("─" * 60)

# --- Load provider keys already present in the local .env ---------------------
$Providers = [ordered]@{
    '1' = @{ Name = 'OpenAI';    EnvVar = 'OPENAI_API_KEY';    Prefix = 'sk-'   }
    '2' = @{ Name = 'Anthropic'; EnvVar = 'ANTHROPIC_API_KEY'; Prefix = 'sk-ant' }
    '3' = @{ Name = 'Google';    EnvVar = 'GOOGLE_API_KEY';    Prefix = 'AI'    }
}

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

# --- Step 1: promptfoo reachable? ---------------------------------------------
Write-Host "🔍 Checking promptfoo (via npx)..." -ForegroundColor DarkGray
$null = Get-Command npx -ErrorAction SilentlyContinue
if (-not $?) {
    Write-Host "❌ npx not found. Install Node.js (LTS) first: https://nodejs.org" -ForegroundColor Red
    exit 1
}
Write-Host "✅ npx available — promptfoo will run as npx promptfoo@latest" -ForegroundColor Green

# --- Step 2: API key configured? ----------------------------------------------
function Get-ConfiguredProvider {
    foreach ($key in $Providers.Keys) {
        $p = $Providers[$key]
        $val = [Environment]::GetEnvironmentVariable($p.EnvVar, 'Process')
        if (-not [string]::IsNullOrWhiteSpace($val) -and $val -notmatch 'REPLACE') { return $p }
    }
    return $null
}

$active = Get-ConfiguredProvider
if ($active) {
    Write-Host "✅ Provider key detected: $($active.EnvVar) (value hidden)" -ForegroundColor Green
}
else {
    Write-Host "❌ No LLM provider API key found (checked: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Choose your provider:"
    foreach ($key in $Providers.Keys) {
        Write-Host "  $key) $($Providers[$key].Name)  ($($Providers[$key].EnvVar))"
    }
    Write-Host "  q) Cancel"
    $choice = Read-Host "`nSelection"
    if ($choice -eq 'q' -or -not $Providers.Contains($choice)) {
        Write-Host "Cancelled. No changes made." -ForegroundColor DarkGray
        exit 0
    }
    $sel = $Providers[$choice]

    # Masked input — the key is never echoed to the terminal.
    $secure = Read-Host "Paste your $($sel.Name) API key (input hidden)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)

    if ([string]::IsNullOrWhiteSpace($plain)) {
        Write-Host "❌ Empty key — aborted." -ForegroundColor Red
        exit 1
    }
    if ($plain -notlike "$($sel.Prefix)*") {
        Write-Host "⚠️  Key does not start with '$($sel.Prefix)' — continuing anyway (verify it is valid)." -ForegroundColor Yellow
    }

    # Persist to local .env (append or replace the placeholder line).
    $entry = "$($sel.EnvVar)=`"$plain`""
    if (Test-Path $EnvFile) {
        $content = Get-Content $EnvFile -Raw
        if ($content -match "(?m)^#?\s*$($sel.EnvVar)=") {
            $content = $content -replace "(?m)^#?\s*$($sel.EnvVar)=.*$", $entry
        }
        else {
            $content = $content.TrimEnd() + "`n`n# LLM / AGENT EVALS (added by run-evals.ps1, $(Get-Date -Format 'yyyy-MM-dd'))`n$entry`n"
        }
        Set-Content -Path $EnvFile -Value $content -NoNewline -Encoding utf8
    }
    else {
        Set-Content -Path $EnvFile -Value "# Local secrets — NEVER commit (protected by .gitignore + gitleaks)`n$entry`n" -Encoding utf8
    }
    $plain = $null  # scrub from memory ASAP
    [Environment]::SetEnvironmentVariable($sel.EnvVar, '<set>', 'Process')
    Write-Host "✅ Key saved to local .env (git-ignored, gitleaks-protected)" -ForegroundColor Green
    Import-DotEnv
}

# --- Step 3: confirm paid API usage -------------------------------------------
Write-Host ""
Write-Host "⚠️  This will call a PAID LLM API (6 scenarios × agent + judge calls)." -ForegroundColor Yellow
Write-Host "   Typical cost is small, but it is billed to YOUR provider account."
$go = Read-Host "Proceed with evals? [y/N]"
if ($go -notmatch '^(y|yes)$') {
    Write-Host "Cancelled. No API calls were made." -ForegroundColor DarkGray
    exit 0
}

# --- Step 4: run the evals -----------------------------------------------------
Write-Host ""
Write-Host "🚀 Running promptfoo evals..." -ForegroundColor Cyan
Push-Location $RepoRoot
try {
    & npx --yes promptfoo@latest eval -c $Config
    $code = $LASTEXITCODE
}
finally {
    Pop-Location
}

if ($code -eq 0) {
    Write-Host "`n✅ Evals finished. Browse results with:" -ForegroundColor Green
    Write-Host "   npx promptfoo@latest view" -ForegroundColor DarkGray
    if ($View) { & npx --yes promptfoo@latest view }
}
else {
    Write-Host "`n❌ promptfoo exited with code $code — see output above." -ForegroundColor Red
}
exit $code
