# File: scripts/install_service.ps1
# Purpose: Install WatchLockAI Sentinel as Windows Service (P3-003)
#
# This script installs the Sentinel application as a Windows service using:
# - sc.exe command-line tool for service creation
# - PowerShell for service configuration
# - Registry modifications for advanced settings

param(
    [string]$ServiceName = "WatchLockAISentinel",
    [string]$DisplayName = "WatchLockAI Sentinel Security Monitor", 
    [string]$Description = "Endpoint security monitoring and threat detection service",
    [string]$StartType = "Automatic",
    [string]$ServiceAccount = "LocalSystem",
    [string]$ConfigFile = "",
    [switch]$DryRun = $false,
    [switch]$Force = $false,
    [switch]$Help = $false
)

# Administrative check
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Get script directory and paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RootDir = Split-Path -Parent $ScriptDir
$ServiceRunner = Join-Path $ScriptDir "sentinel_service_runner.ps1"
$LogDir = Join-Path $RootDir "logs"
$InstallLog = Join-Path $LogDir "install.log"

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-InstallLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host $logEntry
    Add-Content -Path $InstallLog -Value $logEntry -ErrorAction SilentlyContinue
}

function Show-Help {
    Write-Host @"
WatchLockAI Sentinel Service Installer

Usage:
  install_service.ps1 [Options]

Options:
  -ServiceName      Service name (default: WatchLockAISentinel)
  -DisplayName      Display name for service
  -Description      Service description
  -StartType        Service start type: Automatic, Manual, Disabled (default: Automatic)
  -ServiceAccount   Service account: LocalSystem, LocalService, NetworkService (default: LocalSystem)
  -ConfigFile       Path to configuration file (.env format)
  -Force            Force installation even if service exists
  -DryRun           Show what would be done without executing
  -Help             Show this help message

Examples:
  # Basic installation
  .\install_service.ps1

  # Install with custom configuration
  .\install_service.ps1 -ConfigFile "C:\Config\sentinel.env" -StartType Manual

  # Force reinstall
  .\install_service.ps1 -Force

  # Dry run to test installation
  .\install_service.ps1 -DryRun

Prerequisites:
  - PowerShell running as Administrator
  - Python installed and in system PATH
  - WatchLockAI Sentinel application files present

"@
}

function Test-Prerequisites {
    Write-InstallLog "Checking installation prerequisites"
    
    # Check admin privileges
    if (-not $isAdmin) {
        Write-InstallLog "ERROR: This script must be run as Administrator" "ERROR"
        Write-InstallLog "Please run PowerShell as Administrator and try again" "ERROR"
        return $false
    }
    
    # Check Python availability
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-InstallLog "Python found: $pythonVersion"
        } else {
            Write-InstallLog "WARNING: Python not found in system PATH" "WARN"
            Write-InstallLog "Service may fail to start without Python available" "WARN"
        }
    } catch {
        Write-InstallLog "WARNING: Unable to verify Python installation" "WARN"
    }
    
    # Check service runner exists
    if (-not (Test-Path $ServiceRunner)) {
        Write-InstallLog "ERROR: Service runner not found: $ServiceRunner" "ERROR"
        return $false
    }
    
    # Check application entry point
    $appEntry = Join-Path $RootDir "app.py"
    if (-not (Test-Path $appEntry)) {
        Write-InstallLog "WARNING: Application entry point not found: $appEntry" "WARN"
        Write-InstallLog "Ensure WatchLockAI Sentinel application is properly installed" "WARN"
    }
    
    Write-InstallLog "Prerequisites check completed"
    return $true
}

function Test-ServiceExists {
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        return $null -ne $service
    } catch {
        return $false
    }
}

function Remove-ExistingService {
    Write-InstallLog "Removing existing service: $ServiceName"
    
    if ($DryRun) {
        Write-InstallLog "DRY RUN: Would remove existing service"
        return $true
    }
    
    try {
        # Stop service if running
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-InstallLog "Stopping service: $ServiceName"
            Stop-Service -Name $ServiceName -Force -ErrorAction Stop
            Start-Sleep -Seconds 5
        }
        
        # Remove service using sc.exe
        Write-InstallLog "Deleting service: $ServiceName"
        $result = & sc.exe delete $ServiceName
        
        if ($LASTEXITCODE -eq 0) {
            Write-InstallLog "Service removed successfully"
            Start-Sleep -Seconds 2  # Allow time for cleanup
            return $true
        } else {
            Write-InstallLog "Failed to remove service: $result" "ERROR"
            return $false
        }
    } catch {
        Write-InstallLog "Error removing service: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Install-SentinelService {
    Write-InstallLog "Installing WatchLockAI Sentinel service"
    
    # Build service command
    $serviceCommand = "powershell.exe -ExecutionPolicy Bypass -File `"$ServiceRunner`" run"
    
    if ($ConfigFile) {
        $serviceCommand += " -ConfigFile `"$ConfigFile`""
    }
    
    Write-InstallLog "Service command: $serviceCommand"
    
    if ($DryRun) {
        Write-InstallLog "DRY RUN: Would install service with:"
        Write-InstallLog "  Name: $ServiceName"
        Write-InstallLog "  Display Name: $DisplayName" 
        Write-InstallLog "  Description: $Description"
        Write-InstallLog "  Start Type: $StartType"
        Write-InstallLog "  Service Account: $ServiceAccount"
        Write-InstallLog "  Binary Path: $serviceCommand"
        return $true
    }
    
    try {
        # Create service using sc.exe
        Write-InstallLog "Creating service with sc.exe"
        
        $scArgs = @(
            "create",
            $ServiceName,
            "binPath=", "`"$serviceCommand`"",
            "DisplayName=", "`"$DisplayName`"",
            "start=", $StartType.ToLower()
        )
        
        $result = & sc.exe $scArgs
        
        if ($LASTEXITCODE -ne 0) {
            Write-InstallLog "Failed to create service: $result" "ERROR"
            return $false
        }
        
        Write-InstallLog "Service created successfully"
        
        # Set service description
        Write-InstallLog "Setting service description"
        & sc.exe description $ServiceName $Description | Out-Null
        
        # Configure service recovery options
        Write-InstallLog "Configuring service recovery options"
        & sc.exe failure $ServiceName reset= 86400 actions= restart/30000/restart/60000/restart/60000 | Out-Null
        
        # Set service account if not LocalSystem
        if ($ServiceAccount -ne "LocalSystem") {
            Write-InstallLog "Configuring service account: $ServiceAccount"
            & sc.exe config $ServiceName obj= $ServiceAccount | Out-Null
        }
        
        Write-InstallLog "Service installation completed successfully"
        return $true
        
    } catch {
        Write-InstallLog "Error installing service: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-ServiceInstallation {
    Write-InstallLog "Verifying service installation"
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction Stop
        
        Write-InstallLog "Service Details:"
        Write-InstallLog "  Name: $($service.Name)"
        Write-InstallLog "  Display Name: $($service.DisplayName)"
        Write-InstallLog "  Status: $($service.Status)"
        Write-InstallLog "  Start Type: $($service.StartType)"
        
        # Test service startup (dry run)
        if (-not $DryRun) {
            Write-InstallLog "Testing service startup..."
            try {
                Start-Service -Name $ServiceName -ErrorAction Stop
                Start-Sleep -Seconds 5
                
                $runningService = Get-Service -Name $ServiceName
                if ($runningService.Status -eq "Running") {
                    Write-InstallLog "Service started successfully"
                    
                    # Stop service after test
                    Stop-Service -Name $ServiceName -Force
                    Write-InstallLog "Service stopped after test"
                } else {
                    Write-InstallLog "WARNING: Service failed to start properly" "WARN"
                }
            } catch {
                Write-InstallLog "WARNING: Service startup test failed: $($_.Exception.Message)" "WARN"
            }
        }
        
        return $true
    } catch {
        Write-InstallLog "Service verification failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-InstallationSummary {
    Write-Host ""
    Write-Host "=== Installation Summary ===" -ForegroundColor Green
    Write-Host "Service Name: $ServiceName"
    Write-Host "Display Name: $DisplayName"
    Write-Host "Start Type: $StartType"
    Write-Host "Service Account: $ServiceAccount"
    if ($ConfigFile) {
        Write-Host "Config File: $ConfigFile"
    }
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Configure required environment variables:"
    Write-Host "   - ADMIN_TOKEN (for admin API access)"
    Write-Host "   - CONSOLE_AUTH_SESSION_KEY (if using web console)"
    Write-Host ""
    Write-Host "2. Start the service:"
    Write-Host "   Start-Service -Name $ServiceName"
    Write-Host ""
    Write-Host "3. Check service status:"
    Write-Host "   Get-Service -Name $ServiceName"
    Write-Host ""
    Write-Host "4. View logs:"
    Write-Host "   Get-Content '$InstallLog'"
    Write-Host ""
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-InstallLog "=== WatchLockAI Sentinel Service Installation Started ==="
Write-InstallLog "Service Name: $ServiceName"
Write-InstallLog "Display Name: $DisplayName"
Write-InstallLog "Start Type: $StartType"

# Check prerequisites
if (-not (Test-Prerequisites)) {
    Write-InstallLog "Prerequisites check failed - installation aborted" "ERROR"
    exit 1
}

# Handle existing service
if (Test-ServiceExists) {
    if ($Force) {
        Write-InstallLog "Service exists - forcing reinstallation"
        if (-not (Remove-ExistingService)) {
            Write-InstallLog "Failed to remove existing service - installation aborted" "ERROR"
            exit 1
        }
    } else {
        Write-InstallLog "Service already exists - use -Force to reinstall" "ERROR"
        Write-InstallLog "Or run: .\uninstall_service.ps1" "ERROR"
        exit 1
    }
}

# Install service
if (-not (Install-SentinelService)) {
    Write-InstallLog "Service installation failed" "ERROR"
    exit 1
}

# Verify installation
if (-not (Test-ServiceInstallation)) {
    Write-InstallLog "Service verification failed" "ERROR"
    exit 1
}

Write-InstallLog "=== Installation Completed Successfully ==="

if (-not $DryRun) {
    Show-InstallationSummary
}

exit 0
