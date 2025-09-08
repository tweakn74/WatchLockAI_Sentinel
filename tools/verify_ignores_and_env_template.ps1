<# =====================================================================
Verify/repair .gitignore and ensure .env.template
Usage:
  powershell -ExecutionPolicy Bypass -File tools\verify_ignores_and_env_template.ps1 -Fix -Stage -Commit -Push `
    -CommitMessage "chore: track .env.template (ignore .env) + hygiene"
===================================================================== #>

param(
  [switch]$Fix,
  [switch]$Stage,
  [switch]$Commit,
  [switch]$Push,
  [string]$CommitMessage = "chore: track .env.template (ignore .env) + hygiene"
)

$ErrorActionPreference = "Stop"

function Invoke-Exec {
  param([Parameter(Mandatory=$true)][string]$Cmd,[switch]$AllowFail)
  Write-Host ">> $Cmd" -ForegroundColor Cyan
  cmd /c $Cmd | Out-Host
  if (-not $AllowFail -and $LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Cmd" }
}

function Test-RepoRoot { Test-Path ".git" }

function Add-LinesIfMissing {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string[]]$Lines
  )
  # Normalize input: coerce to array and drop empties
  if ($Lines -isnot [System.Array]) { $Lines = @($Lines) }
  $Lines = $Lines | Where-Object { $_ -and $_.Trim().Length -gt 0 }

  if (-not (Test-Path $Path)) { New-Item -ItemType File -Path $Path -Force | Out-Null }
  $existing = @(Get-Content -Path $Path -ErrorAction SilentlyContinue)
  $added = 0
  foreach ($line in $Lines) {
    if ($existing -notcontains $line) { Add-Content -Path $Path -Value $line; $added++ }
  }
  if ($added -gt 0) { Write-Host "Updated $Path (+$added lines)" -ForegroundColor Green }
  else { Write-Host "$Path already has required lines" -ForegroundColor DarkGray }
}

function Set-FileContentIfChanged {
  param([Parameter(Mandatory=$true)][string]$Path,[Parameter(Mandatory=$true)][string]$Content)
  $dir = Split-Path -Parent $Path
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  $current = if (Test-Path $Path) { Get-Content -Path $Path -Raw -ErrorAction SilentlyContinue } else { "" }
  if ($current -ne $Content) { Set-Content -Path $Path -Value $Content -Encoding UTF8; Write-Host "Wrote $Path" -ForegroundColor Green }
  else { Write-Host "$Path is up to date" -ForegroundColor DarkGray }
}

function Update-IgnoreRules {
  param([switch]$DoFix)
  $rules = @(
    "# Secrets & runtime"
    ".env"
    ".devagentzero/"
    ""
    "# Node artifacts"
    "node_modules/"
    "ui/node_modules/"
    ""
    "# Track the environment template"
    "!.env.template"
  )
  # Filter empties up front to avoid binding issues
  $rules = $rules | Where-Object { $_ -and $_.Trim().Length -gt 0 }

  if ($DoFix) {
    Add-LinesIfMissing ".gitignore" $rules
  } else {
    if (-not (Test-Path ".gitignore")) { throw ".gitignore not found" }
    $content = Get-Content ".gitignore"
    $missing = foreach ($r in $rules) { if ($content -notcontains $r) { $r } }
    if ($missing.Count -gt 0) {
      Write-Host "Missing in .gitignore:" -ForegroundColor Yellow
      $missing | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
      throw "Run with -Fix to add missing rules."
    }
  }
}

function New-EnvTemplate {
  param([switch]$DoFix)
  $tpl = @"
# Example environment template for DevAgentZero
# Copy to .env and fill in real values (never commit .env)

# --- OpenAI / LLMs ---
OPENAI_API_KEY=
OPENAI_BASE_URL=

# --- Ollama (local) ---
OLLAMA_BASE_URL=http://127.0.0.1:11434

# --- Pulselet adapter ---
PULSELET_BASE_URL=http://127.0.0.1:8000
PULSELET_TIMEOUT=30

# --- Server / FastAPI ---
DAZ_HOST=127.0.0.1
DAZ_PORT=8080
DAZ_ADMIN_TOKEN=

# --- Misc ---
LOG_LEVEL=INFO
"@
  if ($DoFix) { Set-FileContentIfChanged ".env.template" $tpl }
  else { if (-not (Test-Path ".env.template")) { throw ".env.template is missing. Run with -Fix to create it." } }
}

# ---- main ----
if (-not (Test-RepoRoot)) { throw "Run this from the repo root (where .git exists)." }

try {
  Update-IgnoreRules -DoFix:$Fix
  New-EnvTemplate  -DoFix:$Fix

  if ($Stage) {
    Invoke-Exec 'git add .gitignore'
    # force-add template in case a broad ignore blocks *.env*
    Invoke-Exec 'git add -f .env.template'
  }

  if ($Commit) {
    if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
      $CommitMessage = "chore: track .env.template (ignore .env) + hygiene"
    }
    Invoke-Exec ("git commit -m ""{0}""" -f $CommitMessage)
  }

  if ($Push) { Invoke-Exec 'git push' }

  Write-Host "Done." -ForegroundColor Green
}
catch {
  Write-Host $_.Exception.Message -ForegroundColor Red
  exit 1
}
