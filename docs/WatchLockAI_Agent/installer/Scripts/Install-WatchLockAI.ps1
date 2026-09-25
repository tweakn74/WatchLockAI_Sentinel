# WatchLockAI Agent Installation Script
# Requires Administrator privileges

param(
    [Parameter(Mandatory=$false)]
    [string]$ConsoleEndpoint = "https://console.watchlockai.com",
    
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "$env:ProgramFiles\WatchLockAI"
)

Write-Host "WatchLockAI Agent Installer v1.0" -ForegroundColor Green
Write-Host "Installing WatchLockAI Endpoint Security Agent..." -ForegroundColor Yellow

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator. Please run PowerShell as Administrator and try again."
    exit 1
}

# Check Windows version compatibility
$osVersion = [System.Environment]::OSVersion.Version
if ($osVersion.Major -lt 10) {
    Write-Error "WatchLockAI requires Windows 10 or Windows 11. Current version: $($osVersion)"
    exit 1
}

Write-Host "[x] Administrator privileges confirmed" -ForegroundColor Green
Write-Host "[x] Windows version compatible: $($osVersion)" -ForegroundColor Green

try {
    # Create installation directory
    Write-Host "Creating installation directory: $InstallPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    
    # Create subdirectories
    $configDir = Join-Path $InstallPath "Config"
    $logsDir = Join-Path $InstallPath "Logs"
    $evidenceDir = Join-Path $InstallPath "Evidence"
    
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
    
    Write-Host "[x] Installation directories created" -ForegroundColor Green
    
    # Copy service executable (assuming it's in the same directory as this script)
    $serviceExe = "WatchLockAI.Service.exe"
    $sourceExe = Join-Path $PSScriptRoot $serviceExe
    $targetExe = Join-Path $InstallPath $serviceExe
    
    if (Test-Path $sourceExe) {
        Copy-Item $sourceExe $targetExe -Force
        Write-Host "[x] Service executable copied" -ForegroundColor Green
    } else {
        Write-Warning "Service executable not found: $sourceExe"
    }
    
    # Create service configuration
    $configContent = @"
{
  "ServiceName": "WatchLockAI",
  "ServiceDisplayName": "WatchLockAI Endpoint Security",
  "ServiceDescription": "Autonomous AI-powered cybersecurity endpoint agent",
  "ConsoleEndpoint": "$ConsoleEndpoint",
  "LogLevel": "Information",
  "AutoResponseEnabled": false,
  "ThreatDetectionEnabled": true,
  "BehavioralLearningEnabled": true,
  "ForensicsEnabled": true,
  "TamperproofEnabled": true,
  "HeartbeatInterval": 60,
  "UpdateInterval": 3600,
  "MemoryLimit": 512
}
"@
    
    $configFile = Join-Path $configDir "appsettings.json"
    $configContent | Out-File -FilePath $configFile -Encoding UTF8
    Write-Host "[x] Configuration file created" -ForegroundColor Green
    
    # Install Windows Service
    Write-Host "Installing Windows Service..." -ForegroundColor Yellow
    
    $serviceName = "WatchLockAI"
    $serviceDisplayName = "WatchLockAI Endpoint Security"
    $serviceDescription = "Autonomous AI-powered cybersecurity endpoint agent"
    
    # Remove existing service if it exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Host "Removing existing service..." -ForegroundColor Yellow
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        sc.exe delete $serviceName
        Start-Sleep -Seconds 2
    }
    
    # Create new service
    $createResult = sc.exe create $serviceName binPath= "`"$targetExe`"" DisplayName= "$serviceDisplayName" start= auto
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[x] Windows Service created" -ForegroundColor Green
        
        # Set service description
        sc.exe description $serviceName "$serviceDescription"
        
        # Configure service recovery actions
        sc.exe failure $serviceName reset= 86400 actions= restart/30000/restart/60000/restart/120000
        
        Write-Host "[x] Service recovery configured" -ForegroundColor Green
    } else {
        Write-Error "Failed to create Windows Service: $createResult"
        exit 1
    }
    
    # Configure Windows Firewall exceptions
    Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow
    
    $firewallRules = @(
        @{Name="WatchLockAI-Console-Out"; Direction="Outbound"; Action="Allow"; Protocol="TCP"; RemotePort="443,80"},
        @{Name="WatchLockAI-Agent-In"; Direction="Inbound"; Action="Allow"; Protocol="TCP"; LocalPort="8443"}
    )
    
    foreach ($rule in $firewallRules) {
        try {
            New-NetFirewallRule -DisplayName $rule.Name -Direction $rule.Direction -Action $rule.Action -Protocol $rule.Protocol -RemotePort $rule.RemotePort -LocalPort $rule.LocalPort -ErrorAction SilentlyContinue
            Write-Host "[x] Firewall rule created: $($rule.Name)" -ForegroundColor Green
        } catch {
            Write-Warning "Failed to create firewall rule: $($rule.Name)"
        }
    }
    
    # Set appropriate permissions
    Write-Host "Setting security permissions..." -ForegroundColor Yellow
    
    # Grant SYSTEM full control
    $acl = Get-Acl $InstallPath
    $systemSid = New-Object System.Security.Principal.SecurityIdentifier "S-1-5-18"
    $systemAccess = New-Object System.Security.AccessControl.FileSystemAccessRule($systemSid, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
    $acl.SetAccessRule($systemAccess)
    
    # Grant Administrators full control
    $adminsSid = New-Object System.Security.Principal.SecurityIdentifier "S-1-5-32-544"
    $adminsAccess = New-Object System.Security.AccessControl.FileSystemAccessRule($adminsSid, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
    $acl.SetAccessRule($adminsAccess)
    
    # Remove inheritance and other permissions
    $acl.SetAccessRuleProtection($true, $false)
    Set-Acl -Path $InstallPath -AclObject $acl
    
    Write-Host "[x] Security permissions configured" -ForegroundColor Green
    
    # Create Windows Event Log source
    Write-Host "Creating Windows Event Log source..." -ForegroundColor Yellow
    try {
        New-EventLog -LogName "Application" -Source "WatchLockAI" -ErrorAction SilentlyContinue
        Write-Host "[x] Event Log source created" -ForegroundColor Green
    } catch {
        Write-Warning "Event Log source may already exist or failed to create"
    }
    
    # Start the service
    Write-Host "Starting WatchLockAI service..." -ForegroundColor Yellow
    Start-Service -Name $serviceName
    
    # Wait for service to start
    $timeout = 30
    $timer = 0
    do {
        Start-Sleep -Seconds 1
        $timer++
        $service = Get-Service -Name $serviceName
    } while ($service.Status -ne "Running" -and $timer -lt $timeout)
    
    if ($service.Status -eq "Running") {
        Write-Host "[x] WatchLockAI service started successfully" -ForegroundColor Green
    } else {
        Write-Warning "Service start timeout - please check service status manually"
    }
    
    # Installation summary
    Write-Host "`n" + "="*60 -ForegroundColor Green
    Write-Host "WatchLockAI Agent Installation Complete!" -ForegroundColor Green
    Write-Host "="*60 -ForegroundColor Green
    Write-Host "Installation Path: $InstallPath" -ForegroundColor White
    Write-Host "Service Name: $serviceName" -ForegroundColor White
    Write-Host "Console Endpoint: $ConsoleEndpoint" -ForegroundColor White
    Write-Host "Service Status: $($service.Status)" -ForegroundColor White
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "1. Verify service is running: Get-Service WatchLockAI" -ForegroundColor White
    Write-Host "2. Check logs in: $logsDir" -ForegroundColor White
    Write-Host "3. Configure additional settings via console" -ForegroundColor White
    Write-Host "4. Monitor agent health in management console" -ForegroundColor White
    
} catch {
    Write-Error "Installation failed: $($_.Exception.Message)"
    Write-Host "Rolling back installation..." -ForegroundColor Yellow
    
    # Cleanup on failure
    try {
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        sc.exe delete $serviceName -ErrorAction SilentlyContinue
        Remove-Item -Path $InstallPath -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Warning "Cleanup may be incomplete - manual intervention required"
    }
    
    exit 1
}
