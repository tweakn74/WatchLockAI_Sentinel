# Install / Uninstall (Windows)
- Build: `.\service\installer\build_installer.ps1 -Version 1.0.0 -OutputDir dist`
- No-NSIS path: run `dist\WatchLockAI_Sentinel\WatchLockAI_Sentinel.exe`
- NSIS path: run `WatchLockAI_Sentinel_Setup_v1.0.0.exe`
- Service control: Services.msc or `sc start/stop WatchLockAISentinel`