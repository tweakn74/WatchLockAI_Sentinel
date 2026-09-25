# Development Workflow Patterns - WatchLockAI Sentinel

## Overview

This document outlines development patterns, testing strategies, debugging approaches, and best practices specific to the WatchLockAI Sentinel codebase. It provides guidance for developers working on the event-driven, multi-component architecture.

## Development Environment Setup

### Prerequisites
```bash
# Python 3.10+ required
python --version  # Should be 3.10+

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Verify core imports work
python -c "from app_core.bus import EventBus; print('Core imports: OK')"
python -c "from app_core.schemas import FileEvent; print('Schema imports: OK')"
```

### Platform Guards
Always use platform guards for Windows-specific functionality:

```python
import sys
import platform

# Platform detection
IS_WINDOWS = sys.platform.startswith('win')
IS_LINUX = sys.platform.startswith('linux')

# Windows-specific imports
if IS_WINDOWS:
    try:
        import win32serviceutil
        import win32service
        WINDOWS_SERVICE_AVAILABLE = True
    except ImportError:
        WINDOWS_SERVICE_AVAILABLE = False
else:
    WINDOWS_SERVICE_AVAILABLE = False

# Usage in code
def install_service() -> bool:
    """Install Windows service with platform guard."""
    if not IS_WINDOWS:
        print("Error: Windows service installation not available on this platform")
        return False
        
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Error: Windows service APIs not available")
        return False
    
    # Windows-specific implementation
    win32serviceutil.InstallService(...)
```

### Configuration for Development
```yaml
# config.yaml for development
version: 1

monitoring:
  file_system:
    enabled: true
    paths:
      - "./test_data"  # Use local test directory
    compute_entropy: true  # Enable for testing
    burst_window_sec: 5    # Shorter window for testing

  processes:
    enabled: false  # Disable to reduce noise during development

  registry:
    enabled: false  # Disable on non-Windows or for focused testing

  network:
    enabled: false  # Disable to reduce noise

health:
  enabled: true
  cpu_warn: 95    # Higher threshold for development

alerts:
  toast_notifications: false  # Disable to avoid interruptions
  log_jsonl: true
  jsonl_path: "./logs/dev_alerts.jsonl"

responses:
  allow_destructive_actions: false  # Safety first
  require_user_consent: true
```

## Testing Patterns

### Unit Testing with Event Bus

```python
import pytest
import asyncio
from app_core.bus import EventBus
from app_core.schemas import FileEvent, EventType

@pytest.fixture
async def event_bus():
    """Create and start an event bus for testing."""
    bus = EventBus(max_history=100)
    await bus.start()
    yield bus
    await bus.stop()

@pytest.mark.asyncio
async def test_file_event_processing(event_bus):
    """Test file event processing through rules engine."""
    from detection.rules_engine import RulesEngine
    
    # Initialize rules engine with test config
    rules_engine = RulesEngine({}, event_bus, None)
    await rules_engine.start()
    
    # Track published alerts
    published_alerts = []
    
    def alert_handler(alert):
        published_alerts.append(alert)
    
    event_bus.subscribe(DetectionAlert, alert_handler, "test_handler")
    
    # Create high-entropy file event
    file_event = FileEvent(
        event_type=EventType.CREATED,
        path="suspicious.exe",
        entropy=7.9,  # High entropy
        size_bytes=1024
    )
    
    # Publish event and wait for processing
    await event_bus.publish(file_event)
    await asyncio.sleep(0.1)  # Allow processing time
    
    # Verify alert was generated
    assert len(published_alerts) > 0
    alert = published_alerts[0]
    assert alert.category == AlertCategory.RANSOMWARE
    assert alert.severity == AlertSeverity.HIGH
    
    # Cleanup
    await rules_engine.stop()
```

### Mock Components for Isolation

```python
class MockKnowledgeLoader:
    """Mock knowledge loader for testing."""
    
    def __init__(self):
        self.query_calls = []
    
    def query_knowledge(self, query: str, limit: int = 10):
        self.query_calls.append((query, limit))
        return [
            KnowledgeHit(
                content="Mock threat intelligence content",
                filename="test.md",
                section="test_section",
                lines="1-10",
                confidence=0.8
            )
        ]

class MockEventBus:
    """Mock event bus for unit testing."""
    
    def __init__(self):
        self.published_events = []
        self.subscriptions = []
    
    async def publish(self, event):
        self.published_events.append(event)
    
    def subscribe(self, event_type, callback, name, filter_func=None):
        subscription = MockSubscription(event_type, callback, name)
        self.subscriptions.append(subscription)
        return subscription

# Usage in tests
def test_threat_intel_enrichment():
    """Test threat intelligence enrichment with mocks."""
    mock_loader = MockKnowledgeLoader()
    threat_intel_db = ThreatIntelDB(mock_loader)
    
    # Create test alert
    alert = DetectionAlert(
        severity=AlertSeverity.HIGH,
        category=AlertCategory.RANSOMWARE,
        tag="test-alert",
        entities={"file": "suspicious.exe"},
        confidence=0.9,
        rationale="Test alert",
        provenance=ProvenanceInfo(file="test.py", section="test")
    )
    
    # Test enrichment
    enriched_alert = threat_intel_db.enrich_alert(alert)
    
    # Verify knowledge base was queried
    assert len(mock_loader.query_calls) > 0
    assert "suspicious.exe" in str(mock_loader.query_calls)
    
    # Verify alert was enriched
    assert "threat_intel" in enriched_alert.entities
```

### Integration Testing

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_ransomware_detection():
    """Integration test for ransomware detection pipeline."""
    
    # Create temporary test directory
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup configuration for test
        config = SentinelConfig()
        config.monitoring.file_system.paths = [temp_dir]
        config.monitoring.file_system.enabled = True
        config.monitoring.file_system.compute_entropy = True
        
        # Initialize components
        event_bus = EventBus()
        await event_bus.start()
        
        # Start file system monitor
        fs_monitor = FileSystemMonitor(config.monitoring.file_system, event_bus)
        await fs_monitor.start()
        
        # Start rules engine
        rules_engine = RulesEngine({}, event_bus, None)
        await rules_engine.start()
        
        # Track alerts
        alerts = []
        event_bus.subscribe(DetectionAlert, alerts.append, "test_collector")
        
        # Create high-entropy file (simulate ransomware)
        test_file = os.path.join(temp_dir, "encrypted.txt")
        with open(test_file, "wb") as f:
            # Write high-entropy data
            import random
            f.write(bytes([random.randint(0, 255) for _ in range(1024)]))
        
        # Wait for detection
        await asyncio.sleep(1.0)
        
        # Verify ransomware alert was generated
        assert len(alerts) > 0
        ransomware_alerts = [a for a in alerts if a.category == AlertCategory.RANSOMWARE]
        assert len(ransomware_alerts) > 0
        
        # Cleanup
        await fs_monitor.stop()
        await rules_engine.stop()
        await event_bus.stop()
```

## Debugging Patterns

### Event Bus Debugging

```python
# Enable debug logging for event bus
import logging
logging.getLogger("app_core.bus").setLevel(logging.DEBUG)

# Add debug subscriber to see all events
def debug_event_handler(event):
    print(f"DEBUG: {type(event).__name__}: {event}")

event_bus.subscribe(
    [FileEvent, ProcessEvent, NetworkEvent, RegistryEvent, HealthMetric, DetectionAlert],
    debug_event_handler,
    "debug_subscriber"
)

# Check event bus statistics
stats = event_bus.get_stats()
print(f"Events published: {stats['events_published']}")
print(f"Events delivered: {stats['events_delivered']}")
print(f"Active subscriptions: {stats['active_subscriptions']}")
print(f"Delivery success: {stats.get('delivery_success_count', 0)}")
print(f"Delivery failures: {stats.get('delivery_failure_count', 0)}")
```

### Component Status Debugging

```python
def debug_component_status(sentinel_service):
    """Debug helper to check component status."""
    
    print("=== Component Status ===")
    
    # Event bus status
    if sentinel_service.event_bus:
        stats = sentinel_service.event_bus.get_stats()
        print(f"Event Bus: Running={sentinel_service.event_bus._running}")
        print(f"  Published: {stats['events_published']}")
        print(f"  Delivered: {stats['events_delivered']}")
        print(f"  Subscriptions: {stats['active_subscriptions']}")
    
    # Collectors status
    print(f"Collectors: {len(sentinel_service.collectors)} active")
    for name, collector in sentinel_service.collectors.items():
        status = getattr(collector, 'get_status', lambda: {'status': 'unknown'})()
        print(f"  {name}: {status}")
    
    # Rules engine status
    if sentinel_service.rules_engine:
        status = sentinel_service.rules_engine.get_status()
        print(f"Rules Engine: {status}")
    
    # Alert manager status
    if sentinel_service.alert_manager:
        stats = sentinel_service.alert_manager.get_stats()
        print(f"Alert Manager: {stats}")

# Usage during debugging
debug_component_status(sentinel_service)
```

### Configuration Debugging

```python
def debug_configuration():
    """Debug configuration loading and validation."""
    
    try:
        config = load_config()
        print("[x] Configuration loaded successfully")
        
        # Validate configuration
        warnings = validate_config(config)
        if warnings:
            print("[WARN] Configuration warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("[x] Configuration validation passed")
        
        # Check operational mode
        from config.operational_mode import get_mode
        mode = get_mode()
        print(f"[x] Operational mode: {mode}")
        
        # Check feature flags
        print("Feature flags:")
        import os
        flags = [
            "HEALTH_ENDPOINT_ENABLED",
            "METRICS_DEBUG_ENABLED",
            "CONFIG_HOT_RELOAD_ENABLED",
            "MITRE_API_ENABLED",
            "STREAM_ENABLED"
        ]
        for flag in flags:
            value = os.getenv(flag, "0")
            print(f"  {flag}: {value}")
            
    except Exception as e:
        print(f"[FAIL] Configuration error: {e}")
        import traceback
        traceback.print_exc()

# Run configuration debug
debug_configuration()
```

## Performance Profiling

### Event Processing Performance

```python
import time
import statistics
from collections import defaultdict

class EventPerformanceProfiler:
    """Profile event processing performance."""
    
    def __init__(self):
        self.processing_times = defaultdict(list)
        self.event_counts = defaultdict(int)
    
    def profile_event_handler(self, event_type_name: str):
        """Decorator to profile event handler performance."""
        def decorator(handler_func):
            async def wrapper(event):
                start_time = time.perf_counter()
                try:
                    result = await handler_func(event)
                    return result
                finally:
                    end_time = time.perf_counter()
                    processing_time = end_time - start_time
                    
                    self.processing_times[event_type_name].append(processing_time)
                    self.event_counts[event_type_name] += 1
            
            return wrapper
        return decorator
    
    def get_stats(self):
        """Get performance statistics."""
        stats = {}
        for event_type, times in self.processing_times.items():
            if times:
                stats[event_type] = {
                    "count": len(times),
                    "avg_ms": statistics.mean(times) * 1000,
                    "min_ms": min(times) * 1000,
                    "max_ms": max(times) * 1000,
                    "p95_ms": statistics.quantiles(times, n=20)[18] * 1000 if len(times) > 20 else max(times) * 1000
                }
        return stats

# Usage
profiler = EventPerformanceProfiler()

@profiler.profile_event_handler("FileEvent")
async def _handle_file_event(self, event: FileEvent):
    # Original handler implementation
    pass

# Check performance after running
stats = profiler.get_stats()
for event_type, perf in stats.items():
    print(f"{event_type}: {perf['count']} events, avg {perf['avg_ms']:.2f}ms")
```

### Memory Usage Monitoring

```python
import psutil
import gc

def monitor_memory_usage():
    """Monitor memory usage during development."""
    
    process = psutil.Process()
    
    print("=== Memory Usage ===")
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.1f} MB")
    
    # Python object counts
    print("\n=== Python Objects ===")
    gc.collect()  # Force garbage collection
    
    object_counts = {}
    for obj in gc.get_objects():
        obj_type = type(obj).__name__
        object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
    
    # Show top object types
    top_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for obj_type, count in top_objects:
        print(f"  {obj_type}: {count}")

# Run periodically during development
import threading
import time

def periodic_memory_monitor():
    while True:
        monitor_memory_usage()
        time.sleep(30)  # Every 30 seconds

# Start background monitoring
monitor_thread = threading.Thread(target=periodic_memory_monitor, daemon=True)
monitor_thread.start()
```

## Code Quality Patterns

### Type Hints and Validation

```python
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

if TYPE_CHECKING:
    from app_core.bus import EventBus
    from app_core.config import SentinelConfig

class ComponentBase:
    """Base class for Sentinel components with type safety."""
    
    def __init__(self, config: Dict[str, Any], event_bus: 'EventBus') -> None:
        self.config = config
        self.event_bus = event_bus
        self._running = False
    
    async def start(self) -> None:
        """Start component - must be implemented by subclasses."""
        raise NotImplementedError
    
    async def stop(self) -> None:
        """Stop component - must be implemented by subclasses."""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """Get component status."""
        return {
            "running": self._running,
            "component_type": self.__class__.__name__
        }
```

### Error Handling Patterns

```python
import functools
from loguru import logger

def safe_async_handler(component_name: str):
    """Decorator for safe async event handlers."""
    def decorator(handler_func):
        @functools.wraps(handler_func)
        async def wrapper(*args, **kwargs):
            try:
                return await handler_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {component_name}.{handler_func.__name__}: {e}")
                # Don't re-raise - keep system running
                return None
        return wrapper
    return decorator

# Usage
class FileSystemMonitor:
    @safe_async_handler("FileSystemMonitor")
    async def _handle_file_event(self, event):
        # Handler implementation
        # Errors are logged but don't crash the system
        pass
```

### Configuration Validation

```python
def validate_component_config(config_section: Dict[str, Any], component_name: str) -> List[str]:
    """Validate component configuration and return warnings."""
    warnings = []
    
    # Check required fields
    required_fields = ["enabled"]
    for field in required_fields:
        if field not in config_section:
            warnings.append(f"{component_name}: Missing required field '{field}'")
    
    # Check field types and values
    if "enabled" in config_section and not isinstance(config_section["enabled"], bool):
        warnings.append(f"{component_name}: 'enabled' must be boolean")
    
    # Component-specific validation
    if component_name == "file_system":
        if config_section.get("enabled") and not config_section.get("paths"):
            warnings.append("file_system: No monitoring paths configured")
    
    return warnings

# Usage in component initialization
def initialize_file_system_monitor(config):
    warnings = validate_component_config(config, "file_system")
    for warning in warnings:
        logger.warning(warning)
    
    if config.get("enabled", False):
        return FileSystemMonitor(config)
    return None
```

## Deployment and Packaging

### Development vs Production

```python
import os

def is_development_mode() -> bool:
    """Check if running in development mode."""
    return os.getenv("SENTINEL_ENV", "production").lower() in ["dev", "development"]

def get_log_level() -> str:
    """Get appropriate log level for environment."""
    if is_development_mode():
        return "DEBUG"
    return os.getenv("LOG_LEVEL", "INFO")

# Configure logging based on environment
from loguru import logger

logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level=get_log_level(),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
```

### Build Validation

```python
def validate_build():
    """Validate build integrity before deployment."""
    
    print("=== Build Validation ===")
    
    # Check core imports
    try:
        from app_core.bus import EventBus
        from app_core.schemas import FileEvent
        from app_core.config import load_config
        print("[x] Core imports successful")
    except ImportError as e:
        print(f"[FAIL] Core import failed: {e}")
        return False
    
    # Check configuration loading
    try:
        config = load_config()
        print("[x] Configuration loading successful")
    except Exception as e:
        print(f"[FAIL] Configuration loading failed: {e}")
        return False
    
    # Check platform compatibility
    import sys
    if sys.version_info < (3, 10):
        print(f"[FAIL] Python version {sys.version} < 3.10")
        return False
    print(f"[x] Python version {sys.version} OK")
    
    # Check optional dependencies
    optional_deps = [
        ("win32serviceutil", "Windows service support"),
        ("plyer", "Toast notifications"),
        ("sentence_transformers", "ML embeddings")
    ]
    
    for module, description in optional_deps:
        try:
            __import__(module)
            print(f"[x] Optional dependency {module} available")
        except ImportError:
            print(f"[WARN] Optional dependency {module} not available ({description})")
    
    print("[x] Build validation completed")
    return True

if __name__ == "__main__":
    validate_build()
```

This development workflow documentation provides practical patterns for working with the WatchLockAI Sentinel codebase, emphasizing the event-driven architecture, proper testing strategies, and debugging approaches specific to this system.
