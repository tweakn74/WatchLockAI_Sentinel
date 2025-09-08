# Overwrite both PowerShell profile variants with a clean git-commit-all (no RunPreCommitAll)
$now = Get-Date -Format yyyyMMdd-HHmmss
$profiles = @(
  $PROFILE,
  ($PROFILE -replace '\\PowerShell\\','\\WindowsPowerShell\\'),
  ($PROFILE -replace '\\WindowsPowerShell\\','\\PowerShell\\')
) | Select-Object -Unique | Where-Object { $_ -and $_.Trim() }

$body = @'
function pip { python -m pip @args }

function git-commit-all {
    param(
        [string]$CommitMessage = "chore: bulk sync",
        [string]$RefactorBranch = "daz/refactor-20250825-1853",
        [switch]$EnsureDocsKeep,
        [switch]$EnsureReadmeBadge,
        [switch]$AutoupdateHooks,
        [switch]$OpenPR
    )
    $scriptPath = Join-Path (Get-Location) "tools\all_in_one_git_push_commit.ps1"
    if (-not (Test-Path $scriptPath)) {
        Write-Error "Could not find $scriptPath. Run from the repo root."
        return
    }
    & $scriptPath `
      -CommitMessage:$CommitMessage `
      -RefactorBranch:$RefactorBranch `
      -EnsureDocsKeep:$EnsureDocsKeep `
      -EnsureReadmeBadge:$EnsureReadmeBadge `
      -AutoupdateHooks:$AutoupdateHooks `
      -OpenPR:$OpenPR
}
'@

foreach ($p in $profiles) {
  $dir = Split-Path -Parent $p
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  if (Test-Path $p) { Copy-Item $p "$p.bak_$now" -Force }
  Set-Content -LiteralPath $p -Value $body -Encoding UTF8
}

# Reload any that exist
foreach ($p in $profiles) { if (Test-Path $p) { . $p } }

Write-Host "Profiles updated & reloaded. Backups created with suffix _$now" -ForegroundColor Green
