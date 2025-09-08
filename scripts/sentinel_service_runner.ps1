# File: scripts/sentinel_service_runner.ps1
# Purpose: Windows service runner for WatchLockAI Sentinel (P3-003)
#
# This script acts as the service executable, handling:
# - Environment variable setup
# - Python path configuration  
# - Graceful shutdown handling
# - Service logging

param(
    [string]$Action = "run",
    [string]$ConfigFile = "",
    [switch]$DryRun = $false
)

# Service configuration
$ServiceName = "WatchLockAISentinel"
$ServiceDisplayName = "WatchLockAI Sentinel Security Monitor"
$ServiceDescription = "Endpoint security monitoring and threat detection service"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RootDir = Split-Path -Parent $ScriptDir

# Service paths
$PythonExe = "python"
$ServiceEntry = Join-Path $RootDir "app.py"
$LogDir = Join-Path $RootDir "logs"
$ServiceLog = Join-Path $LogDir "service.log"

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-ServiceLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Write to console and log file
    Write-Host $logEntry
    Add-Content -Path $ServiceLog -Value $logEntry -ErrorAction SilentlyContinue
}

function Test-PythonAvailable {
    try {
        $pythonVersion = & $PythonExe --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ServiceLog "Python available: $pythonVersion"
            return $true
        }
    } catch {
        Write-ServiceLog "Python not found in PATH" "ERROR"
        return $false
    }
    
    return $false
}

function Set-ServiceEnvironment {
    Write-ServiceLog "Setting up service environment"
    
    # Core service flags
    $env:SERVICE_ENABLED = "1"
    $env:HEALTH_ENDPOINT_ENABLED = "1"
    
    # Logging configuration (use service-friendly settings)
    $env:LOG_MAX_BYTES = "2097152"  # 2MB for service logs
    $env:LOG_BACKUPS = "10"         # More backups for services
    $env:LOG_REDACT_SECRETS = "1"   # Always enable for services
    
    # Default security settings for service mode
    $env:ADMIN_AUTH_ENABLED = "1"   # Recommend enabling admin auth for services
    $env:RATE_LIMIT_ENABLED = "1"   # Enable rate limiting for services
    
    # Disable debug features in service mode
    $env:METRICS_DEBUG_ENABLED = "0"
    $env:CONFIG_HOT_RELOAD_ENABLED = "0"
    
    # Load additional configuration from file if specified
    if ($ConfigFile -and (Test-Path $ConfigFile)) {
        Write-ServiceLog "Loading configuration from: $ConfigFile"
        try {
            Get-Content $ConfigFile | ForEach-Object {
                if ($_ -match "^([^#=]+)=(.+)$") {
                    $key = $matches[1].Trim()
                    $value = $matches[2].Trim().Trim('"', "'")
                    Set-Item -Path "env:$key" -Value $value
                    Write-ServiceLog "Config: $key=[CONFIGURED]"
                }
            }
        } catch {
            Write-ServiceLog "Warning: Failed to load config file: $($_.Exception.Message)" "WARN"
        }
    }
    
    Write-ServiceLog "Environment configured for service mode"
}

function Start-SentinelService {
    Write-ServiceLog "Starting WatchLockAI Sentinel service"
    
    if ($DryRun) {
        Write-ServiceLog "DRY RUN: Would start service with:"
        Write-ServiceLog "  Python: $PythonExe"
        Write-ServiceLog "  Entry Point: $ServiceEntry"
        Write-ServiceLog "  Working Directory: $RootDir"
        Write-ServiceLog "  Service Log: $ServiceLog"
        return
    }
    
    # Validate prerequisites
    if (-not (Test-PythonAvailable)) {
        Write-ServiceLog "Python runtime not available" "ERROR"
        exit 1
    }
    
    if (-not (Test-Path $ServiceEntry)) {
        Write-ServiceLog "Service entry point not found: $ServiceEntry" "ERROR"
        exit 1
    }
    
    # Setup environment
    Set-ServiceEnvironment
    
    # Change to service directory
    Set-Location $RootDir
    Write-ServiceLog "Changed to service directory: $RootDir"
    
    # Start the Python service
    try {
        Write-ServiceLog "Executing: $PythonExe $ServiceEntry"
        & $PythonExe $ServiceEntry
        
        if ($LASTEXITCODE -ne 0) {
            Write-ServiceLog "Service exited with code: $LASTEXITCODE" "ERROR"
            exit $LASTEXITCODE
        }
        
        Write-ServiceLog "Service completed successfully"
    } catch {
        Write-ServiceLog "Service execution failed: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

function Stop-SentinelService {
    Write-ServiceLog "Stopping WatchLockAI Sentinel service"
    
    if ($DryRun) {
        Write-ServiceLog "DRY RUN: Would stop service"
        return
    }
    
    # Attempt graceful shutdown
    try {
        # Send termination signal to Python processes
        $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*$ServiceEntry*"
        }
        
        foreach ($process in $pythonProcesses) {
            Write-ServiceLog "Terminating Python process: $($process.Id)"
            $process.CloseMainWindow()
            Start-Sleep -Seconds 2
            
            if (-not $process.HasExited) {
                $process.Kill()
                Write-ServiceLog "Forcefully terminated process: $($process.Id)" "WARN"
            }
        }
        
        Write-ServiceLog "Service stopped"
    } catch {
        Write-ServiceLog "Error during service shutdown: $($_.Exception.Message)" "WARN"
    }
}

function Get-ServiceStatus {
    Write-ServiceLog "Checking service status"
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service) {
            Write-ServiceLog "Service Status: $($service.Status)"
            Write-ServiceLog "Service Start Type: $($service.StartType)"
            return $service.Status
        } else {
            Write-ServiceLog "Service not found: $ServiceName" "WARN"
            return "NotFound"
        }
    } catch {
        Write-ServiceLog "Error checking service status: $($_.Exception.Message)" "ERROR"
        return "Error"
    }
}

function Show-Usage {
    Write-Host @"
WatchLockAI Sentinel Service Runner

Usage:
  sentinel_service_runner.ps1 [Action] [Options]

Actions:
  run           Start the service (default)
  stop          Stop the service
  status        Check service status
  help          Show this help message

Options:
  -ConfigFile   Path to configuration file (.env format)
  -DryRun       Show what would be done without executing

Examples:
  # Run service normally
  .\sentinel_service_runner.ps1 run

  # Run with custom config
  .\sentinel_service_runner.ps1 run -ConfigFile "C:\Config\sentinel.env"

  # Check service status
  .\sentinel_service_runner.ps1 status

  # Dry run to test configuration
  .\sentinel_service_runner.ps1 run -DryRun

Environment Variables:
  SERVICE_ENABLED=1                 # Enable service mode
  ADMIN_TOKEN=<secure_token>        # Required for admin endpoints
  CONSOLE_AUTH_SESSION_KEY=<key>    # Required for web console (64+ chars hex)
  
"@
}

# Main execution
switch ($Action.ToLower()) {
    "run" { Start-SentinelService }
    "stop" { Stop-SentinelService }
    "status" { Get-ServiceStatus }
    "help" { Show-Usage }
    default {
        Write-ServiceLog "Unknown action: $Action" "ERROR"
        Show-Usage
        exit 1
    }
}
