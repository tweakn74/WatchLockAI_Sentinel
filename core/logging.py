"""Logging configuration for WatchLockAI Sentinel with JSONL support for events and alerts."""

from __future__ import annotations

import json
import logging
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from .schemas import DetectionAlert, SentinelEvent


class JSONLEventHandler:
    """Custom handler for JSONL event logging with provenance tracking."""

    def __init__(self, log_path: str) -> None:
        """Initialize JSONL handler.

        Args:
            log_path: Path to JSONL log file.
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event: SentinelEvent) -> None:
        """Log event to JSONL file.

        Args:
            event: Event to log.
        """
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                json.dump(event.model_dump(), f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            logger.error(f"Failed to write event to JSONL: {e}")


class JSONLAlertHandler(JSONLEventHandler):
    """Specialized handler for alert logging with enhanced metadata."""

    def log_alert(self, alert: DetectionAlert) -> None:
        """Log alert with enhanced metadata.

        Args:
            alert: Alert to log.
        """
        # Add alert-specific metadata
        alert_data = alert.model_dump()
        alert_data["log_type"] = "alert"
        alert_data["logged_at"] = datetime.now(timezone.utc).isoformat()

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                json.dump(alert_data, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            logger.error(f"Failed to write alert to JSONL: {e}")


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_jsonl_events: bool = True,
    enable_jsonl_alerts: bool = True,
) -> dict[str, Any]:
    """Setup comprehensive logging for Sentinel.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_dir: Directory for log files.
        enable_console: Enable console logging.
        enable_file: Enable rotating file logging.
        enable_jsonl_events: Enable JSONL event logging.
        enable_jsonl_alerts: Enable JSONL alert logging.

    Returns:
        Dictionary containing logger handlers and configuration.
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    # Remove default logger
    logger.remove()

    handlers: dict[str, Any] = {}

    # Console logging
    if enable_console:
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
        handlers["console"] = True

    # Rotating file logging
    if enable_file:
        logger.add(
            log_dir_path / "sentinel.log",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )
        handlers["file"] = log_dir_path / "sentinel.log"

    # JSONL event logging
    if enable_jsonl_events:
        events_handler = JSONLEventHandler(str(log_dir_path / "events.jsonl"))
        handlers["events_jsonl"] = events_handler

    # JSONL alert logging
    if enable_jsonl_alerts:
        alerts_handler = JSONLAlertHandler(str(log_dir_path / "alerts.jsonl"))
        handlers["alerts_jsonl"] = alerts_handler

    # Add debug logging for development
    if log_level == "DEBUG":
        logger.add(
            log_dir_path / "debug.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="5 MB",
            retention="7 days",
            compression="zip",
        )
        handlers["debug"] = log_dir_path / "debug.log"

    logger.info(f"Logging initialized: level={log_level}, handlers={list(handlers.keys())}")

    return handlers


def setup_windows_event_log() -> logging.Handler | None:
    """Setup Windows Event Log integration (optional).

    Returns:
        Windows event log handler if available, None otherwise.
    """
    try:
        # Only attempt Windows imports on Windows platform
        if platform.system() != "Windows":
            logger.info("Running on non-Windows platform - Windows Event Log integration disabled")
            return None
            
        import win32evtlog  # type: ignore[import-untyped]
        import win32evtlogutil  # type: ignore[import-untyped]

        # Create custom event log handler for high-severity alerts
        class WindowsEventHandler(logging.Handler):
            def __init__(self, app_name: str = "WatchLockAI_Sentinel") -> None:
                super().__init__()
                self.app_name = app_name

            def emit(self, record: logging.LogRecord) -> None:
                if record.levelno >= logging.ERROR:
                    try:
                        win32evtlogutil.ReportEvent(
                            self.app_name,
                            1,  # Event ID
                            eventCategory=0,
                            eventType=win32evtlog.EVENTLOG_ERROR_TYPE,
                            strings=[record.getMessage()],
                        )
                    except Exception:
                        pass  # Silently fail if Windows Event Log unavailable

        handler = WindowsEventHandler()
        handler.setLevel(logging.ERROR)

        # Add to standard Python logging (loguru doesn't directly support Windows Event Log)
        python_logger = logging.getLogger("sentinel.windows_events")
        python_logger.addHandler(handler)
        python_logger.setLevel(logging.ERROR)

        logger.info("Windows Event Log integration enabled")
        return handler

    except ImportError:
        logger.debug("Windows Event Log not available (pywin32 not installed)")
        return None
    except Exception as e:
        logger.warning(f"Failed to setup Windows Event Log: {e}")
        return None


def log_event(event: SentinelEvent, handlers: dict[str, Any]) -> None:
    """Log event using appropriate handlers.

    Args:
        event: Event to log.
        handlers: Dictionary of logging handlers from setup_logging().
    """
    # Standard logging
    logger.debug(f"Event: {event.__class__.__name__} - {event.model_dump()}")

    # JSONL logging
    if "events_jsonl" in handlers:
        handlers["events_jsonl"].log_event(event)


def log_alert(alert: DetectionAlert, handlers: dict[str, Any]) -> None:
    """Log alert using appropriate handlers with enhanced tracking.

    Args:
        alert: Alert to log.
        handlers: Dictionary of logging handlers from setup_logging().
    """
    # Enhanced logging for alerts
    logger.warning(
        f"ALERT [{alert.severity.upper()}] {alert.tag}: {alert.rationale} "
        f"(confidence: {alert.confidence:.2f}, provenance: {alert.provenance.file}#{alert.provenance.section})",
    )

    # JSONL logging
    if "alerts_jsonl" in handlers:
        handlers["alerts_jsonl"].log_alert(alert)

    # Windows Event Log for high-severity alerts
    if alert.severity in ["medium", "high"]:
        python_logger = logging.getLogger("sentinel.windows_events")
        python_logger.error(
            f"Sentinel Alert [{alert.severity.upper()}] {alert.tag}: {alert.rationale}",
        )


def get_log_stats(log_dir: str = "logs") -> dict[str, Any]:
    """Get logging statistics and health information.

    Args:
        log_dir: Directory containing log files.

    Returns:
        Dictionary with logging statistics.
    """
    log_dir_path = Path(log_dir)
    stats: dict[str, Any] = {
        "log_dir": str(log_dir_path.absolute()),
        "log_files": [],
        "total_size_mb": 0.0,
    }

    if log_dir_path.exists():
        for log_file in log_dir_path.glob("*.log*"):
            file_size = log_file.stat().st_size / (1024 * 1024)  # MB
            stats["log_files"].append({
                "name": log_file.name,
                "size_mb": round(file_size, 2),
                "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
            })
            stats["total_size_mb"] += file_size

        stats["total_size_mb"] = round(stats["total_size_mb"], 2)

    return stats
