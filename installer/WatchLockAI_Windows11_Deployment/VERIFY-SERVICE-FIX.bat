@echo off
cls
echo ================================================================
echo        WatchLockAI v2.1 Service Verification Tool
echo        Tests if Error 1053 has been fixed
echo ================================================================
echo.

echo [1/5] Checking if WatchLockAI service exists...
sc query WatchLockAI >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Service found
    for /f "tokens=3" %%i in ('sc query WatchLockAI ^| find "STATE"') do set state=%%i
    echo    Current state: %state%
) else (
    echo ❌ Service not found - run installer first
    goto end
)

echo.
echo [2/5] Testing service start capability...
sc stop WatchLockAI >nul 2>&1
timeout /t 3 /nobreak >nul
sc start WatchLockAI >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Service start command successful
) else (
    echo ❌ Service start command failed
    goto end
)

echo.
echo [3/5] Waiting for service to reach running state...
timeout /t 10 /nobreak >nul
for /f "tokens=3" %%i in ('sc query WatchLockAI ^| find "STATE"') do set finalstate=%%i
if "%finalstate%"=="RUNNING" (
    echo ✅ Service is RUNNING - Error 1053 FIXED!
) else (
    echo ❌ Service state: %finalstate%
    echo    Error 1053 may still be present
)

echo.
echo [4/5] Testing AI Brain connectivity...
timeout /t 5 /nobreak >nul
curl -s http://localhost:9999/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ AI Brain is responding on port 9999
) else (
    echo ⚠️  AI Brain not yet responding (may still be starting)
)

echo.
echo [5/5] Checking system tray process...
tasklist /fi "imagename eq powershell.exe" | find "powershell.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ System tray process detected
) else (
    echo ⚠️  System tray may not be running
)

echo.
echo ================================================================
echo                    VERIFICATION COMPLETE
echo ================================================================
echo.
if "%finalstate%"=="RUNNING" (
    echo 🎉 SUCCESS: WatchLockAI service is RUNNING!
    echo 🔧 Error 1053 has been FIXED!
    echo.
    echo Next steps:
    echo 1. Look for WatchLockAI icon in system tray
    echo 2. Right-click tray icon for menu options
    echo 3. Open console: https://sn2cnaszh2.space.minimax.io
) else (
    echo ❌ Issue detected - service not running properly
    echo Please check the installation logs for details
)

:end
echo.
pause