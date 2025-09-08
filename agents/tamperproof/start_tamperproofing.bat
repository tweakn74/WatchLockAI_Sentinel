@echo off
echo 🛡️ Starting WatchLockAI Tamperproofing System...
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

:: Install requirements if needed
if not exist "watchlockai_tamperproof.log" (
    echo 📦 Installing Python requirements...
    pip install -r requirements.txt
)

:: Start tamperproofing system
echo ✅ Launching Tamperproofing System...
echo 🔒 Protection mechanisms will activate...
echo.

:: Start main tamperproofing core
start "WatchLockAI-Tamperproof" python tamperproof_core.py

:: Start watchdog service
timeout /t 5 /nobreak >nul
start "WatchLockAI-Watchdog" python watchdog_service.py

echo ✅ WatchLockAI Tamperproofing System is now active!
echo 🛡️ All protection mechanisms are running in the background.
echo.
echo Press any key to exit this window (protection will continue running)...
pause >nul
