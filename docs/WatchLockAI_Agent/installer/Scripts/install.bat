@echo off
REM WatchLockAI Agent Installer Wrapper
REM This script launches the PowerShell installer with appropriate parameters

echo WatchLockAI Agent Installer
echo ===========================

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer must be run as Administrator.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Set default console endpoint if not provided
if "%1"=="" (
    set CONSOLE_ENDPOINT=https://console.watchlockai.com
) else (
    set CONSOLE_ENDPOINT=%1
)

echo Installing WatchLockAI Agent...
echo Console Endpoint: %CONSOLE_ENDPOINT%
echo.

REM Launch PowerShell installer
powershell.exe -ExecutionPolicy Bypass -File "%~dp0Install-WatchLockAI.ps1" -ConsoleEndpoint "%CONSOLE_ENDPOINT%"

if %errorLevel% equ 0 (
    echo.
    echo Installation completed successfully!
    echo WatchLockAI Agent is now protecting this system.
) else (
    echo.
    echo Installation failed. Please check the error messages above.
)

pause
