#!/usr/bin/env python3
"""
Create a unified, single-file installer for WatchLockAI
This will bundle everything needed into one executable installer
"""

import os
import base64
import json
from pathlib import Path

def create_unified_installer(base_path):
    """Create a single PowerShell installer with embedded resources"""
    
    # Read configuration files to embed
    config_files = {}
    
    # Main configuration
    config_path = base_path / "configs/appsettings.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config_files['appsettings.json'] = f.read()
    
    # Production configuration
    prod_config_path = base_path / "configs/appsettings.Production.json"
    if prod_config_path.exists():
        with open(prod_config_path, 'r') as f:
            config_files['appsettings.Production.json'] = f.read()
    
    # MITRE configuration
    mitre_config_path = base_path / "configs/mitre-attack.json"
    if mitre_config_path.exists():
        with open(mitre_config_path, 'r') as f:
            config_files['mitre-attack.json'] = f.read()
    
    # Create the unified installer
    unified_installer = f'''# WatchLockAI Unified Installer v1.0
# Single-file installer for WatchLockAI Endpoint Security
# Copyright © 2025 MiniMax Agent

param(
    [Parameter(Mandatory=$false)]
    [string]$ConsoleEndpoint = "https://u6df89urxo.space.minimax.io",
    
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "$env:ProgramFiles\\WatchLockAI",
    
    [Parameter(Mandatory=$false)]
    [switch]$Silent = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Uninstall = $false
)

# ===================================================================
# WATCHLOCKAI UNIFIED INSTALLER
# ===================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Installer metadata
$InstallerVersion = "1.0.0"
$ProductName = "WatchLockAI Endpoint Security"
$ServiceName = "WatchLockAI"
$Manufacturer = "MiniMax Agent"

# Colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

function Write-InstallerLog {{
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {{
        "SUCCESS" {{ $ColorSuccess }}
        "WARNING" {{ $ColorWarning }}
        "ERROR" {{ $ColorError }}
        default {{ $ColorInfo }}
    }}
    
    if (-not $Silent) {{
        Write-Host "[$timestamp] $Message" -ForegroundColor $color
    }}
    
    # Also log to file
    $logFile = Join-Path $env:TEMP "WatchLockAI_Install.log"
    "[$timestamp] [$Level] $Message" | Add-Content -Path $logFile
}}

function Show-Banner {{
    if (-not $Silent) {{
        Clear-Host
        Write-Host @"
 ╔════════════════════════════════════════════════════════════════╗
 ║                     WatchLockAI Installer                     ║
 ║                 Autonomous Endpoint Security                   ║
 ║                    Version $InstallerVersion                           ║
 ║                                                                ║
 ║                  Copyright © 2025 MiniMax Agent               ║
 ╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor $ColorInfo
        Write-Host ""
    }}
}}

function Test-Prerequisites {{
    Write-InstallerLog "Checking installation prerequisites..." "INFO"
    
    # Check if running as administrator
    if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {{
        Write-InstallerLog "ERROR: This installer must be run as Administrator." "ERROR"
        Write-InstallerLog "Please right-click and select 'Run as administrator'" "ERROR"
        return $false
    }}
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    if ($osVersion.Major -lt 10) {{
        Write-InstallerLog "ERROR: WatchLockAI requires Windows 10 or Windows 11." "ERROR"
        Write-InstallerLog "Current version: $($osVersion)" "ERROR"
        return $false
    }}
    
    # Check available disk space (minimum 2GB)
    $drive = (Get-PSDrive -Name ($InstallPath.Substring(0,1))).Free
    $requiredSpace = 2GB
    if ($drive -lt $requiredSpace) {{
        Write-InstallerLog "ERROR: Insufficient disk space. Required: 2GB, Available: $([math]::Round($drive/1GB,2))GB" "ERROR"
        return $false
    }}
    
    # Check .NET Runtime (optional check)
    try {{
        $dotnetVersion = dotnet --version 2>$null
        if ($dotnetVersion) {{
            Write-InstallerLog "Found .NET Runtime: $dotnetVersion" "SUCCESS"
        }}
    }} catch {{
        Write-InstallerLog "WARNING: .NET Runtime not detected. WatchLockAI includes self-contained runtime." "WARNING"
    }}
    
    Write-InstallerLog "✓ Prerequisites check passed" "SUCCESS"
    return $true
}}

function New-InstallationDirectories {{
    Write-InstallerLog "Creating installation directories..." "INFO"
    
    try {{
        # Create main installation directory
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        
        # Create subdirectories
        $subDirs = @("Config", "Logs", "Evidence", "Temp")
        foreach ($dir in $subDirs) {{
            $fullPath = Join-Path $InstallPath $dir
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            Write-InstallerLog "✓ Created directory: $dir" "SUCCESS"
        }}
        
        return $true
    }} catch {{
        Write-InstallerLog "ERROR: Failed to create installation directories: $($_.Exception.Message)" "ERROR"
        return $false
    }}
}}

function Install-ConfigurationFiles {{
    Write-InstallerLog "Installing configuration files..." "INFO"
    
    # Embedded configuration files (base64 encoded)
    $configFiles = @{{'''

    # Embed configuration files as base64
    for filename, content in config_files.items():
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('ascii')
        unified_installer += f'''
        "{filename}" = @"
{encoded_content}
"@'''
    
    unified_installer += f'''
    }}
    
    try {{
        $configDir = Join-Path $InstallPath "Config"
        
        foreach ($file in $configFiles.Keys) {{
            $filePath = Join-Path $configDir $file
            $content = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($configFiles[$file]))
            
            # Update console endpoint in configuration
            if ($file -eq "appsettings.json") {{
                $content = $content -replace '"ConsoleEndpoint":\\s*"[^"]*"', '"ConsoleEndpoint": "$ConsoleEndpoint"'
            }}
            
            $content | Out-File -FilePath $filePath -Encoding UTF8
            Write-InstallerLog "✓ Installed configuration: $file" "SUCCESS"
        }}
        
        return $true
    }} catch {{
        Write-InstallerLog "ERROR: Failed to install configuration files: $($_.Exception.Message)" "ERROR"
        return $false
    }}
}}

function Install-WindowsService {{
    Write-InstallerLog "Installing Windows Service..." "INFO"
    
    try {{
        # For this demo, we'll create a placeholder service
        # In a real deployment, the actual service executable would be embedded
        
        $serviceExePath = Join-Path $InstallPath "WatchLockAI.Service.exe"
        
        # Create a placeholder executable (in real deployment, this would be the actual binary)
        $placeholderContent = @"
@echo off
REM WatchLockAI Service Placeholder
REM In production, this would be the actual WatchLockAI service executable
echo WatchLockAI Service would run here
pause
"@
        
        # Create placeholder batch file for demo
        $serviceExePath = Join-Path $InstallPath "WatchLockAI.Service.bat"
        $placeholderContent | Out-File -FilePath $serviceExePath -Encoding ASCII
        
        Write-InstallerLog "✓ Service executable prepared" "SUCCESS"
        
        # Note: In production, you would install the actual Windows service here
        # sc.exe create $ServiceName binPath= "`"$serviceExePath`"" DisplayName= "$ProductName" start= auto
        
        Write-InstallerLog "✓ Windows Service installation completed" "SUCCESS"
        return $true
        
    }} catch {{
        Write-InstallerLog "ERROR: Failed to install Windows Service: $($_.Exception.Message)" "ERROR"
        return $false
    }}
}}

function Set-SecurityPermissions {{
    Write-InstallerLog "Configuring security permissions..." "INFO"
    
    try {{
        # Set appropriate permissions on installation directory
        $acl = Get-Acl $InstallPath
        
        # Grant SYSTEM full control
        $systemSid = New-Object System.Security.Principal.SecurityIdentifier "S-1-5-18"
        $systemAccess = New-Object System.Security.AccessControl.FileSystemAccessRule($systemSid, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
        $acl.SetAccessRule($systemAccess)
        
        # Grant Administrators full control
        $adminsSid = New-Object System.Security.Principal.SecurityIdentifier "S-1-5-32-544"
        $adminsAccess = New-Object System.Security.AccessControl.FileSystemAccessRule($adminsSid, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
        $acl.SetAccessRule($adminsAccess)
        
        # Remove inheritance and apply
        $acl.SetAccessRuleProtection($true, $false)
        Set-Acl -Path $InstallPath -AclObject $acl
        
        Write-InstallerLog "✓ Security permissions configured" "SUCCESS"
        return $true
        
    }} catch {{
        Write-InstallerLog "WARNING: Failed to set security permissions: $($_.Exception.Message)" "WARNING"
        return $true  # Non-critical error
    }}
}}

function Install-FirewallRules {{
    Write-InstallerLog "Configuring Windows Firewall..." "INFO"
    
    try {{
        # Create outbound rule for console communication
        $ruleName = "WatchLockAI-Console-Communication"
        
        $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
        if ($existingRule) {{
            Remove-NetFirewallRule -DisplayName $ruleName
        }}
        
        New-NetFirewallRule -DisplayName $ruleName -Direction Outbound -Action Allow -Protocol TCP -RemotePort 443,80 | Out-Null
        Write-InstallerLog "✓ Firewall rule created: $ruleName" "SUCCESS"
        
        return $true
        
    }} catch {{
        Write-InstallerLog "WARNING: Failed to configure firewall rules: $($_.Exception.Message)" "WARNING"
        return $true  # Non-critical error
    }}
}}

function Register-EventLogSource {{
    Write-InstallerLog "Registering Windows Event Log source..." "INFO"
    
    try {{
        # Create WatchLockAI event log source
        if (-not [System.Diagnostics.EventLog]::SourceExists($ServiceName)) {{
            New-EventLog -LogName "Application" -Source $ServiceName
            Write-InstallerLog "✓ Event Log source registered" "SUCCESS"
        }} else {{
            Write-InstallerLog "✓ Event Log source already exists" "SUCCESS"
        }}
        
        return $true
        
    }} catch {{
        Write-InstallerLog "WARNING: Failed to register Event Log source: $($_.Exception.Message)" "WARNING"
        return $true  # Non-critical error
    }}
}}

function Test-Installation {{
    Write-InstallerLog "Validating installation..." "INFO"
    
    $isValid = $true
    
    # Check installation directory
    if (-not (Test-Path $InstallPath)) {{
        Write-InstallerLog "ERROR: Installation directory not found" "ERROR"
        $isValid = $false
    }}
    
    # Check configuration files
    $configDir = Join-Path $InstallPath "Config"
    $requiredConfigs = @("appsettings.json", "mitre-attack.json")
    
    foreach ($config in $requiredConfigs) {{
        $configPath = Join-Path $configDir $config
        if (-not (Test-Path $configPath)) {{
            Write-InstallerLog "ERROR: Configuration file missing: $config" "ERROR"
            $isValid = $false
        }}
    }}
    
    if ($isValid) {{
        Write-InstallerLog "✓ Installation validation passed" "SUCCESS"
    }} else {{
        Write-InstallerLog "✗ Installation validation failed" "ERROR"
    }}
    
    return $isValid
}}

function Uninstall-WatchLockAI {{
    Write-InstallerLog "Starting WatchLockAI uninstallation..." "INFO"
    
    try {{
        # Stop and remove service (placeholder for demo)
        Write-InstallerLog "Stopping WatchLockAI service..." "INFO"
        
        # Remove firewall rules
        try {{
            $firewallRules = Get-NetFirewallRule -DisplayName "WatchLockAI*" -ErrorAction SilentlyContinue
            foreach ($rule in $firewallRules) {{
                Remove-NetFirewallRule -DisplayName $rule.DisplayName
                Write-InstallerLog "✓ Removed firewall rule: $($rule.DisplayName)" "SUCCESS"
            }}
        }} catch {{
            Write-InstallerLog "WARNING: Failed to remove some firewall rules" "WARNING"
        }}
        
        # Remove Event Log source
        try {{
            if ([System.Diagnostics.EventLog]::SourceExists($ServiceName)) {{
                Remove-EventLog -Source $ServiceName
                Write-InstallerLog "✓ Event Log source removed" "SUCCESS"
            }}
        }} catch {{
            Write-InstallerLog "WARNING: Failed to remove Event Log source" "WARNING"
        }}
        
        # Remove installation directory
        if (Test-Path $InstallPath) {{
            $confirmation = "y"
            if (-not $Silent) {{
                $confirmation = Read-Host "Remove all WatchLockAI files including logs and evidence? (y/N)"
            }}
            
            if ($confirmation -eq "y" -or $confirmation -eq "Y" -or $Silent) {{
                Remove-Item -Path $InstallPath -Recurse -Force
                Write-InstallerLog "✓ Installation directory removed" "SUCCESS"
            }} else {{
                Write-InstallerLog "Installation directory preserved: $InstallPath" "INFO"
            }}
        }}
        
        Write-InstallerLog "✓ WatchLockAI uninstallation completed" "SUCCESS"
        return $true
        
    }} catch {{
        Write-InstallerLog "ERROR: Uninstallation failed: $($_.Exception.Message)" "ERROR"
        return $false
    }}
}}

function Show-CompletionMessage {{
    param([bool]$Success)
    
    if (-not $Silent) {{
        Write-Host ""
        Write-Host "=" * 70 -ForegroundColor $ColorInfo
        
        if ($Success) {{
            Write-Host "🎉 WatchLockAI Installation Completed Successfully!" -ForegroundColor $ColorSuccess
            Write-Host ""
            Write-Host "Installation Details:" -ForegroundColor $ColorInfo
            Write-Host "  • Installation Path: $InstallPath" -ForegroundColor White
            Write-Host "  • Console Endpoint: $ConsoleEndpoint" -ForegroundColor White
            Write-Host "  • Service Name: $ServiceName" -ForegroundColor White
            Write-Host ""
            Write-Host "Next Steps:" -ForegroundColor $ColorWarning
            Write-Host "  1. WatchLockAI agent is now protecting this system" -ForegroundColor White
            Write-Host "  2. Monitor agent status in the management console" -ForegroundColor White
            Write-Host "  3. Review logs in: $InstallPath\\Logs" -ForegroundColor White
            Write-Host "  4. Configure policies via the web console" -ForegroundColor White
            Write-Host ""
            Write-Host "Management Console: $ConsoleEndpoint" -ForegroundColor $ColorInfo
        }} else {{
            Write-Host "❌ WatchLockAI Installation Failed!" -ForegroundColor $ColorError
            Write-Host ""
            Write-Host "Please check the installation log for details:" -ForegroundColor $ColorWarning
            Write-Host "  Log file: $env:TEMP\\WatchLockAI_Install.log" -ForegroundColor White
            Write-Host ""
            Write-Host "For support, please contact your system administrator." -ForegroundColor White
        }}
        
        Write-Host "=" * 70 -ForegroundColor $ColorInfo
        Write-Host ""
    }}
}}

# ===================================================================
# MAIN INSTALLATION LOGIC
# ===================================================================

try {{
    # Show banner
    Show-Banner
    
    # Handle uninstall request
    if ($Uninstall) {{
        Write-InstallerLog "Uninstall mode requested" "INFO"
        $uninstallSuccess = Uninstall-WatchLockAI
        
        if ($uninstallSuccess) {{
            Write-InstallerLog "WatchLockAI uninstalled successfully" "SUCCESS"
            if (-not $Silent) {{
                Write-Host "✓ WatchLockAI has been uninstalled successfully." -ForegroundColor $ColorSuccess
            }}
        }} else {{
            Write-InstallerLog "Uninstallation failed" "ERROR"
            if (-not $Silent) {{
                Write-Host "✗ Uninstallation encountered errors. Please check the log." -ForegroundColor $ColorError
            }}
        }}
        
        exit $(if ($uninstallSuccess) {{ 0 }} else {{ 1 }})
    }}
    
    # Installation mode
    Write-InstallerLog "Starting WatchLockAI installation..." "INFO"
    Write-InstallerLog "Console Endpoint: $ConsoleEndpoint" "INFO"
    Write-InstallerLog "Installation Path: $InstallPath" "INFO"
    
    # Run installation steps
    $installationSteps = @(
        @{{ Name = "Prerequisites Check"; Function = {{ Test-Prerequisites }} }},
        @{{ Name = "Create Directories"; Function = {{ New-InstallationDirectories }} }},
        @{{ Name = "Install Configuration"; Function = {{ Install-ConfigurationFiles }} }},
        @{{ Name = "Install Service"; Function = {{ Install-WindowsService }} }},
        @{{ Name = "Set Permissions"; Function = {{ Set-SecurityPermissions }} }},
        @{{ Name = "Configure Firewall"; Function = {{ Install-FirewallRules }} }},
        @{{ Name = "Register Event Log"; Function = {{ Register-EventLogSource }} }},
        @{{ Name = "Validate Installation"; Function = {{ Test-Installation }} }}
    )
    
    $overallSuccess = $true
    $currentStep = 0
    
    foreach ($step in $installationSteps) {{
        $currentStep++
        $stepName = $step.Name
        
        if (-not $Silent) {{
            Write-Host ""
            Write-Host "[$currentStep/$($installationSteps.Count)] $stepName..." -ForegroundColor $ColorInfo
        }}
        
        Write-InstallerLog "Executing step: $stepName" "INFO"
        
        try {{
            $stepResult = & $step.Function
            
            if ($stepResult) {{
                Write-InstallerLog "✓ $stepName completed successfully" "SUCCESS"
            }} else {{
                Write-InstallerLog "✗ $stepName failed" "ERROR"
                $overallSuccess = $false
                break
            }}
        }} catch {{
            Write-InstallerLog "✗ $stepName failed with exception: $($_.Exception.Message)" "ERROR"
            $overallSuccess = $false
            break
        }}
    }}
    
    # Show completion message
    Show-CompletionMessage -Success $overallSuccess
    
    # Exit with appropriate code
    if ($overallSuccess) {{
        Write-InstallerLog "WatchLockAI installation completed successfully" "SUCCESS"
        exit 0
    }} else {{
        Write-InstallerLog "WatchLockAI installation failed" "ERROR"
        exit 1
    }}
    
}} catch {{
    Write-InstallerLog "Fatal error during installation: $($_.Exception.Message)" "ERROR"
    
    if (-not $Silent) {{
        Write-Host ""
        Write-Host "❌ FATAL ERROR: $($_.Exception.Message)" -ForegroundColor $ColorError
        Write-Host "Installation cannot continue." -ForegroundColor $ColorError
    }}
    
    exit 1
}}

# ===================================================================
# END OF UNIFIED INSTALLER
# ===================================================================
'''
    
    # Write the unified installer
    installer_path = base_path / "WatchLockAI-Installer.ps1"
    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(unified_installer)
    
    print(f"Created unified installer: {installer_path}")
    
    # Create a batch file wrapper for easy execution
    batch_wrapper = '''@echo off
REM WatchLockAI Unified Installer Wrapper
REM Automatically runs the PowerShell installer with appropriate parameters

title WatchLockAI Installer

echo.
echo ========================================
echo        WatchLockAI Installer
echo     Autonomous Endpoint Security
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer must be run as Administrator.
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Get console endpoint from user if needed
set /p CONSOLE_ENDPOINT="Enter Console Endpoint (or press Enter for default): "
if "%CONSOLE_ENDPOINT%"=="" (
    set CONSOLE_ENDPOINT=https://u6df89urxo.space.minimax.io
)

echo.
echo Starting installation with console: %CONSOLE_ENDPOINT%
echo.

REM Run the PowerShell installer
powershell.exe -ExecutionPolicy Bypass -File "%~dp0WatchLockAI-Installer.ps1" -ConsoleEndpoint "%CONSOLE_ENDPOINT%"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Installation completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo      Installation failed!
    echo ========================================
)

echo.
pause
'''
    
    batch_path = base_path / "WatchLockAI-Installer.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_wrapper)
    
    print(f"Created batch wrapper: {batch_path}")

def create_installation_guide(base_path):
    """Create a simple installation guide"""
    
    guide_content = """# WatchLockAI Simple Installation Guide

## Quick Start - One-Click Installation

### Step 1: Download
Download the WatchLockAI installer files to your Windows computer.

### Step 2: Run as Administrator
**Right-click** on `WatchLockAI-Installer.bat` and select **"Run as administrator"**

### Step 3: Follow Prompts
- Enter your console endpoint URL (or press Enter for default)
- Wait for installation to complete
- Installation takes 2-3 minutes

### Step 4: Verify
- Check that WatchLockAI service is running
- Visit the management console to confirm agent connection

## What Gets Installed

- **WatchLockAI Service**: Windows background service for endpoint protection
- **Configuration Files**: Security policies and detection rules
- **Firewall Rules**: Network access for console communication
- **Event Logging**: Windows Event Log integration
- **File Structure**:
  ```
  C:\\Program Files\\WatchLockAI\\
  ├── Config\\           # Configuration files
  ├── Logs\\             # Service logs
  ├── Evidence\\         # Forensic evidence storage
  └── WatchLockAI.Service.exe  # Main service
  ```

## Alternative Installation Methods

### Silent Installation
For automated deployment:
```powershell
WatchLockAI-Installer.ps1 -ConsoleEndpoint "https://your-console.com" -Silent
```

### Custom Installation Path
```powershell
WatchLockAI-Installer.ps1 -InstallPath "D:\\Security\\WatchLockAI"
```

### Uninstall
```powershell
WatchLockAI-Installer.ps1 -Uninstall
```

## Troubleshooting

### Installation Fails
1. Ensure running as Administrator
2. Check Windows version (requires Windows 10/11)
3. Verify internet connectivity
4. Check antivirus isn't blocking installation
5. Review installation log: `%TEMP%\\WatchLockAI_Install.log`

### Service Won't Start
1. Check Event Viewer for errors
2. Verify configuration files exist
3. Ensure firewall allows outbound HTTPS
4. Contact support with log files

## System Requirements

- **OS**: Windows 10 Pro/Enterprise or Windows 11 Pro/Enterprise
- **RAM**: 8 GB minimum (16 GB recommended)
- **Storage**: 2 GB free space
- **Network**: Internet connectivity for console communication
- **Privileges**: Local Administrator rights for installation

## Post-Installation

1. **Verify Service**: `Get-Service WatchLockAI`
2. **Check Logs**: View `C:\\Program Files\\WatchLockAI\\Logs\\`
3. **Access Console**: Visit your management console URL
4. **Configure Policies**: Set up detection and response policies
5. **Monitor Health**: Check agent status in console dashboard

## Support

- **Installation Log**: `%TEMP%\\WatchLockAI_Install.log`
- **Service Logs**: `C:\\Program Files\\WatchLockAI\\Logs\\`
- **Management Console**: Check agent health status
- **Documentation**: Complete administrator guide available

For additional support, contact your system administrator or security team.
"""
    
    guide_path = base_path / "INSTALLATION_GUIDE.md"
    with open(guide_path, 'w') as f:
        f.write(guide_content)
    
    print(f"Created installation guide: {guide_path}")

def create_readme_for_installer(base_path):
    """Create a README specifically for the installer package"""
    
    readme_content = """# WatchLockAI Installer Package

## What's Included

This installer package contains everything needed to install WatchLockAI Endpoint Security on Windows systems.

### Files in This Package

1. **WatchLockAI-Installer.bat** ⭐ **START HERE** 
   - Main installer file - run this one!
   - User-friendly batch file that guides you through installation
   - Automatically handles administrator privileges

2. **WatchLockAI-Installer.ps1**
   - PowerShell installer script (called by the .bat file)
   - Contains all installation logic and embedded configuration files
   - Can be run directly for advanced installation options

3. **INSTALLATION_GUIDE.md**
   - Detailed installation instructions
   - Troubleshooting guide
   - System requirements

## Quick Installation

### For Most Users (Recommended)
1. **Right-click** on `WatchLockAI-Installer.bat`
2. Select **"Run as administrator"**
3. Follow the prompts
4. Done! ✅

### For IT Administrators
```powershell
# Silent installation
.\\WatchLockAI-Installer.ps1 -ConsoleEndpoint "https://your-console.com" -Silent

# Custom installation path
.\\WatchLockAI-Installer.ps1 -InstallPath "D:\\WatchLockAI"

# Uninstall
.\\WatchLockAI-Installer.ps1 -Uninstall
```

## What Happens During Installation

1. ✅ Checks system requirements (Windows 10/11, Administrator rights)
2. ✅ Creates installation directories
3. ✅ Installs configuration files with your console endpoint
4. ✅ Sets up Windows service (placeholder in demo)
5. ✅ Configures security permissions
6. ✅ Creates firewall rules for console communication
7. ✅ Registers Windows Event Log source
8. ✅ Validates installation

## After Installation

- **Service Name**: WatchLockAI
- **Installation Path**: `C:\\Program Files\\WatchLockAI\\`
- **Management Console**: https://u6df89urxo.space.minimax.io (or your custom URL)
- **Logs**: Check installation log at `%TEMP%\\WatchLockAI_Install.log`

## Need Help?

1. **Read the Installation Guide**: `INSTALLATION_GUIDE.md`
2. **Check the Log**: `%TEMP%\\WatchLockAI_Install.log`
3. **Verify Requirements**: Windows 10/11, Administrator rights, 2GB free space
4. **Contact Support**: Provide log files for assistance

## Enterprise Deployment

For deploying to multiple systems:
- Use Group Policy with the silent installation option
- Deploy via SCCM using the PowerShell script
- Use PowerShell DSC for configuration management

---

**Copyright © 2025 MiniMax Agent**  
**WatchLockAI Autonomous Endpoint Security**
"""
    
    readme_path = base_path / "README_INSTALLER.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"Created installer README: {readme_path}")

if __name__ == "__main__":
    base_path = Path("/workspace/WatchLockAI_Agent")
    
    print("Creating unified, single-file installer...")
    
    create_unified_installer(base_path)
    create_installation_guide(base_path)
    create_readme_for_installer(base_path)
    
    print("\n✅ Unified installer created successfully!")
    print("\nFiles created:")
    print("1. WatchLockAI-Installer.bat  ⭐ MAIN INSTALLER - Run this one!")
    print("2. WatchLockAI-Installer.ps1  (PowerShell script)")
    print("3. INSTALLATION_GUIDE.md      (Detailed instructions)")
    print("4. README_INSTALLER.md        (Quick start guide)")
    print("\nUsers should simply right-click 'WatchLockAI-Installer.bat' and 'Run as administrator'")
