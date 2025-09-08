"""Configuration management for WatchLockAI Sentinel based on Knowledge Pack specifications."""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Callable, cast

import yaml
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Hot reload configuration from environment (default OFF for non-regression)
CONFIG_HOT_RELOAD_ENABLED = os.getenv("CONFIG_HOT_RELOAD_ENABLED", "0") == "1"
CONFIG_HOT_RELOAD_INTERVAL = float(os.getenv("CONFIG_HOT_RELOAD_INTERVAL", "3.0"))
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.yaml")

# Private hot reload state
_reload_task: asyncio.Task[None] | None = None
_last_mtime: float | None = None
_version: int = 0
_subscribers: list[Callable[[SentinelConfig], None]] = []
_current_config: SentinelConfig | None = None


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


class ProcessConfig(BaseModel):
    """Process monitoring configuration per process_monitor.md."""

    enabled: bool = True
    poll_interval_ms: int = 1000
    capture_hash: bool = False


class RegistryConfig(BaseModel):
    """Registry monitoring configuration per registry_monitor.md."""

    enabled: bool = True
    watch_keys: list[str] = Field(default_factory=lambda: [
        "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
    ])
    method: str = Field(default="notify", pattern="^(notify|polling)$")


class NetworkConfig(BaseModel):
    """Network monitoring configuration per net_monitor.md."""

    enabled: bool = True
    track_process_association: bool = True
    poll_interval_ms: int = 1000
    include_udp: bool = True


class HealthConfig(BaseModel):
    """Health monitoring configuration per health_monitor.md."""

    enabled: bool = True
    cpu_warn: int = 90
    ram_warn: int = 90
    disk_warn_pct_free: int = 5
    temp_warn_c: float | None = None


class MonitoringConfig(BaseModel):
    """Combined monitoring configuration."""

    file_system: FileSystemConfig = Field(default_factory=FileSystemConfig)
    processes: ProcessConfig = Field(default_factory=ProcessConfig)
    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)


class RAGConfig(BaseModel):
    """RAG system configuration per loader.py requirements."""

    index_dir: str = "detection/knowledge/index"
    mode: str = Field(default="embeddings", pattern="^(embeddings|fts)$")


class AlertsConfig(BaseModel):
    """Alerts configuration per alerts.md."""

    toast_notifications: bool = True
    log_jsonl: str = "logs/alerts.jsonl"


class ResponsesConfig(BaseModel):
    """Response actions configuration per actions.md."""

    allow_destructive_actions: bool = False


class OperationalConfig(BaseModel):
    """Operational control configuration for monitoring mode."""

    mode: str = Field(default="observe", pattern="^(observe|alert|contain|quarantine|offline)$")

    @property
    def current_mode(self) -> str:
        """Get current operational mode from persistent storage.
        
        Returns:
            Current operational mode from config/operational_mode.json.
        """
        try:
            # Import here to avoid circular imports
            from config.operational_mode import get_mode  # type: ignore[import]
            return get_mode()
        except Exception:
            # Fallback to configured default if storage unavailable
            return self.mode


class ServiceConfig(BaseModel):
    """Windows service configuration."""

    install_on_setup: bool = True


class PrivacyConfig(BaseModel):
    """Privacy configuration per requirements."""

    outbound_disabled_by_default: bool = True


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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False,
        "extra": "forbid",
    }


def load_config(config_path: str | None = None) -> SentinelConfig:
    """Load configuration from YAML file or environment variables.

    Args:
        config_path: Path to config.yaml file. If None, uses default locations.

    Returns:
        Loaded configuration object.

    Raises:
        FileNotFoundError: If config file not found and no defaults available.
        ValueError: If config file is invalid YAML or contains invalid values.
    """
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
            return SentinelConfig(**cast(dict[str, Any], config_data))
        except yaml.YAMLError as e:
            msg = f"Invalid YAML in config file {config_path_obj}: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Error loading config from {config_path_obj}: {e}"
            raise ValueError(msg) from e

    # Return default configuration
    return SentinelConfig()


def save_default_config(config_path: str = "config.yaml") -> None:
    """Save default configuration to YAML file.

    Args:
        config_path: Path where to save the config file.
    """
    config = SentinelConfig()
    config_dict = config.model_dump()

    # Create directories if needed
    config_path_obj = Path(config_path)
    config_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path_obj, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)


def validate_config(config: SentinelConfig) -> list[str]:
    """Validate configuration and return list of warnings/issues.

    Args:
        config: Configuration to validate.

    Returns:
        List of validation warnings or issues.
    """
    warnings: list[str] = []

    # Validate file paths exist (where applicable)
    for path in config.monitoring.file_system.paths:
        expanded_path = Path(path.replace("%USERPROFILE%", str(Path.home())))
        if not expanded_path.exists():
            warnings.append(f"Monitored path does not exist: {path}")

    # Validate polling intervals are reasonable
    if config.monitoring.processes.poll_interval_ms < 100:
        warnings.append("Process poll interval may be too aggressive (< 100ms)")

    if config.monitoring.network.poll_interval_ms < 100:
        warnings.append("Network poll interval may be too aggressive (< 100ms)")

    # Validate health thresholds
    if config.health.cpu_warn > 100 or config.health.cpu_warn < 0:
        warnings.append("CPU warning threshold should be between 0-100")

    if config.health.ram_warn > 100 or config.health.ram_warn < 0:
        warnings.append("RAM warning threshold should be between 0-100")

    if config.health.disk_warn_pct_free > 100 or config.health.disk_warn_pct_free < 0:
        warnings.append("Disk warning threshold should be between 0-100")

    return warnings


def start_hot_reload(loop: asyncio.AbstractEventLoop | None = None) -> None:
    """Start configuration hot reload watcher (no-op if disabled or already running).
    
    Args:
        loop: Event loop to use. If None, uses current loop.
    """
    global _reload_task
    
    if not CONFIG_HOT_RELOAD_ENABLED:
        logger.debug("Config hot reload disabled (CONFIG_HOT_RELOAD_ENABLED=0)")
        return
    
    if _reload_task is not None:
        logger.warning("Config hot reload already running")
        return
    
    try:
        if loop is None:
            loop = asyncio.get_event_loop()
        
        _reload_task = loop.create_task(_watch_config())
        logger.info(f"Config hot reload started (watching {CONFIG_PATH}, interval={CONFIG_HOT_RELOAD_INTERVAL}s)")
    except Exception as e:
        logger.error(f"Failed to start config hot reload: {e}")


def stop_hot_reload() -> None:
    """Stop configuration hot reload watcher (safe cancel/await)."""
    global _reload_task
    
    if _reload_task is None:
        return
    
    try:
        _reload_task.cancel()
        _reload_task = None
        logger.info("Config hot reload stopped")
    except Exception as e:
        logger.error(f"Error stopping config hot reload: {e}")


def subscribe_on_change(cb: Callable[[SentinelConfig], None]) -> None:
    """Subscribe to configuration change notifications.
    
    Args:
        cb: Callback function to invoke when config changes.
    """
    global _subscribers
    _subscribers.append(cb)
    logger.debug(f"Config change subscriber added (total: {len(_subscribers)})")


async def _watch_config() -> None:
    """Watch configuration file for changes and reload atomically."""
    global _last_mtime, _version, _current_config
    
    config_path = Path(CONFIG_PATH)
    
    try:
        # Initialize last known mtime
        if config_path.exists():
            _last_mtime = config_path.stat().st_mtime
        else:
            _last_mtime = None
        
        logger.debug(f"Config watcher initialized (file exists: {config_path.exists()})")
        
        while True:
            await asyncio.sleep(CONFIG_HOT_RELOAD_INTERVAL)
            
            try:
                # Check if file exists and get current mtime
                if not config_path.exists():
                    if _last_mtime is not None:
                        logger.warning(f"Config file {CONFIG_PATH} was deleted")
                        _last_mtime = None
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
                        logger.exception(f"Config hot-reload ignored (validation/parse error): {e}")
                        # Keep old config on error
                        
            except OSError as e:
                # File system errors (permissions, etc.)
                logger.error(f"Config file access error: {e}")
                
    except asyncio.CancelledError:
        logger.debug("Config watcher cancelled")
        raise
    except Exception as e:
        logger.exception(f"Config watcher unexpected error: {e}")


def get_current_config() -> SentinelConfig | None:
    """Get the current hot-reloaded configuration.
    
    Returns:
        Current configuration if available, None otherwise.
    """
    return _current_config


def get_config_version() -> int:
    """Get current configuration version number.
    
    Returns:
        Configuration version (increments on each reload).
    """
    return _version
