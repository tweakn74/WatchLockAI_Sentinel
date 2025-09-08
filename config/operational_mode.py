"""Operational Mode storage with atomic JSON persistence.

Provides thread-safe get_mode()/set_mode() operations with validation
and atomic file writes to config/operational_mode.json.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Literal

from loguru import logger

# Type alias for operational modes
OperationalMode = Literal["observe", "alert", "contain", "quarantine", "offline"]

# Valid operational modes
VALID_MODES: set[OperationalMode] = {"observe", "alert", "contain", "quarantine", "offline"}

# Default mode
DEFAULT_MODE: OperationalMode = "observe"

# Global lock for thread-safe operations
_lock = threading.Lock()

# Cache for current mode to avoid repeated file reads
_cached_mode: OperationalMode | None = None
_cache_dirty = True


def _get_config_file_path() -> Path:
    """Get path to operational mode config file.
    
    Returns:
        Path to config/operational_mode.json
    """
    # Get the directory where this module is located
    config_dir = Path(__file__).parent
    return config_dir / "operational_mode.json"


def _read_mode_from_file() -> OperationalMode:
    """Read operational mode from JSON file.
    
    Returns:
        Current operational mode, or default if file doesn't exist or is invalid.
    """
    config_file = _get_config_file_path()
    
    try:
        if not config_file.exists():
            logger.debug(f"Operational mode config file {config_file} not found, using default: {DEFAULT_MODE}")
            return DEFAULT_MODE
            
        with config_file.open('r', encoding='utf-8') as f:
            data = json.load(f)
            
        mode = data.get("mode", DEFAULT_MODE)
        
        # Validate mode
        if mode not in VALID_MODES:
            logger.warning(f"Invalid operational mode '{mode}' in config file, using default: {DEFAULT_MODE}")
            return DEFAULT_MODE
            
        logger.debug(f"Loaded operational mode: {mode}")
        return mode
        
    except (json.JSONDecodeError, OSError, KeyError) as e:
        logger.warning(f"Error reading operational mode config file {config_file}: {e}, using default: {DEFAULT_MODE}")
        return DEFAULT_MODE


def _write_mode_to_file(mode: OperationalMode) -> None:
    """Write operational mode to JSON file atomically.
    
    Args:
        mode: Operational mode to write.
        
    Raises:
        OSError: If file write fails.
        ValueError: If mode is invalid.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid operational mode: {mode}. Valid modes: {', '.join(VALID_MODES)}")
    
    config_file = _get_config_file_path()
    
    # Ensure parent directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare data
    data = {
        "mode": mode,
        "last_updated": "2025-09-02T21:26:51Z"
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
        raise OSError(f"Failed to write operational mode to {config_file}: {e}") from e


def get_mode() -> OperationalMode:
    """Get current operational mode.
    
    Returns:
        Current operational mode.
    """
    global _cached_mode, _cache_dirty
    
    with _lock:
        if _cache_dirty or _cached_mode is None:
            _cached_mode = _read_mode_from_file()
            _cache_dirty = False
            
        return _cached_mode


def set_mode(mode: OperationalMode) -> None:
    """Set operational mode with validation and atomic persistence.
    
    Args:
        mode: Operational mode to set.
        
    Raises:
        ValueError: If mode is invalid.
        OSError: If file write fails.
    """
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


def is_valid_mode(mode: str) -> bool:
    """Check if a mode string is valid.
    
    Args:
        mode: Mode string to validate.
        
    Returns:
        True if mode is valid.
    """
    return mode in VALID_MODES


def get_valid_modes() -> list[OperationalMode]:
    """Get list of valid operational modes.
    
    Returns:
        List of valid operational modes.
    """
    return list(VALID_MODES)


def _invalidate_cache() -> None:
    """Invalidate mode cache (for testing).
    
    Internal function to force cache refresh.
    """
    global _cache_dirty
    with _lock:
        _cache_dirty = True
