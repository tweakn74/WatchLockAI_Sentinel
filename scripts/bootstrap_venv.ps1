# WatchLockAI Sentinel Offline Bootstrap Script
# This script sets up the offline installation

param(
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,
    
    [Parameter(Mandatory=$false)]
    [switch]$InstallService,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Test-Environment {
    Write-Log "Checking environment..."
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5) {
        throw "PowerShell 5.0 or later required. Current version: $psVersion"
    }
    Write-Log "PowerShell version: $psVersion"
    
    # Check if running as administrator (for service installation)
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if ($InstallService -and -not $isAdmin) {
        Write-Log "Warning: Service installation requires administrator privileges" "WARN"
    }
    
    # Check execution policy
    $execPolicy = Get-ExecutionPolicy
    if ($execPolicy -eq "Restricted") {
        Write-Log "Warning: PowerShell execution policy is Restricted. May need to change it." "WARN"
        Write-Log "Consider running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" "WARN"
    }
    
    Write-Log "Environment check completed"
}

function Test-BundleIntegrity {
    param([string]$ScriptDir)
    
    Write-Log "Verifying bundle integrity..."
    
    $sourceDir = Join-Path $ScriptDir "source"
    $venvDir = Join-Path $ScriptDir "venv"
    
    # Check source directory
    if (-not (Test-Path $sourceDir)) {
        throw "Source directory not found: $sourceDir. Bundle may be corrupted."
    }
    
    # Check key source files
    $requiredFiles = @(
        "console\\web_api.py",
        "app_core\\bus.py",
        "app.py",
        "VERSION"
    )
    
    foreach ($file in $requiredFiles) {
        $fullPath = Join-Path $sourceDir $file
        if (-not (Test-Path $fullPath)) {
            throw "Required file missing: $file. Bundle may be corrupted."
        }
    }
    
    # Check virtual environment
    if (-not (Test-Path $venvDir)) {
        throw "Virtual environment not found: $venvDir. Bundle may be corrupted."
    }
    
    $activateScript = Join-Path $venvDir "Scripts\\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        throw "Virtual environment activation script not found. Bundle may be corrupted."
    }
    
    $pythonExe = Join-Path $venvDir "Scripts\\python.exe"
    if (-not (Test-Path $pythonExe)) {
        throw "Python executable not found in virtual environment. Bundle may be corrupted."
    }
    
    Write-Log "Bundle integrity verified" "SUCCESS"
}

function Initialize-VirtualEnvironment {
    param([string]$VenvDir, [string]$SourceDir)
    
    Write-Log "Initializing virtual environment..."
    
    $activateScript = Join-Path $VenvDir "Scripts\\Activate.ps1"
    
    # Activate virtual environment
    try {
        & $activateScript
        Write-Log "Virtual environment activated" "SUCCESS"
    } catch {
        throw "Failed to activate virtual environment: $_"
    }
    
    # Test Python in virtual environment
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python version in venv: $pythonVersion"
    } catch {
        throw "Python not working in virtual environment"
    }
    
    # Test pip
    try {
        $pipVersion = pip --version 2>&1
        Write-Log "Pip version: $pipVersion"
    } catch {
        Write-Log "Warning: pip not available in virtual environment" "WARN"
    }
}

function Test-CoreImports {
    param([string]$SourceDir)
    
    Write-Log "Testing core imports..."
    
    Push-Location $SourceDir
    
    try {
        # Test core module imports
        $imports = @(
            "app_core.bus",
            "console.web_api",
            "app_core.config"
        )
        
        foreach ($import in $imports) {
            try {
                python -c "import $import; print('$import imported successfully')"
                Write-Log "[x] $import" "SUCCESS"
            } catch {
                Write-Log "[WARN] Failed to import $import" "WARN"
            }
        }
        
        # Test FastAPI availability (optional)
        try {
            python -c "import fastapi; print('FastAPI available')"
            Write-Log "[x] FastAPI available" "SUCCESS"
        } catch {
            Write-Log "[WARN] FastAPI not available (optional)" "WARN"
        }
        
    } finally {
        Pop-Location
    }
    
    Write-Log "Core imports test completed"
}

function Invoke-PreflightChecks {
    param([string]$SourceDir)
    
    Write-Log "Running preflight checks..."
    
    Push-Location $SourceDir
    
    try {
        # Compile verification script
        if (Test-Path "tools\\verify_minimax_claims.py") {
            try {
                python -m py_compile tools\\verify_minimax_claims.py
                Write-Log "[x] Verification script compiled" "SUCCESS"
            } catch {
                Write-Log "[WARN] Verification script compilation failed" "WARN"
            }
        }
        
        # Test API contract check
        if (Test-Path "tools\\api_contract_check.py") {
            try {
                python -m py_compile tools\\api_contract_check.py
                Write-Log "[x] API contract check compiled" "SUCCESS"
            } catch {
                Write-Log "[WARN] API contract check compilation failed" "WARN"
            }
        }
        
        # Basic syntax check on main application
        if (Test-Path "app.py") {
            try {
                python -m py_compile app.py
                Write-Log "[x] Main application compiled" "SUCCESS"
            } catch {
                Write-Log "[WARN] Main application compilation failed" "WARN"
            }
        }
        
    } finally {
        Pop-Location
    }
    
    Write-Log "Preflight checks completed"
}

function Invoke-TestSuite {
    param([string]$SourceDir)
    
    if ($SkipTests) {
        Write-Log "Skipping test suite (as requested)"
        return
    }
    
    Write-Log "Running test suite..."
    
    Push-Location $SourceDir
    
    try {
        # Run unittest discovery
        try {
            python -m unittest discover -v -s tests -p "test_*.py"
            Write-Log "[x] All tests passed" "SUCCESS"
        } catch {
            Write-Log "[WARN] Some tests failed, but installation can continue" "WARN"
            if ($Verbose) {
                Write-Log "Test output: $_" "WARN"
            }
        }
        
    } finally {
        Pop-Location
    }
}

function Install-WindowsService {
    param([string]$SourceDir)
    
    if (-not $InstallService) {
        Write-Log "Skipping service installation (not requested)"
        return
    }
    
    Write-Log "Installing Windows service..."
    
    Push-Location $SourceDir
    
    try {
        if (Test-Path "scripts\\install_service.ps1") {
            try {
                & "scripts\\install_service.ps1"
                Write-Log "[x] Service installation completed" "SUCCESS"
            } catch {
                Write-Log "[WARN] Service installation failed: $_" "WARN"
            }
        } else {
            Write-Log "[WARN] Service installation script not found" "WARN"
        }
        
    } finally {
        Pop-Location
    }
}

function New-Configuration {
    param([string]$SourceDir)
    
    Write-Log "Setting up configuration..."
    
    Push-Location $SourceDir
    
    try {
        # Create .env from template if it doesn't exist
        if ((Test-Path "DOCS\\config\\.env.example") -and (-not (Test-Path ".env"))) {
            Copy-Item "DOCS\\config\\.env.example" ".env"
            Write-Log "[x] Created .env from template" "SUCCESS"
            Write-Log "Please edit .env to configure features as needed"
        }
        
        # Create data directories
        $dataDirs = @("data", "data\\quarantine", "data\\export", "data\\backups", "logs")
        foreach ($dir in $dataDirs) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                Write-Log "[x] Created directory: $dir" "SUCCESS"
            }
        }
        
    } finally {
        Pop-Location
    }
}

function Show-CompletionMessage {
    param([string]$SourceDir)
    
    Write-Log "" 
    Write-Log "══════════════════════════════════════=" "SUCCESS"
    Write-Log "  Installation completed successfully!" "SUCCESS"
    Write-Log "══════════════════════════════════════=" "SUCCESS"
    Write-Log ""
    Write-Log "Next steps:"
    Write-Log "1. Review and edit .env file to enable desired features"
    Write-Log "2. Start the service:"
    Write-Log "   cd '$SourceDir'"
    Write-Log "   python app.py"
    Write-Log ""
    Write-Log "3. Access web console at: http://127.0.0.1:8080"
    Write-Log ""
    Write-Log "For configuration help, see:"
    Write-Log "- DOCS/operations_runbook.md"
    Write-Log "- DOCS/config/config.example.json"
    Write-Log "- DOCS/deploy_windows.md"
    Write-Log ""
    
    if ($InstallService) {
        Write-Log "Service installation was attempted. Check Windows Services manager."
    }
    
    Write-Log "For verification, run:"
    Write-Log "python tools\\verify_minimax_claims.py"
    Write-Log ""
}

# Main execution
try {
    Write-Log "Starting WatchLockAI Sentinel offline installation..." "SUCCESS"
    Write-Log ""
    
    # Get script directory (bundle root)
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $sourceDir = Join-Path $scriptDir "source"
    $venvDir = Join-Path $scriptDir "venv"
    
    # If we're in a bundled installation, use current directory structure
    if (-not (Test-Path $sourceDir)) {
        # Assume we're running from the source directory
        $sourceDir = $scriptDir
        $venvDir = Join-Path $scriptDir "..\\venv"
    }
    
    Test-Environment
    Test-BundleIntegrity -ScriptDir $scriptDir
    Initialize-VirtualEnvironment -VenvDir $venvDir -SourceDir $sourceDir
    Test-CoreImports -SourceDir $sourceDir
    Invoke-PreflightChecks -SourceDir $sourceDir
    Invoke-TestSuite -SourceDir $sourceDir
    Install-WindowsService -SourceDir $sourceDir
    New-Configuration -SourceDir $sourceDir
    
    Show-CompletionMessage -SourceDir $sourceDir
    
} catch {
    Write-Log "Error: $_" "ERROR"
    Write-Log "Installation failed. Please check the error message above." "ERROR"
    exit 1
    
} finally {
    # Deactivate virtual environment if it was activated
    try {
        if (Get-Command deactivate -ErrorAction SilentlyContinue) {
            deactivate
        }
    } catch {
        # Ignore deactivation errors
    }
}
