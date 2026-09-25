@echo off
REM WatchLockAI MSI Build Script
REM Requires WiX Toolset v3.11 or later

echo Building WatchLockAI MSI Installer...
echo =====================================

REM Set paths
set WIX_PATH="%WIX%bin"
set SOURCE_DIR=..\..\src\WatchLockAI.Service\bin\Release\net8.0-windows\win-x64\publish
set CONFIG_DIR=..\..\configs
set OUTPUT_DIR=.\Output

REM Create output directory
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

REM Verify WiX is installed
if not exist %WIX_PATH%\candle.exe (
    echo ERROR: WiX Toolset not found. Please install WiX Toolset v3.11 or later.
    echo Download from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)

REM Verify source files exist
if not exist %SOURCE_DIR%\WatchLockAI.Service.exe (
    echo ERROR: Service executable not found. Please build the project first.
    echo Expected location: %SOURCE_DIR%\WatchLockAI.Service.exe
    pause
    exit /b 1
)

echo Compiling WiX source...
%WIX_PATH%\candle.exe -dSourceDir=%SOURCE_DIR% -dConfigDir=%CONFIG_DIR% -ext WixFirewallExtension WatchLockAI.wxs

if %errorlevel% neq 0 (
    echo ERROR: WiX compilation failed.
    pause
    exit /b 1
)

echo Linking MSI package...
%WIX_PATH%\light.exe -ext WixUIExtension -ext WixFirewallExtension -out %OUTPUT_DIR%\WatchLockAI-Setup.msi WatchLockAI.wixobj

if %errorlevel% neq 0 (
    echo ERROR: MSI linking failed.
    pause
    exit /b 1
)

echo.
echo =====================================
echo MSI package created successfully!
echo Location: %OUTPUT_DIR%\WatchLockAI-Setup.msi
echo =====================================

REM Clean up temporary files
del WatchLockAI.wixobj 2>nul

pause
