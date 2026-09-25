# Component Integration Patterns - WatchLockAI Sentinel

## Overview

WatchLockAI Sentinel uses an event-driven architecture where components communicate through a central event bus. This document describes the integration patterns, data flows, and communication protocols between major system components.

## System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Collectors    │    │  Detection      │    │   Response      │
│                 │    │  Engines        │    │   Systems       │
│ * FileSystem    │    │ * Rules Engine  │    │ * Alert Mgr     │
│ * Process       │───>│ * Behavioral    │───>│ * Actions Mgr   │
│ * Registry      │    │ * Threat Intel  │    │ * Playbooks     │
│ * Network       │    │ * ML Scoring    │    │ * UI Tray       │
│ * Health        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Event Bus     │
                    │                 │
                    │ * Pub/Sub       │
                    │ * Type Routing  │
                    │ * History       │
                    │ * Metrics       │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Web API       │
                    │                 │
                    │ * REST Endpoints│
                    │ * SSE Streaming │
                    │ * Web Console   │
                    └─────────────────┘
```

## Event Bus Integration Patterns

### Publisher Pattern (Collectors)

Collectors generate typed events and publish them to the event bus:

```python
# File System Monitor
class FileSystemMonitor:
    def __init__(self, config: FileSystemConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
    
    async def _handle_file_event(self, event_path: str, event_type: str):
        """Handle file system event and publish to bus."""
        file_event = FileEvent(
            event_type=EventType(event_type),
            path=str(event_path),
            size_bytes=self._get_file_size(event_path),
            entropy=self._calculate_entropy(event_path) if self.config.compute_entropy else None,
            proc_pid=self._get_associated_process(),
            proc_name=self._get_process_name()
        )
        
        await self.event_bus.publish(file_event)
        logger.debug(f"Published FileEvent: {event_type} {event_path}")
```

### Subscriber Pattern (Detection Engines)

Detection engines subscribe to relevant event types:

```python
# Rules Engine
class RulesEngine:
    def __init__(self, config: dict, event_bus: EventBus):
        self.event_bus = event_bus
        self._subscriptions: list[EventSubscription] = []
    
    async def start(self) -> None:
        """Start rules engine and subscribe to events."""
        # Subscribe to all event types
        self._subscriptions.append(
            self.event_bus.subscribe(FileEvent, self._handle_file_event, "rules_engine")
        )
        self._subscriptions.append(
            self.event_bus.subscribe(ProcessEvent, self._handle_process_event, "rules_engine")
        )
        self._subscriptions.append(
            self.event_bus.subscribe(RegistryEvent, self._handle_registry_event, "rules_engine")
        )
        self._subscriptions.append(
            self.event_bus.subscribe(NetworkEvent, self._handle_network_event, "rules_engine")
        )
        self._subscriptions.append(
            self.event_bus.subscribe(HealthMetric, self._handle_health_metric, "rules_engine")
        )
    
    async def _handle_file_event(self, event: FileEvent) -> None:
        """Process file event through detection rules."""
        # Check ransomware burst rule
        alert = self.ransomware_detector.check_file_event(event)
        if alert:
            await self.event_bus.publish(alert)
```

### Filtered Subscriptions

Components can subscribe with filters for specific event characteristics:

```python
# Behavioral Engine - High entropy files only
def high_entropy_filter(event: FileEvent) -> bool:
    return event.entropy is not None and event.entropy > 7.0

subscription = event_bus.subscribe(
    FileEvent,
    behavioral_engine.analyze_suspicious_file,
    "behavioral_engine_entropy",
    filter_func=high_entropy_filter
)

# Network Monitor - Outbound connections only
def outbound_filter(event: NetworkEvent) -> bool:
    return event.event_type == NetworkEventType.CONNECTION and event.raddr_ip is not None

subscription = event_bus.subscribe(
    NetworkEvent,
    egress_detector.check_outbound_connection,
    "egress_detector",
    filter_func=outbound_filter
)
```

## Service Initialization Flow

### Startup Sequence

The SentinelService orchestrates component initialization in dependency order:

```python
class SentinelService:
    async def initialize(self) -> None:
        """Initialize Sentinel service components in dependency order."""
        try:
            # 1. Load configuration
            self.config = load_config(self.config_path)
            
            # 2. Setup logging
            setup_logging(self.config)
            
            # 3. Initialize event bus (core dependency)
            self.event_bus = EventBus()
            await self.event_bus.start()
            
            # 4. Initialize knowledge loader and build index
            self.knowledge_loader = KnowledgeLoader()
            stats = self.knowledge_loader.rebuild_index()
            
            # 5. Initialize components in parallel where possible
            await self._initialize_collectors()
            await self._initialize_detection_engine()
            await self._initialize_response_managers()
            await self._initialize_web_api()
            
            self.startup_time = time.time()
            logger.info("Sentinel service initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentinel service: {e}")
            raise
```

### Component Dependencies

```python
async def _initialize_collectors(self) -> None:
    """Initialize all monitoring collectors."""
    # Collectors depend on: event_bus, config
    
    if self.config.monitoring.file_system.enabled:
        self.collectors["fs"] = FileSystemMonitor(
            self.config.monitoring.file_system,
            self.event_bus,
        )
        await self.collectors["fs"].start()
    
    if self.config.monitoring.processes.enabled:
        self.collectors["proc"] = ProcessMonitor(
            self.config.monitoring.processes,
            self.event_bus,
        )
        await self.collectors["proc"].start()

async def _initialize_detection_engine(self) -> None:
    """Initialize detection engines."""
    # Detection engines depend on: event_bus, config, knowledge_loader
    
    self.rules_engine = RulesEngine(
        self.config,
        self.event_bus,
        self.knowledge_loader,
    )
    await self.rules_engine.start()

async def _initialize_response_managers(self) -> None:
    """Initialize response management systems."""
    # Response managers depend on: event_bus, config
    
    self.alert_manager = AlertManager(
        self.config.alerts,
        self.event_bus,
    )
    await self.alert_manager.start()
    
    self.actions_manager = ResponseActionsManager(
        self.config.responses,
        self.config.operational,
    )
```

## Data Flow Patterns

### Event Processing Pipeline

1. **Event Generation**: Collectors monitor system activity
2. **Event Publishing**: Events published to event bus
3. **Event Routing**: Bus routes events to subscribers by type
4. **Detection Processing**: Detection engines analyze events
5. **Alert Generation**: Suspicious activity generates alerts
6. **Response Execution**: Alerts trigger automated responses
7. **Notification**: Users notified via multiple channels

### Example: Ransomware Detection Flow

```python
# 1. File System Monitor detects file creation
file_event = FileEvent(
    event_type=EventType.CREATED,
    path="C:\\Users\\victim\\Documents\\important.txt.encrypted",
    entropy=7.9,  # High entropy indicates encryption
    proc_name="suspicious.exe"
)

# 2. Event published to bus
await event_bus.publish(file_event)

# 3. Rules Engine receives event
async def _handle_file_event(self, event: FileEvent) -> None:
    # Ransomware detector analyzes file
    alert = self.ransomware_detector.check_file_event(event)
    if alert:
        # 4. Alert generated and published
        await self.event_bus.publish(alert)

# 5. Alert Manager receives alert
async def _process_alert(self, alert: DetectionAlert) -> None:
    # Send notifications
    await self.toast_handler.send_notification(alert)
    await self.jsonl_logger.log_alert(alert)
    
    # Add to tray buffer
    self.tray_buffer.add_alert(alert)

# 6. Playbook system evaluates response
async def trigger(self, rule, ctx: Dict[str, Any]) -> None:
    current_mode = self.mode_provider()
    if current_mode in ("contain", "quarantine"):
        # Execute automated response
        await self._execute_response(rule.response, rule, ctx)
```

## Cross-Component Communication

### Configuration Changes

Components can subscribe to configuration changes:

```python
def on_config_change(new_config: SentinelConfig) -> None:
    """Handle configuration changes."""
    # Update collector settings
    if hasattr(self, 'fs_monitor'):
        self.fs_monitor.update_config(new_config.monitoring.file_system)
    
    # Update detection thresholds
    if hasattr(self, 'rules_engine'):
        self.rules_engine.update_thresholds(new_config)

# Subscribe to config changes
subscribe_to_config_changes(on_config_change)
```

### Operational Mode Changes

Components respond to operational mode changes:

```python
class ResponseActionsManager:
    def _get_current_operational_mode(self) -> str:
        """Get current operational mode from storage."""
        try:
            from config.operational_mode import get_mode
            return get_mode()
        except Exception:
            return "observe"
    
    def _check_mode_enforcement(self, action_type: ActionType) -> bool:
        """Check if action is allowed in current mode."""
        current_mode = self._get_current_operational_mode()
        
        if current_mode == "observe":
            return action_type == ActionType.PAUSE_MONITORING
        elif current_mode == "alert":
            return action_type in [ActionType.PAUSE_MONITORING]
        elif current_mode == "contain":
            return action_type in [ActionType.PAUSE_MONITORING, ActionType.TERMINATE_PROCESS]
        elif current_mode == "quarantine":
            return True  # All actions allowed
        else:  # offline
            return False  # No actions allowed
```

## Web API Integration

### Real-time Event Streaming

The Web API provides Server-Sent Events for real-time monitoring:

```python
@app.get("/api/stream/events")
async def stream_events(request: Request):
    """Stream detection events via SSE."""
    
    async def event_generator():
        # Subscribe to detection alerts
        received_events = []
        
        def alert_handler(alert: DetectionAlert):
            received_events.append(alert)
        
        subscription = event_bus.subscribe(
            DetectionAlert,
            alert_handler,
            "sse_stream"
        )
        
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                # Send any new events
                while received_events:
                    alert = received_events.pop(0)
                    yield f"data: {alert.model_dump_json()}\n\n"
                
                await asyncio.sleep(0.1)
        finally:
            event_bus.unsubscribe(subscription)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### Status Aggregation

The API aggregates status from multiple components:

```python
@app.get("/api/status")
async def get_status() -> StatusResponse:
    """Get comprehensive service status."""
    
    # Collect status from all components
    collectors_status = {}
    for name, collector in sentinel_service.collectors.items():
        collectors_status[name] = collector.get_status()
    
    rules_engine_status = {}
    if sentinel_service.rules_engine:
        rules_engine_status = sentinel_service.rules_engine.get_status()
    
    event_bus_status = sentinel_service.event_bus.get_stats()
    
    return StatusResponse(
        running=sentinel_service.running,
        uptime_seconds=time.time() - sentinel_service.startup_time,
        collectors=collectors_status,
        rules_engine=rules_engine_status,
        event_bus=event_bus_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
```

## Error Handling and Resilience

### Component Isolation

Components are isolated to prevent cascading failures:

```python
async def _deliver_event(self, event: SentinelEvent) -> None:
    """Deliver event to all matching subscribers with isolation."""
    
    for subscription in subscriptions:
        try:
            # Isolated delivery - failures don't affect other subscribers
            if asyncio.iscoroutinefunction(subscription.callback):
                await subscription.callback(event)
            else:
                subscription.callback(event)
            
            # Update success metrics
            subscription.event_count += 1
            self._deliver_ok += 1
            
        except Exception as e:
            # Log error but continue with other subscribers
            logger.error(f"Event delivery failed to {subscription.subscriber_name}: {e}")
            self._deliver_fail += 1
            
            # Mark subscription as potentially dead
            dead_subscriptions.append(subscription)
```

### Graceful Degradation

Components gracefully handle missing dependencies:

```python
class ThreatIntelDB:
    def __init__(self, loader: KnowledgeLoader | None = None):
        self.loader = loader
        self._available = loader is not None
    
    def search(self, query: str, k: int = 10) -> list[dict[str, Any]]:
        """Search with graceful degradation."""
        if not self._available:
            logger.warning("Threat intel search unavailable - knowledge loader not initialized")
            return []
        
        try:
            return self._perform_search(query, k)
        except Exception as e:
            logger.error(f"Threat intel search failed: {e}")
            return []
```

## Performance Optimization

### Asynchronous Processing

All I/O operations are asynchronous to prevent blocking:

```python
class FileSystemMonitor:
    async def start(self) -> None:
        """Start monitoring with async event handling."""
        self.observer = Observer()
        
        for path in self.config.paths:
            event_handler = AsyncFileEventHandler(self._handle_event)
            self.observer.schedule(event_handler, path, recursive=True)
        
        self.observer.start()
        logger.info(f"File system monitoring started for {len(self.config.paths)} paths")
    
    async def _handle_event(self, event) -> None:
        """Handle file system event asynchronously."""
        # Process event without blocking the observer
        asyncio.create_task(self._process_file_event(event))
```

### Event Batching

High-frequency events can be batched for efficiency:

```python
class NetworkMonitor:
    def __init__(self, config: NetworkConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self._event_batch = []
        self._batch_size = 10
        self._batch_timeout = 1.0
    
    async def _batch_events(self) -> None:
        """Batch network events for efficient processing."""
        while self.running:
            await asyncio.sleep(self._batch_timeout)
            
            if self._event_batch:
                # Process batch of events
                batch = self._event_batch.copy()
                self._event_batch.clear()
                
                for event in batch:
                    await self.event_bus.publish(event)
```

## Testing Integration

### Component Mocking

Components can be mocked for isolated testing:

```python
class MockEventBus:
    def __init__(self):
        self.published_events = []
        self.subscriptions = []
    
    async def publish(self, event: SentinelEvent) -> None:
        self.published_events.append(event)
    
    def subscribe(self, event_type, callback, name, filter_func=None):
        subscription = MockSubscription(event_type, callback, name)
        self.subscriptions.append(subscription)
        return subscription

# Test with mock event bus
def test_rules_engine():
    mock_bus = MockEventBus()
    rules_engine = RulesEngine({}, mock_bus)
    
    # Test event processing
    file_event = FileEvent(event_type=EventType.CREATED, path="test.txt")
    await rules_engine._handle_file_event(file_event)
    
    # Verify alert was published
    assert len(mock_bus.published_events) > 0
    assert isinstance(mock_bus.published_events[0], DetectionAlert)
```

### Integration Testing

End-to-end integration tests validate component interactions:

```python
@pytest.mark.asyncio
async def test_end_to_end_detection():
    """Test complete detection pipeline."""
    
    # Initialize real components
    event_bus = EventBus()
    await event_bus.start()
    
    rules_engine = RulesEngine({}, event_bus)
    await rules_engine.start()
    
    alert_manager = AlertManager({}, event_bus)
    await alert_manager.start()
    
    # Simulate suspicious file event
    file_event = FileEvent(
        event_type=EventType.CREATED,
        path="suspicious.exe",
        entropy=7.9
    )
    
    # Publish event and wait for processing
    await event_bus.publish(file_event)
    await asyncio.sleep(0.1)
    
    # Verify alert was generated and processed
    assert len(alert_manager.get_recent_alerts()) > 0
    
    # Cleanup
    await event_bus.stop()
```
