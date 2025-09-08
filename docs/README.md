# WatchLockAI Sentinel
Windows-first host security monitor: file/process/registry/network/health with RAG-backed rules.
- Local-first, privacy by default
- Typed Pydantic models and async event bus
- Tray UI + Windows Service
- Packaged via PyInstaller (optional NSIS installer)

## Quick Build
PowerShell: `.\service\installer\build_installer.ps1 -Version 1.0.0 -OutputDir dist`
Artifacts: `dist\WatchLockAI_Sentinel\...` and optional `WatchLockAI_Sentinel_Setup_v1.0.0.exe`