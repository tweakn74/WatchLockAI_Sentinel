# Configuration Contract - WatchLockAI Sentinel

**Version:** 1.0.0  
**Generated:** 2025-09-04  
**Component:** P3-001 Config Schema & Migration  

## Overview

This document defines the complete configuration contract for WatchLockAI Sentinel, including all environment variables, their types, defaults, and validation rules.

## Configuration Schema

### Core Service Configuration

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `HEALTH_ENDPOINT_ENABLED` | boolean | `1` | Enable /api/metrics/health endpoint | 0/1, true/false |
| `METRICS_DEBUG_ENABLED` | boolean | `0` | Enable debug metrics endpoints | 0/1, true/false |
| `CONFIG_HOT_RELOAD_ENABLED` | boolean | `0` | Enable configuration hot reload | 0/1, true/false |
| `CONFIG_HOT_RELOAD_DEBOUNCE_MS` | integer | `750` | Hot reload debounce time in milliseconds | 100-5000 |

### Authentication & RBAC

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `ADMIN_AUTH_ENABLED` | boolean | `0` | Enable admin authentication for /api/admin/* routes | 0/1, true/false |
| `ADMIN_TOKEN` | string | - | Admin authentication token | Required when ADMIN_AUTH_ENABLED=1 |
| `RATE_LIMIT_ENABLED` | boolean | `0` | Enable API rate limiting | 0/1, true/false |

### P2-001: Anomaly Detection

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `ANOMALY_ENABLED` | boolean | `0` | Enable anomaly detection system | 0/1, true/false |
| `ANOMALY_SKLEARN_ENABLED` | boolean | `0` | Enable sklearn-based anomaly detection | 0/1, true/false |

### P2-002: Quarantine System

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `QUARANTINE_ENABLED` | boolean | `0` | Enable file quarantine system | 0/1, true/false |
| `QUARANTINE_DIR` | string | `data/quarantine` | Directory for quarantined files | Path validation |

### P2-003: Console Authentication

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `CONSOLE_AUTH_ENABLED` | boolean | `0` | Enable console web authentication | 0/1, true/false |
| `CONSOLE_AUTH_SESSION_KEY` | string | - | Session signing key (32+ bytes hex) | Required when enabled, min 64 chars |
| `CONSOLE_AUTH_USER_DB` | string | `data/auth/users.json` | User database file path | Path validation |

### P2-004: Streaming/SSE

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `STREAM_ENABLED` | boolean | `0` | Enable Server-Sent Events streaming | 0/1, true/false |
| `STREAM_TYPE` | string | `sse` | Streaming protocol type | Enum: [sse] |
| `STREAM_HEALTH_INTERVAL_MS` | integer | `1000` | Health metrics streaming interval | 100-30000 |
| `STREAM_REQUIRE_AUTH` | boolean | `0` | Require authentication for streaming endpoints | 0/1, true/false |

### P3-002: Log Rotation & Redaction

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `LOG_MAX_BYTES` | integer | `1048576` | Maximum log file size in bytes | 1024-104857600 |
| `LOG_BACKUPS` | integer | `5` | Number of backup log files to keep | 1-50 |
| `LOG_REDACT_SECRETS` | boolean | `1` | Enable secret redaction in logs | 0/1, true/false |

### P3-003: Service Packaging

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `SERVICE_ENABLED` | boolean | `0` | Enable Windows service mode | 0/1, true/false |

### P3-005: Plugin System

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `PLUGINS_ENABLED` | boolean | `0` | Enable plugin/extension system | 0/1, true/false |
| `PLUGINS_DIR` | string | `plugins` | Directory containing plugin modules | Path validation |

### P3-006: Telemetry Export

| Variable | Type | Default | Description | Validation |
|----------|------|---------|-------------|------------|
| `EXPORT_ENABLED` | boolean | `0` | Enable telemetry export functionality | 0/1, true/false |
| `EXPORT_FORMAT` | string | `ndjson` | Export file format | Enum: [ndjson, csv] |
| `EXPORT_INCLUDE` | string | `metrics,events` | Comma-separated list of data types to export | CSV validation |

## Configuration Validation Rules

### Type Validation

- **boolean**: Accepts `0`, `1`, `true`, `false`, `yes`, `no`, `on`, `off` (case-insensitive)
- **integer**: Must be valid integer within specified min/max bounds
- **string**: String validation with optional length constraints and enum values

### Dependency Validation

The configuration system validates dependencies between settings:

1. **ADMIN_TOKEN required when ADMIN_AUTH_ENABLED=1**
   - If admin authentication is enabled, the admin token must be provided
   
2. **CONSOLE_AUTH_SESSION_KEY required when CONSOLE_AUTH_ENABLED=1**
   - Session key must be at least 64 characters (32+ bytes in hex)
   - Used for signing session cookies

3. **Path Dependencies**
   - Directory paths are validated for existence when features are enabled
   - Parent directories are created automatically when possible

## API Endpoint

### GET /api/admin/config/schema

**Authentication:** Requires admin authentication (RBAC-gated)

**Response Format:**
```json
{
  "schema": {
    "type": "object",
    "title": "WatchLockAI Sentinel Configuration Schema",
    "version": "1.0.0",
    "properties": {
      "HEALTH_ENDPOINT_ENABLED": {
        "type": "boolean",
        "default": "1",
        "description": "Enable /api/metrics/health endpoint"
      }
      // ... additional properties
    }
  },
  "summary": {
    "validation": {
      "valid": true,
      "errors": [],
      "warnings": [],
      "config": {
        // Current configuration values
      }
    },
    "enabled_features": ["HEALTH_ENDPOINT_ENABLED"],
    "total_settings": 25,
    "schema_version": "1.0.0"
  }
}
```

## Migration Support

The configuration system includes automatic migration support for legacy configuration keys:

### Legacy Key Mappings

| Legacy Key | New Key |
|------------|---------|
| `ENABLE_HEALTH` | `HEALTH_ENDPOINT_ENABLED` |
| `DEBUG_METRICS` | `METRICS_DEBUG_ENABLED` |
| `HOT_RELOAD` | `CONFIG_HOT_RELOAD_ENABLED` |
| `ADMIN_ENABLE` | `ADMIN_AUTH_ENABLED` |
| `RATE_LIMIT` | `RATE_LIMIT_ENABLED` |
| `ANOMALY_DETECT` | `ANOMALY_ENABLED` |
| `FILE_QUARANTINE` | `QUARANTINE_ENABLED` |
| `AUTH_ENABLE` | `CONSOLE_AUTH_ENABLED` |
| `AUTH_KEY` | `CONSOLE_AUTH_SESSION_KEY` |
| `STREAM_ENABLE` | `STREAM_ENABLED` |

### Migration Tool Usage

```bash
# Check current configuration
python tools/config_migrate.py --list

# Perform dry run to see what would be migrated  
python tools/config_migrate.py --dry-run

# Apply migrations with backup
python tools/config_migrate.py

# Create backup only
python tools/config_migrate.py --backup

# Migrate specific config file
python tools/config_migrate.py --config-file /path/to/config.env
```

## Configuration Best Practices

### Security

1. **Environment Variables**: Store sensitive values like `ADMIN_TOKEN` and `CONSOLE_AUTH_SESSION_KEY` in environment variables, not config files
2. **Session Keys**: Generate cryptographically secure session keys with at least 32 bytes of entropy
3. **File Permissions**: Ensure config files have appropriate read permissions (0600 recommended)

### Performance  

1. **Feature Flags**: Only enable features you need to minimize resource usage
2. **Log Rotation**: Configure appropriate log rotation settings for your disk space
3. **Rate Limiting**: Enable rate limiting in production environments

### Operational

1. **Hot Reload**: Use hot reload sparingly in production (default OFF)
2. **Debug Endpoints**: Disable debug endpoints in production (METRICS_DEBUG_ENABLED=0)
3. **Backup**: Always create configuration backups before applying migrations

## Validation Integration

The configuration schema is integrated with:

1. **Preflight Checks**: Configuration validation runs during service startup
2. **Health Endpoint**: Configuration status included in `/api/metrics/health`
3. **Admin API**: Real-time validation available via `/api/admin/config/schema`
4. **Migration Tool**: Automatic validation after configuration migrations

## Schema Versioning

The configuration schema uses semantic versioning:

- **Major version**: Breaking changes to existing configuration keys
- **Minor version**: New configuration keys added (backward compatible)
- **Patch version**: Bug fixes and clarifications (no functional changes)

Current schema version: **1.0.0**
