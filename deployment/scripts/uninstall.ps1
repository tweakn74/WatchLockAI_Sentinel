# File: scripts/uninstall_service.ps1
# Purpose: Uninstall WatchLockAI Sentinel Windows Service (P3-003)
#
# This script safely removes the Sentinel Windows service:
# - Stops the service if running
# - Removes service registration
# - Cleans up service-related files (optional)
# - Preserves logs and configuration by default

param(
    [string]$ServiceName = "WatchLockAISentinel",
    [switch]$CleanLogs = $false,
    [switch]$CleanConfig = $false,
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
$LogDir = Join-Path $RootDir "logs"
$ConfigDir = Join-Path $RootDir "config"
$UninstallLog = Join-Path $LogDir "uninstall.log"

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-UninstallLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host $logEntry
    Add-Content -Path $UninstallLog -Value $logEntry -ErrorAction SilentlyContinue
}

function Show-Help {
    Write-Host @"
WatchLockAI Sentinel Service Uninstaller

Usage:
  uninstall_service.ps1 [Options]

Options:
  -ServiceName      Service name to uninstall (default: WatchLockAISentinel)
  -CleanLogs        Remove log files during uninstallation
  -CleanConfig      Remove configuration files during uninstallation
  -Force            Force uninstall even if service is running
  -DryRun           Show what would be done without executing
  -Help             Show this help message

Examples:
  # Basic uninstall (preserves logs and config)
  .\uninstall_service.ps1

  # Uninstall with log cleanup
  .\uninstall_service.ps1 -CleanLogs

  # Complete uninstall (removes everything)
  .\uninstall_service.ps1 -CleanLogs -CleanConfig

  # Force uninstall running service
  .\uninstall_service.ps1 -Force

  # Dry run to test uninstallation
  .\uninstall_service.ps1 -DryRun

Prerequisites:
  - PowerShell running as Administrator

"@
}

function Test-Prerequisites {
    Write-UninstallLog "Checking uninstallation prerequisites"
    
    if (-not $isAdmin) {
        Write-UninstallLog "ERROR: This script must be run as Administrator" "ERROR"
        Write-UninstallLog "Please run PowerShell as Administrator and try again" "ERROR"
        return $false
    }
    
    Write-UninstallLog "Prerequisites check completed"
    return $true
}

function Get-ServiceInfo {
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        return $service
    } catch {
        return $null
    }
}

function Stop-SentinelService {
    param([object]$Service)
    
    Write-UninstallLog "Stopping service: $ServiceName"
    
    if ($DryRun) {
        Write-UninstallLog "DRY RUN: Would stop service"
        return $true
    }
    
    try {
        if ($Service.Status -eq "Running") {
            Write-UninstallLog "Service is running - attempting graceful shutdown"
            Stop-Service -Name $ServiceName -Force -ErrorAction Stop
            
            # Wait for service to stop
            $timeout = 30  # seconds
            $elapsed = 0
            
            while ($elapsed -lt $timeout) {
                Start-Sleep -Seconds 2
                $elapsed += 2
                
                $currentService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
                if (-not $currentService -or $currentService.Status -ne "Running") {
                    Write-UninstallLog "Service stopped successfully"
                    return $true
                }
            }
            
            Write-UninstallLog "WARNING: Service did not stop within $timeout seconds" "WARN"
            
            if ($Force) {
                Write-UninstallLog "Force flag specified - proceeding with uninstall"
                return $true
            } else {
                Write-UninstallLog "Use -Force to uninstall running service" "ERROR"
                return $false
            }
        } else {
            Write-UninstallLog "Service is not running"
            return $true
        }
    } catch {
        Write-UninstallLog "Error stopping service: $($_.Exception.Message)" "ERROR"
        
        if ($Force) {
            Write-UninstallLog "Force flag specified - continuing despite error" "WARN"
            return $true
        }
        
        return $false
    }
}

function Remove-ServiceRegistration {
    Write-UninstallLog "Removing service registration"
    
    if ($DryRun) {
        Write-UninstallLog "DRY RUN: Would remove service registration"
        return $true
    }
    
    try {
        # Remove service using sc.exe
        Write-UninstallLog "Deleting service: $ServiceName"
        $result = & sc.exe delete $ServiceName
        
        if ($LASTEXITCODE -eq 0) {
            Write-UninstallLog "Service registration removed successfully"
            Start-Sleep -Seconds 2  # Allow time for cleanup
            return $true
        } else {
            Write-UninstallLog "Failed to remove service registration: $result" "ERROR"
            return $false
        }
    } catch {
        Write-UninstallLog "Error removing service registration: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Remove-LogFiles {
    if (-not $CleanLogs) {
        Write-UninstallLog "Preserving log files (use -CleanLogs to remove)"
        return $true
    }
    
    Write-UninstallLog "Removing log files"
    
    if ($DryRun) {
        Write-UninstallLog "DRY RUN: Would remove log directory: $LogDir"
        return $true
    }
    
    try {
        if (Test-Path $LogDir) {
            # Create backup of current uninstall log before removal
            $backupLog = Join-Path $env:TEMP "sentinel_uninstall_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
            Copy-Item $UninstallLog $backupLog -ErrorAction SilentlyContinue
            Write-UninstallLog "Uninstall log backed up to: $backupLog"
            
            Remove-Item $LogDir -Recurse -Force
            Write-UninstallLog "Log directory removed: $LogDir"
        } else {
            Write-UninstallLog "Log directory not found: $LogDir"
        }
        
        return $true
    } catch {
        Write-UninstallLog "Error removing log files: $($_.Exception.Message)" "WARN"
        return $true  # Non-critical error
    }
}

function Remove-ConfigFiles {
    if (-not $CleanConfig) {
        Write-UninstallLog "Preserving configuration files (use -CleanConfig to remove)"
        return $true
    }
    
    Write-UninstallLog "Removing configuration files"
    
    if ($DryRun) {
        Write-UninstallLog "DRY RUN: Would remove config directory: $ConfigDir"
        return $true
    }
    
    try {
        if (Test-Path $ConfigDir) {
            Remove-Item $ConfigDir -Recurse -Force
            Write-UninstallLog "Configuration directory removed: $ConfigDir"
        } else {
            Write-UninstallLog "Configuration directory not found: $ConfigDir"
        }
        
        return $true
    } catch {
        Write-UninstallLog "Error removing configuration files: $($_.Exception.Message)" "WARN"
        return $true  # Non-critical error
    }
}

function Test-ServiceRemoval {
    Write-UninstallLog "Verifying service removal"
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        
        if ($service) {
            Write-UninstallLog "WARNING: Service still exists after uninstall" "WARN"
            Write-UninstallLog "Service Status: $($service.Status)"
            return $false
        } else {
            Write-UninstallLog "Service successfully removed"
            return $true
        }
    } catch {
        Write-UninstallLog "Service removal verified (service not found)"
        return $true
    }
}

function Show-UninstallSummary {
    param([bool]$Success)
    
    Write-Host ""
    if ($Success) {
        Write-Host "=== Uninstallation Completed Successfully ===" -ForegroundColor Green
    } else {
        Write-Host "=== Uninstallation Completed with Warnings ===" -ForegroundColor Yellow
    }
    
    Write-Host "Service Name: $ServiceName"
    Write-Host "Logs Removed: $CleanLogs"
    Write-Host "Config Removed: $CleanConfig"
    
    if (-not $CleanLogs) {
        Write-Host ""
        Write-Host "Log files preserved in: $LogDir" -ForegroundColor Yellow
    }
    
    if (-not $CleanConfig -and (Test-Path $ConfigDir)) {
        Write-Host "Config files preserved in: $ConfigDir" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Uninstall log: $UninstallLog" -ForegroundColor Cyan
    Write-Host ""
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-UninstallLog "=== WatchLockAI Sentinel Service Uninstallation Started ==="
Write-UninstallLog "Service Name: $ServiceName"
Write-UninstallLog "Clean Logs: $CleanLogs"
Write-UninstallLog "Clean Config: $CleanConfig"

# Check prerequisites
if (-not (Test-Prerequisites)) {
    Write-UninstallLog "Prerequisites check failed - uninstallation aborted" "ERROR"
    exit 1
}

# Check if service exists
$serviceInfo = Get-ServiceInfo
if (-not $serviceInfo) {
    Write-UninstallLog "Service not found: $ServiceName" "WARN"
    Write-UninstallLog "Service may have already been uninstalled"
    
    # Still attempt cleanup if requested
    if ($CleanLogs -or $CleanConfig) {
        Write-UninstallLog "Performing file cleanup as requested"
        Remove-LogFiles | Out-Null
        Remove-ConfigFiles | Out-Null
    }
    
    Write-UninstallLog "Uninstallation completed"
    exit 0
}

Write-UninstallLog "Found service: $($serviceInfo.DisplayName)"
Write-UninstallLog "Service Status: $($serviceInfo.Status)"

# Stop service if running
if (-not (Stop-SentinelService -Service $serviceInfo)) {
    Write-UninstallLog "Failed to stop service - uninstallation aborted" "ERROR"
    exit 1
}

# Remove service registration
if (-not (Remove-ServiceRegistration)) {
    Write-UninstallLog "Failed to remove service registration" "ERROR"
    exit 1
}

# Clean up files if requested
Remove-LogFiles | Out-Null
Remove-ConfigFiles | Out-Null

# Verify removal
$removalSuccess = Test-ServiceRemoval

Write-UninstallLog "=== Uninstallation Process Completed ==="

if (-not $DryRun) {
    Show-UninstallSummary -Success $removalSuccess
}

if ($removalSuccess) {
    exit 0
} else {
    exit 1
}
