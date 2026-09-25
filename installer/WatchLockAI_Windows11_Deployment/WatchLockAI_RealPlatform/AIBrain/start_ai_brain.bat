@echo off
echo [BRAIN] Starting WatchLockAI Agentic AI Brain...
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
if not exist "watchlockai_memory.db" (
    echo [PKG] Installing Python requirements...
    pip install -r requirements.txt
)

:: Start AI Brain
echo [PASS] Launching WatchLockAI AI Brain...
python ai_brain_core.py

pause
