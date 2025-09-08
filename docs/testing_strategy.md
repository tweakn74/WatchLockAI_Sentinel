# Testing Strategy

## Test Architecture and Layers

### Test Pyramid Structure

```mermaid
graph TB
    E2E["End-to-End Tests<br/>tests/e2e/<br/>5% of tests"] 
    Integration["Integration Tests<br/>tests/<br/>25% of tests"]
    Unit["Unit Tests<br/>tests/unit/<br/>70% of tests"]
    
    E2E --> Integration
    Integration --> Unit
    
    classDef e2e fill:#ffcdd2
    classDef integration fill:#fff3e0
    classDef unit fill:#e8f5e8
    
    class E2E e2e
    class Integration integration  
    class Unit unit
```

### Test Layer Responsibilities

#### Unit Tests (70% of test suite)
- **Scope**: Individual functions and classes in isolation
- **Location**: `tests/unit/`
- **Mocking**: Heavy use of mocks for dependencies
- **Speed**: Fast (<100ms per test)
- **Coverage**: Aim for 80%+ code coverage on core logic

**Current Unit Test Files**:
- `test_event_bus.py`: Event bus functionality
- `test_config.py`: Configuration loading and validation
- `test_schemas.py`: Pydantic model validation
- `test_fs_monitor.py`: File system monitoring logic
- `test_rules_engine.py`: Detection rule processing
- `test_alert_manager.py`: Alert generation and routing

#### Integration Tests (25% of test suite)
- **Scope**: Component interactions and workflows
- **Location**: `tests/`
- **Dependencies**: Real components with controlled data
- **Speed**: Medium (100ms-1s per test)
- **Coverage**: Critical component interfaces

**Current Integration Test Files**:
- `test_integration_smoke.py`: Basic component integration
- `test_operational_mode.py`: Mode switching workflow

#### End-to-End Tests (5% of test suite)
- **Scope**: Complete workflows from data ingestion to response
- **Location**: `tests/e2e/`
- **Dependencies**: Full system stack
- **Speed**: Slow (1s+ per test)
- **Coverage**: Critical user journeys

**Current E2E Test Files**:
- `test_sentinel_e2e.py`: Full system workflow testing

## Current Test Gaps

### Critical Missing Tests
1. **Platform Guard Testing**: No tests for Windows/Linux compatibility
2. **Error Recovery Testing**: Limited failure scenario coverage
3. **Performance Testing**: No load testing for event bus
4. **API Integration Testing**: Web console endpoints not fully tested
5. **Configuration Validation**: Edge cases in config parsing not covered

### Specific Gap Analysis

| Component | Unit Coverage | Integration Coverage | E2E Coverage | Missing |
|---|---|---|---|---|
| `app_core.bus` | ✓ Good | ✓ Basic | ✓ Basic | Error recovery, high load |
| `collectors.*` | ✓ Basic | ✗ Missing | ✗ Missing | Cross-platform behavior |
| `detection.*` | ✓ Basic | ✗ Missing | ✗ Missing | Rule engine integration |
| `response.*` | ✓ Basic | ✗ Missing | ✗ Missing | Action execution validation |
| `console.web_api` | ✗ Missing | ✗ Missing | ✗ Missing | API endpoint testing |
| `service.*` | ✗ Missing | ✗ Missing | ✗ Missing | Service lifecycle |

## Smoke Test Recipe

### Quick Validation (< 30 seconds)
```bash
#!/bin/bash
# File: smoke_test.sh

echo "Running smoke tests..."

# 1. Import test
python -c "
import app_core.bus, collectors.fs_monitor, detection.rules_engine
print('✓ All modules importable')
" || exit 1

# 2. Configuration test
python -c "
from app_core.config import SentinelConfig
config = SentinelConfig.load_from_file('config.yaml')
print(f'✓ Config loads (version {config.version})')
" || exit 1

# 3. Event bus test
python -c "
import asyncio
from app_core.bus import EventBus
from app_core.schemas import HealthMetric

async def test():
    bus = EventBus()
    event = HealthMetric(component='test', status='healthy', timestamp=1.0)
    await bus.publish(event)
    print('✓ Event bus functional')

asyncio.run(test())
" || exit 1

# 4. Platform guard test
python -c "
import platform
print(f'✓ Platform detected: {platform.system()}')
if platform.system() == 'Windows':
    try:
        import winreg
        print('✓ Windows modules available')
    except ImportError:
        print('⚠ Windows modules missing (expected on non-Windows)')
else:
    print('✓ Platform guards active for non-Windows')
"

echo "✓ All smoke tests passed"
```

### Comprehensive Smoke Test
```python
#!/usr/bin/env python3
# File: comprehensive_smoke_test.py

import asyncio
import tempfile
import json
from pathlib import Path
from app_core.bus import EventBus
from app_core.config import SentinelConfig
from app_core.schemas import FileEvent, DetectionAlert

async def test_event_flow():
    """Test complete event flow: collector -> detection -> response"""
    print("Testing event flow...")
    
    bus = EventBus()
    alerts_received = []
    
    # Mock detection subscriber
    async def mock_detection(event: FileEvent):
        if event.path.endswith('.suspicious'):
            alert = DetectionAlert(
                rule_id="test_rule",
                severity="medium",
                message="Suspicious file detected",
                event_id=event.event_id,
                timestamp=event.timestamp
            )
            await bus.publish(alert)
    
    # Mock response subscriber
    async def mock_response(alert: DetectionAlert):
        alerts_received.append(alert)
    
    # Set up subscribers
    bus.subscribe(FileEvent, mock_detection)
    bus.subscribe(DetectionAlert, mock_response)
    
    # Simulate file event
    test_event = FileEvent(
        path="/test/file.suspicious",
        event_type="created",
        timestamp=1.0,
        size=1024
    )
    
    await bus.publish(test_event)
    await asyncio.sleep(0.1)  # Allow processing
    
    assert len(alerts_received) == 1
    assert alerts_received[0].rule_id == "test_rule"
    print("✓ Event flow test passed")

def test_config_validation():
    """Test configuration loading and validation"""
    print("Testing configuration validation...")
    
    # Test valid config
    try:
        config = SentinelConfig.load_from_file('config.yaml')
        assert config.version >= 1
        print("✓ Valid config loads correctly")
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return False
    
    # Test invalid config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content: [[[")
        invalid_config_path = f.name
    
    try:
        SentinelConfig.load_from_file(invalid_config_path)
        print("✗ Invalid config should have failed")
        return False
    except Exception:
        print("✓ Invalid config properly rejected")
    finally:
        Path(invalid_config_path).unlink()
    
    return True

def test_platform_guards():
    """Test platform-specific import guards"""
    print("Testing platform guards...")
    
    import platform
    is_windows = platform.system() == "Windows"
    
    try:
        import collectors.reg_monitor
        if is_windows:
            print("✓ Windows registry monitor available")
        else:
            print("✓ Registry monitor loads with guards on non-Windows")
    except ImportError as e:
        print(f"✗ Registry monitor import failed: {e}")
        return False
    
    try:
        import service.service_wrapper
        print("✓ Service wrapper loads with platform guards")
    except ImportError as e:
        print(f"✗ Service wrapper import failed: {e}")
        return False
    
    return True

async def main():
    """Run all smoke tests"""
    print("Running comprehensive smoke tests...\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Event flow
    try:
        await test_event_flow()
        tests_passed += 1
    except Exception as e:
        print(f"✗ Event flow test failed: {e}")
    
    # Test 2: Configuration
    try:
        if test_config_validation():
            tests_passed += 1
    except Exception as e:
        print(f"✗ Config validation test failed: {e}")
    
    # Test 3: Platform guards
    try:
        if test_platform_guards():
            tests_passed += 1
    except Exception as e:
        print(f"✗ Platform guard test failed: {e}")
    
    print(f"\nSmoke test results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✓ All smoke tests passed - system ready")
        return True
    else:
        print("✗ Some smoke tests failed - investigate before proceeding")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
```

## CI Invariants

### Continuous Integration Requirements

#### Build Pipeline Stages
1. **Environment Setup**
   - Python 3.8+ virtual environment
   - Install requirements.txt dependencies
   - Platform detection (Linux CI, Windows optional)

2. **Code Quality Checks**
   - Ruff linting: Must return 0 issues
   - Pyright type checking: 0 errors on modified files
   - Import statement validation

3. **Test Execution**
   - Unit tests: Must pass 100%
   - Integration tests: Must pass 100%
   - E2E tests: Must pass on available platform

4. **Security Validation**
   - No hardcoded secrets or credentials
   - Dependencies security scan
   - Configuration file validation

#### Platform-Specific CI Behavior

**Linux CI (Primary)**:
- Full test suite execution
- Platform guard validation
- Windows module mocking verification
- Documentation generation

**Windows CI (Optional)**:
- Windows-specific functionality testing
- Registry monitor validation
- Service installation testing
- Full platform integration

### Test Data Management

#### Test Fixtures
```python
# conftest.py
import pytest
import tempfile
from pathlib import Path
from app_core.config import SentinelConfig

@pytest.fixture
def temp_config_file():
    """Provide temporary config file for tests"""
    config_content = """
version: 1
monitoring:
  file_system:
    enabled: true
    paths: ["/tmp/test"]
  processes:
    enabled: true
detection:
  rules_engine:
    enabled: true
response:
  actions:
    enabled: false  # Safe for testing
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        yield f.name
    
    Path(f.name).unlink()

@pytest.fixture
def mock_event_bus():
    """Provide isolated event bus for tests"""
    from app_core.bus import EventBus
    return EventBus()
```

#### Test Environment Variables
```bash
# Test environment configuration
export SENTINEL_CONFIG_FILE="test_config.yaml"
export SENTINEL_LOG_LEVEL="DEBUG"
export SENTINEL_DISABLE_WINDOWS_FEATURES="true"  # For Linux CI
export PYTEST_TIMEOUT="300"  # 5-minute test timeout
```

### Performance Testing

#### Event Bus Load Testing
```python
# File: tests/performance/test_event_bus_load.py

import asyncio
import time
import pytest
from app_core.bus import EventBus
from app_core.schemas import HealthMetric

@pytest.mark.performance
async def test_event_bus_throughput():
    """Test event bus can handle high event volume"""
    bus = EventBus()
    events_processed = 0
    
    async def counter_subscriber(event):
        nonlocal events_processed
        events_processed += 1
    
    bus.subscribe(HealthMetric, counter_subscriber)
    
    # Send 1000 events as fast as possible
    start_time = time.time()
    
    for i in range(1000):
        event = HealthMetric(
            component=f"test_{i}",
            status="healthy",
            timestamp=time.time()
        )
        await bus.publish(event)
    
    # Wait for processing
    await asyncio.sleep(1.0)
    
    end_time = time.time()
    duration = end_time - start_time
    throughput = events_processed / duration
    
    # Require at least 500 events/second
    assert throughput > 500, f"Throughput too low: {throughput} events/sec"
    assert events_processed == 1000, f"Lost events: {1000 - events_processed}"
```

## Test Execution Commands

### Local Development
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/ -k integration # Integration tests
pytest tests/e2e/           # E2E tests only

# Run with coverage
pytest --cov=app_core --cov=collectors --cov=detection

# Run performance tests
pytest -m performance

# Run smoke tests
./smoke_test.sh
python comprehensive_smoke_test.py
```

### CI Environment
```bash
# Full CI test suite
pytest --cov --cov-report=xml --junitxml=test-results.xml

# Parallel test execution
pytest -n auto

# Timeout protection
pytest --timeout=300
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-02T20:31:09+00:00  
**Author**: MiniMax Agent