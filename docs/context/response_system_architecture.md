# Response System Architecture - WatchLockAI Sentinel

## Overview

The WatchLockAI Sentinel response system provides automated and manual response capabilities for detected threats. The system implements operational mode enforcement, user consent workflows, and comprehensive action logging with safety guardrails.

## Core Components

### Alert Management (`response/alerts.py`)

Centralized alert processing and notification system:

#### Alert Handlers

**ToastNotificationHandler**
- Desktop toast notifications for real-time alerts
- Configurable notification content and duration
- Cross-platform support via plyer library
- Graceful degradation when notifications unavailable

**JSONLAlertLogger**
- Structured logging of alerts to JSONL format
- Configurable log file paths and rotation
- Machine-readable format for analysis tools
- Atomic write operations for data integrity

**TrayAlertBuffer**
- In-memory buffer for system tray display
- Recent alerts accessible via tray menu
- Configurable buffer size and retention
- Thread-safe access for UI components

#### Alert Processing Flow
```python
async def _process_alert(self, alert: DetectionAlert) -> None:
    """Process incoming detection alert through all handlers."""
    logger.info(f"Processing alert: {alert.id} [{alert.severity.upper()}] {alert.tag}")
    
    # Update statistics
    self._stats["alerts_processed"] += 1
    
    # Add to tray buffer
    self.tray_buffer.add_alert(alert)
    
    # Send toast notification
    if self.config.toast_notifications:
        success = await self.toast_handler.send_notification(alert)
        if success:
            self._stats["toast_notifications_sent"] += 1
    
    # Log to JSONL
    success = await self.jsonl_logger.log_alert(alert)
    if success:
        self._stats["jsonl_logs_written"] += 1
```

### Response Actions (`response/actions.py`)

Automated response action execution with operational mode enforcement:

#### Action Types

**ProcessTerminator**
- Terminate suspicious processes by PID
- Graceful termination with fallback to force kill
- Process validation and safety checks
- Cross-platform process management

**MonitoringController**
- Pause/resume monitoring components
- Temporary monitoring suspension
- Component state management
- Graceful restart capabilities

**DirectoryQuarantiner** (Stub Implementation)
- Directory isolation and quarantine
- File system access restrictions
- Quarantine metadata tracking
- Restoration capabilities

#### Operational Mode Enforcement
```python
def _check_mode_enforcement(self, action_type: ActionType, action_description: str) -> ActionRecord | None:
    """Check operational mode enforcement for an action."""
    current_mode = self._get_current_operational_mode()
    
    # Enforcement rules based on operational mode
    if current_mode == "offline":
        # offline: no outbound/destructive actions; log intent only
        if action_type in [ActionType.TERMINATE_PROCESS, ActionType.QUARANTINE_DIRECTORY]:
            logger.info(f"[OFFLINE MODE] Would perform: {action_description}")
            return ActionRecord(
                action_type,
                {"blocked_reason": "offline_mode"},
                ActionResult.UNAUTHORIZED,
                f"Action blocked in offline mode: {action_description}",
            )
    
    elif current_mode == "alert":
        # alert: allow alerting/logging; block containment/quarantine actions
        if action_type in [ActionType.TERMINATE_PROCESS, ActionType.QUARANTINE_DIRECTORY]:
            logger.warning(f"[ALERT MODE] Blocking containment action: {action_description}")
            return ActionRecord(
                action_type,
                {"blocked_reason": "alert_mode"},
                ActionResult.UNAUTHORIZED,
                f"Containment action blocked in alert mode: {action_description}",
            )
```

#### Action Execution
```python
async def execute_action(self, action_type: ActionType, parameters: dict[str, Any]) -> ActionRecord:
    """Execute response action with full safety checks."""
    action_description = f"{action_type.value} with {parameters}"
    
    # Check operational mode enforcement
    mode_block = self._check_mode_enforcement(action_type, action_description)
    if mode_block:
        self.action_history.append(mode_block)
        return mode_block
    
    # Check destructive action permissions
    if action_type in [ActionType.TERMINATE_PROCESS, ActionType.QUARANTINE_DIRECTORY]:
        if not self.config.allow_destructive_actions:
            return ActionRecord(
                action_type,
                parameters,
                ActionResult.UNAUTHORIZED,
                "Destructive actions disabled in configuration",
            )
    
    # Execute action through appropriate handler
    if action_type == ActionType.TERMINATE_PROCESS:
        result = self.process_terminator.terminate_process(parameters.get("pid"))
    elif action_type == ActionType.PAUSE_MONITORING:
        result = self.monitoring_controller.pause_monitoring()
    elif action_type == ActionType.QUARANTINE_DIRECTORY:
        result = self.directory_quarantiner.quarantine_directory(parameters.get("path"))
    
    # Record action in history
    self.action_history.append(result)
    return result
```

### Playbooks (`response/playbooks.py`)

MITRE ATT&CK response playbooks with mode-aware execution:

#### Playbook Triggers
```python
async def trigger(self, rule, ctx: Dict[str, Any]) -> None:
    """Trigger playbook response for matched rule."""
    try:
        # Always publish an AlertEvent first
        alert_event = {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "severity": rule.severity,
            "context": ctx,
            "playbook_triggered": True
        }
        
        if self.bus:
            self.bus.publish("AlertEvent", alert_event)
            logger.info(f"Published AlertEvent for rule {rule.id}")
        
        # Check operational mode for reactive responses
        current_mode = self.mode_provider()
        logger.info(f"Current operational mode: {current_mode}")
        
        # Only execute reactive responses in contain/quarantine modes
        if current_mode not in ("contain", "quarantine"):
            logger.info(f"Mode {current_mode} - skipping reactive response")
            return
        
        # Execute response based on rule.response
        if rule.response:
            await self._execute_response(rule.response, rule, ctx)
            
    except Exception as e:
        logger.error(f"Error in playbook trigger for rule {rule.id}: {e}")
        # Never raise - playbooks must be resilient
```

#### Response Actions
```python
async def _execute_response(self, response: str, rule, ctx: Dict[str, Any]) -> None:
    """Execute specific response action."""
    trigger_data = ctx.get("trigger_data", {})
    
    if response == "disable_account":
        username = trigger_data.get("username")
        if username:
            action_request = {
                "action": "disable_account",
                "target_user": username,
                "rule_id": rule.id,
                "severity": rule.severity,
                "reason": f"Triggered by MITRE rule: {rule.name}"
            }
            
            if self.bus:
                self.bus.publish("ActionRequestEvent", action_request)
                logger.warning(f"Account disable requested for user: {username}")
    
    elif response == "quarantine_directory":
        directory = trigger_data.get("directory")
        if directory:
            action_request = {
                "action": "quarantine_directory",
                "target_path": directory,
                "rule_id": rule.id,
                "severity": rule.severity
            }
            
            if self.bus:
                self.bus.publish("ActionRequestEvent", action_request)
                logger.warning(f"Directory quarantine requested: {directory}")
```

## Operational Mode System

### Mode Definitions

**observe**: Passive monitoring only
- Collect events and generate alerts
- No automated response actions
- Full logging and notification

**alert**: Active alerting with limited response
- All observe mode capabilities
- Toast notifications and logging
- Block containment/quarantine actions
- Allow monitoring control actions

**contain**: Active containment responses
- All alert mode capabilities
- Process termination allowed
- Network isolation permitted
- Directory quarantine blocked

**quarantine**: Full response capabilities
- All contain mode capabilities
- Directory quarantine allowed
- File system restrictions
- Maximum response authority

**offline**: Minimal operations mode
- Event collection only
- No outbound connections
- No destructive actions
- Log intended actions only

### Mode Enforcement Implementation
```python
def _get_current_operational_mode(self) -> str:
    """Get current operational mode from storage."""
    try:
        from config.operational_mode import get_mode
        return get_mode()
    except Exception as e:
        logger.warning(f"Failed to get operational mode: {e}, using default 'observe'")
        return "observe"
```

## User Consent and Safety

### Consent Workflow
```python
def _request_user_consent(self, action_type: ActionType, parameters: dict[str, Any]) -> bool:
    """Request user consent for destructive actions."""
    if not self.config.require_user_consent:
        return True
    
    consent_id = str(uuid.uuid4())
    consent_request = {
        "id": consent_id,
        "action_type": action_type.value,
        "parameters": parameters,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "timeout_seconds": 300,  # 5 minute timeout
    }
    
    self._pending_consent_requests[consent_id] = consent_request
    
    # Notify UI components of pending consent request
    # Implementation depends on UI integration
    
    return False  # Consent pending
```

### Safety Guardrails
- Operational mode enforcement prevents unauthorized actions
- Configuration flags control destructive action availability
- User consent requirements for high-impact operations
- Action history logging for audit trails
- Graceful degradation when components unavailable

## Integration with Detection System

### Alert Processing Pipeline
1. **Detection Engine** → Generates DetectionAlert events
2. **Alert Manager** → Processes alerts through notification handlers
3. **Playbook System** → Evaluates automated response triggers
4. **Action Manager** → Executes approved response actions
5. **Audit System** → Records all actions and decisions

### Event Bus Integration
```python
# Alert Manager subscribes to DetectionAlert events
subscription = event_bus.subscribe(
    DetectionAlert,
    self._process_alert,
    "alert_manager"
)

# Playbook system subscribes to MITRE rule matches
subscription = event_bus.subscribe(
    "AlertEvent",
    self.playbooks.trigger,
    "playbook_responder"
)
```

## Configuration and Customization

### Alert Configuration
```yaml
alerts:
  toast_notifications: true
  log_jsonl: true
  jsonl_path: "logs/alerts.jsonl"
  tray_buffer_size: 50
```

### Response Configuration
```yaml
responses:
  allow_destructive_actions: false
  require_user_consent: true
  action_timeout_seconds: 30
  max_action_history: 1000
```

### Operational Configuration
```yaml
operational:
  mode: "observe"  # Default mode
  # Runtime mode stored in config/operational_mode.json
```

## Monitoring and Observability

### Alert Statistics
```python
stats = alert_manager.get_stats()
# Returns:
# {
#     "alerts_processed": 150,
#     "toast_notifications_sent": 145,
#     "jsonl_logs_written": 150,
#     "started_at": "2025-01-01T00:00:00Z"
# }
```

### Action History
```python
recent_actions = actions_manager.get_recent_actions(limit=10)
# Returns list of ActionRecord objects with:
# - action_type, parameters, result, message, timestamp
```

### Performance Metrics
- Alert processing latency
- Action execution times
- Notification delivery success rates
- Mode enforcement effectiveness

## Security Considerations

### Action Authorization
- Operational mode-based access control
- Configuration-based permission gates
- User consent for destructive operations
- Audit logging for all actions

### Data Protection
- Sensitive parameter redaction in logs
- Secure storage of action history
- Encrypted communication for remote actions
- Privacy-preserving alert content

### System Integrity
- Process validation before termination
- Path validation for quarantine operations
- Resource limit enforcement
- Graceful failure handling

## Testing and Validation

### Unit Testing
- Mock action execution for safety
- Operational mode enforcement validation
- Alert processing pipeline testing
- Configuration validation

### Integration Testing
- End-to-end response workflows
- Cross-component communication
- Error condition handling
- Performance under load

### Safety Testing
- Destructive action prevention
- Mode enforcement validation
- Consent workflow testing
- Audit trail verification
