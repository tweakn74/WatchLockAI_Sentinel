<# =====================================================================
File: tools/install_git_commit_all.ps1
Version: 1.0.0
Purpose:
  - Install a PowerShell helper function `git-commit-all`
  - Function wraps tools\all_in_one_git_push_commit.ps1
  - Reloads profile so command is available immediately
===================================================================== #>

$ErrorActionPreference = "Stop"

# Define the function text
$functionText = @'
function git-commit-all {
    param(
        [string]$CommitMessage = "chore: bulk sync + hygiene",
        [string]$RefactorBranch = "daz/refactor-latest",
        [switch]$EnsureDocsKeep,
        [switch]$EnsureReadmeBadge,
        [switch]$AutoupdateHooks,
        [switch]$RunPreCommitAll,
        [switch]$NoVerify,
        [switch]$OpenPR
    )

    $scriptPath = "tools\\all_in_one_git_push_commit.ps1"
    if (-not (Test-Path $scriptPath)) {
        Write-Error "Cannot find $scriptPath"
        return
    }

    powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath `
        -CommitMessage $CommitMessage `
        -RefactorBranch $RefactorBranch `
        -EnsureDocsKeep:$EnsureDocsKeep `
        -EnsureReadmeBadge:$EnsureReadmeBadge `
        -AutoupdateHooks:$AutoupdateHooks `
        -RunPreCommitAll:$RunPreCommitAll `
        -NoVerify:$NoVerify `
        -OpenPR:$OpenPR
}
'@

# Find profile path
$profilePath = $PROFILE
if (-not (Test-Path (Split-Path $profilePath))) {
    New-Item -ItemType Directory -Path (Split-Path $profilePath) -Force | Out-Null
}

# Add or update function in profile
if (Test-Path $profilePath) {
    $profileContent = Get-Content -Path $profilePath -Raw
    if ($profileContent -match "function git-commit-all") {
        Write-Host "Updating existing git-commit-all function in $profilePath" -ForegroundColor Yellow
        $profileContent = [regex]::Replace($profileContent, "function git-commit-all.*?`n\}", $functionText, "Singleline")
        Set-Content -Path $profilePath -Value $profileContent -Encoding UTF8
    } else {
        Write-Host "Adding git-commit-all function to $profilePath" -ForegroundColor Green
        Add-Content -Path $profilePath -Value "`n$functionText`n"
    }
} else {
    Write-Host "Creating profile and adding git-commit-all function to $profilePath" -ForegroundColor Green
    Set-Content -Path $profilePath -Value $functionText -Encoding UTF8
}

# Reload profile immediately
. $PROFILE
Write-Host "✅ git-commit-all function installed. Try it now!" -ForegroundColor Green
