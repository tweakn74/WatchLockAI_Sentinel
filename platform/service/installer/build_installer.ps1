Param([string]$Version="0.2.0",[string]$OutputDir="dist")
$ErrorActionPreference="Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent | Split-Path -Parent
Set-Location $repo

# venv + deps
if (!(Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\python -m pip install --upgrade pip
& .\.venv\Scripts\python -m pip install -r requirements.txt

# Preserve prior state
& .\.venv\Scripts\python tools\migrate_prior_state.py

# Quality gates (fail-fast)
& .\.venv\Scripts\python tools\repair_and_validate.py
if ($LASTEXITCODE -ne 0) { throw "Quality gates failed." }

# PyInstaller (one-folder)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
& .\.venv\Scripts\pyinstaller --noconfirm --clean --name "WatchLockAI_Sentinel" --onedir app.py

# Move artifacts
Move-Item -Force "dist\WatchLockAI_Sentinel" "$OutputDir\WatchLockAI_Sentinel" -ErrorAction SilentlyContinue

# Optional NSIS
$nsis = (Get-Command makensis.exe -ErrorAction SilentlyContinue)
if ($nsis) {
  $installer = Join-Path $OutputDir "WatchLockAI_Installer.exe"
  $nsi = @"
OutFile "$installer"
InstallDir "\$PROGRAMFILES\WatchLockAI\Sentinel"
Section "Install"
SetOutPath \$INSTDIR
File /r "$($OutputDir)\WatchLockAI_Sentinel\*"
CreateShortCut "\$SMPROGRAMS\WatchLockAI Console.lnk" "\$INSTDIR\WatchLockAI_Sentinel.exe"
SectionEnd
"@
  $nsiPath = Join-Path $OutputDir "watchlockai.nsi"
  $nsi | Out-File -Encoding ASCII $nsiPath
  & $nsis.Source $nsiPath
}

# Source ZIP
$zip = Join-Path $OutputDir "WatchLockAI_Source.zip"
if (Test-Path $zip) { Remove-Item -Force $zip }
Compress-Archive -Path * -DestinationPath $zip -Force

# Artifact assertions
if (!(Test-Path "$OutputDir\WatchLockAI_Sentinel")) { throw "Missing one-folder build." }
if (!(Test-Path $zip)) { throw "Missing source zip." }
Write-Host "Build complete. Artifacts in $OutputDir"
