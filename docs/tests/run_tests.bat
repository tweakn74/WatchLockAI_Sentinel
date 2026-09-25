@echo off
REM WatchLockAI Integration Test Runner for Windows
REM Runs the complete test suite

echo WatchLockAI Integration Test Suite
echo ===================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

REM Set default console endpoint if not provided
if "%1"=="" (
    set CONSOLE_ENDPOINT=https://u6df89urxo.space.minimax.io
) else (
    set CONSOLE_ENDPOINT=%1
)

echo Console Endpoint: %CONSOLE_ENDPOINT%
echo.

REM Run the test suite
python tests\run_tests.py --console "%CONSOLE_ENDPOINT%" --output-dir test_results

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo =====================================
    echo [PASS] ALL TESTS PASSED!
    echo WatchLockAI platform is ready for deployment.
    echo =====================================
) else (
    echo.
    echo =====================================
    echo [FAIL] SOME TESTS FAILED!
    echo Please review test results before deployment.
    echo =====================================
)

pause
