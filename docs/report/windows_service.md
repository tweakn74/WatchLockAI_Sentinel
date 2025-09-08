# Windows Service Installation Guide - WatchLockAI Sentinel

**Version:** 1.0.0  
**Component:** P3-003 Windows Service Packaging  
**Generated:** 2025-09-04  

## Overview

WatchLockAI Sentinel can be installed and run as a Windows service for production deployments. This provides several advantages:

- **Automatic startup** on system boot
- **Service recovery** options for high availability
- **System integration** with Windows Event Log
- **Background operation** without user login required
- **Centralized management** via Windows Service Manager

## Prerequisites

### System Requirements

- **Windows 10/11** or **Windows Server 2016+**
- **PowerShell 5.1** or later
- **Python 3.8+** installed and available in system PATH
- **Administrator privileges** for service installation

### Application Requirements

- WatchLockAI Sentinel application files properly deployed
- Required Python dependencies installed
- Configuration files prepared (optional)

## Installation Process

### Step 1: Prepare Configuration (Optional)

Create a configuration file with your desired settings:

```env
# Service Configuration
SERVICE_ENABLED=1
HEALTH_ENDPOINT_ENABLED=1

# Security Settings
ADMIN_AUTH_ENABLED=1
ADMIN_TOKEN=your_secure_admin_token_here
RATE_LIMIT_ENABLED=1

# Web Console (if needed)
CONSOLE_AUTH_ENABLED=1
CONSOLE_AUTH_SESSION_KEY=64_character_hex_string_here

# Logging Settings
LOG_MAX_BYTES=2097152
LOG_BACKUPS=10
LOG_REDACT_SECRETS=1

# Disable debug features for service mode
METRICS_DEBUG_ENABLED=0
CONFIG_HOT_RELOAD_ENABLED=0
```

Save this as `C:\Config\sentinel.env` or similar location.

### Step 2: Install Service

Open PowerShell as Administrator and navigate to the Sentinel application directory:

```powershell
# Basic installation
.\scripts\install_service.ps1

# Install with custom configuration
.\scripts\install_service.ps1 -ConfigFile "C:\Config\sentinel.env"

# Install with custom service settings
.\scripts\install_service.ps1 -DisplayName "My Sentinel Monitor" -StartType Manual

# Test installation (dry run)
.\scripts\install_service.ps1 -DryRun
```

### Step 3: Verify Installation

```powershell
# Check service status
Get-Service -Name WatchLockAISentinel

# View service details
Get-WmiObject -Class Win32_Service -Filter "Name='WatchLockAISentinel'"

# Test service startup
Start-Service -Name WatchLockAISentinel
```

## Service Management

### Start/Stop Service

```powershell
# Start service
Start-Service -Name WatchLockAISentinel

# Stop service
Stop-Service -Name WatchLockAISentinel

# Restart service
Restart-Service -Name WatchLockAISentinel
```

### Check Service Status

```powershell
# Get service status
Get-Service -Name WatchLockAISentinel | Format-List

# View running processes
Get-Process -Name python | Where-Object {$_.CommandLine -like "*app.py*"}
```

### Service Configuration

```powershell
# Change startup type
Set-Service -Name WatchLockAISentinel -StartupType Automatic

# Set service to delayed start (after other services)
Set-Service -Name WatchLockAISentinel -StartupType Automatic
sc.exe config WatchLockAISentinel start= delayed-auto

# Configure service recovery
sc.exe failure WatchLockAISentinel reset= 86400 actions= restart/30000/restart/60000/restart/60000
```

## Service Architecture

### Service Components

1. **Service Runner** (`sentinel_service_runner.ps1`)
   - Main service executable
   - Handles environment setup
   - Manages Python process lifecycle
   - Provides graceful shutdown

2. **Service Installer** (`install_service.ps1`)
   - Automated service installation
   - Configuration validation
   - Service testing and verification

3. **Service Uninstaller** (`uninstall_service.ps1`)
   - Clean service removal
   - Optional cleanup of logs/config
   - Verification of complete removal

### Service Execution Flow

```
Windows Service Manager
    ↓
PowerShell Service Runner
    ↓ 
Environment Configuration
    ↓
Python Application (app.py)
    ↓
WatchLockAI Sentinel Components
```

### Service Logging

The service creates multiple log files:

- **Service Logs**: `logs/service.log` - Service runner operations
- **Application Logs**: `logs/sentinel.log` - Main application logs
- **Install Logs**: `logs/install.log` - Installation process logs
- **Audit Logs**: `logs/audit.log` - Security and access logs

All logs use rotation and redaction as configured.

## Configuration Options

### Service-Specific Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `SERVICE_ENABLED` | Enable service mode optimizations | `0` (OFF) |
| `LOG_MAX_BYTES` | Service log file size limit | `2097152` (2MB) |
| `LOG_BACKUPS` | Number of rotated log files | `10` |
| `ADMIN_AUTH_ENABLED` | Enable admin API authentication | `1` (ON) |
| `RATE_LIMIT_ENABLED` | Enable API rate limiting | `1` (ON) |

### Service Optimization

When `SERVICE_ENABLED=1`, the service runner automatically:

- Sets appropriate logging levels for service operation
- Enables security features (admin auth, rate limiting)
- Disables debug features and hot reload
- Configures larger log rotation settings
- Optimizes for background operation

### Service Account Configuration

The service runs under **LocalSystem** by default. To use a different account:

```powershell
# Install with specific service account
.\scripts\install_service.ps1 -ServiceAccount "LocalService"

# Change service account after installation
sc.exe config WatchLockAISentinel obj= "NT AUTHORITY\LocalService"
```

**Service Account Options:**

- **LocalSystem**: Full system privileges (default)
- **LocalService**: Limited privileges, no network access
- **NetworkService**: Limited privileges with network access
- **Custom Domain Account**: For enterprise environments

## Troubleshooting

### Common Issues

**Service fails to start:**

1. Check service logs: `Get-Content logs\service.log -Tail 50`
2. Verify Python is in system PATH: `python --version`
3. Test manual execution: `.\scripts\sentinel_service_runner.ps1 run -DryRun`

**Permission errors:**

1. Verify service account has appropriate permissions
2. Check file/directory permissions in application folder
3. Review Windows Event Log for additional details

**Application crashes:**

1. Check application logs: `Get-Content logs\sentinel.log -Tail 50`
2. Verify all required environment variables are set
3. Test application in non-service mode first

### Debug Commands

```powershell
# Test service runner manually
.\scripts\sentinel_service_runner.ps1 run -DryRun

# View service configuration
sc.exe qc WatchLockAISentinel

# Check service dependencies
sc.exe enumdepend WatchLockAISentinel

# View Windows Event Log
Get-EventLog -LogName Application -Source "WatchLockAISentinel" -Newest 10
```

### Recovery Options

**Service hangs or becomes unresponsive:**

```powershell
# Force stop service
Stop-Service -Name WatchLockAISentinel -Force

# Kill related processes
Get-Process -Name python | Where-Object {$_.CommandLine -like "*app.py*"} | Stop-Process -Force

# Restart service
Start-Service -Name WatchLockAISentinel
```

**Reinstall service:**

```powershell
# Uninstall existing service
.\scripts\uninstall_service.ps1 -Force

# Reinstall with current settings
.\scripts\install_service.ps1 -Force
```

## Uninstallation

### Standard Uninstall

```powershell
# Basic uninstall (preserves logs and config)
.\scripts\uninstall_service.ps1

# Complete removal
.\scripts\uninstall_service.ps1 -CleanLogs -CleanConfig

# Force uninstall running service
.\scripts\uninstall_service.ps1 -Force
```

### Manual Cleanup (if needed)

```powershell
# Remove service registration
sc.exe delete WatchLockAISentinel

# Clean up service logs
Remove-Item "logs\*" -Force -Recurse

# Remove from Windows Event Log
# (Entries will age out automatically)
```

## Security Considerations

### Service Account Security

- Use least-privilege service accounts when possible
- Avoid running as LocalSystem in high-security environments
- Consider using Managed Service Accounts (MSAs) in domain environments

### File System Security

```powershell
# Set restrictive permissions on service directory
icacls "C:\WatchLockAI" /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F" /grant "Administrators:(OI)(CI)F" /remove "Users" /T

# Secure log files
icacls "C:\WatchLockAI\logs" /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F" /grant "Administrators:(OI)(CI)R" /T

# Protect configuration files
icacls "C:\Config\sentinel.env" /grant "NT AUTHORITY\SYSTEM:F" /grant "Administrators:F" /remove "Users"
```

### Network Security

- Configure Windows Firewall rules for required ports
- Use HTTPS for web console access
- Implement proper authentication tokens

## Performance Tuning

### Service Optimization

```env
# Optimized service configuration
LOG_MAX_BYTES=5242880       # 5MB logs for better performance
LOG_BACKUPS=20              # More history for services
STREAM_ENABLED=0            # Disable streaming if not needed
PLUGINS_ENABLED=0           # Disable plugins if not used
```

### Resource Monitoring

```powershell
# Monitor service resource usage
Get-Process -Name python | Where-Object {$_.CommandLine -like "*app.py*"} | Format-Table Name,CPU,WorkingSet

# Check service uptime
Get-Service -Name WatchLockAISentinel | Select-Object Name,Status,StartType

# Monitor log file growth
Get-ChildItem logs\*.log | Select-Object Name,Length,LastWriteTime
```

## Integration Examples

### Event Log Integration

The service integrates with Windows Event Log for centralized monitoring:

```powershell
# View service-related events
Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='WatchLockAISentinel'}

# Set up event forwarding (if using WEF)
wecutil cs sentinel-subscription.xml
```

### Monitoring Integration

```powershell
# SCOM/SCCM monitoring
# Monitor service status via WMI
Get-WmiObject -Class Win32_Service -Filter "Name='WatchLockAISentinel'" | Select-Object State,Status

# Nagios/Icinga monitoring via PowerShell
$service = Get-Service -Name WatchLockAISentinel -ErrorAction SilentlyContinue
if ($service -and $service.Status -eq 'Running') { 
    Write-Host "OK - Service is running" 
    exit 0 
} else { 
    Write-Host "CRITICAL - Service not running" 
    exit 2 
}
```

## Best Practices

### Production Deployment

1. **Use configuration files** instead of environment variables
2. **Enable all security features** (admin auth, rate limiting)
3. **Configure service recovery** options
4. **Set up log monitoring** and rotation
5. **Test service startup** and shutdown procedures
6. **Document custom configurations** for your environment

### Maintenance

1. **Regular log review** for security events
2. **Monitor service resource usage**
3. **Keep Python runtime updated**
4. **Backup configuration files**
5. **Test service recovery procedures**

### Change Management

1. **Test changes in non-production first**
2. **Use configuration files for settings changes**
3. **Document all customizations**
4. **Plan service restart windows**
5. **Verify operation after changes**
