# WatchLockAI Windows Agent Core

## [U+1F5A5] Overview

The WatchLockAI Windows Agent Core provides real-time monitoring and protection for Windows systems. It monitors file system activities, process execution, network connections, and registry changes to detect and respond to security threats.

## [TARGET] Core Capabilities

### **Real-time Monitoring**
- **File System Monitor** - Track file creation, modification, and deletion
- **Process Monitor** - Monitor process creation and termination
- **Network Monitor** - Analyze network connections and traffic
- **Registry Monitor** - Detect registry changes and persistence mechanisms
- **Browser Monitor** - Monitor web browsing activities for threats

### **AI Integration**
- **Event Analysis** - All events sent to AI Brain for intelligent analysis
- **Threat Detection** - AI-powered threat classification and response
- **Behavioral Analysis** - Machine learning-based anomaly detection
- **Real-time Response** - Automated threat response actions

## [START] Quick Start

### **Installation**
```bash
pip install -r requirements.txt
```

### **Configuration**
Edit `agent_config.json` to customize monitoring settings:
```json
{
  "ai_brain_url": "http://localhost:9999",
  "monitoring_enabled": {
    "file_system": true,
    "processes": true,
    "network": true,
    "registry": true,
    "browser": true
  },
  "reporting_interval": 300
}
```

### **Run as Console Application**
```bash
python windows_agent_core.py
```

### **Run as Windows Service**
```bash
# Install service
python agent_service.py install

# Start service
python agent_service.py start

# Stop service
python agent_service.py stop

# Uninstall service
python agent_service.py uninstall
```

## [SEARCH] Monitoring Components

### **File System Monitor**
- Monitors critical system directories
- Detects suspicious file modifications
- Analyzes file hashes and metadata
- Identifies malware and unauthorized changes

**Monitored Locations:**
- `C:\Windows\System32`
- `C:\Program Files`
- `C:\Program Files (x86)`
- `C:\Users`

### **Process Monitor**
- Tracks process creation and termination
- Analyzes command line arguments
- Detects suspicious processes and patterns
- Monitors process injection and hollowing

**Detected Threats:**
- Known malware processes
- Suspicious command line patterns
- Process spawning from unusual locations
- Encoded PowerShell commands

### **Network Monitor**
- Monitors network connections
- Analyzes traffic patterns
- Detects C2 communications
- Identifies suspicious destinations

**Detection Capabilities:**
- Suspicious port connections
- Unusual IP addresses
- Network beaconing patterns
- Unauthorized external connections

### **Registry Monitor**
- Monitors persistence mechanisms
- Detects malicious registry entries
- Tracks autostart locations
- Identifies configuration changes

**Monitored Keys:**
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- `HKLM\SYSTEM\CurrentControlSet\Services`

### **Browser Monitor**
- Monitors web browsing activities
- Detects malicious websites
- Analyzes download patterns
- Identifies phishing attempts

**Browser Support:**
- Google Chrome
- Mozilla Firefox
- Microsoft Edge

## [U+1F527] Configuration Options

### **Monitoring Settings**
```json
{
  "monitoring_enabled": {
    "file_system": true,    // Enable file system monitoring
    "processes": true,      // Enable process monitoring
    "network": true,        // Enable network monitoring
    "registry": true,       // Enable registry monitoring
    "browser": true         // Enable browser monitoring
  }
}
```

### **Alert Thresholds**
```json
{
  "alert_thresholds": {
    "process_creation_rate": 10,     // Max processes per minute
    "network_connections_rate": 20,  // Max connections per minute
    "file_modifications_rate": 50    // Max file changes per minute
  }
}
```

### **Ignored Processes**
```json
{
  "ignored_processes": [
    "System", "Idle", "Registry", "smss.exe",
    "csrss.exe", "wininit.exe", "services.exe"
  ]
}
```

## [BARS] Event Types

### **File System Events**
- `file_created` - New file created
- `file_modified` - Existing file modified
- `file_deleted` - File deleted
- `file_suspicious` - Suspicious file activity

### **Process Events**
- `process_created` - New process started
- `process_terminated` - Process ended
- `process_suspicious` - Suspicious process behavior

### **Network Events**
- `network_connection` - New network connection
- `network_suspicious` - Suspicious network activity

### **Registry Events**
- `registry_modified` - Registry key/value changed
- `registry_suspicious` - Suspicious registry activity

## [LOCK] Security Features

### **Tamper Protection**
- Self-monitoring capabilities
- Integrity verification
- Protected configuration
- Secure communication with AI Brain

### **Stealth Operation**
- Low resource footprint
- Minimal system impact
- Background operation
- Silent monitoring mode

## [U+1F9EA] Testing

```bash
python test_agent.py
```

**Test Coverage:**
- File system monitoring
- Process monitoring
- Network monitoring
- Configuration loading
- Event reporting
- Browser monitoring
- Integration tests

## [CHART] Performance

### **Resource Usage**
- **CPU Usage:** < 5% average
- **Memory Usage:** < 100MB average
- **Disk I/O:** Minimal impact
- **Network:** Lightweight reporting

### **Scalability**
- Supports enterprise deployments
- Central management via AI Brain
- Configurable monitoring intensity
- Optimized for 24/7 operation

## [U+1F527] Troubleshooting

### **Common Issues**

**Agent won't start:**
```bash
# Check Python installation
python --version

# Verify dependencies
pip install -r requirements.txt

# Check permissions
# Run as Administrator if needed
```

**Service installation fails:**
```bash
# Install pywin32
pip install pywin32

# Run as Administrator
python agent_service.py install
```

**AI Brain connection issues:**
```bash
# Verify AI Brain is running
curl http://localhost:9999/health

# Check configuration
# Verify ai_brain_url in agent_config.json
```

## [RELOAD] Integration with WatchLockAI

The Windows Agent integrates seamlessly with other WatchLockAI components:

- **AI Brain** - Sends all events for intelligent analysis
- **WatchSleuth Forensics** - Provides evidence for investigations
- **Management Console** - Centralized monitoring and control
- **Tamperproofing** - Protected against disable attempts

## [U+1F4DD] Logging

Agent activities are logged to:
- `watchlockai_agent.log` - Main agent log
- `watchlockai_service.log` - Service-specific log
- Windows Event Log (when running as service)

**Log Levels:**
- **INFO** - Normal operations
- **WARNING** - Potential threats detected
- **ERROR** - System errors and failures
- **DEBUG** - Detailed monitoring information

---

**WatchLockAI Windows Agent** - Real-time protection for the modern enterprise.
