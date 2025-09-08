# WatchSleuth Forensic Engine

## 🔍 Overview

WatchSleuth is an advanced digital forensics and incident investigation engine inspired by Autopsy/Sleuthkit functionality with AI-enhanced analysis capabilities. It provides comprehensive forensic analysis tools for Windows environments.

## 🎯 Core Capabilities

### **File System Forensics**
- **MFT Analysis** - Master File Table parsing and timeline reconstruction
- **Shadow Copy Analysis** - Volume Shadow Service snapshot examination
- **Deleted File Carving** - Recovery of deleted files using signature-based carving

### **System Forensics**
- **Registry Analysis** - Windows registry hive examination and persistence detection
- **Event Log Analysis** - Windows Event Log (EVTX) parsing and correlation
- **Prefetch Analysis** - Windows Prefetch file analysis for execution artifacts

### **Communication Forensics**
- **Email Analysis** - PST, EML, and MSG file parsing
- **Browser Forensics** - Web browser history and artifact analysis
- **Network Artifacts** - Network connection and traffic analysis

### **Advanced Analysis**
- **Timeline Analysis** - Comprehensive timeline creation and event correlation
- **Attack Pattern Detection** - MITRE ATT&CK-based attack sequence identification
- **Chain of Custody** - Complete evidence handling and documentation

## 🚀 Quick Start

### **Installation**
```bash
pip install -r requirements.txt
```

### **Start Investigation**
```python
from watchsleuth_engine import WatchSleuthForensicEngine

# Initialize engine
engine = WatchSleuthForensicEngine("./my_case")

# Start investigation
case_id = engine.start_investigation(
    "Security Incident 2025-001",
    "Forensic Analyst",
    "Investigation of suspected data breach"
)

# Add evidence
artifact_id = engine.add_evidence(
    "/path/to/evidence.dd",
    "Disk image from compromised system"
)

# Perform analysis
results = engine.perform_comprehensive_analysis(case_id)

# Export report
engine.export_case_report(case_id, "investigation_report.json")
```

## 🛠️ Forensic Tools

### **Command Line Interface**
```bash
# MFT Analysis
python forensic_tools.py mft /path/to/mft -o mft_analysis.json

# Registry Analysis
python forensic_tools.py registry /path/to/SYSTEM -o registry_analysis.json

# Browser Analysis
python forensic_tools.py browser /path/to/History --type chrome -o browser_analysis.json

# Full Investigation
python forensic_tools.py investigate /evidence/dir --name "Case 2025-001" --investigator "John Doe"
```

### **Timeline Analysis**
```python
from timeline_analysis import TimelineVisualizer, EventCorrelator

# Create visual timeline
visualizer = TimelineVisualizer()
visualizer.load_timeline_data('timeline.json')
visualizer.create_timeline_chart('timeline.png', hours=24)
visualizer.create_activity_heatmap('heatmap.png')

# Correlate events
correlator = EventCorrelator()
correlator.load_events(events)
clusters = correlator.find_event_clusters(time_window_minutes=5)
attack_analysis = correlator.analyze_attack_sequence()
```

## 📊 Analysis Capabilities

### **MFT (Master File Table) Analysis**
- File creation, modification, access timestamps
- Deleted file metadata recovery
- File system timeline reconstruction
- NTFS attribute analysis

### **Registry Forensics**
- Autostart persistence mechanism detection
- User activity reconstruction
- System configuration analysis
- Malware registry artifact identification

### **Browser Forensics**
- Visited URL extraction and analysis
- Download history reconstruction
- Search query analysis
- Suspicious website identification

### **Email Forensics**
- Email metadata extraction
- Attachment analysis
- Communication pattern analysis
- Phishing email detection

## 🎯 Investigation Workflow

### **1. Case Initialization**
```python
case_id = engine.start_investigation(case_name, investigator, description)
```

### **2. Evidence Collection**
```python
# Add various evidence types
engine.add_evidence("disk_image.dd", "Primary system disk")
engine.add_evidence("memory_dump.mem", "System memory dump")
engine.add_evidence("network_capture.pcap", "Network traffic")
```

### **3. Comprehensive Analysis**
```python
results = engine.perform_comprehensive_analysis(case_id)
```

### **4. Timeline Creation**
- Automatic timeline generation from all evidence sources
- Event correlation and clustering
- Attack sequence identification

### **5. Report Generation**
```python
engine.export_case_report(case_id, "final_report.json")
```

## 📈 Advanced Features

### **AI-Enhanced Analysis**
- Behavioral pattern recognition
- Anomaly detection in timeline events
- Automated attack chain reconstruction
- Machine learning-based artifact classification

### **Integration Capabilities**
- Export to MISP (Malware Information Sharing Platform)
- STIX/TAXII threat intelligence integration
- Integration with WatchLockAI threat detection

### **Visualization Tools**
- Interactive timeline charts
- Activity heatmaps
- Network relationship graphs
- Attack vector visualizations

## 🔧 Configuration

### **Evidence Templates**
```json
{
  "common_artifacts": {
    "windows_locations": {
      "prefetch": "C:\Windows\Prefetch\*.pf",
      "event_logs": "C:\Windows\System32\winevt\Logs\*.evtx",
      "registry_hives": [
        "C:\Windows\System32\config\SYSTEM",
        "C:\Windows\System32\config\SOFTWARE"
      ]
    }
  }
}
```

### **Chain of Custody**
All evidence handling includes:
- MD5 and SHA256 hash verification
- Timestamped custody transfers
- Complete audit trail
- Evidence integrity validation

## 🧪 Testing

```bash
python test_forensics.py
```

## 📝 Case Report Format

```json
{
  "case_information": {
    "case_id": "case_20250101_120000",
    "generated_at": "2025-01-01T12:00:00",
    "tool": "WatchSleuth Forensic Engine v1.0"
  },
  "executive_summary": {
    "findings_count": 15,
    "evidence_processed": 342,
    "key_findings": [
      "Potential persistence mechanisms detected",
      "Suspicious web browsing activity identified"
    ]
  },
  "detailed_analysis": {
    "mft_analysis": {...},
    "registry_analysis": {...},
    "timeline": [...],
    "findings": [...]
  }
}
```

## 🔒 Security Considerations

- All evidence handling maintains chain of custody
- Hash verification for integrity validation
- Secure evidence storage and access controls
- Audit logging of all forensic activities

## 🤝 Integration with WatchLockAI

WatchSleuth integrates seamlessly with the WatchLockAI ecosystem:
- **Real-time Analysis** - Live forensic artifact collection during incident response
- **AI Correlation** - Cross-reference findings with AI threat detection
- **Automated Investigation** - Triggered forensic analysis based on AI alerts
- **Unified Reporting** - Combined threat intelligence and forensic findings

---

**WatchSleuth Forensic Engine** - Professional digital forensics for the modern enterprise.
