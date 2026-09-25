@echo off
echo ================================================================
echo        WatchLockAI v2.0 Installation Test Script
echo ================================================================
echo.

echo Testing AI Brain connectivity...
curl -s http://localhost:9999/status 2>nul
if %errorlevel% equ 0 (
    echo [PASS] AI Brain is responding on port 9999
) else (
    echo [FAIL] AI Brain is not responding on port 9999
    echo    Please ensure the service is running
)

echo.
echo Testing Windows Service...
sc query WatchLockAI >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] WatchLockAI service is installed
    for /f "tokens=3" %%i in ('sc query WatchLockAI ^| find "STATE"') do set state=%%i
    echo    Service state: %state%
) else (
    echo [FAIL] WatchLockAI service is not installed
)

echo.
echo Testing System Tray...
tasklist /fi "imagename eq powershell.exe" | find "powershell.exe" >nul
if %errorlevel% equ 0 (
    echo [PASS] PowerShell processes detected (likely system tray)
) else (
    echo [WARN]  No PowerShell processes found
)

echo.
echo Testing Console Access...
curl -s https://sn2cnaszh2.space.minimax.io 2>nul | find "WatchLockAI" >nul
if %errorlevel% equ 0 (
    echo [PASS] Enhanced console is accessible
) else (
    echo [WARN]  Console may not be accessible (check internet connection)
)

echo.
echo ================================================================
echo Test completed. Check results above.
echo ================================================================
pause