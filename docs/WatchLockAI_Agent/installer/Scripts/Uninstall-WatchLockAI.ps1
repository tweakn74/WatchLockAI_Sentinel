# WatchLockAI Agent Uninstallation Script
# Requires Administrator privileges

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

Write-Host "WatchLockAI Agent Uninstaller v1.0" -ForegroundColor Red
Write-Host "Removing WatchLockAI Endpoint Security Agent..." -ForegroundColor Yellow

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator. Please run PowerShell as Administrator and try again."
    exit 1
}

$serviceName = "WatchLockAI"
$installPath = "$env:ProgramFiles\WatchLockAI"

try {
    # Check if service exists
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    
    if ($service) {
        Write-Host "Stopping WatchLockAI service..." -ForegroundColor Yellow
        
        # Stop the service
        if ($service.Status -eq "Running") {
            Stop-Service -Name $serviceName -Force
            
            # Wait for service to stop
            $timeout = 30
            $timer = 0
            do {
                Start-Sleep -Seconds 1
                $timer++
                $service = Get-Service -Name $serviceName
            } while ($service.Status -ne "Stopped" -and $timer -lt $timeout)
            
            if ($service.Status -eq "Stopped") {
                Write-Host "[x] Service stopped" -ForegroundColor Green
            } else {
                Write-Warning "Service stop timeout - forcing termination"
                # Force kill any remaining processes
                Get-Process -Name "WatchLockAI*" -ErrorAction SilentlyContinue | Stop-Process -Force
            }
        }
        
        # Remove the service
        Write-Host "Removing Windows Service..." -ForegroundColor Yellow
        $deleteResult = sc.exe delete $serviceName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[x] Windows Service removed" -ForegroundColor Green
        } else {
            Write-Warning "Failed to remove service: $deleteResult"
        }
    } else {
        Write-Host "Service not found - skipping service removal" -ForegroundColor Yellow
    }
    
    # Remove firewall rules
    Write-Host "Removing firewall rules..." -ForegroundColor Yellow
    $firewallRules = @("WatchLockAI-Console-Out", "WatchLockAI-Agent-In")
    foreach ($ruleName in $firewallRules) {
        try {
            Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
            Write-Host "[x] Removed firewall rule: $ruleName" -ForegroundColor Green
        } catch {
            Write-Warning "Failed to remove firewall rule: $ruleName"
        }
    }
    
    # Remove Event Log source
    Write-Host "Removing Event Log source..." -ForegroundColor Yellow
    try {
        Remove-EventLog -Source "WatchLockAI" -ErrorAction SilentlyContinue
        Write-Host "[x] Event Log source removed" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to remove Event Log source"
    }
    
    # Remove installation directory
    if (Test-Path $installPath) {
        Write-Host "Removing installation directory..." -ForegroundColor Yellow
        
        if (-not $Force) {
            $confirmation = Read-Host "Remove all WatchLockAI files including logs and evidence? (y/N)"
            if ($confirmation -ne "y" -and $confirmation -ne "Y") {
                Write-Host "Installation directory preserved at: $installPath" -ForegroundColor Yellow
                Write-Host "Use -Force parameter to remove all files" -ForegroundColor Yellow
                return
            }
        }
        
        try {
            Remove-Item -Path $installPath -Recurse -Force
            Write-Host "[x] Installation directory removed" -ForegroundColor Green
        } catch {
            Write-Warning "Failed to remove installation directory: $($_.Exception.Message)"
            Write-Host "Manual removal may be required: $installPath" -ForegroundColor Yellow
        }
    }
    
    # Remove registry entries (if any)
    Write-Host "Cleaning registry entries..." -ForegroundColor Yellow
    try {
        Remove-Item -Path "HKLM:\SOFTWARE\WatchLockAI" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "[x] Registry entries cleaned" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to clean some registry entries"
    }
    
    Write-Host "`n" + "="*60 -ForegroundColor Green
    Write-Host "WatchLockAI Agent Uninstallation Complete!" -ForegroundColor Green
    Write-Host "="*60 -ForegroundColor Green
    Write-Host "All WatchLockAI components have been removed from this system." -ForegroundColor White
    Write-Host "`nNote: Some logs may remain in Windows Event Log." -ForegroundColor Yellow
    
} catch {
    Write-Error "Uninstallation failed: $($_.Exception.Message)"
    Write-Host "Manual cleanup may be required." -ForegroundColor Yellow
    exit 1
}
