# Event Contracts and Message Flow

## Event Producer → Consumer Mapping

| Producer Module | Event Type | Consumer Modules | Routing | Notes |
|---|---|---|---|---|
| `collectors.fs_monitor` | `FileEvent` | `detection.rules_engine`, `detection.behavioral_engine` | Event Bus | File system activity monitoring |
| `collectors.proc_monitor` | `ProcessEvent` | `detection.rules_engine`, `detection.behavioral_engine`, `response.actions` | Event Bus | Process lifecycle tracking |
| `collectors.reg_monitor` | `RegistryEvent` | `detection.rules_engine` | Event Bus | Windows registry changes (Windows only) |
| `collectors.net_monitor` | `NetworkEvent` | `detection.rules_engine`, `detection.behavioral_engine` | Event Bus | Network connection monitoring |
| `collectors.health_monitor` | `HealthMetric` | `response.alert_manager` | Event Bus | System health metrics |
| `detection.rules_engine` | `DetectionAlert` | `response.alert_manager`, `response.actions`, `console.web_api` | Event Bus | Threat detection alerts |
| `response.alert_manager` | `DetectionAlert` (enriched) | `console.web_api`, `ui.tray_app` | Event Bus | Alert notifications |
| `response.actions` | `ActionEvent` | `console.web_api`, logging system | Event Bus | Response action execution records |

## Event Bus Subscribers

### Detection Layer Subscribers
- **rules_engine**: Subscribes to all monitoring events (File, Process, Registry, Network)
- **behavioral_engine**: Subscribes to File, Process, Network events for behavior analysis
- **threat_intel_db**: No direct event subscription (query-based lookup service)

### Response Layer Subscribers  
- **alert_manager**: Subscribes to DetectionAlert events from detection engines
- **actions**: Subscribes to DetectionAlert events that require response actions

### UI/API Layer Subscribers
- **web_api**: Subscribes to DetectionAlert and ActionEvent for dashboard display
- **tray_app**: Subscribes to DetectionAlert for system tray notifications

## Message Flow Patterns

### Primary Detection Flow
```
Collector → EventBus → RulesEngine → DetectionAlert → AlertManager → UI/Actions
```

### Health Monitoring Flow  
```
HealthMonitor → EventBus → AlertManager → UI/TrayNotification
```

### Response Action Flow
```
DetectionAlert → EventBus → ActionManager → ActionEvent → EventBus → Logging/UI
```

### Configuration Change Flow
```
WebAPI → OperationalMode → ConfigChange → EventBus → AllComponents
```

## Event Schema Contracts

Detailed event field specifications and validation rules can be found in the accompanying `schema.json` file.

## Event Delivery Guarantees

- **At-least-once**: Events delivered to all active subscribers
- **Async delivery**: Non-blocking event publication with background delivery
- **Weak references**: Automatic cleanup of inactive subscribers
- **Error isolation**: Subscriber failures don't affect other subscribers or publisher
- **Event history**: Configurable event replay capability (default: 1000 events)

## Event Filtering

- **Type-based**: Subscribers register for specific event types
- **Custom filters**: Optional filter functions for fine-grained event selection
- **Performance**: Filtering applied before event delivery to minimize overhead
