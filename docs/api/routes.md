# API Routes Documentation

## REST API Endpoints

| Method | Path | Handler | Input Models | Output Models | Notes | Known Issues |
|---|---|---|---|---|---|---|
| **GET** | `/api/status` | `get_status()` | None | `StatusResponse` | Service status and component health | May return 503 if service unavailable |
| **GET** | `/api/alerts` | `get_alerts()` | Query params | `AlertSummary` | Recent alerts with severity counts | Returns empty summary on error |
| **GET** | `/api/detections` | `get_detections()` | `limit`, `severity`, `tag` params | `DetectionResponse` | Detection events with filtering | Requires rules engine availability |
| **POST** | `/api/actions/pause` | `pause_monitoring()` | `duration_minutes` (default: 5) | `ActionResponse` | Pause monitoring temporarily | Requires actions manager |
| **POST** | `/api/actions/resume` | `resume_monitoring()` | None | `ActionResponse` | Resume paused monitoring | Requires actions manager |
| **GET** | `/api/ti/search` | `search_threat_intelligence()` | `query`, `limit` params | `ThreatIntelResponse` | Search threat intelligence DB | Query must be ≥2 chars, limit 1-50 |
| **GET** | `/api/policies` | `get_policies()` | None | `PolicyResponse` | Current operational policies | Returns mode and destructive actions setting |
| **POST** | `/api/policies` | `set_policies()` | `operational_mode` in JSON | `PolicyUpdateResponse` | Update operational policies | Only accepts 'monitor' or 'proactive' modes |
| **GET** | `/api/operational_mode` | `get_operational_mode()` | None | `OperationalModeResponse` | Current operational mode | From `console.api.operational_mode` router |
| **PUT** | `/api/operational_mode` | `set_operational_mode()` | `OperationalModeRequest` | `OperationalModeUpdateResponse` | Set operational mode | Validates against allowed modes |
| **GET** | `/health` | `health_check()` | None | `{"status": "healthy"}` | Simple health check | Always returns 200 OK |

## Web Console Pages

| Method | Path | Handler | Template | Purpose | Notes |
|---|---|---|---|---|---|
| **GET** | `/` | `dashboard()` | `dashboard.html` | Main monitoring dashboard | Service status overview |
| **GET** | `/detections` | `detections_page()` | `detections.html` | Detection events view | Alert and detection history |
| **GET** | `/assets` | `assets_page()` | `assets.html` | Asset monitoring | File and system asset tracking |
| **GET** | `/accounts` | `accounts_page()` | `accounts.html` | Account activity | User and process account monitoring |
| **GET** | `/processes` | `processes_page()` | `processes.html` | Process monitoring | Script and process activity |
| **GET** | `/policies` | `policies_page()` | `policies.html` | Policy configuration | Operational mode and policy management |

## OpenAPI Documentation

- **Swagger UI**: `/api/docs` 
- **ReDoc**: `/api/redoc`
- **OpenAPI Spec**: Available at runtime from FastAPI

## API Model Schemas

### Response Models

#### StatusResponse
```json
{
  "running": true,
  "uptime_seconds": 3600.0,
  "collectors": {"fs_monitor": "running", "proc_monitor": "running"},
  "rules_engine": {"status": "active", "rules_loaded": 45},
  "event_bus": {"subscribers": 8, "events_processed": 1205},
  "timestamp": "2025-09-03T03:02:21.123456Z"
}
```

#### AlertSummary
```json
{
  "total_alerts": 25,
  "critical_alerts": 3,
  "warning_alerts": 15,
  "info_alerts": 7,
  "recent_alerts": [{"id": "alert-123", "severity": "high", "...": "..."}]
}
```

#### ThreatIntelResponse
```json
{
  "success": true,
  "query": "lateral movement",
  "total_results": 15,
  "results": [{"technique": "T1021", "description": "Remote Services", "...": "..."}],
  "frameworks_searched": ["MITRE_ATT&CK", "Cyber_Kill_Chain"],
  "timestamp": "2025-09-03T03:02:21.123456Z"
}
```

#### OperationalModeResponse
```json
{
  "mode": "observe",
  "timestamp": "2025-09-03T03:02:21.123456Z"
}
```

### Request Models

#### OperationalModeRequest
```json
{
  "mode": "observe"
}
```

#### Policy Update Request
```json
{
  "operational_mode": "proactive"
}
```

## Authentication & Security

- **Local Only**: API binds to 127.0.0.1 by default (localhost only)
- **No Authentication**: Currently no authentication required (assumed local access)
- **CORS**: Not configured (same-origin requests only)

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Successful operation
- **400 Bad Request**: Invalid input parameters
- **500 Internal Server Error**: Service component failure
- **503 Service Unavailable**: Required service component not available

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

## API Dependencies

### Required Service Components
- **SentinelService**: Main service instance (required for all endpoints)
- **AlertManager**: Required for `/api/alerts` endpoint  
- **RulesEngine**: Required for `/api/detections` endpoint
- **ActionsManager**: Required for `/api/actions/*` endpoints
- **ThreatIntelDB**: Required for `/api/ti/search` endpoint

### Missing Component Behavior
- Returns **503 Service Unavailable** when required components are not initialized
- Graceful fallback for optional components (returns empty/default responses)

## Configuration Integration

### Operational Mode Integration
- **Storage**: Persisted in `config/operational_mode.json` 
- **Runtime**: Synchronized with `app_core.config.OperationalConfig`
- **Valid Modes**: `observe`, `alert`, `contain`, `quarantine`, `offline`
- **API Updates**: Changes propagated to all service components

### Policy Management
- **Configuration File**: Updates written to `config.yaml`
- **Runtime Config**: Synchronized with `SentinelConfig` instance
- **Destructive Actions**: Controlled by `responses.allow_destructive_actions` setting

## Performance Considerations

- **Event Filtering**: API endpoints support filtering to reduce response size
- **Pagination**: Implicit limits on response sizes (alerts: 50, detections: 100)
- **Async Operations**: All endpoints are async for better concurrency
- **Error Isolation**: Component failures don't crash entire API server
