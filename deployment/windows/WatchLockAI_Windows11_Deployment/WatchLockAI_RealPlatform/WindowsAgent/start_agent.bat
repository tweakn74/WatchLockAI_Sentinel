@echo off
echo 🖥️ Starting WatchLockAI Windows Agent...
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
if not exist "watchlockai_agent.log" (
    echo 📦 Installing Python requirements...
    pip install -r requirements.txt
)

:: Start agent
echo ✅ Launching WatchLockAI Agent...
python windows_agent_core.py

pause
