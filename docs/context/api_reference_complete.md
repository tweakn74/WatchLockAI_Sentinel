# API Reference - WatchLockAI Sentinel

## Overview

The WatchLockAI Sentinel API provides comprehensive REST endpoints for monitoring, management, and operational control. The API is built with FastAPI and includes authentication, rate limiting, and feature flags for different operational modes.

## Base Configuration

- **Base URL**: `http://127.0.0.1:8080` (default)
- **OpenAPI Docs**: `/api/docs` (Swagger UI)
- **ReDoc**: `/api/redoc`
- **Content-Type**: `application/json`

## Core API Endpoints

### Health and Status

#### GET `/api/status`
Returns service status and component health.

**Response Model**: `StatusResponse`
```json
{
  "running": true,
  "uptime_seconds": 3600.0,
  "collectors": {
    "fs_monitor": "running",
    "proc_monitor": "running",
    "reg_monitor": "running",
    "net_monitor": "running",
    "health_monitor": "running"
  },
  "rules_engine": {
    "status": "running",
    "rules_loaded": 25,
    "recent_detections": 3
  },
  "event_bus": {
    "events_published": 1234,
    "events_delivered": 1230,
    "active_subscriptions": 8
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

#### GET `/api/metrics/health` (requires `HEALTH_ENDPOINT_ENABLED=1`)
Composite health check with observability metrics.

**Response Model**: `CompositeHealthResponse`
```json
{
  "service": {
    "status": "healthy",
    "uptime_seconds": 3600.0
  },
  "event_bus": {
    "delivery_success_count": 1230,
    "delivery_failure_count": 4
  },
  "flags": {
    "HEALTH_ENDPOINT_ENABLED": "1",
    "METRICS_DEBUG_ENABLED": "0"
  },
  "version": "1.0.0"
}
```

### Operational Mode Management

#### GET `/api/operational_mode`
Get current operational mode.

**Response Model**: `OperationalModeResponse`
```json
{
  "mode": "observe",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

#### PUT `/api/operational_mode`
Set operational mode with validation.

**Request Model**: `OperationalModeRequest`
```json
{
  "mode": "alert"
}
```

**Valid Modes**: `observe`, `alert`, `contain`, `quarantine`, `offline`

**Response Model**: `OperationalModeUpdateResponse`
```json
{
  "success": true,
  "mode": "alert",
  "message": "Operational mode updated successfully",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### Alerts and Detections

#### GET `/api/alerts`
Get recent alerts with optional filtering.

**Query Parameters**:
- `limit`: Number of alerts to return (default: 50, max: 500)
- `severity`: Filter by severity (`low`, `medium`, `high`)
- `category`: Filter by category (`ransomware`, `persistence`, `process`, `network`, `health`, `general`)

**Response Model**: `AlertSummary`
```json
{
  "total_alerts": 15,
  "critical_alerts": 2,
  "warning_alerts": 8,
  "info_alerts": 5,
  "recent_alerts": [
    {
      "id": "uuid-here",
      "severity": "high",
      "category": "ransomware",
      "tag": "file-entropy-burst",
      "rationale": "High entropy file creation burst detected",
      "timestamp": "2025-01-01T12:00:00Z",
      "confidence": 0.95
    }
  ]
}
```

#### GET `/api/detections`
Get detection events with filtering.

**Query Parameters**:
- `limit`: Number of detections (default: 100)
- `severity`: Filter by severity
- `tag`: Filter by detection tag

**Response Model**: `DetectionResponse`
```json
{
  "total_detections": 25,
  "detections": [
    {
      "rule_id": "mitre_t1486",
      "rule_name": "Data Encrypted for Impact",
      "severity": "high",
      "timestamp": "2025-01-01T12:00:00Z",
      "trigger_data": {
        "file_path": "/documents/important.txt.encrypted",
        "process": "ransomware.exe"
      }
    }
  ],
  "filters": {
    "severity": "high",
    "tag": null
  }
}
```

### MITRE ATT&CK Integration (requires `MITRE_API_ENABLED=1`)

#### GET `/api/mitre/coverage`
Get MITRE ATT&CK rule coverage information.

**Response Model**: `MITRECoverageResponse`
```json
{
  "enabled": true,
  "profile": "endpoint_basic",
  "rules_count": 25,
  "by_tactic": {
    "initial_access": 3,
    "execution": 5,
    "persistence": 4,
    "privilege_escalation": 2,
    "defense_evasion": 3,
    "credential_access": 2,
    "discovery": 2,
    "lateral_movement": 1,
    "collection": 1,
    "exfiltration": 1,
    "impact": 1
  },
  "rules": [
    {
      "id": "mitre_t1486",
      "name": "Data Encrypted for Impact",
      "tactic": "impact",
      "technique": "T1486",
      "event": "FileEvent",
      "threshold": 10,
      "window_s": 60,
      "severity": "high",
      "response": "quarantine_directory"
    }
  ]
}
```

## Authentication Endpoints (requires `CONSOLE_AUTH_ENABLED=1`)

### POST `/api/auth/login`
Authenticate user and create session.

**Request Model**: `LoginRequest`
```json
{
  "username": "admin",
  "password": "secure_password"
}
```

**Response Model**: `AuthResponse`
```json
{
  "status": "success",
  "message": "Login successful"
}
```

**Rate Limiting**: 10 attempts per minute per IP

### POST `/api/auth/logout`
Logout and destroy session.

**Response Model**: `AuthResponse`
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

### GET `/api/auth/me`
Get current authenticated user information.

**Response Model**: `UserInfoResponse`
```json
{
  "user": "admin"
}
```

## Admin Endpoints (requires `ADMIN_AUTH_ENABLED=1` and admin authentication)

### Configuration Management

#### GET `/api/admin/config/schema`
Get configuration schema and validation state.

```json
{
  "schema_version": "1.0",
  "total_settings": 45,
  "validation_errors": [],
  "schema": {
    "monitoring": {
      "file_system": {
        "enabled": {"type": "bool", "default": true},
        "paths": {"type": "array", "items": "string"}
      }
    }
  }
}
```

#### POST `/api/admin/config/reload`
Reload configuration from file.

**Query Parameters**:
- `debounce_ms`: Debounce delay in milliseconds (default: 750)

### Backup and Restore (requires `BACKUP_ENABLED=1`)

#### POST `/api/admin/backup`
Create system backup.

```json
{
  "backup_id": "backup_20250101_120000",
  "created_at": "2025-01-01T12:00:00Z",
  "size_bytes": 1048576,
  "components": ["config", "logs", "knowledge_index"]
}
```

#### POST `/api/admin/restore`
Restore from backup.

**Request Body**:
```json
{
  "backup_id": "backup_20250101_120000"
}
```

### Performance Monitoring (requires `PERF_PROBE_ENABLED=1`)

#### POST `/api/admin/perf/probe`
Run performance probe test.

**Query Parameters**:
- `clients`: Number of concurrent clients (1-50, default: 10)
- `duration_s`: Test duration in seconds (0.1-60.0, default: 5.0)
- `endpoint`: Endpoint to test (default: `/api/metrics/health`)

```json
{
  "test_duration_s": 5.0,
  "total_requests": 500,
  "successful_requests": 498,
  "failed_requests": 2,
  "avg_response_time_ms": 45.2,
  "p95_response_time_ms": 89.1,
  "requests_per_second": 99.6
}
```

#### GET `/api/admin/perf/quick`
Run quick performance check.

```json
{
  "status": "ok",
  "response_time_ms": 12.5,
  "memory_usage_mb": 128.4,
  "cpu_usage_pct": 15.2
}
```

## Streaming Endpoints (requires `STREAM_ENABLED=1`)

### GET `/api/stream/health`
Server-Sent Events stream for health metrics.

**Content-Type**: `text/event-stream`

```
data: {"cpu_pct": 25.5, "ram_pct": 60.2, "timestamp": "2025-01-01T12:00:00Z"}

data: {"cpu_pct": 26.1, "ram_pct": 60.3, "timestamp": "2025-01-01T12:00:01Z"}
```

### GET `/api/stream/events`
Server-Sent Events stream for detection events.

```
data: {"event_type": "DetectionAlert", "severity": "high", "tag": "ransomware-burst", "timestamp": "2025-01-01T12:00:00Z"}
```

## Feature Flags and Environment Variables

### Core Features
- `HEALTH_ENDPOINT_ENABLED`: Enable health metrics endpoint (default: 0)
- `METRICS_DEBUG_ENABLED`: Enable debug metrics (default: 0)
- `CONFIG_HOT_RELOAD_ENABLED`: Enable config hot reload (default: 0)

### Authentication
- `CONSOLE_AUTH_ENABLED`: Enable session-based auth (default: 0)
- `ADMIN_AUTH_ENABLED`: Enable admin authentication (default: 0)

### Advanced Features
- `MITRE_API_ENABLED`: Enable MITRE ATT&CK endpoints (default: 0)
- `STREAM_ENABLED`: Enable SSE streaming (default: 0)
- `BACKUP_ENABLED`: Enable backup/restore (default: 0)
- `PERF_PROBE_ENABLED`: Enable performance testing (default: 0)
- `ANOMALY_ENABLED`: Enable anomaly detection (default: 0)
- `QUARANTINE_ENABLED`: Enable quarantine features (default: 0)

### Rate Limiting
- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: 0)
- `CONSOLE_AUTH_RATE_LIMIT`: Login attempts per minute (default: 10)

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### Common Status Codes
- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `429`: Too Many Requests (rate limited)
- `500`: Internal Server Error
- `503`: Service Unavailable (feature disabled)

## Web Console Routes

### Static Pages
- `GET /`: Main dashboard
- `GET /console/`: Console interface
- `GET /console/info`: System information page
- `GET /alerts`: Alerts management page
- `GET /policies`: Policy configuration page

### Template Rendering
All web console routes serve HTML templates with embedded JavaScript for dynamic content loading via the REST API.

## Security Considerations

### Authentication
- Session-based authentication with secure cookies
- Rate limiting on login attempts
- Admin role separation for sensitive operations

### Network Security
- Binds to `127.0.0.1` by default (localhost only)
- HTTPS support via reverse proxy
- CORS headers for web console integration

### Input Validation
- Pydantic model validation for all requests
- SQL injection prevention in database queries
- Path traversal protection for file operations
- XSS prevention in web console templates
