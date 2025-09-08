# WatchLockAI Sentinel - Observability Playbook

## Overview

This document provides operational guidance for monitoring, troubleshooting, and maintaining the WatchLockAI Sentinel system using built-in observability features.

## Health Monitoring

### Primary Health Endpoint

**Endpoint:** `GET /api/metrics/health` (default ON)
- **Status:** Available when `HEALTH_ENDPOINT_ENABLED=1` (default)
- **Purpose:** Composite health check combining service status and event bus metrics
- **Rate Limit:** 60 requests/minute when rate limiting enabled
- **Authentication:** None required

**Response Format:**
```json
{
  "ok": true,
  "components": {
    "event_bus": {
      "delivery_success_count": 1250,
      "delivery_failure_count": 3
    },
    "service": {
      "status": "running",
      "uptime_seconds": 86400
    }
  },
  "uptime_s": 86400
}
```

### Simple Health Check

**Endpoint:** `GET /health`
- **Status:** Always available
- **Purpose:** Basic liveness probe
- **Response:** `{"status": "healthy", "timestamp": "2025-01-01T12:00:00Z"}`

## Anomaly Detection Observability

### Anomaly Surfaces

The behavioral anomaly detection system (P2-001) provides monitoring capabilities for detecting unusual system behavior patterns.

#### Feature Extraction

The system extracts the following feature vectors for anomaly scoring:

- **Temporal Features:**
  - `hour_of_day` (0-23): Current hour for circadian pattern detection
  - `day_of_week` (0-6): Day of week for weekly pattern analysis
  - `time_since_last_activity`: Time elapsed since last recorded activity

- **System Load Features:**
  - `cpu_usage_pct`: CPU utilization percentage
  - `memory_usage_pct`: Memory utilization percentage
  - `disk_io_rate`: Disk I/O operations rate
  - `network_io_rate`: Network I/O operations rate

- **Event-Based Features:**
  - `event_count`: Total number of events in observation window
  - `error_count`: Number of error-level events
  - `unique_sources`: Count of unique event sources

#### Anomaly Score Endpoint

**Endpoint:** `GET /api/anomaly/score?window={minutes}` (debug-only)
- **Status:** Available when `ANOMALY_ENABLED=1` AND `METRICS_DEBUG_ENABLED=1`
- **Purpose:** Retrieve current anomaly score for specified time window
- **Rate Limit:** 10 requests/minute when rate limiting enabled
- **Authentication:** None required

**Parameters:**
- `window`: Time window in minutes (1-1440, default: 60)

**Response Format:**
```json
{
  "score": 2.34,
  "n": 25,
  "enabled": true,
  "window_minutes": 60,
  "sklearn_available": false
}
```

**Score Interpretation:**
- `score < 2.0`: Normal behavior
- `score 2.0-4.0`: Mild anomaly, investigate if persistent
- `score > 4.0`: Strong anomaly, immediate investigation recommended

#### Anomaly Model Training

**Endpoint:** `POST /api/admin/anomaly/train` (admin-only)
- **Status:** Available when `ANOMALY_ENABLED=1` AND `ANOMALY_SKLEARN_ENABLED=1` AND `ADMIN_AUTH_ENABLED=1`
- **Purpose:** Train Isolation Forest model for advanced anomaly detection
- **Rate Limit:** 2 requests/hour when rate limiting enabled
- **Authentication:** Requires `X-Admin-Token` header

**Response Format:**
```json
{
  "status": "training_complete",
  "n_samples": 150,
  "n_features": 10,
  "model_saved": "models/anomaly_iforest.pkl"
}
```

**Training Status Values:**
- `training_complete`: Model successfully trained and saved
- `insufficient_data`: Not enough data for training (requires >10 samples)
- `sklearn_unavailable`: scikit-learn dependency not available
- `training_failed`: Training failed with error details

#### Anomaly Detection Troubleshooting

**Common Issues:**

1. **No Anomaly Score Available**
   - Verify `ANOMALY_ENABLED=1` in environment
   - Verify `METRICS_DEBUG_ENABLED=1` for score endpoint access
   - Check system logs for import errors

2. **Training Endpoint Not Available**
   - Verify `ANOMALY_SKLEARN_ENABLED=1` in environment
   - Verify `ADMIN_AUTH_ENABLED=1` and `ADMIN_TOKEN` configured
   - Install scikit-learn: `pip install scikit-learn`

3. **Low Quality Anomaly Scores**
   - Allow more time for baseline establishment (>100 observations recommended)
   - Verify feature extraction is capturing relevant system metrics
   - Consider training Isolation Forest model for improved accuracy

## Quarantine System Workflows

The file quarantine system (P2-002) provides secure file isolation capabilities with full audit trail and restore functionality.

### Quarantine Operations

#### File Quarantine

**Endpoint:** `POST /api/admin/quarantine?path={file_path}` (admin-only)
- **Status:** Available when `QUARANTINE_ENABLED=1` AND `ADMIN_AUTH_ENABLED=1`
- **Purpose:** Securely quarantine suspicious files
- **Rate Limit:** 10 requests/hour when rate limiting enabled
- **Authentication:** Requires `X-Admin-Token` header

**Quarantine Process:**
1. Compute SHA256 hash of source file
2. Move file to quarantine directory using atomic `os.replace()`
3. Apply Windows ACL hardening via `icacls` (best-effort)
4. Record audit log entry in `data/quarantine/audit_log.jsonl`
5. Update quarantine mapping in `data/quarantine/mapping.json`

**Response Format:**
```json
{
  "status": "quarantined",
  "sha256": "a1b2c3d4e5f6...",
  "dst": "data/quarantine/suspicious_file.txt_a1b2c3d4_1640995200",
  "acl_hardened": true,
  "enabled": true
}
```

#### File Restore

**Endpoint:** `POST /api/admin/quarantine/restore?sha256={hash}&target_path={optional}`
- **Status:** Available when `QUARANTINE_ENABLED=1` AND `ADMIN_AUTH_ENABLED=1`
- **Purpose:** Restore quarantined files to original or custom location
- **Rate Limit:** 10 requests/hour when rate limiting enabled
- **Authentication:** Requires `X-Admin-Token` header

**Restore Process:**
1. Validate SHA256 format and locate in quarantine mapping
2. Verify quarantined file exists and integrity (re-hash)
3. Check destination path availability
4. Atomic move from quarantine to target location
5. Remove from quarantine mapping
6. Record audit log entry

**Response Format:**
```json
{
  "status": "restored",
  "sha256": "a1b2c3d4e5f6...",
  "restored_to": "/original/path/file.txt",
  "enabled": true
}
```

### Quarantine Audit Trail

All quarantine operations are logged to `data/quarantine/audit_log.jsonl` with structured entries:

```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "action": "quarantine_success",
  "path_src": "/suspicious/file.txt",
  "path_dst": "data/quarantine/file.txt_a1b2c3d4_1640995200",
  "sha256": "a1b2c3d4e5f6...",
  "error": ""
}
```

**Audit Actions:**
- `quarantine_success`: File successfully quarantined
- `quarantine_failed`: Quarantine operation failed
- `restore_success`: File successfully restored
- `restore_failed`: Restore operation failed

### Quarantine System Monitoring

#### Status Monitoring

Query quarantine system status through the management interface:

```python
from console.quarantine import get_quarantine_status
status = get_quarantine_status()
```

**Status Information:**
- `enabled`: Quarantine system enabled state
- `quarantine_dir`: Quarantine directory path
- `quarantined_files`: Count of currently quarantined files
- `audit_log`: Audit log file path

#### Operational Workflows

**Daily Quarantine Review:**
1. Review audit log for quarantine activities: `tail -f data/quarantine/audit_log.jsonl`
2. Check quarantine directory disk usage: `du -sh data/quarantine/`
3. Validate quarantine mapping consistency
4. Review failed operations and investigate root causes

**File Recovery Process:**
1. Identify file by SHA256 hash from incident response
2. Verify file exists in quarantine: check mapping.json
3. Test restore to safe location first
4. Perform production restore once validated

**Troubleshooting:**

1. **Quarantine Endpoint Not Available**
   - Verify `QUARANTINE_ENABLED=1` in environment
   - Verify `ADMIN_AUTH_ENABLED=1` and `ADMIN_TOKEN` configured
   - Check admin authentication headers

2. **Quarantine Operation Failed**
   - Check source file exists and is accessible
   - Verify quarantine directory permissions
   - Review audit log for specific error details

3. **ACL Hardening Not Applied**
   - Verify running on Windows platform
   - Check `icacls` command availability
   - Review process permissions for ACL modification

4. **Restore Operation Failed**
   - Verify SHA256 hash exists in quarantine mapping
   - Check destination path availability
   - Verify file integrity (re-compute SHA256)

## Structured Logging

All observability endpoints emit structured logs for centralized monitoring and analysis.

### Log Format

```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "route": "/api/metrics/health",
  "counters": {"delivery_success_count": 100, "delivery_failure_count": 1},
  "uptime_s": 3600
}
```

### Log Destinations

- **Primary:** Loguru logger (if available)
- **Fallback:** Python stdlib logging to `sentinel.metrics` logger

## Rate Limiting

When `RATE_LIMIT_ENABLED=1`, the following rate limits apply:

| Endpoint | Rate Limit | Window |
|----------|------------|---------|
| `/api/metrics/health` | 60 requests | 60 seconds |
| `/api/anomaly/score` | 10 requests | 60 seconds |
| `/api/admin/anomaly/train` | 2 requests | 3600 seconds |
| `/api/admin/quarantine` | 10 requests | 3600 seconds |
| `/api/admin/quarantine/restore` | 10 requests | 3600 seconds |
| `/api/admin/config/reload` | 5 requests | 60 seconds |

Rate limit violations return HTTP 429 status with retry information.

## Environment Configuration

### Feature Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `HEALTH_ENDPOINT_ENABLED` | `1` | Enable composite health endpoint |
| `METRICS_DEBUG_ENABLED` | `0` | Enable debug-only metrics endpoints |
| `ANOMALY_ENABLED` | `0` | Enable anomaly detection system |
| `ANOMALY_SKLEARN_ENABLED` | `0` | Enable sklearn-based model training |
| `QUARANTINE_ENABLED` | `0` | Enable file quarantine system |
| `ADMIN_AUTH_ENABLED` | `0` | Enable admin endpoint authentication |
| `RATE_LIMIT_ENABLED` | `0` | Enable API rate limiting |

### Directory Structure

```
data/
├── anomaly/
│   └── state.json              # Anomaly detection state
├── quarantine/
│   ├── audit_log.jsonl         # Quarantine audit trail
│   ├── mapping.json            # Quarantine file mapping
│   └── <quarantined_files>     # Quarantined files
└── ...

models/
└── anomaly_iforest.pkl         # Trained anomaly detection model
```

## Integration Points

### Event Bus Integration

- Anomaly detection system can consume event bus metrics
- Structured logging integrates with existing logging infrastructure
- Health endpoints provide event bus observability metrics

### External Monitoring

- Health endpoints compatible with standard HTTP monitoring tools
- Structured logs suitable for log aggregation platforms (ELK, Splunk)
- Rate limiting headers provide monitoring integration points

## Maintenance

### Regular Tasks

1. **Weekly:** Review anomaly scores and model performance
2. **Weekly:** Audit quarantine operations and cleanup old files
3. **Monthly:** Retrain anomaly models with accumulated data
4. **Monthly:** Review rate limiting metrics and adjust limits if needed

### Performance Considerations

- Anomaly detection state persistence is lightweight (JSON format)
- Quarantine operations use atomic file moves for consistency
- Rate limiting uses in-memory token buckets for efficiency
- All operations designed to fail gracefully without service impact
