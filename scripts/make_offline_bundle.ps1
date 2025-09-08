# WatchLockAI Sentinel Offline Bundle Creator (P5-004)
# Creates a self-contained offline installation package

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "WatchLockAI_Sentinel_Offline.zip",
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludePython,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check if we're in the correct directory
    if (-not (Test-Path "console\web_api.py")) {
        throw "Must run from WatchLockAI_Sentinel root directory"
    }
    
    # Check for Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Found Python: $pythonVersion"
    } catch {
        throw "Python not found in PATH. Please install Python 3.8+"
    }
    
    # Check for pip
    try {
        pip --version | Out-Null
        Write-Log "Found pip"
    } catch {
        throw "pip not found. Please ensure pip is installed"
    }
    
    Write-Log "Prerequisites check passed"
}

function New-TempDirectory {
    $tempPath = [System.IO.Path]::GetTempPath()
    $bundleName = "SentinelBundle_" + (Get-Date -Format "yyyyMMdd_HHmmss")
    $bundleDir = Join-Path $tempPath $bundleName
    
    New-Item -ItemType Directory -Path $bundleDir -Force | Out-Null
    Write-Log "Created temporary bundle directory: $bundleDir"
    
    return $bundleDir
}

function Copy-SourceFiles {
    param([string]$BundleDir)
    
    Write-Log "Copying source files..."
    
    $sourceDir = Join-Path $BundleDir "source"
    New-Item -ItemType Directory -Path $sourceDir -Force | Out-Null
    
    # Core directories to include
    $includeDirs = @(
        "console", "app_core", "collectors", "detection", "response", 
        "tools", "tests", "config", "service", "ui", "scripts",
        "DOCS", "plugins"
    )
    
    foreach ($dir in $includeDirs) {
        if (Test-Path $dir) {
            Write-Log "Copying directory: $dir"
            $destDir = Join-Path $sourceDir $dir
            Copy-Item -Path $dir -Destination $destDir -Recurse -Force
        }
    }
    
    # Core files to include
    $includeFiles = @(
        "requirements.txt", "requirements-test.txt", "pyproject.toml",
        "VERSION", "CHANGELOG.md", "README.md", "app.py"
    )
    
    foreach ($file in $includeFiles) {
        if (Test-Path $file) {
            Write-Log "Copying file: $file"
            Copy-Item -Path $file -Destination (Join-Path $sourceDir $file) -Force
        }
    }
    
    Write-Log "Source files copied successfully"
}

function New-VirtualEnvironment {
    param([string]$BundleDir)
    
    Write-Log "Creating virtual environment..."
    
    $venvDir = Join-Path $BundleDir "venv"
    
    # Create virtual environment
    python -m venv $venvDir
    
    # Activate virtual environment
    $activateScript = Join-Path $venvDir "Scripts\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        throw "Failed to create virtual environment"
    }
    
    & $activateScript
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements if they exist
    if (Test-Path "requirements.txt") {
        Write-Log "Installing requirements..."
        python -m pip install -r requirements.txt --no-cache-dir
    }
    
    # Install test requirements if they exist
    if (Test-Path "requirements-test.txt") {
        Write-Log "Installing test requirements..."
        python -m pip install -r requirements-test.txt --no-cache-dir
    }
    
    # Install common packages for offline use
    $commonPackages = @(
        "fastapi", "uvicorn", "pydantic", "loguru", "psutil", 
        "pyyaml", "requests", "pytest", "mock"
    )
    
    foreach ($package in $commonPackages) {
        try {
            python -m pip install $package --no-cache-dir
            Write-Log "Installed: $package"
        } catch {
            Write-Log "Warning: Failed to install $package" "WARN"
        }
    }
    
    # Deactivate virtual environment
    deactivate
    
    Write-Log "Virtual environment created successfully"
}

function New-Bundle {
    param([string]$BundleDir, [string]$OutputPath)
    
    Write-Log "Creating final bundle: $OutputPath"
    
    # Remove existing bundle if it exists
    if (Test-Path $OutputPath) {
        Remove-Item $OutputPath -Force
    }
    
    # Create ZIP archive
    try {
        Compress-Archive -Path "$BundleDir\*" -DestinationPath $OutputPath -CompressionLevel Optimal
        Write-Log "Bundle created successfully: $OutputPath"
        
        # Show bundle size
        $bundleSize = (Get-Item $OutputPath).Length
        $bundleSizeMB = [math]::Round($bundleSize / 1MB, 2)
        Write-Log "Bundle size: $bundleSizeMB MB"
        
    } catch {
        throw "Failed to create bundle: $_"
    }
}

function Remove-TempDirectory {
    param([string]$BundleDir)
    
    try {
        Remove-Item $BundleDir -Recurse -Force
        Write-Log "Temporary directory cleaned up"
    } catch {
        Write-Log "Warning: Could not clean up temporary directory: $BundleDir" "WARN"
    }
}

# Main execution
try {
    Write-Log "Starting offline bundle creation..."
    
    Test-Prerequisites
    
    $bundleDir = New-TempDirectory
    
    Copy-SourceFiles -BundleDir $bundleDir
    New-VirtualEnvironment -BundleDir $bundleDir
    New-Bundle -BundleDir $bundleDir -OutputPath $OutputPath
    
    Write-Log "Offline bundle creation completed successfully!"
    Write-Log "Bundle location: $(Resolve-Path $OutputPath)"
    
} catch {
    Write-Log "Error: $_" "ERROR"
    exit 1
    
} finally {
    if ($bundleDir -and (Test-Path $bundleDir)) {
        Remove-TempDirectory -BundleDir $bundleDir
    }
}
