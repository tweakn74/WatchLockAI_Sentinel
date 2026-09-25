#!/usr/bin/env python3
"""
Create Windows installer and configuration files for WatchLockAI Agent
"""

import os
from pathlib import Path

def create_installer_scripts(base_path):
    """Create Windows installer scripts and configuration"""
    
    # PowerShell installation script
    install_script = """# WatchLockAI Agent Installation Script
# Requires Administrator privileges

param(
    [Parameter(Mandatory=$false)]
    [string]$ConsoleEndpoint = "https://console.watchlockai.com",
    
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "$env:ProgramFiles\\WatchLockAI"
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
"""
    
    with open(base_path / "installer/Scripts/Install-WatchLockAI.ps1", "w") as f:
        f.write(install_script)
    
    # Uninstall script
    uninstall_script = """# WatchLockAI Agent Uninstallation Script
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
$installPath = "$env:ProgramFiles\\WatchLockAI"

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
        Remove-Item -Path "HKLM:\\SOFTWARE\\WatchLockAI" -Recurse -Force -ErrorAction SilentlyContinue
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
"""
    
    with open(base_path / "installer/Scripts/Uninstall-WatchLockAI.ps1", "w") as f:
        f.write(uninstall_script)
    
    # Batch installer wrapper
    batch_installer = """@echo off
REM WatchLockAI Agent Installer Wrapper
REM This script launches the PowerShell installer with appropriate parameters

echo WatchLockAI Agent Installer
echo ===========================

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer must be run as Administrator.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Set default console endpoint if not provided
if "%1"=="" (
    set CONSOLE_ENDPOINT=https://console.watchlockai.com
) else (
    set CONSOLE_ENDPOINT=%1
)

echo Installing WatchLockAI Agent...
echo Console Endpoint: %CONSOLE_ENDPOINT%
echo.

REM Launch PowerShell installer
powershell.exe -ExecutionPolicy Bypass -File "%~dp0Install-WatchLockAI.ps1" -ConsoleEndpoint "%CONSOLE_ENDPOINT%"

if %errorLevel% equ 0 (
    echo.
    echo Installation completed successfully!
    echo WatchLockAI Agent is now protecting this system.
) else (
    echo.
    echo Installation failed. Please check the error messages above.
)

pause
"""
    
    with open(base_path / "installer/Scripts/install.bat", "w") as f:
        f.write(batch_installer)
    
    print("Created installer scripts")

def create_configuration_files(base_path):
    """Create configuration files and templates"""
    
    # Main application configuration
    app_config = """{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "Microsoft.Hosting.Lifetime": "Information"
    },
    "EventLog": {
      "LogLevel": {
        "Default": "Warning"
      },
      "SourceName": "WatchLockAI"
    },
    "File": {
      "Path": "Logs/watchlockai-.log",
      "RollingInterval": "Day",
      "RetainedFileCountLimit": 30,
      "FileSizeLimitBytes": 10485760
    }
  },
  "WatchLockAI": {
    "ServiceName": "WatchLockAI",
    "ServiceDisplayName": "WatchLockAI Endpoint Security",
    "ServiceDescription": "Autonomous AI-powered cybersecurity endpoint agent",
    "AgentId": null,
    "ConsoleEndpoint": "https://console.watchlockai.com",
    "HeartbeatInterval": 60,
    "UpdateInterval": 3600,
    "ConfigurationRefreshInterval": 300,
    "MemoryLimit": 512,
    "MaxConcurrentInvestigations": 5,
    "ThreatDetection": {
      "Enabled": true,
      "ScanInterval": 30,
      "EnableMitreMapping": true,
      "EnableBehavioralAnalysis": true,
      "AnomalyThreshold": 0.7,
      "EnableFilelessDetection": true,
      "EnablePowerShellMonitoring": true,
      "EnableRegistryMonitoring": true,
      "EnableNetworkMonitoring": true
    },
    "Response": {
      "AutoResponseEnabled": false,
      "RequireApproval": true,
      "MaxAutoResponseSeverity": "Medium",
      "EnableProcessQuarantine": true,
      "EnableNetworkBlocking": true,
      "EnableAccountIsolation": false,
      "ResponseTimeout": 300
    },
    "BehavioralLearning": {
      "Enabled": true,
      "LearningPeriod": 7,
      "BaselineUpdateInterval": 24,
      "EnableUserBaselines": true,
      "EnableProcessBaselines": true,
      "EnableNetworkBaselines": true
    },
    "Forensics": {
      "Enabled": true,
      "AutoInvestigate": true,
      "RetainEvidenceDays": 90,
      "MaxEvidenceSize": 1073741824,
      "EnableMemoryCapture": false,
      "EnableRegistrySnapshots": true,
      "EnableFileSystemMonitoring": true,
      "EnableEventLogCollection": true
    },
    "Tamperproof": {
      "Enabled": true,
      "IntegrityCheckInterval": 300,
      "WatchdogInterval": 60,
      "EnableAntiDebugging": true,
      "EnableProcessMonitoring": true,
      "EnableRegistryProtection": true,
      "BlockUninstallAttempts": true
    },
    "Integration": {
      "EnableDefender": true,
      "EnableAzure": false,
      "EnableSiem": false,
      "DefenderExclusions": [
        "%ProgramFiles%\\WatchLockAI"
      ]
    },
    "Performance": {
      "MaxCpuUsage": 15,
      "MaxMemoryUsage": 512,
      "EnablePerformanceMonitoring": true,
      "ThrottleOnHighUsage": true
    }
  }
}"""
    
    with open(base_path / "configs/appsettings.json", "w") as f:
        f.write(app_config)
    
    # Production configuration overlay
    prod_config = """{
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "WatchLockAI": "Information"
    }
  },
  "WatchLockAI": {
    "ThreatDetection": {
      "ScanInterval": 15
    },
    "Response": {
      "AutoResponseEnabled": true,
      "RequireApproval": false,
      "MaxAutoResponseSeverity": "High"
    },
    "Tamperproof": {
      "IntegrityCheckInterval": 180,
      "WatchdogInterval": 30
    },
    "Performance": {
      "MaxCpuUsage": 10,
      "MaxMemoryUsage": 384
    }
  }
}"""
    
    with open(base_path / "configs/appsettings.Production.json", "w") as f:
        f.write(prod_config)
    
    # Development configuration
    dev_config = """{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft": "Information"
    }
  },
  "WatchLockAI": {
    "ConsoleEndpoint": "https://console-dev.watchlockai.com",
    "ThreatDetection": {
      "ScanInterval": 60,
      "AnomalyThreshold": 0.5
    },
    "Response": {
      "AutoResponseEnabled": false,
      "RequireApproval": true
    },
    "Tamperproof": {
      "Enabled": false
    }
  }
}"""
    
    with open(base_path / "configs/appsettings.Development.json", "w") as f:
        f.write(dev_config)
    
    # MITRE ATT&CK configuration
    mitre_config = """{
  "MitreAttackMatrix": {
    "Version": "v13.1",
    "LastUpdated": "2025-01-01T00:00:00Z",
    "Techniques": {
      "T1059.001": {
        "Name": "PowerShell",
        "Tactic": "Execution",
        "Description": "Adversaries may abuse PowerShell commands and scripts for execution",
        "DetectionPatterns": [
          "powershell",
          "-encodedcommand",
          "-noprofile",
          "-windowstyle hidden",
          "invoke-expression",
          "downloadstring"
        ],
        "Severity": "Medium",
        "Enabled": true
      },
      "T1218.011": {
        "Name": "Rundll32",
        "Tactic": "Defense Evasion",
        "Description": "Adversaries may abuse rundll32.exe to proxy execution of malicious code",
        "DetectionPatterns": [
          "rundll32.exe",
          "javascript:",
          "vbscript:",
          "shell32.dll",
          "advpack.dll"
        ],
        "Severity": "High",
        "Enabled": true
      },
      "T1055": {
        "Name": "Process Injection",
        "Tactic": "Defense Evasion",
        "Description": "Adversaries may inject code into processes in order to evade process-based defenses",
        "DetectionPatterns": [
          "CreateRemoteThread",
          "SetWindowsHookEx",
          "QueueUserAPC",
          "NtMapViewOfSection"
        ],
        "Severity": "High",
        "Enabled": true
      },
      "T1003": {
        "Name": "OS Credential Dumping",
        "Tactic": "Credential Access",
        "Description": "Adversaries may attempt to dump credentials to obtain account login information",
        "DetectionPatterns": [
          "lsass.exe",
          "sekurlsa",
          "mimikatz",
          "procdump"
        ],
        "Severity": "Critical",
        "Enabled": true
      }
    }
  }
}"""
    
    with open(base_path / "configs/mitre-attack.json", "w") as f:
        f.write(mitre_config)
    
    print("Created configuration files")

def create_documentation_files(base_path):
    """Create documentation and deployment guides"""
    
    # README file
    readme_content = """# WatchLockAI Endpoint Security Agent

## Overview
WatchLockAI is an autonomous, AI-powered cybersecurity endpoint agent that provides next-generation threat detection, investigation, and response capabilities for Windows systems.

## Features
- **AI-Powered Threat Detection**: Local LLM-based analysis with MITRE ATT&CK framework integration
- **Behavioral Baselining**: Adaptive learning of user, process, and system behavior patterns
- **Automated Response**: Configurable automated threat containment and remediation
- **Digital Forensics**: Built-in investigation engine with timeline analysis and evidence collection
- **Tamperproof Protection**: Self-protecting architecture resistant to evasion attempts
- **Enterprise Integration**: Native integration with Microsoft Defender, Azure Security Center, and third-party tools

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 Pro/Enterprise or Windows 11 Pro/Enterprise
- **Processor**: 64-bit x86 processor with 2+ cores
- **Memory**: 8 GB RAM (minimum), 16 GB recommended
- **Storage**: 2 GB free disk space for installation, 10 GB for operations
- **Network**: Internet connectivity for console communication
- **Privileges**: Local Administrator rights for installation

### Recommended Requirements
- **Processor**: 64-bit x86 processor with 4+ cores
- **Memory**: 16 GB RAM or higher
- **Storage**: SSD with 20 GB+ free space
- **Network**: Stable broadband connection

## Installation

### Quick Installation
1. Download the WatchLockAI installer package
2. Right-click `install.bat` and select "Run as administrator"
3. Follow the installation prompts
4. Verify service is running: `Get-Service WatchLockAI`

### PowerShell Installation
```powershell
# Run as Administrator
.\\Install-WatchLockAI.ps1 -ConsoleEndpoint "https://your-console.domain.com"
```

### Silent Installation
```powershell
# Run as Administrator
.\\Install-WatchLockAI.ps1 -ConsoleEndpoint "https://console.watchlockai.com" -Silent
```

## Configuration

### Main Configuration File
Location: `C:\\Program Files\\WatchLockAI\\Config\\appsettings.json`

Key configuration sections:
- **ThreatDetection**: Detection engine settings
- **Response**: Automated response configuration  
- **BehavioralLearning**: Machine learning parameters
- **Forensics**: Investigation and evidence settings
- **Tamperproof**: Self-protection configuration

### Environment-Specific Configurations
- `appsettings.Development.json` - Development environment
- `appsettings.Production.json` - Production environment

## Operation

### Service Management
```powershell
# Check service status
Get-Service WatchLockAI

# Start service
Start-Service WatchLockAI

# Stop service
Stop-Service WatchLockAI

# Restart service
Restart-Service WatchLockAI
```

### Log Locations
- **Service Logs**: `C:\\Program Files\\WatchLockAI\\Logs\\`
- **Windows Event Log**: Application Log, Source: "WatchLockAI"
- **Evidence Storage**: `C:\\Program Files\\WatchLockAI\\Evidence\\`

### Performance Monitoring
Monitor resource usage through:
- Windows Performance Monitor
- Task Manager
- WatchLockAI management console
- Service logs

## Security Considerations

### Firewall Configuration
The installer automatically configures Windows Firewall rules:
- **Outbound**: HTTPS (443) to console endpoint
- **Inbound**: TCP 8443 for agent management (optional)

### Antivirus Exclusions
Add these paths to antivirus exclusions:
- `C:\\Program Files\\WatchLockAI\\`
- Service executable: `WatchLockAI.Service.exe`

### Network Requirements
Outbound connectivity required to:
- Management console endpoint (HTTPS/443)
- Threat intelligence feeds (HTTPS/443)
- Update servers (HTTPS/443)

## Troubleshooting

### Service Won't Start
1. Check Windows Event Log for errors
2. Verify configuration file syntax
3. Ensure adequate disk space and memory
4. Check network connectivity to console
5. Verify Windows version compatibility

### High Resource Usage
1. Check `MaxCpuUsage` and `MaxMemoryUsage` settings
2. Review scan intervals and thresholds
3. Enable performance throttling
4. Check for system conflicts

### Detection Issues
1. Verify MITRE ATT&CK configuration
2. Check behavioral learning settings
3. Review anomaly thresholds
4. Validate threat intelligence feeds

### Log Analysis
```powershell
# View recent service logs
Get-Content "C:\\Program Files\\WatchLockAI\\Logs\\*.log" | Select-Object -Last 100

# Check Windows Event Log
Get-EventLog -LogName Application -Source "WatchLockAI" -Newest 50
```

## Uninstallation

### Standard Uninstallation
```powershell
# Run as Administrator
.\\Uninstall-WatchLockAI.ps1
```

### Force Uninstallation (removes all data)
```powershell
# Run as Administrator
.\\Uninstall-WatchLockAI.ps1 -Force
```

## Support

### Documentation
- Installation Guide: `docs\\deployment\\installation-guide.md`
- Administrator Guide: `docs\\deployment\\admin-guide.md`
- API Documentation: `docs\\api\\`

### Technical Support
- Management console help system
- Enterprise support portal
- Technical documentation wiki

### Community
- User forums
- Knowledge base
- Best practices guides

## License
Copyright © 2025 MiniMax Agent. All rights reserved.

## Version History
- **v1.0.0** - Initial release with core detection and response capabilities
"""
    
    with open(base_path / "README.md", "w") as f:
        f.write(readme_content)
    
    # Deployment guide
    deployment_guide = """# WatchLockAI Deployment Guide

## Enterprise Deployment Strategy

### Planning Phase
1. **Environment Assessment**
   - Inventory target systems
   - Network topology analysis
   - Security policy review
   - Integration requirements

2. **Pilot Deployment**
   - Select pilot group (10-50 systems)
   - Deploy in monitoring-only mode
   - Validate detection accuracy
   - Tune configuration

3. **Phased Rollout**
   - Deploy by department/location
   - Enable response capabilities gradually
   - Monitor performance impact
   - Gather feedback

### Deployment Methods

#### Group Policy Deployment
1. Create GPO for WatchLockAI installation
2. Copy installer to SYSVOL share
3. Configure startup script
4. Test on pilot OU
5. Apply to production OUs

#### SCCM Deployment
1. Package installer as SCCM application
2. Configure detection rules
3. Set deployment requirements
4. Create device collections
5. Deploy to collections

#### PowerShell DSC
1. Create DSC configuration
2. Define installation resources
3. Configure LCM settings
4. Apply to target nodes
5. Monitor compliance

### Configuration Management

#### Centralized Configuration
- Use management console for policy distribution
- Implement configuration baselines
- Monitor compliance status
- Automate policy updates

#### Local Configuration Override
- Emergency configuration changes
- Site-specific settings
- Performance tuning
- Debugging options

### Monitoring and Maintenance

#### Health Monitoring
- Service status monitoring
- Performance metrics collection
- Error rate tracking
- Resource utilization analysis

#### Update Management
- Automated signature updates
- Configuration synchronization
- Software version management
- Rollback procedures

### Troubleshooting

#### Common Issues
1. **Installation Failures**
   - Insufficient privileges
   - Antivirus interference
   - Network connectivity
   - System compatibility

2. **Performance Issues**
   - Resource constraints
   - Configuration tuning
   - Conflicting software
   - System optimization

3. **Detection Problems**
   - False positives/negatives
   - Baseline calibration
   - Threshold adjustment
   - Rule customization

### Best Practices

#### Security
- Use dedicated service accounts
- Implement certificate-based authentication
- Enable audit logging
- Regular security reviews

#### Performance
- Monitor resource usage
- Implement performance baselines
- Use throttling mechanisms
- Optimize scan schedules

#### Operations
- Automate routine tasks
- Implement monitoring alerts
- Maintain documentation
- Train support staff
"""
    
    with open(base_path / "docs/deployment/deployment-guide.md", "w") as f:
        f.write(deployment_guide)
    
    print("Created documentation files")

if __name__ == "__main__":
    base_path = Path("/workspace/WatchLockAI_Agent")
    
    print("Creating installer and configuration files...")
    
    create_installer_scripts(base_path)
    create_configuration_files(base_path)
    create_documentation_files(base_path)
    
    print("Installer and configuration files created successfully!")
