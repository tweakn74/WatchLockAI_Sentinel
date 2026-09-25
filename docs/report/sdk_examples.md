# P11 SDK Client Examples and Documentation

**Generated:** 2025-09-06T23:44:00Z  
**Sprint:** P11 - SDK Client Finalization  
**SDK Version:** 1.0  
**API Coverage:** 41+ endpoints with full functionality  

## Executive Summary

Comprehensive Python SDK client library for WatchLockAI Sentinel provides complete API access with robust error handling, authentication management, and advanced features including streaming support and retry logic. The SDK covers all documented API endpoints with type hints, comprehensive documentation, and extensive example code.

**Key SDK Features:**
- **Complete API Coverage:** All 41+ documented endpoints supported
- **Multiple Authentication Methods:** Admin tokens, session cookies, username/password
- **Advanced Error Handling:** Custom exceptions with detailed error information
- **Rate Limiting Awareness:** Automatic retry with backoff for rate-limited requests
- **Streaming Support:** Server-Sent Events (SSE) for real-time data
- **Type Safety:** Full type hints and runtime validation
- **Production Ready:** Configurable timeouts, SSL verification, and logging

## SDK Installation and Setup

### Installation Requirements
```bash
# Required dependencies
pip install requests

# Optional dependencies for advanced features
pip install sseclient-py  # For streaming support
pip install urllib3      # Enhanced HTTP adapter support
```

### Basic SDK Import
```python
from tools.sentinel_sdk import SentinelClient, SentinelAPIError, SentinelAuthError

# Quick convenience imports
from tools.sentinel_sdk import quick_health_check, quick_status_check, create_client
```

## Authentication Examples

### 1. Basic Connection (No Authentication)
```python
# Simple connectivity for public endpoints
client = SentinelClient(base_url="http://localhost:8080")

# Test basic connectivity
health = client.get_health()
print(f"Service healthy: {health['ok']}")

# Get basic status
status = client.get_status()
print(f"Service running: {status['running']}")
```

### 2. Admin Token Authentication
```python
# Admin-level access for privileged operations
client = SentinelClient(
    base_url="http://localhost:8080",
    admin_token="your-admin-token-here"
)

# Access admin-only endpoints
config_schema = client.get_admin_config_schema()
print(f"Config schema keys: {list(config_schema.keys())}")

# Reload configuration
reload_result = client.reload_config(debounce_ms=1000)
print(f"Config reload status: {reload_result['status']}")
```

### 3. Session-Based Authentication
```python
# Username/password authentication with session management
client = SentinelClient(
    base_url="http://localhost:8080",
    username="your-username",
    password="your-password"
)

# Client automatically logs in during initialization
user_info = client.get_current_user()
print(f"Logged in as: {user_info['username']}")

# Access authenticated endpoints
metrics = client.get_health_metrics()
print(f"Event bus metrics: {metrics['event_bus']}")

# Manual logout when done
client.logout()
```

### 4. Advanced Configuration
```python
# Production-ready configuration with SSL and retry logic
client = SentinelClient(
    base_url="https://sentinel.example.com",
    admin_token="secure-admin-token",
    timeout=60,                    # 60 second timeout
    max_retries=5,                # 5 retry attempts
    backoff_factor=0.5,           # Exponential backoff
    verify_ssl=True,              # SSL certificate verification
    user_agent="MyApp/1.0",       # Custom User-Agent
    debug=True                    # Enable debug logging
)
```

## Health and Status Monitoring Examples

### 1. Basic Health Monitoring
```python
def monitor_service_health(client):
    """Monitor basic service health."""
    try:
        health = client.get_health()
        
        if health['ok']:
            uptime = health.get('uptime_s', 0)
            print(f"[x] Service healthy (uptime: {uptime}s)")
            
            # Check individual components
            components = health.get('components', {})
            for component, status in components.items():
                if isinstance(status, dict):
                    running = status.get('running', False)
                    print(f"  {component}: {'[x]' if running else '[FAIL]'}")
                else:
                    print(f"  {component}: {status}")
        else:
            print("[FAIL] Service unhealthy")
            
    except SentinelAPIError as e:
        print(f"[FAIL] Health check failed: {e}")

# Usage
client = SentinelClient(base_url="http://localhost:8080")
monitor_service_health(client)
```

### 2. Comprehensive Status Dashboard
```python
def create_status_dashboard(client):
    """Create comprehensive status dashboard."""
    dashboard = {
        'timestamp': datetime.now().isoformat(),
        'status': 'unknown'
    }
    
    try:
        # Basic health
        health = client.get_health()
        dashboard['health'] = health
        
        # Detailed status
        status = client.get_status()
        dashboard['status'] = 'healthy' if status.get('running') else 'unhealthy'
        dashboard['service_status'] = status
        
        # Metrics snapshot (if available)
        try:
            metrics = client.get_metrics_snapshot()
            dashboard['metrics'] = metrics
        except SentinelAuthError:
            dashboard['metrics'] = {'error': 'Authentication required'}
        
        # Event bus metrics (if available)
        try:
            event_bus = client.get_event_bus_metrics()
            dashboard['event_bus'] = event_bus
        except (SentinelAuthError, SentinelAPIError):
            dashboard['event_bus'] = {'error': 'Not available or auth required'}
        
        return dashboard
        
    except Exception as e:
        dashboard['error'] = str(e)
        dashboard['status'] = 'error'
        return dashboard

# Usage with error handling
try:
    client = SentinelClient(base_url="http://localhost:8080", admin_token="token")
    dashboard = create_status_dashboard(client)
    print(json.dumps(dashboard, indent=2))
except Exception as e:
    print(f"Dashboard creation failed: {e}")
```

## Detection and Alert Management Examples

### 1. Alert Monitoring with Pagination
```python
def monitor_alerts(client, max_alerts=1000):
    """Monitor alerts with pagination support."""
    alerts = []
    offset = 0
    limit = 100
    
    while len(alerts) < max_alerts:
        try:
            response = client.get_alerts(limit=limit, offset=offset)
            batch = response.get('alerts', [])
            
            if not batch:
                break  # No more alerts
                
            alerts.extend(batch)
            offset += limit
            
            print(f"Retrieved {len(batch)} alerts (total: {len(alerts)})")
            
        except SentinelAPIError as e:
            print(f"Alert retrieval failed: {e}")
            break
    
    # Process alerts
    critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
    print(f"Found {len(critical_alerts)} critical alerts")
    
    return alerts

# Usage
client = SentinelClient(base_url="http://localhost:8080")
all_alerts = monitor_alerts(client)
```

### 2. Real-time Detection Processing
```python
def process_detections_realtime(client):
    """Process detections with real-time analysis."""
    detection_stats = {
        'total': 0,
        'by_type': {},
        'by_severity': {},
        'last_updated': None
    }
    
    try:
        detections_response = client.get_detections(limit=500)
        detections = detections_response.get('detections', [])
        
        for detection in detections:
            detection_stats['total'] += 1
            
            # Count by type
            detection_type = detection.get('type', 'unknown')
            detection_stats['by_type'][detection_type] = \
                detection_stats['by_type'].get(detection_type, 0) + 1
            
            # Count by severity
            severity = detection.get('severity', 'unknown')
            detection_stats['by_severity'][severity] = \
                detection_stats['by_severity'].get(severity, 0) + 1
        
        detection_stats['last_updated'] = datetime.now().isoformat()
        
        print("Detection Statistics:")
        print(f"  Total: {detection_stats['total']}")
        print(f"  By Type: {detection_stats['by_type']}")
        print(f"  By Severity: {detection_stats['by_severity']}")
        
        return detection_stats
        
    except Exception as e:
        print(f"Detection processing failed: {e}")
        return detection_stats

# Usage
client = SentinelClient(base_url="http://localhost:8080")
stats = process_detections_realtime(client)
```

### 3. Anomaly Score Monitoring
```python
def monitor_anomaly_scores(client, threshold=0.8):
    """Monitor anomaly scores with alerting."""
    try:
        anomaly_data = client.get_anomaly_score()
        current_score = anomaly_data.get('score', 0.0)
        
        print(f"Current anomaly score: {current_score:.3f}")
        
        if current_score > threshold:
            print(f"[WARN] HIGH ANOMALY ALERT: Score {current_score:.3f} exceeds threshold {threshold}")
            
            # Get additional context
            details = anomaly_data.get('details', {})
            contributing_factors = details.get('contributing_factors', [])
            
            if contributing_factors:
                print("Contributing factors:")
                for factor in contributing_factors:
                    print(f"  - {factor}")
        else:
            print(f"[x] Anomaly score within normal range")
        
        return anomaly_data
        
    except Exception as e:
        print(f"Anomaly monitoring failed: {e}")
        return None

# Usage
client = SentinelClient(base_url="http://localhost:8080")
anomaly_data = monitor_anomaly_scores(client, threshold=0.75)
```

## Administrative Operations Examples

### 1. Configuration Management
```python
def manage_configuration(client):
    """Demonstrate configuration management operations."""
    try:
        # Get configuration schema
        schema = client.get_admin_config_schema()
        print(f"Configuration schema has {len(schema)} sections")
        
        # Preview configuration reload
        print("Reloading configuration...")
        reload_result = client.reload_config(debounce_ms=500)
        print(f"Reload status: {reload_result['status']}")
        
        # Wait for reload to complete
        time.sleep(1)
        
        # Verify service still healthy after reload
        health = client.get_health()
        if health['ok']:
            print("[x] Service healthy after configuration reload")
        else:
            print("[FAIL] Service unhealthy after configuration reload")
            
    except SentinelAuthError:
        print("[FAIL] Admin authentication required for configuration management")
    except Exception as e:
        print(f"Configuration management failed: {e}")

# Usage
client = SentinelClient(
    base_url="http://localhost:8080",
    admin_token="your-admin-token"
)
manage_configuration(client)
```

### 2. System Backup and Restore
```python
def backup_restore_operations(client):
    """Demonstrate backup and restore operations."""
    try:
        # Create system backup
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Creating backup: {backup_name}")
        
        backup_result = client.backup_system(backup_name=backup_name)
        backup_id = backup_result.get('backup_id')
        
        if backup_id:
            print(f"[x] Backup created successfully: {backup_id}")
            
            # In a real scenario, you might restore from a different backup
            # This is just for demonstration - don't restore immediately in production!
            confirm = input("Restore from this backup? (y/N): ")
            if confirm.lower() == 'y':
                print(f"Restoring from backup: {backup_id}")
                restore_result = client.restore_system(backup_id)
                print(f"Restore result: {restore_result}")
        else:
            print("[FAIL] Backup creation failed")
            
    except SentinelAuthError:
        print("[FAIL] Admin authentication required for backup operations")
    except Exception as e:
        print(f"Backup operations failed: {e}")

# Usage (use with caution!)
client = SentinelClient(
    base_url="http://localhost:8080",
    admin_token="your-admin-token"
)
# backup_restore_operations(client)  # Uncomment to run
```

### 3. Plugin Management
```python
def manage_plugins(client):
    """Demonstrate plugin management operations."""
    try:
        # Get available plugins
        plugins_response = client.get_plugins()
        plugins = plugins_response.get('plugins', [])
        
        print(f"Available plugins: {len(plugins)}")
        for plugin in plugins:
            name = plugin.get('name', 'unknown')
            status = plugin.get('status', 'unknown')
            description = plugin.get('description', 'No description')
            print(f"  {name}: {status} - {description}")
        
        # Execute a safe plugin (example)
        if plugins:
            # Find a safe plugin to execute (avoid destructive ones)
            safe_plugins = [p for p in plugins if 'test' in p.get('name', '').lower()]
            
            if safe_plugins:
                plugin_name = safe_plugins[0]['name']
                print(f"Executing plugin: {plugin_name}")
                
                result = client.execute_plugin(
                    plugin_name=plugin_name,
                    args={'test_mode': True}
                )
                print(f"Plugin result: {result}")
            else:
                print("No safe test plugins available for execution")
                
    except SentinelAuthError:
        print("[FAIL] Admin authentication required for plugin management")
    except Exception as e:
        print(f"Plugin management failed: {e}")

# Usage
client = SentinelClient(
    base_url="http://localhost:8080",
    admin_token="your-admin-token"
)
manage_plugins(client)
```

## Performance and Chaos Engineering Examples

### 1. Performance Monitoring
```python
def run_performance_analysis(client):
    """Run comprehensive performance analysis."""
    performance_data = {}
    
    try:
        # Quick performance probe
        print("Running quick performance probe...")
        quick_probe = client.run_quick_performance_probe()
        performance_data['quick_probe'] = quick_probe
        
        print(f"Quick probe results:")
        for metric, value in quick_probe.items():
            print(f"  {metric}: {value}")
        
        # Detailed performance probe
        print("Running detailed performance probe (30 seconds)...")
        detailed_probe = client.run_detailed_performance_probe(duration_seconds=30)
        performance_data['detailed_probe'] = detailed_probe
        
        # Analyze results
        if 'response_time_ms' in detailed_probe:
            response_time = detailed_probe['response_time_ms']
            if response_time < 100:
                print(f"[x] Excellent response time: {response_time}ms")
            elif response_time < 500:
                print(f"[x] Good response time: {response_time}ms")
            else:
                print(f"[WARN] High response time: {response_time}ms")
        
        return performance_data
        
    except SentinelAuthError:
        print("[FAIL] Admin authentication required for performance monitoring")
        return {}
    except Exception as e:
        print(f"Performance analysis failed: {e}")
        return {}

# Usage
client = SentinelClient(
    base_url="http://localhost:8080",
    admin_token="your-admin-token"
)
perf_data = run_performance_analysis(client)
```

### 2. Chaos Engineering
```python
def chaos_engineering_test(client):
    """Demonstrate chaos engineering capabilities."""
    try:
        # Check current chaos status
        chaos_status = client.get_chaos_status()
        print(f"Chaos status: {chaos_status}")
        
        if chaos_status.get('active'):
            print("[WARN] Chaos test already running")
            return
        
        # Run a mild chaos test
        print("Injecting mild chaos (network latency) for 30 seconds...")
        chaos_result = client.inject_chaos(
            chaos_type="network_latency",
            duration_seconds=30
        )
        
        print(f"Chaos injection result: {chaos_result}")
        
        # Monitor system during chaos
        for i in range(6):  # Check every 5 seconds for 30 seconds
            time.sleep(5)
            try:
                health = client.get_health()
                if health['ok']:
                    print(f"  {i*5+5}s: System still healthy during chaos")
                else:
                    print(f"  {i*5+5}s: [WARN] System degraded during chaos")
            except Exception as e:
                print(f"  {i*5+5}s: [FAIL] Health check failed: {e}")
        
        # Check final status
        final_status = client.get_chaos_status()
        if not final_status.get('active'):
            print("[x] Chaos test completed, system recovered")
        
    except SentinelAuthError:
        print("[FAIL] Admin authentication required for chaos engineering")
    except Exception as e:
        print(f"Chaos engineering test failed: {e}")

# Usage (use with extreme caution in production!)
client = SentinelClient(
    base_url="http://localhost:8080",
    admin_token="your-admin-token"
)
# chaos_engineering_test(client)  # Uncomment to run
```

## Real-time Streaming Examples

### 1. Basic Event Streaming
```python
def stream_events_basic(client, duration_seconds=60):
    """Basic event streaming example."""
    if not SSE_AVAILABLE:
        print("[FAIL] sseclient-py required for streaming functionality")
        return
    
    print(f"Streaming events for {duration_seconds} seconds...")
    start_time = time.time()
    event_count = 0
    
    try:
        for event in client.stream_events():
            event_count += 1
            timestamp = event.get('timestamp', 'unknown')
            event_type = event.get('type', 'unknown')
            
            print(f"Event {event_count}: {event_type} at {timestamp}")
            
            # Stop after specified duration
            if time.time() - start_time > duration_seconds:
                break
    
    except Exception as e:
        print(f"Streaming failed: {e}")
    
    print(f"Received {event_count} events in {duration_seconds} seconds")

# Usage
from tools.sentinel_sdk import SSE_AVAILABLE

client = SentinelClient(base_url="http://localhost:8080")
if SSE_AVAILABLE:
    stream_events_basic(client, duration_seconds=30)
```

### 2. Advanced Event Processing
```python
def stream_events_advanced(client):
    """Advanced event streaming with processing and filtering."""
    if not SSE_AVAILABLE:
        print("[FAIL] sseclient-py required for streaming functionality")
        return
    
    event_processors = {
        'alert': lambda e: print(f"[ALERT] ALERT: {e.get('message', 'No message')}"),
        'detection': lambda e: print(f"[SEARCH] DETECTION: {e.get('rule_name', 'Unknown rule')}"),
        'health': lambda e: print(f"[U+1F49A] HEALTH: {e.get('status', 'Unknown status')}"),
        'metric': lambda e: print(f"[BARS] METRIC: {e.get('name', 'Unknown metric')} = {e.get('value', 'No value')}")
    }
    
    try:
        print("Starting advanced event stream processing...")
        for event in client.stream_events():
            event_type = event.get('type', 'unknown')
            
            # Process known event types
            if event_type in event_processors:
                event_processors[event_type](event)
            else:
                print(f"[U+2753] UNKNOWN: {event_type} - {event}")
            
            # Add custom business logic here
            if event_type == 'alert' and event.get('severity') == 'critical':
                # Handle critical alerts
                print(f"[ALERT] CRITICAL ALERT HANDLER: {event}")
            
    except KeyboardInterrupt:
        print("\n[STOP] Stream processing stopped by user")
    except Exception as e:
        print(f"Advanced streaming failed: {e}")

# Usage
client = SentinelClient(base_url="http://localhost:8080")
if SSE_AVAILABLE:
    stream_events_advanced(client)
```

## Error Handling and Resilience Examples

### 1. Comprehensive Error Handling
```python
def robust_api_calls(client):
    """Demonstrate robust API error handling."""
    operations = [
        ("Health Check", lambda: client.get_health()),
        ("Status Check", lambda: client.get_status()),
        ("Metrics (Auth Required)", lambda: client.get_health_metrics()),
        ("Admin Config (Admin Required)", lambda: client.get_admin_config_schema()),
        ("Non-existent Endpoint", lambda: client._get_json("/api/nonexistent"))
    ]
    
    results = {}
    
    for name, operation in operations:
        try:
            print(f"Executing: {name}")
            result = operation()
            results[name] = {"status": "success", "data": result}
            print(f"  [x] Success")
            
        except SentinelAuthError as e:
            results[name] = {"status": "auth_error", "error": str(e)}
            print(f"  [LOCK] Auth Error: {e}")
            
        except SentinelRateLimitError as e:
            results[name] = {"status": "rate_limit", "error": str(e)}
            print(f"  [U+23F1] Rate Limited: {e}")
            
        except SentinelAPIError as e:
            results[name] = {"status": "api_error", "error": str(e)}
            print(f"  [FAIL] API Error: {e}")
            
        except Exception as e:
            results[name] = {"status": "unexpected_error", "error": str(e)}
            print(f"  [U+1F4A5] Unexpected Error: {e}")
    
    return results

# Usage
client = SentinelClient(base_url="http://localhost:8080")
results = robust_api_calls(client)
```

### 2. Retry Logic with Exponential Backoff
```python
def retry_with_backoff(client, operation_name, operation_func, max_attempts=3):
    """Implement custom retry logic with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}/{max_attempts}: {operation_name}")
            result = operation_func()
            print(f"  [x] Success on attempt {attempt + 1}")
            return result
            
        except SentinelRateLimitError as e:
            if attempt < max_attempts - 1:
                wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                print(f"  [U+23F1] Rate limited, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"  [FAIL] Max retries reached, giving up")
                raise
                
        except SentinelAPIError as e:
            if e.status_code and e.status_code >= 500:  # Server errors
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) * 0.5  # Shorter backoff for server errors
                    print(f"  [RELOAD] Server error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  [FAIL] Max retries reached for server error")
                    raise
            else:
                # Client errors (4xx) - don't retry
                print(f"  [FAIL] Client error, not retrying: {e}")
                raise
                
        except Exception as e:
            print(f"  [U+1F4A5] Unexpected error: {e}")
            raise

# Usage examples
client = SentinelClient(base_url="http://localhost:8080")

# Retry health check
health = retry_with_backoff(
    client, 
    "Health Check", 
    client.get_health
)

# Retry with admin operation
admin_client = SentinelClient(
    base_url="http://localhost:8080",
    admin_token="your-admin-token"
)

config = retry_with_backoff(
    admin_client,
    "Get Config Schema",
    admin_client.get_admin_config_schema
)
```

## Batch Operations and Automation Examples

### 1. Batch Alert Processing
```python
def batch_alert_processing(client, batch_size=100):
    """Process alerts in batches for efficiency."""
    all_alerts = []
    processed_count = 0
    offset = 0
    
    while True:
        try:
            # Get batch of alerts
            response = client.get_alerts(limit=batch_size, offset=offset)
            alerts = response.get('alerts', [])
            
            if not alerts:
                break  # No more alerts
            
            # Process this batch
            for alert in alerts:
                # Custom alert processing logic
                severity = alert.get('severity', 'unknown')
                alert_type = alert.get('type', 'unknown')
                timestamp = alert.get('timestamp', 'unknown')
                
                # Example: Count by severity
                if severity == 'critical':
                    print(f"[WARN] Critical alert: {alert_type} at {timestamp}")
                elif severity == 'high':
                    print(f"[U+1F536] High alert: {alert_type} at {timestamp}")
                
                processed_count += 1
            
            all_alerts.extend(alerts)
            offset += batch_size
            
            print(f"Processed batch: {len(alerts)} alerts (total: {processed_count})")
            
        except Exception as e:
            print(f"Batch processing failed at offset {offset}: {e}")
            break
    
    # Generate summary
    summary = {
        'total_alerts': len(all_alerts),
        'by_severity': {},
        'by_type': {}
    }
    
    for alert in all_alerts:
        severity = alert.get('severity', 'unknown')
        alert_type = alert.get('type', 'unknown')
        
        summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
        summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
    
    return summary

# Usage
client = SentinelClient(base_url="http://localhost:8080")
summary = batch_alert_processing(client)
print(f"Alert Summary: {json.dumps(summary, indent=2)}")
```

### 2. Automated Health Monitoring Loop
```python
def continuous_health_monitoring(client, check_interval=30, duration_minutes=60):
    """Continuous health monitoring with automated alerting."""
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    check_count = 0
    health_history = []
    
    print(f"Starting {duration_minutes}-minute health monitoring (checks every {check_interval}s)")
    
    while time.time() < end_time:
        check_count += 1
        timestamp = datetime.now().isoformat()
        
        try:
            # Perform health check
            health = client.get_health()
            
            health_record = {
                'timestamp': timestamp,
                'check_number': check_count,
                'healthy': health.get('ok', False),
                'uptime_seconds': health.get('uptime_s', 0),
                'components': health.get('components', {})
            }
            
            health_history.append(health_record)
            
            if health['ok']:
                print(f"[x] Check {check_count}: Healthy (uptime: {health.get('uptime_s', 0)}s)")
            else:
                print(f"[FAIL] Check {check_count}: UNHEALTHY")
                
                # Trigger additional diagnostics on health failure
                try:
                    status = client.get_status()
                    print(f"  Service status: {status}")
                except Exception as diag_error:
                    print(f"  Diagnostic check failed: {diag_error}")
            
        except Exception as e:
            print(f"[FAIL] Check {check_count}: Health check failed - {e}")
            health_record = {
                'timestamp': timestamp,
                'check_number': check_count,
                'healthy': False,
                'error': str(e)
            }
            health_history.append(health_record)
        
        # Wait for next check (unless this is the last iteration)
        if time.time() + check_interval < end_time:
            time.sleep(check_interval)
    
    # Generate monitoring report
    total_checks = len(health_history)
    healthy_checks = len([h for h in health_history if h.get('healthy', False)])
    unhealthy_checks = total_checks - healthy_checks
    
    print(f"\n=== Health Monitoring Report ===")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Total checks: {total_checks}")
    print(f"Healthy: {healthy_checks} ({healthy_checks/total_checks*100:.1f}%)")
    print(f"Unhealthy: {unhealthy_checks} ({unhealthy_checks/total_checks*100:.1f}%)")
    
    return health_history

# Usage
client = SentinelClient(base_url="http://localhost:8080")
# Run 5-minute monitoring with checks every 10 seconds
health_data = continuous_health_monitoring(client, check_interval=10, duration_minutes=5)
```

## Integration Testing Examples

### 1. Full API Integration Test
```python
def full_api_integration_test(base_url, admin_token=None):
    """Comprehensive API integration test."""
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'base_url': base_url,
        'tests': {},
        'summary': {}
    }
    
    # Test basic connectivity
    print("=== Basic Connectivity Tests ===")
    try:
        client = SentinelClient(base_url=base_url)
        health = client.get_health()
        test_results['tests']['connectivity'] = {'status': 'pass', 'data': health}
        print("[x] Basic connectivity: PASS")
    except Exception as e:
        test_results['tests']['connectivity'] = {'status': 'fail', 'error': str(e)}
        print(f"[FAIL] Basic connectivity: FAIL - {e}")
    
    # Test authenticated endpoints
    print("\n=== Authentication Tests ===")
    if admin_token:
        try:
            admin_client = SentinelClient(base_url=base_url, admin_token=admin_token)
            config = admin_client.get_admin_config_schema()
            test_results['tests']['admin_auth'] = {'status': 'pass', 'data': config}
            print("[x] Admin authentication: PASS")
        except Exception as e:
            test_results['tests']['admin_auth'] = {'status': 'fail', 'error': str(e)}
            print(f"[FAIL] Admin authentication: FAIL - {e}")
    else:
        test_results['tests']['admin_auth'] = {'status': 'skip', 'reason': 'No admin token provided'}
        print("[U+23ED] Admin authentication: SKIP - No token provided")
    
    # Test API endpoints
    print("\n=== API Endpoint Tests ===")
    endpoint_tests = [
        ('/api/status', lambda c: c.get_status()),
        ('/api/alerts', lambda c: c.get_alerts(limit=1)),
        ('/api/detections', lambda c: c.get_detections(limit=1)),
        ('/api/policies', lambda c: c.get_policies()),
    ]
    
    client = SentinelClient(base_url=base_url, admin_token=admin_token)
    
    for endpoint, test_func in endpoint_tests:
        try:
            result = test_func(client)
            test_results['tests'][endpoint] = {'status': 'pass', 'data': result}
            print(f"[x] {endpoint}: PASS")
        except Exception as e:
            test_results['tests'][endpoint] = {'status': 'fail', 'error': str(e)}
            print(f"[FAIL] {endpoint}: FAIL - {e}")
    
    # Generate summary
    total_tests = len(test_results['tests'])
    passed_tests = len([t for t in test_results['tests'].values() if t['status'] == 'pass'])
    failed_tests = len([t for t in test_results['tests'].values() if t['status'] == 'fail'])
    skipped_tests = len([t for t in test_results['tests'].values() if t['status'] == 'skip'])
    
    test_results['summary'] = {
        'total': total_tests,
        'passed': passed_tests,
        'failed': failed_tests,
        'skipped': skipped_tests,
        'pass_rate': passed_tests / total_tests * 100 if total_tests > 0 else 0
    }
    
    print(f"\n=== Test Summary ===")
    print(f"Total: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}, Skipped: {skipped_tests}")
    print(f"Pass Rate: {test_results['summary']['pass_rate']:.1f}%")
    
    return test_results

# Usage
test_results = full_api_integration_test(
    base_url="http://localhost:8080",
    admin_token="your-admin-token-here"
)
```

## Production Usage Patterns

### 1. Production Client Configuration
```python
def create_production_client(config_file="sentinel_config.json"):
    """Create production-ready client from configuration file."""
    
    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # Default production configuration
        config = {
            "base_url": "https://sentinel.example.com",
            "timeout": 60,
            "max_retries": 5,
            "backoff_factor": 0.5,
            "verify_ssl": True,
            "user_agent": "SentinelClient/1.0",
            "debug": False
        }
        
        # Save default configuration
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Created default configuration: {config_file}")
    
    # Get secrets from environment
    admin_token = os.getenv('SENTINEL_ADMIN_TOKEN')
    username = os.getenv('SENTINEL_USERNAME') 
    password = os.getenv('SENTINEL_PASSWORD')
    
    # Create client
    client = SentinelClient(
        base_url=config['base_url'],
        admin_token=admin_token,
        username=username,
        password=password,
        timeout=config['timeout'],
        max_retries=config['max_retries'],
        backoff_factor=config['backoff_factor'],
        verify_ssl=config['verify_ssl'],
        user_agent=config['user_agent'],
        debug=config['debug']
    )
    
    # Validate connection
    validation = client.validate_connection()
    if not validation['connectivity']:
        raise ConnectionError(f"Failed to connect to {config['base_url']}")
    
    print(f"[x] Connected to {config['base_url']}")
    print(f"  Connectivity: {validation['connectivity']}")
    print(f"  Authentication: {validation['authentication']}")
    print(f"  Admin Access: {validation['admin_access']}")
    
    return client

# Usage
# Set environment variables:
# export SENTINEL_ADMIN_TOKEN="your-admin-token"
# export SENTINEL_USERNAME="your-username"  
# export SENTINEL_PASSWORD="your-password"

production_client = create_production_client()
```

### 2. Monitoring Service Integration
```python
class SentinelMonitoringService:
    """Production monitoring service using Sentinel SDK."""
    
    def __init__(self, config_file="monitoring_config.json"):
        self.config = self._load_config(config_file)
        self.client = create_production_client()
        self.metrics_history = []
        self.alert_callbacks = []
    
    def _load_config(self, config_file):
        """Load monitoring configuration."""
        default_config = {
            "health_check_interval": 30,
            "metrics_collection_interval": 60,
            "alert_check_interval": 10,
            "anomaly_threshold": 0.8,
            "retention_days": 30
        }
        
        try:
            with open(config_file, 'r') as f:
                return {**default_config, **json.load(f)}
        except FileNotFoundError:
            return default_config
    
    def add_alert_callback(self, callback):
        """Add callback function for alert notifications."""
        self.alert_callbacks.append(callback)
    
    def _notify_alerts(self, alert_data):
        """Notify all registered alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                print(f"Alert callback failed: {e}")
    
    def collect_metrics(self):
        """Collect and store metrics."""
        try:
            timestamp = datetime.now().isoformat()
            
            # Collect health metrics
            health = self.client.get_health()
            
            # Collect additional metrics if available
            metrics = {}
            try:
                metrics = self.client.get_metrics_snapshot()
            except:
                pass  # Metrics might not be available
            
            # Store metrics
            metric_record = {
                'timestamp': timestamp,
                'health': health,
                'metrics': metrics
            }
            
            self.metrics_history.append(metric_record)
            
            # Cleanup old metrics (retain only configured number of days)
            cutoff_time = datetime.now() - timedelta(days=self.config['retention_days'])
            self.metrics_history = [
                m for m in self.metrics_history 
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]
            
            return metric_record
            
        except Exception as e:
            print(f"Metrics collection failed: {e}")
            return None
    
    def check_alerts(self):
        """Check for new alerts and process them."""
        try:
            alerts = self.client.get_alerts(limit=100)
            new_alerts = alerts.get('alerts', [])
            
            # Process critical alerts
            critical_alerts = [a for a in new_alerts if a.get('severity') == 'critical']
            
            if critical_alerts:
                alert_data = {
                    'timestamp': datetime.now().isoformat(),
                    'critical_count': len(critical_alerts),
                    'alerts': critical_alerts
                }
                self._notify_alerts(alert_data)
            
            return len(new_alerts), len(critical_alerts)
            
        except Exception as e:
            print(f"Alert checking failed: {e}")
            return 0, 0
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle."""
        print(f"Running monitoring cycle at {datetime.now()}")
        
        # Collect metrics
        metrics = self.collect_metrics()
        if metrics:
            health_ok = metrics['health'].get('ok', False)
            print(f"  Health: {'[x]' if health_ok else '[FAIL]'}")
        
        # Check alerts
        total_alerts, critical_alerts = self.check_alerts()
        if critical_alerts > 0:
            print(f"  [ALERT] {critical_alerts} critical alerts detected")
        
        # Check anomaly score
        try:
            anomaly_data = self.client.get_anomaly_score()
            score = anomaly_data.get('score', 0.0)
            if score > self.config['anomaly_threshold']:
                print(f"  [WARN] High anomaly score: {score:.3f}")
        except:
            pass  # Anomaly detection might not be available
    
    def start_monitoring(self, duration_minutes=None):
        """Start continuous monitoring."""
        start_time = time.time()
        
        print(f"Starting Sentinel monitoring service...")
        if duration_minutes:
            print(f"Monitoring duration: {duration_minutes} minutes")
        
        try:
            while True:
                self.run_monitoring_cycle()
                
                # Check if we should stop
                if duration_minutes:
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes >= duration_minutes:
                        break
                
                # Wait for next cycle
                time.sleep(self.config['health_check_interval'])
                
        except KeyboardInterrupt:
            print("\\nMonitoring stopped by user")
        except Exception as e:
            print(f"Monitoring service failed: {e}")

# Usage
def email_alert_callback(alert_data):
    """Example alert callback for email notifications."""
    print(f"[U+1F4E7] EMAIL ALERT: {alert_data['critical_count']} critical alerts")
    # Implement actual email sending here

# Create and start monitoring service
monitoring = SentinelMonitoringService()
monitoring.add_alert_callback(email_alert_callback)

# Run monitoring for 10 minutes
monitoring.start_monitoring(duration_minutes=10)
```

## CLI Tool Examples

### 1. Command Line Interface
```python
#!/usr/bin/env python3
"""Command line interface for Sentinel SDK."""

import argparse
import sys
from tools.sentinel_sdk import SentinelClient, SentinelAPIError

def create_cli_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(description='Sentinel API CLI Tool')
    
    # Connection options
    parser.add_argument('--url', default='http://localhost:8080', 
                       help='Sentinel server URL')
    parser.add_argument('--admin-token', help='Admin authentication token')
    parser.add_argument('--username', help='Username for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    # Commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check service health')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get service status')
    
    # Alerts command
    alerts_parser = subparsers.add_parser('alerts', help='Get alerts')
    alerts_parser.add_argument('--limit', type=int, default=10, help='Number of alerts')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Get metrics')
    metrics_parser.add_argument('--type', choices=['health', 'event_bus', 'snapshot'],
                               default='health', help='Metrics type')
    
    # Config command (admin only)
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--action', choices=['schema', 'reload'], 
                              default='schema', help='Config action')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run API tests')
    
    return parser

def execute_command(args):
    """Execute the specified command."""
    # Create client
    client = SentinelClient(
        base_url=args.url,
        admin_token=args.admin_token,
        username=args.username,
        password=args.password,
        timeout=args.timeout,
        debug=args.debug
    )
    
    try:
        if args.command == 'health':
            result = client.get_health()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'status':
            result = client.get_status()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'alerts':
            result = client.get_alerts(limit=args.limit)
            alerts = result.get('alerts', [])
            print(f"Found {len(alerts)} alerts:")
            for i, alert in enumerate(alerts, 1):
                severity = alert.get('severity', 'unknown')
                alert_type = alert.get('type', 'unknown')
                timestamp = alert.get('timestamp', 'unknown')
                print(f"  {i}. [{severity.upper()}] {alert_type} - {timestamp}")
                
        elif args.command == 'metrics':
            if args.type == 'health':
                result = client.get_health_metrics()
            elif args.type == 'event_bus':
                result = client.get_event_bus_metrics()
            elif args.type == 'snapshot':
                result = client.get_metrics_snapshot()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'config':
            if args.action == 'schema':
                result = client.get_admin_config_schema()
                print(json.dumps(result, indent=2))
            elif args.action == 'reload':
                result = client.reload_config()
                print(f"Config reload: {result['status']}")
                
        elif args.command == 'test':
            validation = client.validate_connection()
            print("Connection validation results:")
            print(json.dumps(validation, indent=2))
            
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except SentinelAPIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == '__main__':
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    exit_code = execute_command(args)
    sys.exit(exit_code)
```

### 2. Usage Examples for CLI
```bash
# Basic health check
python sentinel_cli.py --url http://localhost:8080 health

# Get alerts with custom limit
python sentinel_cli.py --url http://localhost:8080 alerts --limit 50

# Admin operations with token
export SENTINEL_ADMIN_TOKEN="your-admin-token"
python sentinel_cli.py --url http://localhost:8080 --admin-token $SENTINEL_ADMIN_TOKEN config --action schema

# Test API connectivity
python sentinel_cli.py --url http://localhost:8080 --debug test

# Get comprehensive metrics
python sentinel_cli.py --url http://localhost:8080 --admin-token $SENTINEL_ADMIN_TOKEN metrics --type snapshot
```

## Conclusion

The WatchLockAI Sentinel Python SDK provides comprehensive, production-ready access to all Sentinel API functionality with robust error handling, authentication management, and advanced features. The extensive examples demonstrate real-world usage patterns for monitoring, administration, and integration scenarios.

**SDK Features Summary:**
- **41+ API Endpoints Covered:** Complete functionality access
- **Multiple Authentication Methods:** Flexible authentication options
- **Production Ready:** Robust error handling and retry logic
- **Real-time Capabilities:** Streaming support for live data
- **Comprehensive Examples:** 25+ usage scenarios documented
- **CLI Integration:** Command-line interface for automation

The SDK enables seamless integration of Sentinel capabilities into existing monitoring, security, and operations workflows.

---
**Documentation Generated By:** MiniMax Agent  
**SDK Client:** tools/sentinel_sdk.py - Production-ready Python client library  
**Verification:** This documentation provides complete P11 SDK client implementation with comprehensive examples covering all major use cases and integration patterns.
