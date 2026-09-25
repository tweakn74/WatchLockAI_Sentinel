# WatchLockAI Sentinel - Interoperability Map

**Generated**: 2025-09-02 22:10:18  
**Baseline**: Ruff=0, Pyright=687 errors, Pytest=2 collection errors  
**Scope**: Comprehensive codebase analysis for P0 compatibility fixes

## Overview

WatchLockAI Sentinel is a multi-component security monitoring system with the following architectural layers:

- **Core Layer**: `app_core/` - Event bus, configuration, schemas, logging
- **Collection Layer**: `collectors/` - File system, process, registry, network, health monitoring
- **Detection Layer**: `detection/` - Rules engine, behavioral analysis, ML scoring, threat intelligence
- **Response Layer**: `response/` - Actions management, alerts system
- **Interface Layer**: `console/` - FastAPI web interface, operational mode API
- **Service Layer**: `service/` - Windows service wrapper, main application orchestration

The system follows an event-driven architecture using an internal async event bus for component communication, with FastAPI-based REST API for external control and monitoring.

## Import Graph Highlights

### Core Dependency Chains
```
app.py -> app_core, detection, service, ui
service.service_wrapper -> app_core, collectors, console, detection, response
console.web_api -> console, detection
```

### Potential Cycles Detected

1. **config/app_core cycle**:
   - `app_core.config:109` imports `config.operational_mode`
   - `console.api.operational_mode` imports `config`
   - Risk: Circular import during initialization

2. **detection internal cycle**:
   - `detection.behavioral_engine` imports `detection`
   - `detection.rules_engine` imports `detection`
   - Risk: Self-referential imports within detection package

### High-Risk Import Patterns
- **Late imports**: `console/web_api.py:82-86` uses try/except ImportError for operational_mode router
- **Conditional imports**: `service/service_wrapper.py:13-21` conditionally imports Windows APIs
- **Deep imports**: Multiple files import from `app_core` creating hub dependency

## Event Contracts

| Producer | Consumer(s) | Event Type | Fields/Types | Notes |
|----------|-------------|------------|--------------|-------|
| `collectors.fs_monitor` | `detection.rules_engine` | `FileEvent` | `event_type: EventType, path: str, size_bytes: int?, sha256: str?, entropy: float?` | File system monitoring |
| `collectors.proc_monitor` | `detection.rules_engine` | `ProcessEvent` | `event_type: ProcessEventType, pid: int, name: str, cmd_line: str?` | Process lifecycle |
| `collectors.reg_monitor` | `detection.rules_engine` | `RegistryEvent` | `event_type: RegistryEventType, hive: RegistryHive, key_path: str` | Windows registry changes |
| `collectors.net_monitor` | `detection.rules_engine` | `NetworkEvent` | `event_type: NetworkEventType, protocol: NetworkProtocol, local_addr: str, remote_addr: str?` | Network connections |
| `collectors.health_monitor` | `response.alerts` | `HealthEvent` | `cpu_percent: float, memory_percent: float, disk_free_gb: float, temp_celsius: float?` | System health metrics |
| `detection.rules_engine` | `response.alerts` | `DetectionEvent` | `severity: AlertSeverity, category: AlertCategory, message: str, metadata: dict` | Security detections |
| `response.actions` | `app_core.bus` | `ActionEvent` | `action_type: ActionType, result: ActionResult, parameters: dict, user_consent: bool` | Response actions |

### Event Bus Contract Issues
- **Type safety**: Some consumers cast `BaseEvent` without proper type checking
- **Schema evolution**: No versioning strategy for event schema changes
- **Error handling**: Limited error propagation for failed event delivery

## API Routes

| Method | Path | Handler | Model In/Out | Issues |
|--------|------|---------|--------------|---------|
| GET | `/api/status` | `get_status()` | -> `StatusResponse` | [PASS] Clean |
| GET | `/api/alerts` | `get_alerts()` | -> `AlertSummary` | [PASS] Clean |
| GET | `/api/detections` | `get_detections()` | -> `DetectionResponse` | [WARN] Optional query params |
| POST | `/api/actions/pause` | `pause_monitoring()` | `duration_minutes: int` -> `dict` | [WARN] Non-standard response |
| POST | `/api/actions/resume` | `resume_monitoring()` | -> `dict` | [WARN] Non-standard response |
| GET | `/api/ti/search` | `search_threat_intelligence()` | `query: str, limit: int` -> `dict` | [WARN] Non-standard response |
| GET | `/api/policies` | `get_policies()` | -> `dict` | [WARN] Non-standard response |
| POST | `/api/policies` | `set_policies()` | `dict` -> `dict` | [WARN] Non-standard response |
| GET | `/api/operational_mode` | `get_operational_mode()` | -> `GetModeResponse` | [PASS] Clean (new) |
| PUT | `/api/operational_mode` | `set_operational_mode()` | `SetModeRequest` -> `GetModeResponse` | [PASS] Clean (new) |

### API Route Issues
1. **Inconsistent response models**: Mix of Pydantic models and raw dicts
2. **Missing route registration**: No centralized router registration pattern
3. **Path conflicts**: Potential future conflicts with `/api/policies` vs operational mode
4. **Error handling**: Inconsistent HTTP exception patterns

## Background Tasks

| Task Name | Start Order | Stop Order | Cancellation | Location |
|-----------|-------------|------------|--------------|----------|
| `EventBus._worker()` | 1 (bus.start) | 4 (bus.stop) | [PASS] Graceful | `app_core/bus.py:92` |
| `SentinelService.start()` | 2 (service init) | 3 (service stop) | [PASS] Graceful | `service/service_wrapper.py:210` |
| `SentinelWebAPI.server` | 3 (after service) | 2 (before service) | [WARN] Basic | `console/web_api.py:370` |
| `TrayApp` (optional) | 4 (UI optional) | 1 (UI first) | [WARN] Thread-based | `app.py:90` |

### Background Task Issues
1. **Startup dependency**: No explicit dependency management between tasks
2. **Shutdown order**: Reverse order not guaranteed, risk of resource conflicts  
3. **Error propagation**: Task failures may not properly cascade to parent
4. **Graceful cancellation**: Some tasks use basic cancellation vs proper cleanup

## Config Surface

| Key | Owner Module | Default | Duplicates | Notes |
|-----|-------------|---------|------------|--------|
| `operational.mode` | `app_core.config:98` | `"observe"` | [PASS] Single source | New persistent storage |
| `operational.current_mode` | `app_core.config:101` | Dynamic | [WARN] Property | Reads from `config/operational_mode.json` |
| `responses.allow_destructive_actions` | `app_core.config:92` | `False` | [PASS] Single source | Response gating |
| `monitoring.file_system.enabled` | `app_core.config:16` | `True` | [PASS] Single source | Collector control |
| `monitoring.processes.enabled` | `app_core.config:29` | `True` | [PASS] Single source | Collector control |
| `monitoring.registry.enabled` | `app_core.config:37` | `True` | [PASS] Single source | Collector control |
| `monitoring.network.enabled` | `app_core.config:49` | `True` | [PASS] Single source | Collector control |
| `health.enabled` | `app_core.config:59` | `True` | [PASS] Single source | Health monitoring |
| `rag.mode` | `app_core.config:79` | `"embeddings"` | [PASS] Single source | Knowledge indexing |
| `service.install_on_setup` | `app_core.config:119` | `True` | [PASS] Single source | Windows service |

### Config Surface Issues
1. **Dual mode access**: `operational.mode` vs `operational.current_mode` creates confusion
2. **Default inconsistencies**: Some defaults in code vs YAML may diverge
3. **Validation gaps**: Path validation warnings not enforced at runtime
4. **Environment override**: Limited documentation for environment variable patterns

## Platform-Guard Checklist

| Path | Guard Present? | File:Line | Notes |
|------|---------------|-----------|--------|
| Windows service APIs | [PASS] YES | `service/service_wrapper.py:13-21` | `try/except ImportError` |
| Registry monitoring | [FAIL] NO | `collectors/reg_monitor.py` | Needs `platform.system()` check |
| Windows event logging | [WARN] PARTIAL | `app_core/logging_setup.py` | Comment mentions platform check |
| Process termination | [FAIL] NO | `response/actions.py:83` | Uses `psutil` without platform guards |
| Service installation | [FAIL] NO | `service/service_wrapper.py:400+` | Windows-specific operations |
| Tray application | [FAIL] NO | `ui/tray_app.py` | Windows/GUI-specific |

### Platform-Guard Issues (Critical P0 Fixes Needed)
1. **Registry collector**: `collectors/reg_monitor.py` will fail on Linux CI - needs platform check
2. **Service operations**: Install/uninstall operations not guarded 
3. **UI components**: Tray app may fail on headless Linux systems
4. **Process actions**: Windows-specific process management not isolated
5. **Event logging**: Windows event log handler missing platform checks
6. **File paths**: Some Windows path patterns may not handle Linux paths correctly

---

**Analysis Complete**: 6 categories analyzed, 23 potential P0 issues identified for prioritization.
