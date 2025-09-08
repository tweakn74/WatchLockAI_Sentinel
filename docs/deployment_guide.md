# WatchLockAI Enterprise Deployment Guide

## Overview
Complete deployment guide for the WatchLockAI cybersecurity platform, providing step-by-step instructions for enterprise-scale implementation across Windows 11 environments.

## Pre-Deployment Requirements

### 1. System Prerequisites

#### **Minimum Hardware Requirements**
- **Processor**: 8th generation Intel Core or AMD Ryzen 2000 series (or newer)
- **Memory**: 4 GB RAM minimum, 8 GB recommended
- **Storage**: 2 GB available disk space
- **TPM**: TPM 2.0 chip required for Windows 11 security features
- **Network**: Reliable internet connection for cloud console access

#### **Windows 11 Compatibility**
- **Supported Editions**: Home, Pro, Enterprise, Education
- **Version Requirements**: 22H2 (Build 22621) or newer
- **Security Features**: Secure Boot enabled, TPM 2.0 available
- **PowerShell**: Version 5.1 or newer (included with Windows 11)

#### **Network Requirements**
- **Outbound HTTPS**: Port 443 for Supabase backend communication
- **Web Console**: Port 8080 for local console access
- **DNS Resolution**: Access to public DNS for cloud services
- **Firewall**: Windows Firewall configured for WatchLockAI services

### 2. Administrative Prerequisites

#### **User Account Requirements**
- **Local Administrator**: Required for service installation
- **PowerShell Execution**: RemoteSigned or Unrestricted execution policy
- **Windows Defender**: Administrative access for exclusion configuration
- **Group Policy**: Enterprise environments may require policy updates

#### **Organizational Readiness**
- **Supabase Account**: Organization-level Supabase project configured
- **User Management**: Identity management system integration plan
- **Compliance Requirements**: Understanding of applicable frameworks (NIST, SOC 2, ISO 27001)
- **Support Structure**: Designated security operations team

## Deployment Methods

### 1. Single System Installation

#### **Interactive Installation (Recommended for Testing)**
```bash
# Download the WatchLockAI installer package
# Navigate to the installation directory
cd C:\WatchLockAI_Deployment

# Run the BULLETPROOF-FINAL installer
WatchLockAI-REAL-Installer.bat
```

**Installation Process:**
1. **Administrator Verification**: Installer checks for administrative privileges
2. **System Compatibility**: Validates Windows 11 requirements and TPM 2.0
3. **Python Detection**: Identifies and resolves Python installation issues
4. **Component Installation**: Deploys agent service, web console, and configuration
5. **Service Registration**: Registers WatchLockAI as Windows service
6. **Verification**: Tests service functionality and web console access

**Expected Installation Time**: 5-15 minutes depending on system configuration

#### **Silent Installation**
```bash
# Silent installation for automated deployment
powershell.exe -ExecutionPolicy Bypass -File "WatchLockAI_Agent/installers/BULLETPROOF-FINAL-Installer.ps1" -Silent -LogPath "C:\Deployment\Logs"
```

### 2. Enterprise Mass Deployment

#### **Group Policy Deployment**
```powershell
# Group Policy Computer Startup Script
# Location: Computer Configuration > Policies > Windows Settings > Scripts

# Script: Deploy-WatchLockAI.ps1
param(
    [string]$OrganizationId = "org_enterprise_001",
    [string]$DeploymentServer = "\\deployment-server\WatchLockAI",
    [string]$LogPath = "C:\Windows\Temp\WatchLockAI-Deployment.log"
)

# Copy installer from network share
Copy-Item -Path "$DeploymentServer\*" -Destination "C:\Temp\WatchLockAI" -Recurse -Force

# Execute installation
& "C:\Temp\WatchLockAI\WatchLockAI-REAL-Installer.bat" -OrganizationId $OrganizationId -Silent

# Configure organization-specific settings
$configPath = "C:\Program Files\WatchLockAI\config\appsettings.json"
$config = Get-Content $configPath | ConvertFrom-Json
$config.OrganizationId = $OrganizationId
$config.ConsoleUrl = "https://console.company.com"
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath

# Start and verify service
Start-Service -Name "WatchLockAI"
$serviceStatus = Get-Service -Name "WatchLockAI"
if ($serviceStatus.Status -eq "Running") {
    Write-Host "WatchLockAI deployed successfully on $env:COMPUTERNAME" | Tee-Object -FilePath $LogPath -Append
} else {
    Write-Error "WatchLockAI deployment failed on $env:COMPUTERNAME" | Tee-Object -FilePath $LogPath -Append
}
```

#### **SCCM Deployment Package**
```xml
<!-- SCCM Application Definition -->
<Application>
  <Name>WatchLockAI Security Agent</Name>
  <Version>1.0.0</Version>
  <Publisher>WatchLockAI</Publisher>
  
  <DeploymentType>
    <Technology>Script Installer</Technology>
    <InstallCommand>WatchLockAI-REAL-Installer.bat -Silent -OrganizationId %ORG_ID%</InstallCommand>
    <UninstallCommand>WatchLockAI-Complete-Uninstaller.ps1 -Silent</UninstallCommand>
    
    <DetectionMethod>
      <RegistryKey>HKEY_LOCAL_MACHINE\SOFTWARE\WatchLockAI</RegistryKey>
      <ValueName>Version</ValueName>
      <ValueData>1.0.0</ValueData>
    </DetectionMethod>
    
    <Requirements>
      <OperatingSystem>Windows 11</OperatingSystem>
      <Architecture>x64</Architecture>
      <FreeSpace>2048</FreeSpace>
      <AdminRights>Required</AdminRights>
    </Requirements>
  </DeploymentType>
</Application>
```

#### **Intune Deployment**
```json
{
  "displayName": "WatchLockAI Security Agent",
  "description": "Enterprise cybersecurity agent for Windows 11",
  "publisher": "WatchLockAI",
  "category": "Security",
  
  "installCommandLine": "WatchLockAI-REAL-Installer.bat -Silent -Intune",
  "uninstallCommandLine": "WatchLockAI-Complete-Uninstaller.ps1 -Silent",
  
  "detectionRules": [
    {
      "ruleType": "registry",
      "keyPath": "HKEY_LOCAL_MACHINE\\SOFTWARE\\WatchLockAI",
      "valueName": "InstallPath",
      "operationType": "exists"
    }
  ],
  
  "requirementRules": [
    {
      "ruleType": "operatingSystem",
      "minimumSupportedOperatingSystem": "Windows11",
      "architecture": "x64"
    }
  ]
}
```

### 3. Cloud-Based Deployment

#### **Azure Arc Integration**
```yaml
# Azure Arc deployment configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: watchlockai-deployment
  namespace: arc-system
data:
  install-script: |
    # Download and execute WatchLockAI installer
    Invoke-WebRequest -Uri "https://deployment.watchlockai.com/installer.bat" -OutFile "C:\Temp\installer.bat"
    & "C:\Temp\installer.bat" -AzureArc -OrganizationId $env:AZURE_ORG_ID
  
  config-template: |
    {
      "OrganizationId": "${AZURE_ORG_ID}",
      "ManagementEndpoint": "https://console.watchlockai.com",
      "AzureIntegration": {
        "TenantId": "${AZURE_TENANT_ID}",
        "SubscriptionId": "${AZURE_SUBSCRIPTION_ID}",
        "ResourceGroup": "${AZURE_RESOURCE_GROUP}"
      }
    }
```

## Post-Deployment Configuration

### 1. Service Verification

#### **Service Status Check**
```powershell
# Verify WatchLockAI service is running
$service = Get-Service -Name "WatchLockAI"
Write-Host "Service Status: $($service.Status)"
Write-Host "Service Start Type: $($service.StartType)"

# Check service dependencies
Get-Service -Name "WatchLockAI" -DependentServices
Get-Service -Name "WatchLockAI" -RequiredServices

# Verify web console accessibility
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 10
    Write-Host "Web Console Status: $($response.StatusCode) - $($response.StatusDescription)"
} catch {
    Write-Warning "Web Console not accessible: $($_.Exception.Message)"
}
```

#### **Event Log Monitoring**
```powershell
# Check WatchLockAI event logs
Get-WinEvent -LogName "Application" -FilterHashtable @{ProviderName="WatchLockAI"} -MaxEvents 50

# Monitor for installation events
Get-WinEvent -LogName "System" -FilterHashtable @{ID=7034,7035,7036; ProviderName="Service Control Manager"} | 
    Where-Object {$_.Message -like "*WatchLockAI*"}
```

### 2. Organization Configuration

#### **Supabase Project Setup**
```javascript
// Organization registration in Supabase
const orgConfig = {
  organization_id: 'org_enterprise_001',
  name: 'Enterprise Corporation',
  slug: 'enterprise-corp',
  domain: 'enterprise.com',
  plan_type: 'enterprise',
  settings: {
    timezone: 'UTC',
    retention_days: 365,
    alert_threshold: 'medium',
    compliance_frameworks: ['NIST', 'SOC2', 'ISO27001']
  }
};

// Initialize organization in WatchLockAI console
await supabase
  .from('organizations')
  .insert(orgConfig);
```

#### **User Management Setup**
```sql
-- Create organization users
INSERT INTO user_profiles (organization_id, email, full_name, role, department) VALUES
('org_enterprise_001', 'admin@enterprise.com', 'Security Administrator', 'admin', 'IT Security'),
('org_enterprise_001', 'analyst@enterprise.com', 'Security Analyst', 'analyst', 'SOC Team'),
('org_enterprise_001', 'viewer@enterprise.com', 'Compliance Officer', 'viewer', 'Compliance');

-- Configure role-based policies
INSERT INTO policies (organization_id, name, policy_type, rules, applied_agents) VALUES
('org_enterprise_001', 'Enterprise Security Policy', 'comprehensive', 
 '{"real_time_monitoring": true, "automated_response": true, "compliance_logging": true}',
 ['all_agents']);
```

### 3. Integration Configuration

#### **SIEM Integration (Splunk)**
```conf
# inputs.conf - Splunk configuration for WatchLockAI
[monitor://C:\Program Files\WatchLockAI\logs\*.json]
disabled = false
index = security
sourcetype = watchlockai:json
host_regex = (.*)
crcSalt = <SOURCE>

# transforms.conf - Field extraction
[watchlockai_json]
REGEX = "timestamp":"([^"]+)".*"event_type":"([^"]+)".*"severity":"([^"]+)"
FORMAT = timestamp::$1 event_type::$2 severity::$3
```

#### **Microsoft Defender Integration**
```powershell
# Configure Windows Defender exclusions for WatchLockAI
Add-MpPreference -ExclusionPath "C:\Program Files\WatchLockAI"
Add-MpPreference -ExclusionProcess "WatchLockAI.Service.exe"
Add-MpPreference -ExclusionProcess "WatchLockAI.SystemTray.exe"

# Configure Windows Defender Advanced Threat Protection integration
$defenderConfig = @{
    TenantId = "your-tenant-id"
    AppId = "your-app-id"
    AppSecret = "your-app-secret"
    IntegrationEnabled = $true
}

Set-Content -Path "C:\Program Files\WatchLockAI\config\defender-integration.json" -Value ($defenderConfig | ConvertTo-Json)
```

## Deployment Validation

### 1. Functional Testing

#### **Agent Functionality Test**
```powershell
# Test agent functionality
$testScript = @'
# Simulate threat detection test
$testThreat = @{
    process_name = "test_malware.exe"
    command_line = "test_malware.exe -payload evil"
    parent_process = "explorer.exe"
    threat_level = "test"
}

# Send test event to agent
Invoke-RestMethod -Uri "http://localhost:8080/api/test/threat" -Method POST -Body ($testThreat | ConvertTo-Json) -ContentType "application/json"
'@

Invoke-Expression $testScript
```

#### **Console Accessibility Test**
```javascript
// Web console functionality test
async function testConsoleAccess() {
    try {
        // Test authentication
        const authResponse = await fetch('/api/auth/test', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({test_mode: true})
        });
        
        // Test dashboard data
        const dashboardResponse = await fetch('/api/dashboard/status');
        
        // Test real-time connections
        const ws = new WebSocket('ws://localhost:8080/realtime');
        ws.onopen = () => console.log('Real-time connection established');
        
        return {
            auth: authResponse.ok,
            dashboard: dashboardResponse.ok,
            realtime: ws.readyState === WebSocket.OPEN
        };
    } catch (error) {
        console.error('Console test failed:', error);
        return false;
    }
}
```

### 2. Performance Validation

#### **Resource Usage Monitoring**
```powershell
# Monitor WatchLockAI performance
$performanceCounters = @(
    "\Process(WatchLockAI.Service)\% Processor Time",
    "\Process(WatchLockAI.Service)\Working Set",
    "\Process(WatchLockAI.Service)\Private Bytes"
)

$performance = Get-Counter -Counter $performanceCounters -SampleInterval 5 -MaxSamples 12

$performance.CounterSamples | Group-Object Path | ForEach-Object {
    $counterName = $_.Name
    $avgValue = ($_.Group | Measure-Object CookedValue -Average).Average
    Write-Host "$counterName : $avgValue"
}
```

### 3. Security Validation

#### **Compliance Check**
```powershell
# Validate security configuration
$securityChecks = @{
    'Service Running as System' = (Get-WmiObject Win32_Service -Filter "Name='WatchLockAI'").StartName -eq 'LocalSystem'
    'HTTPS Enabled' = Test-NetConnection -ComputerName localhost -Port 443 -InformationLevel Quiet
    'Audit Logging Enabled' = Test-Path "C:\Program Files\WatchLockAI\logs\audit.log"
    'Encryption Configured' = Test-Path "C:\Program Files\WatchLockAI\config\encryption.key"
}

$securityChecks.GetEnumerator() | ForEach-Object {
    $status = if ($_.Value) { "PASS" } else { "FAIL" }
    Write-Host "$($_.Key): $status"
}
```

## Deployment Troubleshooting

### 1. Common Installation Issues

#### **PowerShell Execution Policy**
```powershell
# Issue: Installation fails due to execution policy
# Solution: Temporarily modify execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Alternative: Bypass for specific script
powershell.exe -ExecutionPolicy Bypass -File "WatchLockAI-REAL-Installer.bat"
```

#### **Python Detection Issues**
```powershell
# Issue: Microsoft Store redirect preventing Python detection
# Solution: Disable Python app execution aliases
# Manual: Settings > Apps > Advanced app settings > App execution aliases
# Automated:
Remove-Item -Path "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe" -Force -ErrorAction SilentlyContinue
```

#### **Service Registration Failures**
```powershell
# Issue: Service fails to register
# Solution: Clean previous installations and retry
sc delete WatchLockAI
Remove-Item -Path "HKLM:\SOFTWARE\WatchLockAI" -Recurse -Force -ErrorAction SilentlyContinue
& "WatchLockAI-REAL-Installer.bat"
```

### 2. Network Connectivity Issues

#### **Supabase Connection Testing**
```powershell
# Test Supabase connectivity
$supabaseUrl = "https://iozahbnaeaccvjyjljmv.supabase.co"
$testEndpoints = @(
    "$supabaseUrl/rest/v1/",
    "$supabaseUrl/auth/v1/health",
    "$supabaseUrl/realtime/v1/"
)

foreach ($endpoint in $testEndpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 10
        Write-Host "$endpoint : OK ($($response.StatusCode))"
    } catch {
        Write-Warning "$endpoint : FAILED ($($_.Exception.Message))"
    }
}
```

### 3. Performance Issues

#### **Resource Optimization**
```powershell
# Optimize WatchLockAI performance
# Increase service priority
sc config WatchLockAI start= auto
sc failure WatchLockAI reset= 86400 actions= restart/60000/restart/60000/restart/60000

# Configure memory limits
$servicePath = "HKLM:\SYSTEM\CurrentControlSet\Services\WatchLockAI"
Set-ItemProperty -Path $servicePath -Name "MemoryLimit" -Value 268435456  # 256MB

# Configure CPU priority
Set-ItemProperty -Path $servicePath -Name "PriorityClass" -Value 2  # High priority
```

## Enterprise Support and Maintenance

### 1. Monitoring and Alerting

#### **Performance Monitoring Setup**
```powershell
# Configure performance monitoring
$monitoringScript = @'
$perfCounters = @(
    "\Process(WatchLockAI.Service)\% Processor Time",
    "\Process(WatchLockAI.Service)\Working Set"
)

$sampleInterval = 300  # 5 minutes
$alertThresholds = @{
    CPU = 80      # 80% CPU
    Memory = 200  # 200MB
}

while ($true) {
    $samples = Get-Counter -Counter $perfCounters -SampleInterval 1 -MaxSamples 1
    
    foreach ($sample in $samples.CounterSamples) {
        $counterName = $sample.Path.Split('\')[-1]
        $value = $sample.CookedValue
        
        if ($counterName -like "*Processor Time*" -and $value -gt $alertThresholds.CPU) {
            Write-EventLog -LogName Application -Source "WatchLockAI-Monitor" -EventId 1001 -EntryType Warning -Message "High CPU usage: $value%"
        }
        
        if ($counterName -like "*Working Set*" -and ($value / 1MB) -gt $alertThresholds.Memory) {
            Write-EventLog -LogName Application -Source "WatchLockAI-Monitor" -EventId 1002 -EntryType Warning -Message "High memory usage: $([math]::Round($value / 1MB, 2)) MB"
        }
    }
    
    Start-Sleep -Seconds $sampleInterval
}
'@

# Create scheduled task for monitoring
$taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -Command `"$monitoringScript`""
$taskTrigger = New-ScheduledTaskTrigger -AtStartup
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "WatchLockAI-Monitor" -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -User "SYSTEM"
```

### 2. Update Management

#### **Automated Update Process**
```powershell
# Automated update script
param(
    [string]$UpdateServerUrl = "https://updates.watchlockai.com",
    [string]$CurrentVersion = "1.0.0"
)

# Check for updates
$updateInfo = Invoke-RestMethod -Uri "$UpdateServerUrl/api/check-update" -Method POST -Body @{
    current_version = $CurrentVersion
    platform = "windows11"
} | ConvertTo-Json

if ($updateInfo.update_available) {
    Write-Host "Update available: $($updateInfo.latest_version)"
    
    # Download update package
    $updatePackage = "$env:TEMP\WatchLockAI-Update-$($updateInfo.latest_version).zip"
    Invoke-WebRequest -Uri $updateInfo.download_url -OutFile $updatePackage
    
    # Verify update integrity
    $downloadHash = Get-FileHash -Path $updatePackage -Algorithm SHA256
    if ($downloadHash.Hash -eq $updateInfo.sha256_hash) {
        Write-Host "Update package verified successfully"
        
        # Stop service
        Stop-Service -Name "WatchLockAI" -Force
        
        # Apply update
        Expand-Archive -Path $updatePackage -DestinationPath "C:\Program Files\WatchLockAI" -Force
        
        # Start service
        Start-Service -Name "WatchLockAI"
        
        Write-Host "Update applied successfully"
    } else {
        Write-Error "Update package verification failed"
    }
} else {
    Write-Host "No updates available"
}
```

This comprehensive deployment guide ensures successful enterprise-scale implementation of the WatchLockAI cybersecurity platform across Windows 11 environments with proper configuration, validation, and ongoing maintenance procedures.
