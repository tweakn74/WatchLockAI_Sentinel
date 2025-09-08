"""Process Monitor implementing process_monitor.md specifications."""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import psutil
from loguru import logger

from core.schemas import ProcessEvent, ProcessEventType

if TYPE_CHECKING:
    from core.bus import EventBus
    from core.config import ProcessConfig


def compute_executable_hash(exe_path: str, max_size_mb: int = 64) -> str | None:
    """Compute SHA-256 hash of executable file if size is reasonable.

    Args:
        exe_path: Path to executable.
        max_size_mb: Maximum file size in MB to hash.

    Returns:
        Hex string of file hash, or None if unable to compute or too large.
    """
    try:
        path_obj = Path(exe_path)
        if not path_obj.exists():
            return None

        # Check file size
        size_mb = path_obj.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            logger.debug(f"Executable too large to hash: {exe_path} ({size_mb:.1f}MB)")
            return None

        hasher = hashlib.sha256()
        with open(path_obj, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    except Exception as e:
        logger.debug(f"Failed to hash executable {exe_path}: {e}")
        return None


class ProcessMonitor:
    """Process monitor implementing process_monitor.md specifications."""

    def __init__(self, config: ProcessConfig, event_bus: EventBus) -> None:
        """Initialize process monitor.

        Args:
            config: Process monitoring configuration.
            event_bus: Event bus for publishing ProcessEvent objects.
        """
        self.config = config
        self.event_bus = event_bus
        self._running = False
        self._task: asyncio.Task[None] | None = None

        # Process tracking for ancestry and lifecycle
        self._known_pids: set[int] = set()
        self._pid_to_ppid: dict[int, int] = {}  # PID -> PPID mapping
        self._pid_start_times: dict[int, str] = {}  # PID -> start timestamp

        logger.info(
            f"ProcessMonitor initialized: poll_interval={config.poll_interval_ms}ms"
        )

    async def start(self) -> None:
        """Start process monitoring."""
        if self._running:
            logger.warning("ProcessMonitor already running")
            return

        if not self.config.enabled:
            logger.info("ProcessMonitor disabled by configuration")
            return

        self._running = True

        # Initialize with current processes
        await self._initialize_process_state()

        # Start monitoring loop
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("ProcessMonitor started")

    async def stop(self) -> None:
        """Stop process monitoring."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

        logger.info("ProcessMonitor stopped")

    async def _initialize_process_state(self) -> None:
        """Initialize tracking state with currently running processes."""
        try:
            current_pids: set[int] = set()

            for proc in psutil.process_iter(["pid", "ppid", "create_time"]):
                try:
                    pid = proc.info["pid"]
                    ppid = proc.info["ppid"]
                    create_time = proc.info["create_time"]

                    current_pids.add(pid)
                    self._pid_to_ppid[pid] = ppid if ppid else 0

                    # Convert create_time to ISO timestamp
                    start_ts = datetime.fromtimestamp(
                        create_time, timezone.utc
                    ).isoformat()
                    self._pid_start_times[pid] = start_ts

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            self._known_pids = current_pids
            logger.debug(f"Initialized with {len(current_pids)} existing processes")

        except Exception as e:
            logger.error(f"Failed to initialize process state: {e}")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop checking for process changes."""
        while self._running:
            try:
                await self._check_process_changes()

                # Sleep based on configured interval
                sleep_time = self.config.poll_interval_ms / 1000.0
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Process monitoring error: {e}")
                await asyncio.sleep(1.0)  # Brief pause on error

    async def _check_process_changes(self) -> None:
        """Check for new/exited processes and emit events."""
        try:
            current_pids: set[int] = set()
            new_processes: list[tuple[Any, dict[str, Any]]] = []

            # Scan current processes
            for proc in psutil.process_iter(
                ["pid", "ppid", "exe", "cmdline", "username", "create_time"]
            ):
                try:
                    info = proc.info
                    pid = info["pid"]
                    current_pids.add(pid)

                    # Check for new process
                    if pid not in self._known_pids:
                        new_processes.append((proc, info))

                        # Update tracking
                        ppid = info["ppid"] if info["ppid"] else 0
                        self._pid_to_ppid[pid] = ppid

                        create_time = info["create_time"]
                        start_ts = datetime.fromtimestamp(
                            create_time, timezone.utc
                        ).isoformat()
                        self._pid_start_times[pid] = start_ts

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Handle new processes
            for proc, info in new_processes:
                await self._handle_process_start(proc, info)

            # Handle exited processes
            exited_pids = self._known_pids - current_pids
            for pid in exited_pids:
                await self._handle_process_exit(pid)

            # Update known PIDs
            self._known_pids = current_pids

        except Exception as e:
            logger.error(f"Error checking process changes: {e}")

    async def _handle_process_start(
        self, proc: psutil.Process, info: dict[str, Any]
    ) -> None:
        """Handle process start event.

        Args:
            proc: psutil Process object.
            info: Process information dictionary.
        """
        try:
            pid = info["pid"]
            ppid = info["ppid"] if info["ppid"] else None
            exe = info.get("exe")
            cmdline_list = info.get("cmdline", [])
            username = info.get("username")

            # Format command line
            cmdline = " ".join(cmdline_list) if cmdline_list else None

            # Compute executable hash if enabled and exe available
            exe_hash = None
            if self.config.capture_hash and exe:
                exe_hash = compute_executable_hash(exe)

            # Get start timestamp
            start_ts = self._pid_start_times.get(pid)

            # Create and publish event
            event = ProcessEvent(
                event_type=ProcessEventType.STARTED,
                pid=pid,
                ppid=ppid,
                exe=exe,
                cmdline=cmdline,
                username=username,
                hash_sha256=exe_hash,
                start_ts=start_ts,
                end_ts=None,
            )

            await self.event_bus.publish(event)
            logger.debug(f"Process started: PID={pid}, exe={exe}")

        except Exception as e:
            logger.warning(
                f"Error handling process start for PID {info.get('pid')}: {e}"
            )

    async def _handle_process_exit(self, pid: int) -> None:
        """Handle process exit event.

        Args:
            pid: Process ID that exited.
        """
        try:
            # Get stored information
            ppid = self._pid_to_ppid.get(pid)
            start_ts = self._pid_start_times.get(pid)
            end_ts = datetime.now(timezone.utc).isoformat()

            # Create and publish event
            event = ProcessEvent(
                event_type=ProcessEventType.EXITED,
                pid=pid,
                ppid=ppid,
                exe=None,  # Not available after exit
                cmdline=None,
                username=None,
                hash_sha256=None,
                start_ts=start_ts,
                end_ts=end_ts,
            )

            await self.event_bus.publish(event)
            logger.debug(f"Process exited: PID={pid}")

            # Clean up tracking data
            self._pid_to_ppid.pop(pid, None)
            self._pid_start_times.pop(pid, None)

        except Exception as e:
            logger.warning(f"Error handling process exit for PID {pid}: {e}")

    def get_process_ancestry(self, pid: int, max_depth: int = 10) -> list[int]:
        """Get process ancestry chain.

        Args:
            pid: Process ID to trace.
            max_depth: Maximum ancestry depth to trace.

        Returns:
            List of PIDs from child to ultimate parent.
        """
        ancestry = [pid]
        current_pid = pid

        for _ in range(max_depth):
            ppid = self._pid_to_ppid.get(current_pid)
            if not ppid or ppid in (0, current_pid):
                break

            ancestry.append(ppid)
            current_pid = ppid

            # Avoid infinite loops
            if ppid in ancestry[:-1]:
                break

        return ancestry

    def is_child_of(self, child_pid: int, parent_pid: int) -> bool:
        """Check if one process is a child of another.

        Args:
            child_pid: Potential child process ID.
            parent_pid: Potential parent process ID.

        Returns:
            True if child_pid is a descendant of parent_pid.
        """
        ancestry = self.get_process_ancestry(child_pid)
        return parent_pid in ancestry

    def get_stats(self) -> dict[str, Any]:
        """Get monitoring statistics.

        Returns:
            Dictionary with monitoring statistics.
        """
        return {
            "enabled": self.config.enabled,
            "running": self._running,
            "poll_interval_ms": self.config.poll_interval_ms,
            "capture_hash": self.config.capture_hash,
            "tracked_processes": len(self._known_pids),
            "ancestry_mappings": len(self._pid_to_ppid),
        }

    def get_process_info(self, pid: int) -> dict[str, Any] | None:
        """Get stored information about a process.

        Args:
            pid: Process ID.

        Returns:
            Dictionary with process information, or None if not tracked.
        """
        if pid not in self._known_pids:
            return None

        return {
            "pid": pid,
            "ppid": self._pid_to_ppid.get(pid),
            "start_ts": self._pid_start_times.get(pid),
            "ancestry": self.get_process_ancestry(pid),
        }
