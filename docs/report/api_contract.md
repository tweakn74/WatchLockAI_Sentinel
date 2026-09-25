# API Contract Documentation

## WatchLockAI Sentinel API Contract - P2-003 & P2-004 Updates

**Generated:** 2025-09-04T08:43:07+00:00  
**Version:** Post P2-004 Implementation

## Environment Flags

| Flag | Default | Scope | Impact |
|------|---------|-------|---------|
| `HEALTH_ENDPOINT_ENABLED` | `1` (ON) | Health metrics | Enables `GET /api/metrics/health` |
| `METRICS_DEBUG_ENABLED` | `0` (OFF) | Debug metrics | Enables debug endpoints |
| `CONFIG_HOT_RELOAD_ENABLED` | `0` (OFF) | Admin operations | Enables `POST /api/admin/config/reload` |
| `RATE_LIMIT_ENABLED` | `0` (OFF) | Rate limiting | Enables token bucket rate limiting |
| `ADMIN_AUTH_ENABLED` | `0` (OFF) | RBAC | Requires `X-Admin-Token` header for admin routes |
| `ADMIN_TOKEN` | `""` | RBAC | Shared secret for admin authentication |
| `ANOMALY_ENABLED` | `0` (OFF) | Anomaly detection | Enables anomaly detection system |
| `ANOMALY_SKLEARN_ENABLED` | `0` (OFF) | Anomaly ML | Enables sklearn-based anomaly training |
| `QUARANTINE_ENABLED` | `0` (OFF) | File quarantine | Enables file quarantine system |
| `CONSOLE_AUTH_ENABLED` | `0` (OFF) | Session auth | Enables cookie-based session authentication |
| `CONSOLE_AUTH_SESSION_KEY` | `""` | Session auth | 32+ byte hex key for session signing |
| `CONSOLE_AUTH_USER_DB` | `data/auth/users.json` | Session auth | User database file path |
| `STREAM_ENABLED` | `0` (OFF) | SSE streaming | Enables Server-Sent Events streaming |
| `STREAM_TYPE` | `sse` | SSE streaming | Streaming type (only 'sse' implemented) |
| `STREAM_HEALTH_INTERVAL_MS` | `1000` | SSE streaming | Health update interval in milliseconds |
| `STREAM_REQUIRE_AUTH` | `0` (OFF) | SSE streaming | Requires session auth for streaming |

## API Endpoints

### Health Metrics (Default ON)

**Endpoint:** `GET /api/metrics/health`  
**Flag:** `HEALTH_ENDPOINT_ENABLED=1` (default)  
**Rate Limit:** 60/minute when `RATE_LIMIT_ENABLED=1`  

**Response:**
```json
{
  "ok": true,
  "components": {
    "event_bus": {
      "delivery_success_count": 0,
      "delivery_failure_count": 0
    },
    "service": {
      "running": true,
      "uptime_seconds": 123.45
    }
  },
  "uptime_s": 123
}
```

**Structured Logging:** Emits JSON log on each call

### Admin Config Reload (Default OFF)

**Endpoint:** `POST /api/admin/config/reload?debounce_ms=750`  
**Flag:** `CONFIG_HOT_RELOAD_ENABLED=0` (default OFF)  
**Rate Limit:** 5/minute when `RATE_LIMIT_ENABLED=1`  
**Auth:** Requires `X-Admin-Token` header when `ADMIN_AUTH_ENABLED=1`

**Response:**
```json
{
  "status": "reloading"
}
```

**Parameters:**
- `debounce_ms` (optional): Integer 0-60000, defaults to 750

### Debug Event Bus Metrics (Default OFF)

**Endpoint:** `GET /api/metrics/event_bus`  
**Flag:** `METRICS_DEBUG_ENABLED=0` (default OFF)  
**Structured Logging:** Emits JSON log on each call

**Response:**
```json
{
  "event_bus": {
    "delivery_success_count": 0,
    "delivery_failure_count": 0
  }
}
```

### Debug Metrics Snapshot (Default OFF) - NEW

**Endpoint:** `GET /api/metrics/snapshot`  
**Flag:** `METRICS_DEBUG_ENABLED=0` (default OFF)  
**Structured Logging:** Emits JSON log on each call

**Response:**
```json
{
  "timestamp": "2025-09-04T07:20:28.123Z",
  "uptime_s": 123,
  "metrics": {
    "event_bus": {
      "delivery_success_count": 0,
      "delivery_failure_count": 0
    },
    "service": {
      "running": true,
      "uptime_seconds": 123.45
    }
  }
}
```

## P2-001: Anomaly Detection Endpoints

### Anomaly Score (Debug + Anomaly Enabled)

**Endpoint:** `GET /api/anomaly/score?window=60`  
**Flags:** `ANOMALY_ENABLED=1` AND `METRICS_DEBUG_ENABLED=1`  
**Rate Limit:** 10/minute when `RATE_LIMIT_ENABLED=1`  
**Auth:** None required

**Response:**
```json
{
  "score": 2.34,
  "n": 25,
  "enabled": true,
  "window_minutes": 60,
  "sklearn_available": false
}
```

**Parameters:**
- `window` (optional): Time window in minutes (1-1440), defaults to 60

**Structured Logging:** Emits JSON log on each call

### Anomaly Model Training (Admin Only)

**Endpoint:** `POST /api/admin/anomaly/train`  
**Flags:** `ANOMALY_ENABLED=1` AND `ANOMALY_SKLEARN_ENABLED=1`  
**Rate Limit:** 2/hour when `RATE_LIMIT_ENABLED=1`  
**Auth:** Requires `X-Admin-Token` header when `ADMIN_AUTH_ENABLED=1`

**Response:**
```json
{
  "status": "training_complete",
  "n_samples": 150,
  "n_features": 10,
  "model_saved": "models/anomaly_iforest.pkl"
}
```

**Status Values:**
- `training_complete`: Model successfully trained
- `insufficient_data`: Need >10 samples for training
- `sklearn_unavailable`: scikit-learn not available
- `training_failed`: Training error occurred

**Structured Logging:** Emits JSON log on each call

## P2-002: File Quarantine Endpoints

### Quarantine File (Admin Only)

**Endpoint:** `POST /api/admin/quarantine?path=/path/to/file`  
**Flag:** `QUARANTINE_ENABLED=1`  
**Rate Limit:** 10/hour when `RATE_LIMIT_ENABLED=1`  
**Auth:** Requires `X-Admin-Token` header when `ADMIN_AUTH_ENABLED=1`

**Response:**
```json
{
  "status": "quarantined",
  "sha256": "a1b2c3d4e5f6789...",
  "dst": "data/quarantine/file.txt_a1b2c3d4_1640995200",
  "acl_hardened": true,
  "enabled": true
}
```

**Parameters:**
- `path` (required): File path to quarantine

**Status Values:**
- `quarantined`: File successfully quarantined
- `error`: Operation failed (with error details)
- `disabled`: Quarantine system disabled

**Structured Logging:** Emits JSON log on each call

### Restore Quarantined File (Admin Only)

**Endpoint:** `POST /api/admin/quarantine/restore?sha256={hash}&target_path={optional}`  
**Flag:** `QUARANTINE_ENABLED=1`  
**Rate Limit:** 10/hour when `RATE_LIMIT_ENABLED=1`  
**Auth:** Requires `X-Admin-Token` header when `ADMIN_AUTH_ENABLED=1`

**Response:**
```json
{
  "status": "restored",
  "sha256": "a1b2c3d4e5f6789...",
  "restored_to": "/original/path/file.txt",
  "enabled": true
}
```

**Parameters:**
- `sha256` (required): SHA256 hash of quarantined file (64 hex chars)
- `target_path` (optional): Custom restore path, defaults to original path

**Status Values:**
- `restored`: File successfully restored
- `error`: Operation failed (with error details)
- `disabled`: Quarantine system disabled

**Structured Logging:** Emits JSON log on each call

## RBAC (Role-Based Access Control) - P1-005

### Default Behavior (ADMIN_AUTH_ENABLED=0)
- All `/api/admin/*` routes accessible without authentication
- Existing behavior preserved for backward compatibility

### Enabled Behavior (ADMIN_AUTH_ENABLED=1)
- All `/api/admin/*` routes require `X-Admin-Token` header
- Token must match `ADMIN_TOKEN` environment variable
- Missing header -> HTTP 403 Forbidden
- Wrong token -> HTTP 403 Forbidden
- Correct token -> Normal operation

### Authentication Flow

```bash
# Without authentication (default)
curl -X POST http://localhost:8080/api/admin/config/reload
# -> 200 OK

# With authentication enabled
export ADMIN_AUTH_ENABLED=1
export ADMIN_TOKEN=my-secret-token

# Missing header
curl -X POST http://localhost:8080/api/admin/config/reload
# -> 403 Forbidden

# Correct header  
curl -X POST http://localhost:8080/api/admin/config/reload \
     -H "X-Admin-Token: my-secret-token"
# -> 200 OK
```

## Rate Limiting - P1-004

### Token Bucket Algorithm
- Per-route, per-client-IP isolation
- Standard library only (no external dependencies)
- Thread-safe with proper locking
- Configurable capacity and refill rates

### Rate Limits (when RATE_LIMIT_ENABLED=1)
- `POST /api/admin/config/reload`: 5 requests/minute
- `GET /api/metrics/health`: 60 requests/minute
- `GET /api/anomaly/score`: 10 requests/minute
- `POST /api/admin/anomaly/train`: 2 requests/hour
- `POST /api/admin/quarantine`: 10 requests/hour
- `POST /api/admin/quarantine/restore`: 10 requests/hour

### Rate Limit Response
```json
HTTP 429 Too Many Requests
{
  "detail": "rate limit exceeded"
}
```

## Structured Logging - P1-006

### Log Format
```json
{
  "timestamp": "2025-09-04T07:20:28.123Z",
  "route": "/api/metrics/health",
  "counters": {
    "delivery_success_count": 0,
    "delivery_failure_count": 0
  },
  "uptime_s": 123
}
```

### Logging Implementation
- Uses existing `loguru` logger if available
- Falls back to `stdlib` logging
- Logs emitted on all metrics endpoint calls
- Error swallowing to maintain API stability

## Verification Commands

### Route ON/OFF Testing
```bash
# Health endpoint default ON
python -c "
from console.web_api import SentinelWebAPI
app = SentinelWebAPI().app
routes = {r.path for r in app.routes}
print('/api/metrics/health' in routes)  # Should be True
"

# Admin reload default OFF
python -c "
import os
os.environ.pop('CONFIG_HOT_RELOAD_ENABLED', None)
from console.web_api import SentinelWebAPI
app = SentinelWebAPI().app
routes = {r.path for r in app.routes}
print('/api/admin/config/reload' in routes)  # Should be False
"

# Enable admin reload
python -c "
import os
os.environ['CONFIG_HOT_RELOAD_ENABLED'] = '1'
from console.web_api import SentinelWebAPI
app = SentinelWebAPI().app
routes = {r.path for r in app.routes}
print('/api/admin/config/reload' in routes)  # Should be True
"
```

### RBAC Testing
```bash
# Default OFF - no auth required
CONFIG_HOT_RELOAD_ENABLED=1 python -c "
from fastapi.testclient import TestClient
from console.web_api import SentinelWebAPI
client = TestClient(SentinelWebAPI().app)
r = client.post('/api/admin/config/reload')
print(r.status_code)  # Should be 200
"

# Enable auth - missing token should fail
CONFIG_HOT_RELOAD_ENABLED=1 ADMIN_AUTH_ENABLED=1 ADMIN_TOKEN=test python -c "
from fastapi.testclient import TestClient
from console.web_api import SentinelWebAPI
client = TestClient(SentinelWebAPI().app)
r = client.post('/api/admin/config/reload')
print(r.status_code)  # Should be 403
"

# Enable auth - correct token should work
CONFIG_HOT_RELOAD_ENABLED=1 ADMIN_AUTH_ENABLED=1 ADMIN_TOKEN=test python -c "
from fastapi.testclient import TestClient
from console.web_api import SentinelWebAPI
client = TestClient(SentinelWebAPI().app)
r = client.post('/api/admin/config/reload', headers={'X-Admin-Token': 'test'})
print(r.status_code)  # Should be 200
"
```

### P2-003: Session Authentication (Default OFF)

**Flag:** `CONSOLE_AUTH_ENABLED=0` (default)

#### Login Endpoint

**Endpoint:** `POST /api/auth/login`  
**Rate Limit:** 10/minute per client IP  
**Requirements:** Valid username/password in request body  

**Request:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Success Response (200):**
```json
{
  "status": "ok",
  "message": "Authentication successful"
}
```

**Cookie:** Sets `sentinel_session` HttpOnly, Secure cookie

**Error Responses:**
- `401`: Invalid credentials
- `429`: Rate limit exceeded
- `503`: Auth module not available

#### Logout Endpoint

**Endpoint:** `POST /api/auth/logout`  

**Success Response (200):**
```json
{
  "status": "ok", 
  "message": "Logout successful"
}
```

**Cookie:** Clears `sentinel_session` cookie

#### Current User Info

**Endpoint:** `GET /api/auth/me`  
**Requirements:** Valid session cookie  

**Success Response (200):**
```json
{
  "user": "admin"
}
```

**Error Responses:**
- `401`: Not authenticated or invalid session

### P2-004: Server-Sent Events Streaming (Default OFF)

**Flag:** `STREAM_ENABLED=0` (default)

#### Health Streaming Endpoint

**Endpoint:** `GET /api/stream/health`  
**Content-Type:** `text/event-stream`  
**Connection Limit:** 2 concurrent connections per client IP  
**Requirements:** Session auth if `STREAM_REQUIRE_AUTH=1`  

**Stream Format:**
```
data: {"timestamp": "2025-09-04T08:43:07Z", "event": "health_update", "data": {...}}

data: {"timestamp": "2025-09-04T08:43:08Z", "event": "health_update", "data": {...}}

```

**Health Data Structure:**
```json
{
  "timestamp": "2025-09-04T08:43:07Z",
  "status": "healthy",
  "uptime_seconds": 1234,
  "service_status": "running",
  "event_bus": {
    "delivery_success_count": 100,
    "delivery_failure_count": 5
  }
}
```

**Error Responses:**
- `401`: Authentication required (when `STREAM_REQUIRE_AUTH=1`)
- `429`: Too many concurrent connections
- `503`: Streaming not enabled

**Configuration:**
- `STREAM_HEALTH_INTERVAL_MS`: Update interval (default 1000ms)
- `STREAM_REQUIRE_AUTH`: Require session authentication (default OFF)

## Backward Compatibility Guarantees

1. **Default Behaviors Preserved**
   - Health endpoint remains ON by default
   - Admin routes remain OFF by default  
   - No authentication required by default

2. **Response Payload Stability**
   - No changes to existing success response shapes
   - Optional parameters only (debounce_ms)
   - Conservative defaults maintained

3. **Import Safety**
   - Graceful degradation when FastAPI unavailable
   - All new functionality skips cleanly
   - No new required runtime dependencies
