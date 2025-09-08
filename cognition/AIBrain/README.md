# WatchLockAI - Agentic AI Brain

## 🧠 Overview

The WatchLockAI Agentic AI Brain is the core intelligence system for autonomous threat detection and response. It implements:

- **Behavioral Modeling** - Learns normal user and system patterns
- **MITRE ATT&CK Integration** - Maps threats to known tactics and techniques  
- **Anti-Pentester Logic** - Differentiates between real threats and security testing
- **Fog-of-War Memory** - Staged memory model for efficient processing
- **Agentic Decision Making** - Autonomous threat assessment and response recommendations

## 🚀 Quick Start

1. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start AI Brain**:
   ```bash
   python ai_brain_core.py
   ```
   Or use the launcher:
   ```bash
   start_ai_brain.bat
   ```

3. **Test Functionality**:
   ```bash
   python test_ai_brain.py
   ```

## 📡 API Endpoints

- `GET /health` - Health check
- `GET /status` - AI Brain status and statistics
- `POST /analyze` - Analyze security event
- `POST /feedback` - Provide learning feedback

## 🔍 Event Analysis

The AI Brain analyzes security events using multiple techniques:

### MITRE ATT&CK Integration
Maps events to known attack techniques:
- T1059: Command and Scripting Interpreter
- T1055: Process Injection  
- T1003: OS Credential Dumping
- T1082: System Information Discovery

### Behavioral Analysis
- User activity patterns
- Temporal analysis (time-of-day, day-of-week)
- Process execution patterns
- Network communication patterns

### Anti-Pentester Logic
Detects authorized security testing:
- Known penetration testing tools
- Red team frameworks
- Security simulation platforms

## 🧮 Machine Learning

Uses advanced ML techniques:
- **Isolation Forest** for anomaly detection
- **Feature Engineering** from security events
- **Behavioral Baselining** with continuous learning
- **Adaptive Thresholds** based on environment

## 🔒 Security Features

- **Tamperproof Design** - Self-monitoring and protection
- **Encrypted Communication** - Secure API endpoints
- **Audit Logging** - Complete analysis trail
- **Memory Protection** - Fog-of-war data handling

## 📊 Example Usage

```python
import requests

# Analyze a security event
event = {
    "timestamp": "2025-01-01T12:00:00",
    "event_type": "powershell_execution",
    "source": "Windows",
    "details": {
        "command": "powershell.exe -encodedcommand abc123",
        "user": "admin"
    },
    "threat_level": "medium"
}

response = requests.post("http://localhost:9999/analyze", json=event)
analysis = response.json()

print(f"Threat detected: {analysis['threat_detected']}")
print(f"Narrative: {analysis['narrative']}")
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Agentic AI Brain              │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ MITRE       │  │ Behavioral      │   │
│  │ ATT&CK      │  │ Baseline        │   │
│  │ Engine      │  │ Engine          │   │
│  └─────────────┘  └─────────────────┘   │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Anti-       │  │ Memory          │   │
│  │ Pentester   │  │ Management      │   │
│  │ Logic       │  │ (Fog-of-War)    │   │
│  └─────────────┘  └─────────────────┘   │
├─────────────────────────────────────────┤
│           HTTP API Server               │
└─────────────────────────────────────────┘
```

## 🔧 Configuration

The AI Brain is self-configuring but can be tuned:

- **Port**: Default 9999 (configurable)
- **Database**: SQLite for persistence
- **Memory Layers**: Automatic fog-of-war management
- **ML Models**: Auto-training with minimum 10 samples

## 📈 Monitoring

Monitor AI Brain health:
- Check `/status` endpoint for statistics
- Review `ai_brain.log` for detailed logs
- Monitor memory usage and database size
- Track threat detection accuracy

## 🚀 Production Deployment

For production use:
1. Configure reverse proxy (nginx/IIS)
2. Set up SSL/TLS certificates
3. Implement authentication/authorization
4. Configure log rotation
5. Set up monitoring and alerting
6. Regular database maintenance

---

**WatchLockAI Agentic AI Brain** - Autonomous cybersecurity intelligence for the modern enterprise.
