@echo off
echo [U+1F465] Starting WatchLockAI Account Sentinel...
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

:: Install requirements if needed
if not exist "accounts.db" (
    echo [PKG] Installing Python requirements...
    pip install -r requirements.txt
)

:: Start Account Sentinel
echo [PASS] Launching Account Sentinel...
echo [U+1F464] User monitoring will begin...
echo.

python account_sentinel_core.py

pause
