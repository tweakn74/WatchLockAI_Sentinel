# Configuration System Architecture - WatchLockAI Sentinel

## Overview

The WatchLockAI Sentinel configuration system provides centralized, type-safe configuration management with YAML-based files, Pydantic validation, environment variable overrides, and optional hot-reload capabilities. The system supports both static configuration and runtime operational mode management.

## Core Components

### Main Configuration (`app_core/config.py`)

Hierarchical configuration system using Pydantic models:

#### Configuration Structure
```python
class SentinelConfig(BaseSettings):
    """Main Sentinel configuration implementing config.yaml structure."""
    
    version: int = 1
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    health: HealthConfig = Field(default_factory=HealthConfig)
    operational: OperationalConfig = Field(default_factory=OperationalConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    alerts: AlertsConfig = Field(default_factory=AlertsConfig)
    responses: ResponsesConfig = Field(default_factory=ResponsesConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig)
```

#### Monitoring Configuration
```python
class MonitoringConfig(BaseModel):
    """Combined monitoring configuration."""
    
    file_system: FileSystemConfig = Field(default_factory=FileSystemConfig)
    processes: ProcessConfig = Field(default_factory=ProcessConfig)
    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)

class FileSystemConfig(BaseModel):
    """File system monitoring configuration per fs_monitor.md."""
    
    enabled: bool = True
    paths: list[str] = Field(default_factory=lambda: ["%USERPROFILE%\\Documents"])
    exclude_globs: list[str] = Field(default_factory=lambda: ["**\\Temp\\**"])
    method: str = Field(default="watchdog", pattern="^(watchdog|polling)$")
    compute_entropy: bool = False
    compute_hash_small_files: bool = False
    small_file_threshold_bytes: int = 1_048_576
    burst_window_sec: int = 10
```

#### Configuration Loading
```python
def load_config(config_path: str | None = None) -> SentinelConfig:
    """Load configuration from YAML file or environment variables."""
    if config_path is None:
        # Try default locations
        possible_paths = [
            Path("config.yaml"),
            Path("configs/config.yaml"),
            Path.home() / ".watchlockai" / "config.yaml",
        ]
        config_path_obj = None
        for path in possible_paths:
            if path.exists():
                config_path_obj = path
                break
    else:
        config_path_obj = Path(config_path)

    if config_path_obj and config_path_obj.exists():
        try:
            with open(config_path_obj, encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            if config_data is None:
                config_data = {}
            return SentinelConfig(**config_data)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file {config_path_obj}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config from {config_path_obj}: {e}")

    # Return default configuration
    return SentinelConfig()
```

### Operational Mode Management (`config/operational_mode.py`)

Thread-safe operational mode storage with atomic persistence:

#### Mode Definitions
```python
# Type alias for operational modes
OperationalMode = Literal["observe", "alert", "contain", "quarantine", "offline"]

# Valid operational modes
VALID_MODES: set[OperationalMode] = {"observe", "alert", "contain", "quarantine", "offline"}

# Default mode
DEFAULT_MODE: OperationalMode = "observe"
```

#### Atomic File Operations
```python
def _write_mode_to_file(mode: OperationalMode) -> None:
    """Write operational mode to JSON file atomically."""
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid operational mode: {mode}. Valid modes: {', '.join(VALID_MODES)}")
    
    config_file = _get_config_file_path()
    
    # Ensure parent directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare data
    data = {
        "mode": mode,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    
    # Atomic write using temporary file
    temp_file = config_file.with_suffix('.tmp')
    
    try:
        with temp_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            f.flush()  # Ensure data is written to disk
            
        # Atomic rename
        temp_file.replace(config_file)
        
        logger.debug(f"Operational mode written to {config_file}: {mode}")
        
    except OSError as e:
        # Clean up temp file on error
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass
        raise OSError(f"Failed to write operational mode to {config_file}: {e}")
```

#### Thread-Safe Access
```python
# Global lock for thread-safe operations
_lock = threading.Lock()
_cached_mode: OperationalMode | None = None
_cache_dirty = True

def get_mode() -> OperationalMode:
    """Get current operational mode."""
    global _cached_mode, _cache_dirty
    
    with _lock:
        if _cache_dirty or _cached_mode is None:
            _cached_mode = _read_mode_from_file()
            _cache_dirty = False
            
        return _cached_mode

def set_mode(mode: OperationalMode) -> None:
    """Set operational mode with validation and atomic persistence."""
    global _cached_mode, _cache_dirty
    
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid operational mode: {mode}. Valid modes: {', '.join(VALID_MODES)}")
    
    with _lock:
        # Write to file first
        _write_mode_to_file(mode)
        
        # Update cache only after successful write
        _cached_mode = mode
        _cache_dirty = False
        
        logger.info(f"Operational mode set to: {mode}")
```

### Hot Reload System

Optional configuration hot-reload with file watching:

#### Hot Reload Configuration
```python
# Hot reload configuration from environment (default OFF for non-regression)
CONFIG_HOT_RELOAD_ENABLED = os.getenv("CONFIG_HOT_RELOAD_ENABLED", "0") == "1"
CONFIG_HOT_RELOAD_INTERVAL = float(os.getenv("CONFIG_HOT_RELOAD_INTERVAL", "3.0"))
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.yaml")
```

#### File Watching Implementation
```python
async def _watch_config() -> None:
    """Background task to watch config file for changes."""
    global _last_mtime, _version, _current_config
    
    config_path = Path(CONFIG_PATH)
    
    while True:
        try:
            await asyncio.sleep(CONFIG_HOT_RELOAD_INTERVAL)
            
            if not config_path.exists():
                continue
                
            current_mtime = config_path.stat().st_mtime
            
            # Check if file changed
            if _last_mtime is None or current_mtime > _last_mtime:
                logger.info(f"Config file {CONFIG_PATH} changed, reloading...")
                
                try:
                    # Load and validate new config
                    new_config = load_config(str(config_path))
                    
                    # Validate the config
                    warnings = validate_config(new_config)
                    if warnings:
                        for warning in warnings:
                            logger.warning(f"Config validation: {warning}")
                    
                    # Atomic update
                    old_config = _current_config
                    _current_config = new_config
                    _version += 1
                    _last_mtime = current_mtime
                    
                    logger.info(f"Config hot-reloaded successfully (version {_version})")
                    
                    # Notify subscribers
                    for subscriber in _subscribers:
                        try:
                            subscriber(new_config)
                        except Exception as e:
                            logger.exception(f"Config change subscriber error: {e}")
                            
                except Exception as e:
                    logger.error(f"Config hot-reload failed: {e}")
                    
        except Exception as e:
            logger.error(f"Config watcher error: {e}")
```

#### Subscription System
```python
def subscribe_to_config_changes(callback: Callable[[SentinelConfig], None]) -> None:
    """Subscribe to configuration change notifications."""
    global _subscribers
    _subscribers.append(callback)
    logger.debug(f"Config change subscriber added: {callback.__name__}")

def unsubscribe_from_config_changes(callback: Callable[[SentinelConfig], None]) -> None:
    """Unsubscribe from configuration change notifications."""
    global _subscribers
    try:
        _subscribers.remove(callback)
        logger.debug(f"Config change subscriber removed: {callback.__name__}")
    except ValueError:
        logger.warning(f"Config change subscriber not found: {callback.__name__}")
```

## Configuration Schema Validation

### Pydantic Integration
```python
class FileSystemConfig(BaseModel):
    """File system monitoring configuration per fs_monitor.md."""
    
    enabled: bool = True
    paths: list[str] = Field(default_factory=lambda: ["%USERPROFILE%\\Documents"])
    exclude_globs: list[str] = Field(default_factory=lambda: ["**\\Temp\\**"])
    method: str = Field(default="watchdog", pattern="^(watchdog|polling)$")
    compute_entropy: bool = False
    compute_hash_small_files: bool = False
    small_file_threshold_bytes: int = 1_048_576
    burst_window_sec: int = 10
```

### Custom Validators
```python
@field_validator("paths")
@classmethod
def validate_paths(cls, v: list[str]) -> list[str]:
    """Validate monitoring paths exist and are accessible."""
    validated_paths = []
    for path in v:
        expanded_path = os.path.expandvars(path)
        if os.path.exists(expanded_path):
            validated_paths.append(expanded_path)
        else:
            logger.warning(f"Monitoring path does not exist: {path}")
    return validated_paths if validated_paths else [os.path.expandvars("%USERPROFILE%\\Documents")]
```

### Configuration Validation
```python
def validate_config(config: SentinelConfig) -> list[str]:
    """Validate configuration and return warnings."""
    warnings = []
    
    # Validate monitoring paths
    if config.monitoring.file_system.enabled:
        if not config.monitoring.file_system.paths:
            warnings.append("File system monitoring enabled but no paths configured")
    
    # Validate network configuration
    if config.monitoring.network.enabled:
        if config.monitoring.network.poll_interval_ms < 100:
            warnings.append("Network polling interval too low, may impact performance")
    
    # Validate health thresholds
    if config.health.cpu_warn > 100 or config.health.cpu_warn < 0:
        warnings.append("CPU warning threshold must be between 0 and 100")
    
    return warnings
```

## Environment Variable Integration

### Pydantic Settings Integration
```python
class SentinelConfig(BaseSettings):
    """Main Sentinel configuration implementing config.yaml structure."""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False,
        "extra": "forbid",
    }
```

### Environment Variable Patterns
```bash
# Override monitoring settings
MONITORING__FILE_SYSTEM__ENABLED=true
MONITORING__FILE_SYSTEM__COMPUTE_ENTROPY=true

# Override alert settings
ALERTS__TOAST_NOTIFICATIONS=false
ALERTS__LOG_JSONL=true

# Override operational settings
OPERATIONAL__MODE=alert
```

## Configuration File Locations

### Search Order
1. `config.yaml` (current directory)
2. `configs/config.yaml` (configs subdirectory)
3. `~/.watchlockai/config.yaml` (user home directory)

### File Format
```yaml
version: 1

monitoring:
  file_system:
    enabled: true
    paths:
      - "%USERPROFILE%\\Documents"
      - "%USERPROFILE%\\Desktop"
    exclude_globs:
      - "**\\Temp\\**"
      - "**\\.git\\**"
    method: "watchdog"
    compute_entropy: false
    compute_hash_small_files: false
    small_file_threshold_bytes: 1048576
    burst_window_sec: 10

  processes:
    enabled: true
    track_children: true
    include_system_processes: false

  registry:
    enabled: true
    monitor_autostart: true
    hives:
      - "HKCU"
      - "HKLM"

  network:
    enabled: true
    track_process_association: true
    poll_interval_ms: 1000
    include_udp: true

health:
  enabled: true
  cpu_warn: 90
  ram_warn: 90
  disk_warn_pct_free: 5
  temp_warn_c: null

operational:
  mode: "observe"

rag:
  enabled: true
  embeddings_model: "sentence-transformers/all-MiniLM-L6-v2"
  chunk_size: 512
  chunk_overlap: 50

alerts:
  toast_notifications: true
  log_jsonl: true
  jsonl_path: "logs/alerts.jsonl"

responses:
  allow_destructive_actions: false
  require_user_consent: true

service:
  install_on_setup: true

privacy:
  outbound_disabled_by_default: true
```

## API Integration

### Configuration Schema Endpoint
```python
@app.get("/api/admin/config/schema")
def admin_config_schema() -> dict:
    """Get configuration schema and current validation state."""
    try:
        schema = SentinelConfig.model_json_schema()
        current_config = get_current_config()
        validation_errors = validate_config(current_config)
        
        return {
            "schema": schema,
            "current_config": current_config.model_dump(),
            "validation_errors": validation_errors,
            "schema_version": "1.0"
        }
    except Exception as e:
        return {"error": str(e), "enabled": True}
```

### Configuration Reload Endpoint
```python
@app.post("/api/admin/config/reload")
async def admin_config_reload(debounce_ms: int = 750) -> dict:
    """Reload configuration from file with debouncing."""
    try:
        # Debounce rapid reload requests
        await asyncio.sleep(debounce_ms / 1000.0)
        
        # Reload configuration
        new_config = load_config()
        warnings = validate_config(new_config)
        
        # Update global configuration
        update_current_config(new_config)
        
        return {
            "status": "success",
            "message": "Configuration reloaded successfully",
            "warnings": warnings,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## Security and Privacy

### Sensitive Data Handling
- Environment variables for secrets
- Configuration file permission validation
- Sensitive field redaction in logs
- Secure default configurations

### Access Control
- Admin authentication for configuration changes
- Operational mode restrictions
- Configuration schema validation
- Audit logging for configuration changes

## Testing and Validation

### Configuration Testing
```python
def test_config_loading():
    """Test configuration loading from various sources."""
    # Test default configuration
    config = SentinelConfig()
    assert config.monitoring.file_system.enabled is True
    
    # Test YAML loading
    config = load_config("test_config.yaml")
    assert config.version == 1
    
    # Test environment variable override
    os.environ["MONITORING__FILE_SYSTEM__ENABLED"] = "false"
    config = SentinelConfig()
    assert config.monitoring.file_system.enabled is False
```

### Validation Testing
```python
def test_config_validation():
    """Test configuration validation."""
    config = SentinelConfig()
    config.health.cpu_warn = 150  # Invalid value
    
    warnings = validate_config(config)
    assert any("CPU warning threshold" in warning for warning in warnings)
```

## Performance Considerations

### Lazy Loading
- Configuration loaded on-demand
- Hot reload disabled by default
- Cached configuration access
- Minimal validation overhead

### Memory Management
- Weak references for subscribers
- Configuration object reuse
- Efficient YAML parsing
- Bounded configuration history

### File I/O Optimization
- Atomic file operations
- Minimal file system polling
- Efficient change detection
- Graceful error handling
