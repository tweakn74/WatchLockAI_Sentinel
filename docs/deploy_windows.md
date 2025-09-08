# Windows Deployment Guide (P5-006)

**Version:** 3.0 Release Candidate  
**Last Updated:** 2025-09-06  
**Target:** Windows 10/11, Windows Server 2019+  
**Scope:** Production deployment with P5 release candidate features

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Setup](#pre-installation-setup)
3. [Installation Methods](#installation-methods)
4. [Service Configuration](#service-configuration)
5. [Security Hardening](#security-hardening)
6. [Verification & Testing](#verification--testing)
7. [Offline Installation Method](#offline-installation-method)
8. [P5 Feature Configuration](#p5-feature-configuration)
9. [Post-Deployment Configuration](#post-deployment-configuration)
10. [Troubleshooting](#troubleshooting)
11. [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements
- **OS:** Windows 10 (1909+) or Windows Server 2019+
- **Python:** 3.8+ (3.10+ recommended for optimal performance)
- **Memory:** 4 GB RAM
- **Disk:** 10 GB free space
- **Network:** Outbound HTTPS (443) for threat intelligence
- **Privileges:** Administrator access for service installation

### Recommended Configuration
- **OS:** Windows 11 or Windows Server 2022
- **Python:** 3.11+
- **Memory:** 8 GB RAM
- **Disk:** 50 GB SSD storage
- **CPU:** 4+ cores
- **Network:** Gigabit Ethernet

### Software Dependencies

#### Required
- Python 3.8+ with pip
- PowerShell 5.1+ (included in Windows)
- Windows Service Control Manager

#### Optional (for enhanced features)
- scikit-learn (anomaly detection)
- FastAPI (web interface)
- psutil (system monitoring)

## Pre-Installation Setup

### 1. Python Installation

#### Download and Install Python

```powershell
# Download Python from python.org
# Or use Windows Package Manager
winget install Python.Python.3.11

# Verify installation
python --version
pip --version
```

#### Configure Python Environment

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install virtualenv (recommended)
pip install virtualenv

# Create virtual environment (optional but recommended)
virtualenv sentinel_env
.\sentinel_env\Scripts\Activate.ps1
```

### 2. Download and Extract Sentinel

```powershell
# Create installation directory
New-Item -ItemType Directory -Force -Path "C:\WatchLockAI_Sentinel"
Set-Location "C:\WatchLockAI_Sentinel"

# Extract source files (from provided archive)
# Expand-Archive -Path "WatchLockAI_Sentinel.zip" -DestinationPath "."

# Or clone from repository
# git clone https://github.com/watchlockai/sentinel.git .
```

### 3. Install Dependencies

```powershell
# Install required packages
pip install -r requirements.txt

# Install optional packages for full functionality
pip install -r requirements-optional.txt  # If available

# Or install specific optional packages
pip install fastapi uvicorn scikit-learn psutil
```

### 4. System Preparation

```powershell
# Create data directories
New-Item -ItemType Directory -Force -Path "data\auth"
New-Item -ItemType Directory -Force -Path "data\anomaly"
New-Item -ItemType Directory -Force -Path "data\quarantine"
New-Item -ItemType Directory -Force -Path "data\backups"
New-Item -ItemType Directory -Force -Path "logs"

# Set appropriate permissions
# (Allow service account read/write access to data and logs)
```

## Installation Methods

### Method 1: PowerShell Script Installation (Recommended)

#### Run Installation Script

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Run installation script
.\scripts\install_service.ps1 -ServiceName "WatchLockAI_Sentinel" -DisplayName "WatchLockAI Sentinel Security Platform" -Description "Advanced endpoint security monitoring and threat detection"
```

#### Installation Script Parameters

```powershell
# Full parameter list
.\scripts\install_service.ps1 `
    -ServiceName "WatchLockAI_Sentinel" `
    -DisplayName "WatchLockAI Sentinel Security Platform" `
    -Description "Advanced endpoint security monitoring and threat detection" `
    -ServiceAccount "LocalSystem" `
    -StartupType "Automatic" `
    -InstallPath "C:\WatchLockAI_Sentinel" `
    -LogPath "C:\WatchLockAI_Sentinel\logs" `
    -DataPath "C:\WatchLockAI_Sentinel\data"
```

#### Installation Script Features
- Automatic service registration
- Service account configuration
- File permission setup
- Registry configuration
- Firewall rule creation (optional)
- Event log source registration

### Method 2: Manual Service Installation

#### Create Service Wrapper Script

```powershell
# Copy service runner script
Copy-Item "scripts\sentinel_service_runner.ps1" "C:\WatchLockAI_Sentinel\sentinel_service.ps1"

# Edit script to set correct paths (if needed)
# notepad C:\WatchLockAI_Sentinel\sentinel_service.ps1
```

#### Register Windows Service

```powershell
# Create service using sc.exe
sc.exe create "WatchLockAI_Sentinel" `
    binPath= "powershell.exe -ExecutionPolicy Bypass -File C:\WatchLockAI_Sentinel\sentinel_service.ps1" `
    DisplayName= "WatchLockAI Sentinel Security Platform" `
    start= auto `
    depend= "Tcpip/Afd"

# Set service description
sc.exe description "WatchLockAI_Sentinel" "Advanced endpoint security monitoring and threat detection platform"

# Configure service recovery
sc.exe failure "WatchLockAI_Sentinel" reset= 86400 actions= restart/60000/restart/60000/restart/60000
```

#### Configure Service Account

```powershell
# Option 1: Use Local System (default)
# No additional configuration needed

# Option 2: Use Network Service
sc.exe config "WatchLockAI_Sentinel" obj= "NT AUTHORITY\NetworkService"

# Option 3: Use custom service account
# sc.exe config "WatchLockAI_Sentinel" obj= "DOMAIN\ServiceAccount" password= "password"
```

## Service Configuration

### Environment Variables

#### Core Configuration

```powershell
# Set environment variables for service
[Environment]::SetEnvironmentVariable("SENTINEL_HOME", "C:\WatchLockAI_Sentinel", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("SENTINEL_LOG_LEVEL", "INFO", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("SENTINEL_PORT", "8080", [EnvironmentVariableTarget]::Machine)
```

#### Security Configuration

```powershell
# Authentication settings
[Environment]::SetEnvironmentVariable("ADMIN_AUTH_ENABLED", "1", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("ADMIN_TOKEN", "$(New-Guid)", [EnvironmentVariableTarget]::Machine)

# Session settings
[Environment]::SetEnvironmentVariable("CONSOLE_AUTH_ENABLED", "1", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("CONSOLE_AUTH_SESSION_KEY", "$(-join ((1..64) | ForEach {'{0:X}' -f (Get-Random -Max 16)}))", [EnvironmentVariableTarget]::Machine)
```

#### Feature Flags

```powershell
# Enable core features
[Environment]::SetEnvironmentVariable("HEALTH_ENDPOINT_ENABLED", "1", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("RATE_LIMIT_ENABLED", "1", [EnvironmentVariableTarget]::Machine)

# Enable P4 features
[Environment]::SetEnvironmentVariable("BACKUP_ENABLED", "1", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("BACKUP_DIR", "C:\WatchLockAI_Sentinel\data\backups", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("LOG_REDACT_SECRETS", "1", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("CONSOLE_UI_ENABLED", "1", [EnvironmentVariableTarget]::Machine)
```

### Configuration Files

#### Create Main Configuration

```powershell
# Copy template configuration
if (Test-Path "config.yaml.template") {
    Copy-Item "config.yaml.template" "config.yaml"
} else {
    # Create basic configuration
    @"
service:
  name: WatchLockAI_Sentinel
  version: 2.0
  debug: false

api:
  host: 127.0.0.1
  port: 8080
  cors_enabled: false

logging:
  level: INFO
  file: logs/sentinel.log
  max_size: 10485760  # 10MB
  backup_count: 5

data:
  directory: data
  quarantine: data/quarantine
  anomaly: data/anomaly

security:
  admin_auth_required: true
  rate_limiting: true
  log_redaction: true
"@ | Out-File -FilePath "config.yaml" -Encoding UTF8
}

# Validate configuration
python tools\config_migrate.py --validate-file config.yaml
```

### Registry Configuration

#### Service Registry Settings

```powershell
# Create service-specific registry keys
$servicePath = "HKLM:\SYSTEM\CurrentControlSet\Services\WatchLockAI_Sentinel\Parameters"
New-Item -Path $servicePath -Force

# Set service parameters
Set-ItemProperty -Path $servicePath -Name "InstallPath" -Value "C:\WatchLockAI_Sentinel"
Set-ItemProperty -Path $servicePath -Name "DataPath" -Value "C:\WatchLockAI_Sentinel\data"
Set-ItemProperty -Path $servicePath -Name "LogPath" -Value "C:\WatchLockAI_Sentinel\logs"
Set-ItemProperty -Path $servicePath -Name "ConfigFile" -Value "C:\WatchLockAI_Sentinel\config.yaml"
```

## Security Hardening

### File System Permissions

#### Set Secure Permissions

```powershell
# Remove inherited permissions and set explicit permissions
icacls "C:\WatchLockAI_Sentinel" /inheritance:d

# Grant service account full control
icacls "C:\WatchLockAI_Sentinel" /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F"
icacls "C:\WatchLockAI_Sentinel" /grant "BUILTIN\Administrators:(OI)(CI)F"

# Grant read/execute to authenticated users (for web access if needed)
icacls "C:\WatchLockAI_Sentinel" /grant "NT AUTHORITY\Authenticated Users:(OI)(CI)RX"

# Secure sensitive directories
icacls "C:\WatchLockAI_Sentinel\data" /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F"
icacls "C:\WatchLockAI_Sentinel\logs" /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F"
```

#### Secure Configuration Files

```powershell
# Restrict access to configuration files
icacls "C:\WatchLockAI_Sentinel\config.yaml" /grant "NT AUTHORITY\SYSTEM:F"
icacls "C:\WatchLockAI_Sentinel\config.yaml" /grant "BUILTIN\Administrators:F"
icacls "C:\WatchLockAI_Sentinel\config.yaml" /remove "NT AUTHORITY\Authenticated Users"
```

### Firewall Configuration

#### Configure Windows Firewall

```powershell
# Create firewall rule for web interface (if needed)
New-NetFirewallRule -DisplayName "WatchLockAI Sentinel Web Interface" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8080 `
    -Action Allow `
    -Profile Domain,Private `
    -Description "Allow access to WatchLockAI Sentinel web interface"

# For production, consider restricting to specific IPs
# New-NetFirewallRule -DisplayName "WatchLockAI Sentinel Admin" `
#     -Direction Inbound `
#     -Protocol TCP `
#     -LocalPort 8080 `
#     -Action Allow `
#     -RemoteAddress "192.168.1.0/24" `
#     -Profile Domain,Private
```

### User Account Control (UAC)

#### Service Account Best Practices

```powershell
# Create dedicated service account (recommended for production)
$password = ConvertTo-SecureString "$(New-Guid)$(New-Guid)" -AsPlainText -Force
New-LocalUser -Name "SentinelService" `
    -Password $password `
    -Description "WatchLockAI Sentinel Service Account" `
    -UserMayNotChangePassword `
    -PasswordNeverExpires

# Grant "Log on as a service" right
# (This requires additional tooling or Group Policy)

# Configure service to use dedicated account
sc.exe config "WatchLockAI_Sentinel" obj= ".\SentinelService" password= "password"
```

### Audit and Logging

#### Enable Security Auditing

```powershell
# Enable file access auditing (optional)
auditpol /set /subcategory:"File System" /success:enable /failure:enable

# Configure audit for Sentinel directories
$auditRule = New-Object System.Security.AccessControl.FileSystemAuditRule(
    "Everyone", 
    "FullControl", 
    "ContainerInherit,ObjectInherit", 
    "None", 
    "Success,Failure"
)

$acl = Get-Acl "C:\WatchLockAI_Sentinel"
$acl.SetAuditRule($auditRule)
Set-Acl "C:\WatchLockAI_Sentinel" $acl
```

## Verification & Testing

### Pre-Flight Checks

```powershell
# Run comprehensive pre-flight validation
python console\preflight_checks.py --verbose

# Check configuration
python tools\config_migrate.py --validate-file config.yaml

# Security scan
python tools\sec_lint.py --fail-on-high

# Self-check (without starting service)
python tools\self_check.py --verbose
```

### Service Testing

#### Start and Test Service

```powershell
# Start the service
Start-Service -Name "WatchLockAI_Sentinel"

# Check service status
Get-Service -Name "WatchLockAI_Sentinel" | Format-List

# Verify service is listening
Test-NetConnection -ComputerName localhost -Port 8080

# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:8080/api/metrics/health"
```

#### Functional Testing

```powershell
# Test admin authentication
$headers = @{ "X-Admin-Token" = $env:ADMIN_TOKEN }
Invoke-RestMethod -Uri "http://localhost:8080/api/admin/config/reload" -Method POST -Headers $headers

# Test backup functionality
$backupResult = Invoke-RestMethod -Uri "http://localhost:8080/api/admin/backup" -Method POST -Headers $headers
Write-Output "Backup created: $($backupResult.path)"

# Test console UI (if enabled)
Start-Process "http://localhost:8080/console/"
```

### Performance Testing

```powershell
# Monitor resource usage
Get-Counter "\Process(python)\% Processor Time", "\Process(python)\Working Set"

# Test API performance
Measure-Command { Invoke-RestMethod -Uri "http://localhost:8080/api/metrics/health" }

# Load testing (basic)
1..100 | ForEach-Object -Parallel {
    Invoke-RestMethod -Uri "http://localhost:8080/api/metrics/health"
} -ThrottleLimit 10
```

### Security Testing

```powershell
# Test authentication bypass (should fail)
try {
    Invoke-RestMethod -Uri "http://localhost:8080/api/admin/config/reload" -Method POST
    Write-Error "Authentication bypass vulnerability!"
} catch {
    Write-Output "Authentication working correctly: $($_.Exception.Message)"
}

# Test rate limiting (if enabled)
# [Perform rapid requests to test rate limiting]

# Test with wrong credentials (should fail)
try {
    $badHeaders = @{ "X-Admin-Token" = "wrong-token" }
    Invoke-RestMethod -Uri "http://localhost:8080/api/admin/config/reload" -Method POST -Headers $badHeaders
    Write-Error "Authorization bypass vulnerability!"
} catch {
    Write-Output "Authorization working correctly: $($_.Exception.Message)"
}
```

## Offline Installation Method

### P5-004: Air-Gapped/Offline Installation

For environments without internet access, use the offline installation bundle.

#### Prerequisites for Offline Installation

- Offline bundle file: `WatchLockAI_Sentinel_Offline.zip`
- Windows 10/11 or Windows Server 2016+
- PowerShell 5.1+ 
- Administrator privileges
- No internet connection required

#### Step 1: Create Offline Bundle (On Connected System)

```powershell
# On a system with internet access
cd C:\WatchLockAI_Sentinel
.\scripts\make_offline_bundle.ps1 -OutputPath "WatchLockAI_Sentinel_Offline.zip" -Verbose

# Transfer the bundle to target system via approved media
```

#### Step 2: Deploy Offline Bundle

```powershell
# On the target (offline) system
# 1. Transfer bundle via USB, CD, or approved network transfer

# 2. Extract bundle
Expand-Archive -Path "WatchLockAI_Sentinel_Offline.zip" -DestinationPath "C:\WatchLockAI_Offline"

# 3. Navigate to bundle directory
cd C:\WatchLockAI_Offline

# 4. Run bootstrap installation
.\bootstrap_venv.ps1 -InstallService -Verbose
```

#### Step 3: Bootstrap Options

```powershell
# Basic installation (no service)
.\bootstrap_venv.ps1

# Install with Windows service
.\bootstrap_venv.ps1 -InstallService

# Skip test suite (faster installation)
.\bootstrap_venv.ps1 -SkipTests -InstallService

# All options combined
.\bootstrap_venv.ps1 -SkipTests -InstallService -Verbose
```

#### Step 4: Post-Bootstrap Configuration

```powershell
# Navigate to source directory
cd source

# Edit configuration
notepad .env

# Verify installation
python tools\verify_minimax_claims.py

# Run self-check
python tools\self_check.py --verbose

# Start service (if not done by bootstrap)
Start-Service -Name "WatchLockAI_Sentinel"
```

### Offline Bundle Contents

- **Pre-configured Virtual Environment:** Python + all dependencies
- **Complete Source Code:** All application files
- **Configuration Templates:** Ready-to-use configuration examples
- **Bootstrap Scripts:** Automated installation and validation
- **Documentation:** Complete offline documentation set

### Offline Installation Validation

```powershell
# Verify bundle integrity
cd C:\WatchLockAI_Offline\source
python -c "import app_core.bus; print('✓ Core modules available')"
python -c "import console.web_api; print('✓ Web API available')"

# Check virtual environment
cd ..\venv\Scripts
.\python.exe --version
.\pip.exe list

# Validate service installation
Get-Service -Name "WatchLockAI_Sentinel" | Format-List
```

## P5 Feature Configuration

### P5-001: Version Management

```powershell
# Check installed version
Get-Content "VERSION"

# View changelog
Get-Content "CHANGELOG.md" | Select-Object -First 50

# View release notes
Get-Content "RELEASE_NOTES_v0.8.md" | Select-Object -First 30
```

### P5-002: Data Retention Configuration

```powershell
# Enable data retention features
[Environment]::SetEnvironmentVariable("RETENTION_ENABLED", "1", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("RETENTION_DAYS", "14", [EnvironmentVariableTarget]::Machine)

# Create scheduled retention task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command `"Invoke-RestMethod -Uri 'http://localhost:8080/api/admin/retention/run?dry=false' -Method POST -Headers @{'X-Admin-Token'='$env:ADMIN_TOKEN'}`""
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"
$principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "WatchLockAI_Retention" -Action $action -Trigger $trigger -Principal $principal -Description "Daily data retention cleanup"
```

### P5-005: Performance Monitoring

```powershell
# Enable performance testing
[Environment]::SetEnvironmentVariable("PERF_PROBE_ENABLED", "1", [EnvironmentVariableTarget]::Machine)

# Test performance probe
curl -X POST -H "X-Admin-Token: $env:ADMIN_TOKEN" "http://localhost:8080/api/admin/perf/quick"

# Scheduled performance monitoring
$perfAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command `"Invoke-RestMethod -Uri 'http://localhost:8080/api/admin/perf/quick' -Headers @{'X-Admin-Token'='$env:ADMIN_TOKEN'} | Out-File -Append 'logs\performance_weekly.log'`""
$perfTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "06:00AM"
Register-ScheduledTask -TaskName "WatchLockAI_PerfMonitor" -Action $perfAction -Trigger $perfTrigger -Description "Weekly performance monitoring"
```

### P5 Environment Variables Reference

```powershell
# P5 Release Candidate Features
[Environment]::SetEnvironmentVariable("RETENTION_ENABLED", "0", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("RETENTION_DAYS", "14", [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("PERF_PROBE_ENABLED", "0", [EnvironmentVariableTarget]::Machine)

# Configuration templates location
# DOCS\config\.env.example - Environment variable template
# DOCS\config\config.example.json - JSON configuration template
```

### P5 API Endpoints

#### Data Retention Endpoints
- `POST /api/admin/retention/run` - Execute retention cleanup
- `GET /api/admin/retention/stats` - Get retention statistics

#### Performance Testing Endpoints  
- `POST /api/admin/perf/probe` - Run performance test
- `GET /api/admin/perf/quick` - Quick performance check

### P5 Security Considerations

```powershell
# Verify P5 security enhancements
# Session cookie security validation
# SSE stream authentication checks  
# Export file integrity verification
# Enhanced API contract validation

# Run enhanced security verifier
python tools\verify_minimax_claims.py
```

## Post-Deployment Configuration

### Monitoring Setup

#### Windows Event Log

```powershell
# Create custom event log source (optional)
New-EventLog -LogName "Application" -Source "WatchLockAI_Sentinel"

# View Sentinel events
Get-WinEvent -LogName Application | Where-Object {$_.ProviderName -eq "WatchLockAI_Sentinel"}
```

#### Performance Counters

```powershell
# Monitor key performance counters
$counters = @(
    "\Process(python)\% Processor Time",
    "\Process(python)\Working Set",
    "\Process(python)\IO Read Bytes/sec",
    "\Process(python)\IO Write Bytes/sec"
)

Get-Counter -Counter $counters -SampleInterval 5 -MaxSamples 12
```

### Scheduled Tasks

#### Automated Maintenance

```powershell
# Create daily health check task
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\WatchLockAI_Sentinel\tools\self_check.py"
$trigger = New-ScheduledTaskTrigger -Daily -At "03:00AM"
$settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -WakeToRun

Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings `
    -TaskName "WatchLockAI Sentinel Health Check" `
    -Description "Daily health check for WatchLockAI Sentinel service"

# Create weekly backup task
$backupAction = New-ScheduledTaskAction -Execute "python" -Argument "C:\WatchLockAI_Sentinel\tools\backup_service.py --auto"
$backupTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "02:00AM"

Register-ScheduledTask -Action $backupAction -Trigger $backupTrigger -Settings $settings `
    -TaskName "WatchLockAI Sentinel Weekly Backup" `
    -Description "Weekly automated backup of WatchLockAI Sentinel"
```

### Integration with SIEM

#### Windows Event Forwarding

```powershell
# Configure event forwarding (to SIEM)
# Create custom XML query for Sentinel events
$eventQuery = @"
<QueryList>
  <Query Id="0" Path="Application">
    <Select Path="Application">*[System[Provider[@Name='WatchLockAI_Sentinel']]]</Select>
  </Query>
</QueryList>
"@

# Configure subscription (on SIEM collector)
# wecutil cs subscription.xml
```

### SSL/TLS Configuration (Production)

```powershell
# For production deployments, configure HTTPS
# This typically involves:
# 1. Obtaining SSL certificate
# 2. Configuring reverse proxy (IIS, nginx)
# 3. Updating firewall rules
# 4. Testing SSL configuration

# Example IIS reverse proxy configuration
# (Requires IIS with Application Request Routing)
```

## Troubleshooting

### Common Installation Issues

#### Service Fails to Install

**Symptoms:** Installation script errors, service not created

**Solutions:**
```powershell
# Check PowerShell execution policy
Get-ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify administrator privileges
([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

# Check Windows Event Log for service creation errors
Get-WinEvent -LogName System | Where-Object {$_.Id -eq 7034 -or $_.Id -eq 7000}
```

#### Python Path Issues

**Symptoms:** "Python not found" errors, import failures

**Solutions:**
```powershell
# Verify Python installation
python --version
where python

# Check PATH environment variable
$env:PATH -split ';' | Where-Object {$_ -like '*Python*'}

# Reinstall Python with "Add to PATH" option
winget install Python.Python.3.11 --override '/quiet PrependPath=1'
```

#### Permission Errors

**Symptoms:** Access denied errors, file permission issues

**Solutions:**
```powershell
# Check service account permissions
icacls "C:\WatchLockAI_Sentinel" /t

# Reset permissions to defaults
.\scripts\fix_permissions.ps1  # If available

# Run as administrator
Start-Process powershell -Verb RunAs
```

### Service Runtime Issues

#### Service Starts but Stops Immediately

**Diagnosis:**
```powershell
# Check application logs
Get-Content "C:\WatchLockAI_Sentinel\logs\sentinel.log" -Tail 50

# Check Windows Event Log
Get-WinEvent -LogName Application -MaxEvents 20 | Where-Object {$_.ProviderName -eq "WatchLockAI_Sentinel"}

# Test manual startup
cd "C:\WatchLockAI_Sentinel"
python app.py
```

#### Network Binding Issues

**Diagnosis:**
```powershell
# Check if port is in use
netstat -an | findstr :8080

# Test port accessibility
Test-NetConnection -ComputerName localhost -Port 8080

# Check firewall rules
Get-NetFirewallRule -DisplayName "*Sentinel*"
```

### Performance Issues

#### High CPU Usage

```powershell
# Monitor CPU usage by component
Get-Counter "\Process(python)\% Processor Time" -Continuous

# Check for infinite loops in logs
Select-String -Path "C:\WatchLockAI_Sentinel\logs\sentinel.log" -Pattern "error|exception|loop"

# Restart service
Restart-Service -Name "WatchLockAI_Sentinel"
```

#### Memory Leaks

```powershell
# Monitor memory usage over time
Get-Counter "\Process(python)\Working Set" -SampleInterval 60 -MaxSamples 60

# Check for memory allocation patterns
Select-String -Path "C:\WatchLockAI_Sentinel\logs\sentinel.log" -Pattern "memory|heap|allocation"
```

### Recovery Procedures

#### Complete Service Recovery

```powershell
# 1. Stop service
Stop-Service -Name "WatchLockAI_Sentinel" -Force

# 2. Backup current state
Copy-Item -Recurse "C:\WatchLockAI_Sentinel\data" "C:\WatchLockAI_Sentinel\data_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# 3. Clear temporary files
Remove-Item "C:\WatchLockAI_Sentinel\data\temp\*" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item "C:\WatchLockAI_Sentinel\logs\*.log.*" -Force -ErrorAction SilentlyContinue

# 4. Reset configuration (if needed)
Copy-Item "C:\WatchLockAI_Sentinel\config.yaml.template" "C:\WatchLockAI_Sentinel\config.yaml" -Force

# 5. Restart service
Start-Service -Name "WatchLockAI_Sentinel"

# 6. Verify recovery
python "C:\WatchLockAI_Sentinel\tools\self_check.py" --verbose
```

## Uninstallation

### Automated Uninstallation

```powershell
# Run uninstallation script
.\scripts\uninstall_service.ps1 -ServiceName "WatchLockAI_Sentinel" -RemoveData $false

# For complete removal including data
.\scripts\uninstall_service.ps1 -ServiceName "WatchLockAI_Sentinel" -RemoveData $true
```

### Manual Uninstallation

#### Stop and Remove Service

```powershell
# Stop service
Stop-Service -Name "WatchLockAI_Sentinel" -Force

# Remove service
sc.exe delete "WatchLockAI_Sentinel"

# Verify removal
Get-Service -Name "WatchLockAI_Sentinel" -ErrorAction SilentlyContinue
```

#### Remove Files and Configuration

```powershell
# Remove application files
Remove-Item "C:\WatchLockAI_Sentinel" -Recurse -Force

# Remove registry entries
Remove-Item "HKLM:\SYSTEM\CurrentControlSet\Services\WatchLockAI_Sentinel" -Recurse -Force -ErrorAction SilentlyContinue

# Remove environment variables
[Environment]::SetEnvironmentVariable("SENTINEL_HOME", $null, [EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("ADMIN_TOKEN", $null, [EnvironmentVariableTarget]::Machine)
# ... (remove other Sentinel-related environment variables)

# Remove firewall rules
Remove-NetFirewallRule -DisplayName "WatchLockAI Sentinel*" -ErrorAction SilentlyContinue

# Remove scheduled tasks
Unregister-ScheduledTask -TaskName "WatchLockAI Sentinel*" -Confirm:$false -ErrorAction SilentlyContinue

# Remove event log source
Remove-EventLog -Source "WatchLockAI_Sentinel" -ErrorAction SilentlyContinue
```

### Post-Uninstallation Verification

```powershell
# Verify service removal
Get-Service -Name "*Sentinel*"

# Check for remaining files
Get-ChildItem "C:\" -Recurse -Name "*WatchLockAI*" -ErrorAction SilentlyContinue

# Check registry
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services" | Where-Object {$_.Name -like "*Sentinel*"}

# Check scheduled tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Sentinel*"}

# Check firewall rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Sentinel*"}
```

---

## Support and Resources

### Documentation
- **Operations Runbook:** `DOCS/operations_runbook.md`
- **Configuration Guide:** `DOCS/config/keys.md`
- **Security Model:** `DOCS/security/threat_model.md`
- **API Documentation:** Access via `/api/docs` when service is running

### Logging and Diagnostics
- **Application Logs:** `C:\WatchLockAI_Sentinel\logs\sentinel.log`
- **Windows Event Log:** Application log, source "WatchLockAI_Sentinel"
- **Self-Check Tool:** `python tools\self_check.py --verbose`
- **Security Scan:** `python tools\sec_lint.py`

### Contact Information
- **Technical Support:** support@watchlockai.com
- **Security Issues:** security@watchlockai.com
- **Documentation:** docs@watchlockai.com

### Version Information
- **Guide Version:** 2.0 (P4 Enhanced)
- **Target Software:** WatchLockAI Sentinel v2.0+
- **Last Updated:** 2025-09-05
- **Compatibility:** Windows 10/11, Server 2019+

---

**Document Classification:** Internal Use  
**Approval:** Technical Lead, Security Team  
**Review Schedule:** Quarterly or with major releases
