# Event System Architecture - WatchLockAI Sentinel

## Overview

The WatchLockAI Sentinel event system is built around an asynchronous publisher-subscriber pattern that enables loose coupling between monitoring collectors and detection/response components. The system uses typed events with Pydantic validation and provides reliable message delivery with observability.

## Core Components

### EventBus (`app_core/bus.py`)

The central message routing system that implements:

- **Asynchronous Processing**: Background worker task processes events from a queue
- **Weak References**: Subscriptions use WeakSet to prevent memory leaks
- **Event History**: Maintains configurable history buffer for debugging and replay
- **Observability**: Tracks delivery success/failure rates and subscription metrics
- **Graceful Shutdown**: Proper cleanup of worker tasks and pending events

#### Key Classes

**EventBus**
- `max_history`: Configurable event history buffer size (default: 1000)
- `_subscriptions`: Dict mapping event types to WeakSet of subscriptions
- `_event_history`: Deque maintaining recent events for debugging
- `_stats`: Delivery metrics and performance counters

**EventSubscription**
- `event_types`: Set of event types this subscription handles
- `callback`: Function to invoke for matching events (sync or async)
- `subscriber_name`: Human-readable identifier for logging
- `filter_func`: Optional additional filtering beyond event type
- `event_count`: Number of events delivered to this subscription

### Event Schemas (`app_core/schemas.py`)

Type-safe event models using Pydantic v2 with validation:

#### Base Event Structure
```python
class BaseEvent(BaseModel):
    host_id: str = Field(default_factory=lambda: socket.gethostname())
    sentinel_version: str = Field(default="1.0.0")
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
```

#### Event Types

**FileEvent**
- `event_type`: CREATED, MODIFIED, DELETED, RENAMED
- `path`: File path
- `old_path`: Previous path for rename events
- `size_bytes`, `sha256`, `entropy`: File metadata
- `proc_pid`, `proc_name`: Associated process information

**ProcessEvent**
- `event_type`: STARTED, EXITED
- `pid`, `ppid`: Process and parent process IDs
- `exe`, `cmdline`: Executable path and command line
- `username`: User context
- `hash_sha256`: Executable hash
- `start_ts`, `end_ts`: Lifecycle timestamps

**RegistryEvent** (Windows-specific)
- `event_type`: CREATED, MODIFIED, DELETED
- `hive`: HKCU, HKLM, HKU, HKCR
- `key_path`: Registry key path
- `value_name`, `value_type`, `data_preview`: Value details
- `proc_pid`, `proc_name`: Associated process

**NetworkEvent**
- `event_type`: CONNECTION, LISTEN, CLOSE
- `pid`, `proc_name`: Associated process
- `laddr_ip`, `laddr_port`: Local address/port
- `raddr_ip`, `raddr_port`: Remote address/port
- `proto`: TCP, UDP, OTHER
- `status`: Connection status

**HealthMetric**
- `cpu_pct`: CPU usage percentage (0-100)
- `ram_pct`: RAM usage percentage (0-100)
- `disk_pct_free`: Free disk space percentage (0-100)
- `temp_c`: Optional temperature in Celsius

**DetectionAlert**
- `id`: Unique alert identifier (UUID)
- `severity`: LOW, MEDIUM, HIGH
- `category`: RANSOMWARE, PERSISTENCE, PROCESS, NETWORK, HEALTH, GENERAL
- `tag`: Human-readable alert type
- `entities`: Key-value pairs of alert context
- `confidence`: Detection confidence (0.0-1.0)
- `rationale`: Human-readable explanation
- `provenance`: Source file/section information
- `suggested_actions`: List of recommended responses

## Event Flow Patterns

### Publisher Pattern
```python
# Collectors publish events
await event_bus.publish(FileEvent(
    event_type=EventType.CREATED,
    path="/suspicious/file.exe",
    entropy=7.8,
    proc_name="malware.exe"
))
```

### Subscriber Pattern
```python
# Detection engines subscribe to events
def handle_file_event(event: FileEvent) -> None:
    if event.entropy and event.entropy > 7.5:
        # High entropy file detected
        alert = create_ransomware_alert(event)
        asyncio.create_task(event_bus.publish(alert))

subscription = event_bus.subscribe(
    FileEvent, 
    handle_file_event, 
    "ransomware_detector"
)
```

### Filtered Subscriptions
```python
# Subscribe only to high-entropy file events
def high_entropy_filter(event: FileEvent) -> bool:
    return event.entropy is not None and event.entropy > 7.0

subscription = event_bus.subscribe(
    FileEvent,
    handle_suspicious_file,
    "entropy_analyzer",
    filter_func=high_entropy_filter
)
```

## Component Integration

### Collectors -> Event Bus
- **File System Monitor**: Publishes FileEvent for file operations
- **Process Monitor**: Publishes ProcessEvent for process lifecycle
- **Registry Monitor**: Publishes RegistryEvent for registry changes
- **Network Monitor**: Publishes NetworkEvent for network activity
- **Health Monitor**: Publishes HealthMetric for system health

### Event Bus -> Detection Engines
- **Rules Engine**: Subscribes to all event types for rule evaluation
- **Behavioral Engine**: Subscribes to events for baseline learning
- **Threat Intel**: Enriches alerts with knowledge base lookups

### Event Bus -> Response Systems
- **Alert Manager**: Subscribes to DetectionAlert for notification/logging
- **Actions Manager**: Subscribes to alerts for automated response
- **Web API**: Provides real-time event streaming via SSE

## Observability and Debugging

### Event Bus Metrics
```python
stats = event_bus.get_stats()
# Returns:
# {
#     "events_published": 1234,
#     "events_delivered": 1230,
#     "active_subscriptions": 8,
#     "started_at": "2025-01-01T00:00:00Z",
#     "delivery_success_count": 1230,
#     "delivery_failure_count": 4
# }
```

### Event History
- Recent events stored in `_event_history` deque
- Configurable retention (default: 1000 events)
- Used for debugging, replay, and forensic analysis

### Subscription Tracking
- Per-subscription event counts and timestamps
- Dead subscription cleanup via weak references
- Subscriber identification for troubleshooting

## Error Handling

### Delivery Failures
- Failed deliveries logged with subscriber details
- Delivery failure counters tracked for monitoring
- Dead subscriptions automatically cleaned up
- Non-blocking: failures don't affect other subscribers

### Event Validation
- Pydantic validation on event creation
- Field constraints (entropy 0-8, ports 0-65535, percentages 0-100)
- Enum validation for event types and categories
- Automatic timestamp and host ID injection

## Performance Considerations

### Asynchronous Processing
- Events queued and processed by background worker
- Non-blocking publish operations
- Concurrent delivery to multiple subscribers
- Graceful backpressure handling

### Memory Management
- Weak references prevent subscription memory leaks
- Bounded event history prevents unbounded growth
- Automatic cleanup of dead subscriptions
- Efficient event routing via type-based dispatch

## Testing and Validation

### Unit Test Patterns
```python
@pytest.mark.asyncio
async def test_event_delivery():
    bus = EventBus()
    await bus.start()
    
    received_events = []
    bus.subscribe(FileEvent, received_events.append, "test")
    
    event = FileEvent(event_type=EventType.CREATED, path="test.txt")
    await bus.publish(event)
    await asyncio.sleep(0.1)  # Allow delivery
    
    assert len(received_events) == 1
    assert received_events[0] == event
```

### Integration Testing
- End-to-end event flow validation
- Subscription lifecycle testing
- Error condition simulation
- Performance and load testing

## Configuration

### Event Bus Settings
- `max_history`: Event history buffer size
- Worker task configuration
- Queue size limits
- Delivery timeout settings

### Event Validation
- Field constraints in Pydantic models
- Custom validators for domain-specific rules
- Enum value validation
- Required vs optional field definitions

## Security Considerations

### Event Sanitization
- Path traversal prevention in file paths
- Registry key validation for Windows events
- Network address validation
- Process name sanitization

### Access Control
- Subscription-based access to event streams
- Component isolation through event filtering
- Audit trail via event history
- Secure event serialization for API exposure
