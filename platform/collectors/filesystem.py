"""File System Monitor implementing fs_monitor.md specifications."""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import math
import os
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING, Any

import psutil
from loguru import logger
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from core.schemas import EventType, FileEvent

if TYPE_CHECKING:
    from core.bus import EventBus
    from core.config import FileSystemConfig


def compute_entropy(data: bytes) -> float:
    """Compute Shannon entropy of data.

    Args:
        data: Byte data to analyze.

    Returns:
        Entropy value between 0.0 and 8.0.
    """
    if not data:
        return 0.0

    # Count byte frequencies
    byte_counts = Counter(data)
    data_len = len(data)

    # Calculate entropy
    entropy = 0.0
    for count in byte_counts.values():
        probability = count / data_len
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return entropy


def compute_file_hash(file_path: Path) -> str | None:
    """Compute SHA-256 hash of file.

    Args:
        file_path: Path to file.

    Returns:
        Hex string of file hash, or None if unable to compute.
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.debug(f"Unable to hash {file_path}: {e}")
        return None


def get_process_for_file(file_path: Path) -> tuple[int | None, str | None]:
    """Best-effort process attribution for file operations on Windows.

    Args:
        file_path: Path to file.

    Returns:
        Tuple of (pid, process_name) or (None, None) if unable to determine.
    """
    try:
        # Get processes with open file handles (best-effort on Windows)
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                # Check if process has files open
                open_files = proc.open_files()
                for open_file in open_files:
                    if Path(open_file.path) == file_path:
                        return proc.info["pid"], proc.info["name"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.debug(f"Process attribution failed for {file_path}: {e}")

    return None, None


class SentinelFileHandler(FileSystemEventHandler):
    """Watchdog event handler implementing fs_monitor.md behavior."""

    def __init__(self, config: FileSystemConfig, event_bus: EventBus) -> None:
        """Initialize file handler.

        Args:
            config: File system monitoring configuration.
            event_bus: Event bus for publishing events.
        """
        super().__init__()
        self.config = config
        self.event_bus = event_bus
        self.exclude_patterns = self._compile_exclude_patterns()
        logger.debug(
            f"FileHandler initialized with {len(self.exclude_patterns)} exclude patterns"
        )

    def _compile_exclude_patterns(self) -> list[str]:
        """Compile exclude glob patterns for faster matching.

        Returns:
            List of compiled patterns.
        """
        return list(self.config.exclude_globs)

    def _should_exclude(self, file_path: str) -> bool:
        """Check if file should be excluded per fs_monitor.md specs.

        Args:
            file_path: Path to check.

        Returns:
            True if file should be excluded.
        """
        import fnmatch

        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def create_file_event(
        self,
        event_type: EventType,
        file_path: str,
        old_path: str | None = None,
    ) -> FileEvent | None:
        """Create FileEvent with optional entropy and hash computation.

        Args:
            event_type: Type of file event.
            file_path: Path to file.
            old_path: Previous path for rename events.

        Returns:
            FileEvent or None if excluded or error.
        """
        # Apply exclude filters before heavy work
        if self._should_exclude(file_path):
            logger.debug(f"Excluded file: {file_path}")
            return None

        path_obj = Path(file_path)

        # Get basic file info
        size_bytes = None
        sha256_hash = None
        entropy = None

        try:
            if path_obj.exists() and path_obj.is_file():
                stat_info = path_obj.stat()
                size_bytes = stat_info.st_size

                # Compute hash and entropy for small files if enabled
                if size_bytes <= self.config.small_file_threshold_bytes:
                    if self.config.compute_hash_small_files:
                        sha256_hash = compute_file_hash(path_obj)

                    if self.config.compute_entropy:
                        try:
                            with open(path_obj, "rb") as f:
                                file_data = f.read()
                            entropy = compute_entropy(file_data)
                        except Exception as e:
                            logger.debug(
                                f"Entropy computation failed for {file_path}: {e}"
                            )

        except Exception as e:
            logger.debug(f"File info gathering failed for {file_path}: {e}")

        # Best-effort process attribution
        proc_pid, proc_name = get_process_for_file(path_obj)

        return FileEvent(
            event_type=event_type,
            path=file_path,
            old_path=old_path,
            size_bytes=size_bytes,
            sha256=sha256_hash,
            entropy=entropy,
            proc_pid=proc_pid,
            proc_name=proc_name,
        )

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            file_event = self.create_file_event(EventType.CREATED, event.src_path)
            if file_event:
                self.event_bus.publish_sync(file_event)
                logger.debug(f"File created: {event.src_path}")

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            file_event = self.create_file_event(EventType.MODIFIED, event.src_path)
            if file_event:
                self.event_bus.publish_sync(file_event)
                logger.debug(f"File modified: {event.src_path}")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        if not event.is_directory:
            file_event = self.create_file_event(EventType.DELETED, event.src_path)
            if file_event:
                self.event_bus.publish_sync(file_event)
                logger.debug(f"File deleted: {event.src_path}")

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file rename/move events with debouncing."""
        if not event.is_directory:
            file_event = self.create_file_event(
                EventType.RENAMED,
                event.dest_path,
                old_path=event.src_path,
            )
            if file_event:
                self.event_bus.publish_sync(file_event)
                logger.debug(f"File renamed: {event.src_path} -> {event.dest_path}")


class PollingFileMonitor:
    """Polling-based file monitor as fallback when watchdog unavailable."""

    def __init__(self, config: FileSystemConfig, event_bus: EventBus) -> None:
        """Initialize polling monitor.

        Args:
            config: File system monitoring configuration.
            event_bus: Event bus for publishing events.
        """
        self.config = config
        self.event_bus = event_bus
        self.handler = SentinelFileHandler(config, event_bus)
        self._file_states: dict[str, float] = {}  # file_path -> mtime
        self._running = False
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start polling monitor."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Polling file monitor started")

    async def stop(self) -> None:
        """Stop polling monitor."""
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        logger.info("Polling file monitor stopped")

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                await self._scan_directories()
                await asyncio.sleep(2.0)  # Poll every 2 seconds
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(5.0)

    async def _scan_directories(self) -> None:
        """Scan monitored directories for changes."""
        current_files: dict[str, float] = {}

        # Scan all monitored paths
        for path_str in self.config.paths:
            expanded_path = os.path.expandvars(path_str)
            path_obj = Path(expanded_path)

            if not path_obj.exists():
                continue

            try:
                # Recursively scan directory
                for file_path in path_obj.rglob("*"):
                    if file_path.is_file():
                        try:
                            mtime = file_path.stat().st_mtime
                            file_str = str(file_path)
                            current_files[file_str] = mtime

                            # Check for new or modified files
                            if file_str in self._file_states:
                                if mtime > self._file_states[file_str]:
                                    # File modified
                                    file_event = self.handler.create_file_event(
                                        EventType.MODIFIED,
                                        file_str,
                                    )
                                    if file_event:
                                        await self.event_bus.publish(file_event)
                            else:
                                # New file
                                file_event = self.handler.create_file_event(
                                    EventType.CREATED,
                                    file_str,
                                )
                                if file_event:
                                    await self.event_bus.publish(file_event)

                        except Exception as e:
                            logger.debug(f"Error processing {file_path}: {e}")

            except Exception as e:
                logger.warning(f"Error scanning {path_obj}: {e}")

        # Check for deleted files
        for file_str in set(self._file_states.keys()) - set(current_files.keys()):
            file_event = self.handler.create_file_event(EventType.DELETED, file_str)
            if file_event:
                await self.event_bus.publish(file_event)

        # Update state
        self._file_states = current_files


class FileSystemMonitor:
    """Main file system monitor implementing fs_monitor.md specifications."""

    def __init__(self, config: FileSystemConfig, event_bus: EventBus) -> None:
        """Initialize file system monitor.

        Args:
            config: File system monitoring configuration.
            event_bus: Event bus for publishing FileEvent objects.
        """
        self.config = config
        self.event_bus = event_bus
        self.observer: Any = None
        self.polling_monitor: PollingFileMonitor | None = None
        self._running = False

        logger.info(
            f"FileSystemMonitor initialized: method={config.method}, paths={len(config.paths)}"
        )

    async def start(self) -> None:
        """Start file system monitoring per configuration."""
        if self._running:
            logger.warning("FileSystemMonitor already running")
            return

        if not self.config.enabled:
            logger.info("FileSystemMonitor disabled by configuration")
            return

        self._running = True

        try:
            if self.config.method == "watchdog":
                await self._start_watchdog()
            else:
                await self._start_polling()
        except Exception as e:
            logger.error(f"Failed to start file monitoring: {e}")
            # Fallback to polling
            if self.config.method == "watchdog":
                logger.info("Falling back to polling mode")
                await self._start_polling()

    async def _start_watchdog(self) -> None:
        """Start watchdog-based monitoring."""
        from watchdog.observers import Observer

        self.observer = Observer()
        handler = SentinelFileHandler(self.config, self.event_bus)

        # Add watches for all configured paths
        assert self.observer is not None  # Help type checker
        for path_str in self.config.paths:
            expanded_path = os.path.expandvars(path_str)
            path_obj = Path(expanded_path)

            if path_obj.exists():
                self.observer.schedule(handler, str(path_obj), recursive=True)
                logger.info(f"Watching directory: {expanded_path}")
            else:
                logger.warning(f"Monitored path does not exist: {expanded_path}")

        self.observer.start()
        logger.info("Watchdog file monitor started")

    async def _start_polling(self) -> None:
        """Start polling-based monitoring."""
        self.polling_monitor = PollingFileMonitor(self.config, self.event_bus)
        await self.polling_monitor.start()

    async def stop(self) -> None:
        """Stop file system monitoring."""
        if not self._running:
            return

        self._running = False

        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Watchdog file monitor stopped")

        if self.polling_monitor:
            await self.polling_monitor.stop()
            self.polling_monitor = None

        logger.info("FileSystemMonitor stopped")

    def get_stats(self) -> dict[str, Any]:
        """Get monitoring statistics.

        Returns:
            Dictionary with monitoring statistics.
        """
        stats = {
            "enabled": self.config.enabled,
            "running": self._running,
            "method": self.config.method,
            "monitored_paths": len(self.config.paths),
            "exclude_patterns": len(self.config.exclude_globs),
            "compute_entropy": self.config.compute_entropy,
            "compute_hash": self.config.compute_hash_small_files,
        }

        # Add method-specific stats
        if self.observer:
            stats["watchdog_watches"] = (
                len(self.observer.watches) if hasattr(self.observer, "watches") else 0
            )

        return stats
