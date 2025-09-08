@echo off
echo.
echo ================================================================
echo        WatchLockAI ULTIMATE Platform Installer
echo              AI-First Real Service Installation
echo ================================================================
echo.
echo This installer follows the LOGICAL ORDER you requested:
echo.
echo   1. 🧠 Deploy AI Brain first and test it
echo   2. 📦 Install modules (AI validates each one)
echo   3. 🔧 Create ACTUAL Windows service 
echo   4. ✅ VERIFY service is really running
echo   5. 🚀 Add to startup automatically
echo   6. 🖥️ Create system tray with FULL functionality
echo   7. 🔍 Final verification - everything ACTUALLY works
echo.
echo The AI Brain will answer questions and validate each module!
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo *** ADMINISTRATOR PRIVILEGES REQUIRED ***
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [ADMIN CHECK] Running with administrator privileges... ✓
echo.

REM Check for Python (required for AI Brain)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo *** PYTHON REQUIRED ***
    echo.
    echo The AI Brain requires Python to run.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo Opening Python download page...
    start https://python.org/downloads
    echo.
    pause
    exit /b 1
)

echo [PYTHON CHECK] Python is installed... ✓
echo.

echo Ready to install WatchLockAI with AI Brain validation!
echo.
echo INSTALLATION WILL:
echo - Create a real AI Brain that answers questions
echo - Install modules and ask AI about each one
echo - Create actual Windows service (not fake)
echo - Verify everything is really running
echo - Add full-featured system tray application
echo.
pause

echo Starting ULTIMATE installation...
echo.

cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "WatchLockAI-ULTIMATE-Installer.ps1"

echo.
echo ================================================================
echo Installation process completed!
echo.
echo If successful, you should see:
echo - WatchLockAI shield icon in system tray
echo - Right-click tray icon for AI interaction menu
echo - Windows service running in services.msc
echo - Console accessible at http://localhost:8080
echo.
echo The AI Brain can answer questions about installed modules!
echo.
pause

exit /b 0
