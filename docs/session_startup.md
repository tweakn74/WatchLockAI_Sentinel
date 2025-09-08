# Session Startup Guide

This runbook covers environment setup, baseline validation, and component testing for development sessions.

## Environment Preparation

### Python Environment Setup

```bash
# Navigate to repository root
cd /workspace/WatchLockAI_Sentinel

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-test.txt

# Verify installation
python -c "import app_core.bus; print('Core modules OK')"
```

### Platform-Specific Setup

#### Linux Development Environment
```bash
# Install system monitoring dependencies
sudo apt-get update
sudo apt-get install -y python3-dev

# Note: Windows-only modules will be mocked
echo "Platform guards active for Linux development"
```

#### Windows Production Environment
```bash
# Install Windows-specific dependencies
pip install pywin32 pywin32-ctypes

# Verify Windows modules
python -c "import win32api; print('Windows modules OK')"
```

## Canonical Baseline Commands

Run these commands from the repository root to establish current system state:

```bash
# Diagnostic baseline (exact commands)
ruff check . --output-format=json > /tmp/ruff.json || true
pyright --project . --outputjson > /tmp/pyright.json || true
pytest -q > /tmp/pytest.txt || true

# Compute canonical counts
python3 /workspace/compute_master_baselines.py

# Compare with recorded baseline
cat DOCS/baselines.txt
```

### Expected Baseline Results
- **Ruff issues**: 0 (clean codebase)
- **Pyright errors**: Variable (platform-dependent)
- **Pytest status**: Depends on available dependencies

## Platform Guard Notes

### Windows-Only Modules
| Module | Purpose | Linux Fallback |
|---|---|---|
| `winreg` | Registry access | Mock/stub implementation |
| `win32service` | Service management | Graceful error messages |
| `win32api` | Windows API calls | Platform detection + skip |

### Guard Pattern Examples
```python
# Platform detection
import platform
IS_WINDOWS = platform.system() == "Windows"

# Conditional imports
try:
    import winreg
except ImportError:
    winreg = None  # Use mock or skip functionality

# Runtime checks
if IS_WINDOWS and winreg:
    # Windows-specific implementation
    pass
else:
    # Cross-platform or degraded implementation
    pass
```

## Component Startup

### 1. Core System Startup

```bash
# Test core event bus
python -c "
from app_core.bus import EventBus
from app_core.config import SentinelConfig

config = SentinelConfig.load_from_file('config.yaml')
bus = EventBus()
print('Core system: OK')
"
```

### 2. Configuration Validation

```bash
# Validate configuration files
python -c "
from app_core.config import SentinelConfig
try:
    config = SentinelConfig.load_from_file('config.yaml')
    print(f'Config loaded: {config.version}')
except Exception as e:
    print(f'Config error: {e}')
"
```

### 3. Start Web Console/API

```bash
# Start development web server
python -m uvicorn console.web_api:app --reload --port 8000

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/status
```

### 4. Start Full System

```bash
# Run the complete sentinel application
python app.py

# Check logs for component initialization
tail -f logs/sentinel.log
```

## Smoke Test Procedure

### Quick Health Check
```bash
# 1. Import all major modules
python -c "
import app_core.bus
import collectors.fs_monitor
import detection.rules_engine
import response.actions
print('All modules importable')
"

# 2. Configuration loads
python -c "
from app_core.config import SentinelConfig
config = SentinelConfig.load_from_file('config.yaml')
print(f'Config version: {config.version}')
"

# 3. Event bus basic functionality
python -c "
from app_core.bus import EventBus
from app_core.schemas import HealthMetric

bus = EventBus()
event = HealthMetric(component='test', status='healthy', timestamp=1.0)
print('Event bus: OK')
"
```

### Event Bus Quick Probe
```python
#!/usr/bin/env python3
# File: smoke_test_event_bus.py

import asyncio
from app_core.bus import EventBus
from app_core.schemas import HealthMetric

async def test_event_flow():
    bus = EventBus()
    
    # Create test subscriber
    received_events = []
    
    async def test_subscriber(event):
        received_events.append(event)
    
    # Subscribe and publish
    bus.subscribe(HealthMetric, test_subscriber)
    
    test_event = HealthMetric(
        component="smoke_test",
        status="healthy",
        timestamp=1.0
    )
    
    await bus.publish(test_event)
    await asyncio.sleep(0.1)  # Allow event processing
    
    assert len(received_events) == 1
    assert received_events[0].component == "smoke_test"
    print("Event bus smoke test: PASSED")

if __name__ == "__main__":
    asyncio.run(test_event_flow())
```

## Troubleshooting Table

| Issue | Symptom | Solution |
|---|---|---|
| **win32/pywin not present** | `ImportError: No module named 'win32api'` | Install `pip install pywin32` or run on Windows |
| **Missing deps** | `ModuleNotFoundError` for loguru, pydantic, etc. | Run `pip install -r requirements.txt` |
| **Platform stubs** | Pyright errors on Windows imports | Add type stubs or improve conditional imports |
| **Config not found** | `FileNotFoundError: config.yaml` | Copy `config.yaml.example` to `config.yaml` |
| **Port already in use** | Web API won't start on 8000 | Change port: `uvicorn console.web_api:app --port 8001` |
| **Permissions error** | File/registry access denied | Run as administrator (Windows) or check file permissions |
| **Event bus timeout** | Components not receiving events | Check async context and event loop setup |
| **Pyright strict errors** | Type checking failures | Add type annotations or proper type guards |

### Common Linux Development Issues

```bash
# Issue: Windows registry imports fail
# Solution: Check platform guards
grep -r "import winreg" . --include="*.py"
# Ensure all winreg imports are properly guarded

# Issue: Service wrapper won't start
# Solution: Mock Windows service behavior
echo "Skip service installation on Linux development"

# Issue: Process monitoring behaves differently
# Solution: Use psutil cross-platform APIs consistently
```

### Diagnostic Commands

```bash
# Check Python environment
python --version
pip list | grep -E "(pydantic|loguru|psutil|fastapi)"

# Check platform detection
python -c "import platform; print(f'Platform: {platform.system()}')"

# Check file permissions
ls -la config.yaml
ls -la logs/

# Check network ports
netstat -tlnp | grep 8000  # Linux
netstat -an | findstr 8000  # Windows
```

## Session Teardown

```bash
# Stop running services
killall -9 python  # Linux (careful!)
# Or use Ctrl+C for graceful shutdown

# Check for leftover processes
ps aux | grep python

# Deactivate virtual environment
deactivate
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-02T20:31:09+00:00  
**Author**: MiniMax Agent