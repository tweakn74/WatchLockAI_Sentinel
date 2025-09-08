"""Registry Monitor implementing registry_monitor.md specifications (Windows only)."""

from __future__ import annotations

import asyncio
import contextlib
import sys
import time
from typing import TYPE_CHECKING, Any

from loguru import logger

from core.schemas import RegistryEvent, RegistryEventType, RegistryHive

if TYPE_CHECKING:
    from core.bus import EventBus
    from core.config import RegistryConfig

# Platform check: Registry monitoring only available on Windows
IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    try:
        import winreg  # type: ignore[import-untyped]

        _windows_available = True
    except ImportError:
        logger.warning("Windows registry APIs not available (pywin32 not installed)")
        _windows_available = False
        winreg = None  # type: ignore
else:
    logger.info("Registry monitoring not available on non-Windows platforms")
    _windows_available = False
    winreg = None  # type: ignore

WINDOWS_AVAILABLE = _windows_available and IS_WINDOWS


def parse_registry_key(key_path: str) -> tuple[RegistryHive, str]:
    r"""Parse registry key path into hive and subkey.

    Args:
        key_path: Full registry key path (e.g., "HKCU\\Software\\...").

    Returns:
        Tuple of (hive, subkey_path).

    Raises:
        ValueError: If key path format is invalid.
    """
    parts = key_path.split("\\", 1)
    if len(parts) != 2:
        msg = f"Invalid registry key path: {key_path}"
        raise ValueError(msg)

    hive_str, subkey = parts

    # Map string to RegistryHive enum
    hive_mapping = {
        "HKCU": RegistryHive.HKCU,
        "HKLM": RegistryHive.HKLM,
        "HKU": RegistryHive.HKU,
        "HKCR": RegistryHive.HKCR,
    }

    if hive_str not in hive_mapping:
        msg = f"Unsupported registry hive: {hive_str}"
        raise ValueError(msg)

    return hive_mapping[hive_str], subkey


def get_winreg_hive(hive: RegistryHive) -> int:
    """Get winreg hive constant from RegistryHive enum.

    Args:
        hive: Registry hive enum.

    Returns:
        winreg hive constant.
    """
    if not WINDOWS_AVAILABLE:
        msg = "Windows registry not available"
        raise RuntimeError(msg)

    mapping: dict[RegistryHive, int] = {
        RegistryHive.HKCU: winreg.HKEY_CURRENT_USER,  # type: ignore[union-attr]
        RegistryHive.HKLM: winreg.HKEY_LOCAL_MACHINE,  # type: ignore[union-attr]
        RegistryHive.HKU: winreg.HKEY_USERS,  # type: ignore[union-attr]
        RegistryHive.HKCR: winreg.HKEY_CLASSES_ROOT,  # type: ignore[union-attr]
    }

    return mapping[hive]


def get_registry_value_info(
    hive: RegistryHive, subkey: str, value_name: str
) -> tuple[str | None, str | None]:
    """Get registry value type and data preview.

    Args:
        hive: Registry hive.
        subkey: Subkey path.
        value_name: Value name.

    Returns:
        Tuple of (value_type, data_preview).
    """
    if not WINDOWS_AVAILABLE:
        return None, None

    try:
        hive_key = get_winreg_hive(hive)

        with winreg.OpenKey(hive_key, subkey, 0, winreg.KEY_READ) as key:  # type: ignore[union-attr]
            value_data, value_type = winreg.QueryValueEx(key, value_name)  # type: ignore[union-attr]

            # Map type to string
            type_mapping: dict[int, str] = {
                winreg.REG_SZ: "REG_SZ",  # type: ignore[union-attr]
                winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ",  # type: ignore[union-attr]
                winreg.REG_BINARY: "REG_BINARY",  # type: ignore[union-attr]
                winreg.REG_DWORD: "REG_DWORD",  # type: ignore[union-attr]
                winreg.REG_DWORD_BIG_ENDIAN: "REG_DWORD_BIG_ENDIAN",  # type: ignore[union-attr]
                winreg.REG_MULTI_SZ: "REG_MULTI_SZ",  # type: ignore[union-attr]
                winreg.REG_QWORD: "REG_QWORD",  # type: ignore[union-attr]
            }

            type_str: str = type_mapping.get(value_type, f"TYPE_{value_type}")  # type: ignore[arg-type]

            # Create data preview (truncate to 200 chars as per specs)
            data_preview: str
            if isinstance(value_data, str):
                data_preview = value_data[:200]
            elif isinstance(value_data, bytes):
                data_preview = value_data.hex()[:200]
            elif isinstance(value_data, list):
                data_preview = str(value_data)[:200]  # type: ignore[arg-type]
            else:
                data_preview = str(value_data)[:200]  # type: ignore[arg-type]

            return type_str, data_preview

    except Exception as e:
        logger.debug(
            f"Failed to get registry value info for {hive.value}\\{subkey}\\{value_name}: {e}"
        )
        return None, None


class RegistrySnapshot:
    """Snapshot of registry key state for change detection."""

    def __init__(self, hive: RegistryHive, subkey: str) -> None:
        """Initialize registry snapshot.

        Args:
            hive: Registry hive.
            subkey: Subkey path.
        """
        self.hive = hive
        self.subkey = subkey
        self.values: dict[str, tuple[Any, int]] = {}  # value_name -> (data, type)
        self.last_updated = time.time()

        self._capture_state()

    def _capture_state(self) -> None:
        """Capture current registry key state."""
        if not WINDOWS_AVAILABLE:
            return

        try:
            hive_key = get_winreg_hive(self.hive)

            with winreg.OpenKey(hive_key, self.subkey, 0, winreg.KEY_READ) as key:  # type: ignore[union-attr]
                # Enumerate all values
                index = 0
                while True:
                    try:
                        value_name, value_data, value_type = winreg.EnumValue(
                            key, index
                        )  # type: ignore[union-attr]
                        self.values[value_name] = (value_data, value_type)
                        index += 1
                    except OSError:
                        break  # No more values

        except Exception as e:
            logger.debug(
                f"Failed to capture registry state for {self.hive.value}\\{self.subkey}: {e}"
            )

    def get_changes(self) -> list[tuple[RegistryEventType, str]]:
        """Get changes since last update.

        Returns:
            List of (event_type, value_name) tuples.
        """
        if not WINDOWS_AVAILABLE:
            return []

        changes: list[tuple[RegistryEventType, str]] = []

        try:
            # Capture new state
            new_values: dict[str, tuple[Any, Any]] = {}
            hive_key = get_winreg_hive(self.hive)

            with winreg.OpenKey(hive_key, self.subkey, 0, winreg.KEY_READ) as key:  # type: ignore[union-attr]
                index = 0
                while True:
                    try:
                        value_name, value_data, value_type = winreg.EnumValue(
                            key, index
                        )  # type: ignore[union-attr]
                        new_values[value_name] = (value_data, value_type)
                        index += 1
                    except OSError:
                        break

            # Compare states
            old_names: set[str] = set(self.values.keys())
            new_names: set[str] = set(new_values.keys())

            # Detect deletions
            for value_name in old_names - new_names:
                changes.append((RegistryEventType.DELETED, value_name))

            # Detect additions
            for value_name in new_names - old_names:
                changes.append((RegistryEventType.CREATED, value_name))

            # Detect modifications
            for value_name in old_names & new_names:
                old_data: Any
                old_type: Any
                old_data, old_type = self.values[value_name]
                new_data: Any
                new_type: Any
                new_data, new_type = new_values[value_name]

                if old_data != new_data or old_type != new_type:
                    changes.append((RegistryEventType.MODIFIED, value_name))

            # Update state
            self.values = new_values
            self.last_updated = time.time()

        except Exception as e:
            logger.warning(
                f"Error detecting registry changes for {self.hive.value}\\{self.subkey}: {e}"
            )

        return changes


class RegistryNotificationMonitor:
    """Registry monitor using Windows notification APIs when available."""

    def __init__(self, hive: RegistryHive, subkey: str, event_bus: EventBus) -> None:
        """Initialize notification monitor.

        Args:
            hive: Registry hive to monitor.
            subkey: Subkey path to monitor.
            event_bus: Event bus for publishing events.
        """
        self.hive = hive
        self.subkey = subkey
        self.event_bus = event_bus
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._snapshot = RegistrySnapshot(hive, subkey)

    async def start(self) -> None:
        """Start notification monitoring."""
        if self._running:
            return

        self._running = True

        if WINDOWS_AVAILABLE:
            try:
                self._task = asyncio.create_task(self._notification_loop())
                logger.debug(
                    f"Started registry notification monitor for {self.hive.value}\\{self.subkey}"
                )
                return
            except Exception as e:
                logger.warning(
                    f"Failed to start registry notifications, falling back to polling: {e}"
                )

        # Fallback to polling
        self._task = asyncio.create_task(self._polling_loop())
        logger.debug(
            f"Started registry polling monitor for {self.hive.value}\\{self.subkey}"
        )

    async def stop(self) -> None:
        """Stop monitoring."""
        self._running = False

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _notification_loop(self) -> None:
        """Notification-based monitoring loop."""
        # Note: This is a simplified implementation
        # Full Windows registry notifications require complex Win32 API usage
        # For now, we'll use polling as a reliable fallback
        await self._polling_loop()

    async def _polling_loop(self) -> None:
        """Polling-based monitoring loop."""
        while self._running:
            try:
                changes = self._snapshot.get_changes()

                for event_type, value_name in changes:
                    await self._emit_registry_event(event_type, value_name)

                await asyncio.sleep(2.0)  # Poll every 2 seconds

            except Exception as e:
                logger.error(f"Registry polling error: {e}")
                await asyncio.sleep(5.0)

    async def _emit_registry_event(
        self, event_type: RegistryEventType, value_name: str
    ) -> None:
        """Emit registry event.

        Args:
            event_type: Type of registry event.
            value_name: Name of the value that changed.
        """
        try:
            # Get value type and data preview
            value_type, data_preview = get_registry_value_info(
                self.hive, self.subkey, value_name
            )

            # Create event
            event = RegistryEvent(
                event_type=event_type,
                hive=self.hive,
                key_path=self.subkey,
                value_name=value_name,
                value_type=value_type,
                data_preview=data_preview,
                proc_pid=None,  # Best-effort process attribution not implemented
                proc_name=None,
            )

            await self.event_bus.publish(event)
            logger.debug(
                f"Registry event: {event_type.value} {self.hive.value}\\{self.subkey}\\{value_name}"
            )

        except Exception as e:
            logger.warning(f"Error emitting registry event: {e}")


class RegistryMonitor:
    """Main registry monitor implementing registry_monitor.md specifications."""

    def __init__(self, config: RegistryConfig, event_bus: EventBus) -> None:
        """Initialize registry monitor.

        Args:
            config: Registry monitoring configuration.
            event_bus: Event bus for publishing RegistryEvent objects.
        """
        self.config = config
        self.event_bus = event_bus
        self._running = False
        self._monitors: list[RegistryNotificationMonitor] = []

        logger.info(
            f"RegistryMonitor initialized: method={config.method}, keys={len(config.watch_keys)}"
        )

        if not WINDOWS_AVAILABLE:
            logger.warning("Registry monitoring limited: Windows APIs not available")

    async def start(self) -> None:
        """Start registry monitoring."""
        if self._running:
            logger.warning("RegistryMonitor already running")
            return

        if not self.config.enabled:
            logger.info("RegistryMonitor disabled by configuration")
            return

        if not WINDOWS_AVAILABLE:
            logger.error("Cannot start registry monitoring: Windows APIs not available")
            return

        self._running = True

        # Create monitors for each configured key
        for key_path in self.config.watch_keys:
            try:
                hive, subkey = parse_registry_key(key_path)
                monitor = RegistryNotificationMonitor(hive, subkey, self.event_bus)
                self._monitors.append(monitor)
                await monitor.start()
                logger.info(f"Monitoring registry key: {key_path}")

            except Exception as e:
                logger.error(f"Failed to monitor registry key {key_path}: {e}")

        logger.info(
            f"RegistryMonitor started with {len(self._monitors)} active monitors"
        )

    async def stop(self) -> None:
        """Stop registry monitoring."""
        if not IS_WINDOWS:
            logger.info("Registry monitoring stop: no-op on non-Windows platform")
            return

        if not self._running:
            return

        self._running = False

        # Stop all monitors
        for monitor in self._monitors:
            await monitor.stop()

        self._monitors.clear()
        logger.info("RegistryMonitor stopped")

    def get_stats(self) -> dict[str, Any]:
        """Get monitoring statistics.

        Returns:
            Dictionary with monitoring statistics.
        """
        return {
            "enabled": self.config.enabled,
            "running": self._running,
            "method": self.config.method if IS_WINDOWS else "disabled",
            "watch_keys": len(self.config.watch_keys),
            "active_monitors": len(self._monitors),
            "windows_available": WINDOWS_AVAILABLE,
            "platform_supported": IS_WINDOWS,
        }
