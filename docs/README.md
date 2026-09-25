# WatchLockAI Endpoint Security Agent

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
.\Install-WatchLockAI.ps1 -ConsoleEndpoint "https://your-console.domain.com"
```

### Silent Installation
```powershell
# Run as Administrator
.\Install-WatchLockAI.ps1 -ConsoleEndpoint "https://console.watchlockai.com" -Silent
```

## Configuration

### Main Configuration File
Location: `C:\Program Files\WatchLockAI\Config\appsettings.json`

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
- **Service Logs**: `C:\Program Files\WatchLockAI\Logs\`
- **Windows Event Log**: Application Log, Source: "WatchLockAI"
- **Evidence Storage**: `C:\Program Files\WatchLockAI\Evidence\`

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
- `C:\Program Files\WatchLockAI\`
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
Get-Content "C:\Program Files\WatchLockAI\Logs\*.log" | Select-Object -Last 100

# Check Windows Event Log
Get-EventLog -LogName Application -Source "WatchLockAI" -Newest 50
```

## Uninstallation

### Standard Uninstallation
```powershell
# Run as Administrator
.\Uninstall-WatchLockAI.ps1
```

### Force Uninstallation (removes all data)
```powershell
# Run as Administrator
.\Uninstall-WatchLockAI.ps1 -Force
```

## Support

### Documentation
- Installation Guide: `docs\deployment\installation-guide.md`
- Administrator Guide: `docs\deployment\admin-guide.md`
- API Documentation: `docs\api\`

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
