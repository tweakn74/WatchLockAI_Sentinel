# Configuration Keys Reference

## Configuration File Structure

Primary configuration is stored in `config.yaml` with runtime operational mode in `config/operational_mode.json`.

| Key Path | Owner Module | Type | Default | Description | Read/Write Locations |
|---|---|---|---|---|---|
| **version** | `app_core.config` | `int` | `1` | Configuration schema version | Read: config loading, Write: config generation |
| **monitoring.file_system.enabled** | `collectors.fs_monitor` | `bool` | `true` | Enable file system monitoring | Read: fs_monitor init, Write: config updates |
| **monitoring.file_system.paths** | `collectors.fs_monitor` | `list[str]` | `["%USERPROFILE%\\Documents"]` | Paths to monitor for file changes | Read: fs_monitor setup, Write: config updates |
| **monitoring.file_system.exclude_globs** | `collectors.fs_monitor` | `list[str]` | `["**\\Temp\\**"]` | Glob patterns for excluded paths | Read: fs_monitor filtering, Write: config updates |
| **monitoring.file_system.method** | `collectors.fs_monitor` | `str` | `"watchdog"` | Monitoring method (watchdog/polling) | Read: fs_monitor init, Write: config updates |
| **monitoring.file_system.compute_entropy** | `collectors.fs_monitor` | `bool` | `false` | Calculate Shannon entropy for files | Read: fs_monitor processing, Write: config updates |
| **monitoring.file_system.compute_hash_small_files** | `collectors.fs_monitor` | `bool` | `false` | Hash files under threshold | Read: fs_monitor processing, Write: config updates |
| **monitoring.file_system.small_file_threshold_bytes** | `collectors.fs_monitor` | `int` | `1048576` | Threshold for small file hashing (1MB) | Read: fs_monitor processing, Write: config updates |
| **monitoring.file_system.burst_window_sec** | `collectors.fs_monitor` | `int` | `10` | Time window for burst event detection | Read: fs_monitor processing, Write: config updates |
| **monitoring.processes.enabled** | `collectors.proc_monitor` | `bool` | `true` | Enable process monitoring | Read: proc_monitor init, Write: config updates |
| **monitoring.processes.poll_interval_ms** | `collectors.proc_monitor` | `int` | `1000` | Process polling interval in milliseconds | Read: proc_monitor loop, Write: config updates |
| **monitoring.processes.capture_hash** | `collectors.proc_monitor` | `bool` | `false` | Capture SHA256 hash of process executables | Read: proc_monitor processing, Write: config updates |
| **monitoring.registry.enabled** | `collectors.reg_monitor` | `bool` | `true` | Enable registry monitoring (Windows only) | Read: reg_monitor init, Write: config updates |
| **monitoring.registry.watch_keys** | `collectors.reg_monitor` | `list[str]` | `["HKCU\\Software\\...\\Run", ...]` | Registry keys to monitor | Read: reg_monitor setup, Write: config updates |
| **monitoring.registry.method** | `collectors.reg_monitor` | `str` | `"notify"` | Registry monitoring method (notify/polling) | Read: reg_monitor init, Write: config updates |
| **monitoring.network.enabled** | `collectors.net_monitor` | `bool` | `true` | Enable network monitoring | Read: net_monitor init, Write: config updates |
| **monitoring.network.track_process_association** | `collectors.net_monitor` | `bool` | `true` | Associate network connections with processes | Read: net_monitor processing, Write: config updates |
| **monitoring.network.poll_interval_ms** | `collectors.net_monitor` | `int` | `1000` | Network polling interval in milliseconds | Read: net_monitor loop, Write: config updates |
| **monitoring.network.include_udp** | `collectors.net_monitor` | `bool` | `true` | Include UDP connections in monitoring | Read: net_monitor processing, Write: config updates |
| **health.enabled** | `collectors.health_monitor` | `bool` | `true` | Enable system health monitoring | Read: health_monitor init, Write: config updates |
| **health.cpu_warn** | `collectors.health_monitor` | `int` | `90` | CPU usage warning threshold (%) | Read: health_monitor alerts, Write: config updates |
| **health.ram_warn** | `collectors.health_monitor` | `int` | `90` | Memory usage warning threshold (%) | Read: health_monitor alerts, Write: config updates |
| **health.disk_warn_pct_free** | `collectors.health_monitor` | `int` | `5` | Disk free space warning threshold (%) | Read: health_monitor alerts, Write: config updates |
| **health.temp_warn_c** | `collectors.health_monitor` | `float` | `null` | Temperature warning threshold (Celsius) | Read: health_monitor alerts, Write: config updates |
| **operational.mode** | `config.operational_mode` | `str` | `"observe"` | **DEPRECATED** - Use operational_mode.json | Read: fallback only, Write: config migration |
| **rag.index_dir** | `detection.knowledge.loader` | `str` | `"detection/knowledge/index"` | Directory for RAG knowledge index | Read: knowledge loader, Write: config updates |
| **rag.mode** | `detection.knowledge.loader` | `str` | `"embeddings"` | RAG search mode (embeddings/fts) | Read: knowledge loader, Write: config updates |
| **alerts.toast_notifications** | `response.alert_manager` | `bool` | `true` | Enable desktop toast notifications | Read: alert_manager, Write: config updates |
| **alerts.log_jsonl** | `response.alert_manager` | `str` | `"logs/alerts.jsonl"` | JSONL log file for alerts | Read: alert_manager, Write: config updates |
| **responses.allow_destructive_actions** | `response.actions` | `bool` | `false` | Allow destructive response actions | Read: actions manager, Write: policy updates |
| **service.install_on_setup** | `service.service_wrapper` | `bool` | `true` | Install as Windows service on setup | Read: service installer, Write: config updates |
| **privacy.outbound_disabled_by_default** | `app_core.config` | `bool` | `true` | Disable outbound connections by default | Read: network policies, Write: config updates |

## Runtime Configuration

### Operational Mode (Persistent)

Stored in `config/operational_mode.json` with atomic updates:

| Key | Type | Default | Valid Values | Description |
|---|---|---|---|---|
| **mode** | `str` | `"observe"` | `observe`, `alert`, `contain`, `quarantine`, `offline` | Current operational mode |
| **last_updated** | `str` | Auto-generated | ISO-8601 timestamp | Last mode change timestamp |

**Access Pattern:**
- **Read**: `config.operational_mode.get_mode()` 
- **Write**: `config.operational_mode.set_mode(mode)`
- **Validation**: `config.operational_mode.is_valid_mode(mode)`

## Configuration Access Patterns

### Loading Hierarchy
1. **config.yaml** -> Primary configuration (all sections)
2. **config/operational_mode.json** -> Runtime operational mode override
3. **Environment variables** -> Prefix-based overrides (SENTINEL_*)
4. **Defaults** -> Pydantic model defaults

### Configuration Writers
- **Web API**: `/api/policies` endpoint updates operational mode
- **Service Setup**: Initial config.yaml generation
- **Operational Mode API**: `/api/operational_mode` endpoint
- **Configuration Management**: Direct config file updates

### Configuration Readers  
- **All Collectors**: Read monitoring.* sections during initialization
- **Detection Engines**: Read rag.* configuration for knowledge loading
- **Response Systems**: Read alerts.* and responses.* for action policies
- **Service Layer**: Read service.* for Windows service behavior
- **Health Monitoring**: Read health.* for alert thresholds

## Environment Variable Overrides

Configuration supports environment variable overrides using `SENTINEL_` prefix:

| Environment Variable | Configuration Key | Example |
|---|---|---|
| `SENTINEL_MONITORING__FILE_SYSTEM__ENABLED` | `monitoring.file_system.enabled` | `SENTINEL_MONITORING__FILE_SYSTEM__ENABLED=false` |
| `SENTINEL_RESPONSES__ALLOW_DESTRUCTIVE_ACTIONS` | `responses.allow_destructive_actions` | `SENTINEL_RESPONSES__ALLOW_DESTRUCTIVE_ACTIONS=true` |
| `SENTINEL_RAG__INDEX_DIR` | `rag.index_dir` | `SENTINEL_RAG__INDEX_DIR=/custom/index/path` |

**Note**: Use double underscore `__` to separate nested configuration levels.

## Configuration Validation

### Pydantic Models
- **SentinelConfig**: Root configuration with all sections
- **MonitoringConfig**: All monitoring collector settings
- **HealthConfig**: System health alert thresholds  
- **OperationalConfig**: Operational mode and policies
- **RAGConfig**: Knowledge system configuration
- **AlertsConfig**: Alert routing and notification settings
- **ResponsesConfig**: Response action policies

### Validation Rules
- **Enum Values**: Operational mode, monitoring methods validated against allowed values
- **Range Constraints**: Health thresholds (0-100%), port numbers (0-65535)
- **Path Validation**: Directory paths checked for existence during initialization
- **Type Coercion**: String/numeric types automatically converted where appropriate

## Configuration File Locations

| File | Purpose | Format | Persistence |
|---|---|---|---|
| `config.yaml` | Primary configuration | YAML | Manual/API updates |
| `config/operational_mode.json` | Runtime operational mode | JSON | API updates with atomic writes |
| `.env` | Environment variables | Key=Value | Manual setup |
| `logs/config_changes.jsonl` | Configuration change audit | JSONL | Automatic logging |

## Thread Safety

- **config.yaml**: Read-only after initial load (restart required for changes)
- **operational_mode.json**: Thread-safe atomic writes with file locking
- **In-memory config**: Immutable after load, new instances created for updates
- **Environment variables**: Read-only from system environment
