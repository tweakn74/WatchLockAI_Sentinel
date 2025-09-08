"""Health Monitor implementing health_monitor.md specifications."""

from __future__ import annotations

import asyncio
import contextlib
import time
from typing import TYPE_CHECKING, Any

import psutil
from loguru import logger

from core.schemas import (
    AlertCategory,
    AlertSeverity,
    DetectionAlert,
    HealthMetric,
    ProvenanceInfo,
)

if TYPE_CHECKING:
    from core.bus import EventBus
    from core.config import HealthConfig


def get_cpu_temperature() -> float | None:
    """Get CPU temperature if available.

    Returns:
        CPU temperature in Celsius, or None if not available.
    """
    try:
        # Try to get temperature sensors
        temps = psutil.sensors_temperatures()

        # Look for CPU temperature
        for name, entries in temps.items():
            if "cpu" in name.lower() or "core" in name.lower():
                for entry in entries:
                    return entry.current

        # Fallback: return first available temperature
        for _name, entries in temps.items():
            for entry in entries:
                return entry.current

    except (AttributeError, OSError):
        # Temperature sensors not available on this system
        pass

    return None


class HealthMonitor:
    """Health monitor implementing health_monitor.md specifications."""

    def __init__(self, config: HealthConfig, event_bus: EventBus) -> None:
        """Initialize health monitor.

        Args:
            config: Health monitoring configuration.
            event_bus: Event bus for publishing HealthMetric and DetectionAlert objects.
        """
        self.config = config
        self.event_bus = event_bus
        self._running = False
        self._task: asyncio.Task[None] | None = None

        # Last metrics for threshold checking
        self._last_metrics: HealthMetric | None = None

        logger.info(
            f"HealthMonitor initialized: CPU warn={config.cpu_warn}%, RAM warn={config.ram_warn}%"
        )

    async def start(self) -> None:
        """Start health monitoring."""
        if self._running:
            logger.warning("HealthMonitor already running")
            return

        if not self.config.enabled:
            logger.info("HealthMonitor disabled by configuration")
            return

        self._running = True

        # Start monitoring loop
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("HealthMonitor started")

    async def stop(self) -> None:
        """Stop health monitoring."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

        logger.info("HealthMonitor stopped")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop sampling health metrics."""
        while self._running:
            try:
                # Collect health metrics
                metrics = await self._collect_health_metrics()

                if metrics:
                    # Publish metrics
                    await self.event_bus.publish(metrics)

                    # Check for threshold violations
                    await self._check_thresholds(metrics)

                    # Update last metrics
                    self._last_metrics = metrics

                # Sample every 5 seconds per spec
                await asyncio.sleep(5.0)

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5.0)

    async def _collect_health_metrics(self) -> HealthMetric | None:
        """Collect current health metrics.

        Returns:
            HealthMetric object or None if collection failed.
        """
        try:
            # CPU usage
            cpu_pct = psutil.cpu_percent(interval=1.0)

            # Memory usage
            memory_info = psutil.virtual_memory()
            ram_pct = memory_info.percent

            # Disk usage (use primary disk)
            disk_usage = psutil.disk_usage("/")
            disk_pct_free = (disk_usage.free / disk_usage.total) * 100

            # Temperature (optional)
            temp_c = get_cpu_temperature()

            metrics = HealthMetric(
                cpu_pct=cpu_pct,
                ram_pct=ram_pct,
                disk_pct_free=disk_pct_free,
                temp_c=temp_c,
            )

            logger.debug(
                f"Health metrics: CPU={cpu_pct:.1f}%, RAM={ram_pct:.1f}%, Disk Free={disk_pct_free:.1f}%, Temp={temp_c}°C"
            )
            return metrics

        except Exception as e:
            logger.error(f"Failed to collect health metrics: {e}")
            return None

    async def _check_thresholds(self, metrics: HealthMetric) -> None:
        """Check metrics against configured thresholds and emit alerts.

        Args:
            metrics: Current health metrics.
        """
        alerts: list[DetectionAlert] = []

        # CPU threshold check
        if metrics.cpu_pct > self.config.cpu_warn:
            alerts.append(
                self._create_health_alert(
                    "cpu-high",
                    f"CPU usage is {metrics.cpu_pct:.1f}% (threshold: {self.config.cpu_warn}%)",
                    {"cpu_pct": metrics.cpu_pct, "threshold": self.config.cpu_warn},
                )
            )

        # RAM threshold check
        if metrics.ram_pct > self.config.ram_warn:
            alerts.append(
                self._create_health_alert(
                    "ram-high",
                    f"RAM usage is {metrics.ram_pct:.1f}% (threshold: {self.config.ram_warn}%)",
                    {"ram_pct": metrics.ram_pct, "threshold": self.config.ram_warn},
                )
            )

        # Disk space threshold check
        if metrics.disk_pct_free < self.config.disk_warn_pct_free:
            alerts.append(
                self._create_health_alert(
                    "disk-low",
                    f"Disk free space is {metrics.disk_pct_free:.1f}% (threshold: {self.config.disk_warn_pct_free}%)",
                    {
                        "disk_pct_free": metrics.disk_pct_free,
                        "threshold": self.config.disk_warn_pct_free,
                    },
                    severity=AlertSeverity.MEDIUM,  # Disk space is more critical
                )
            )

        # Temperature threshold check (if configured and available)
        if (
            self.config.temp_warn_c is not None
            and metrics.temp_c is not None
            and metrics.temp_c > self.config.temp_warn_c
        ):
            alerts.append(
                self._create_health_alert(
                    "temp-high",
                    f"CPU temperature is {metrics.temp_c:.1f}°C (threshold: {self.config.temp_warn_c}°C)",
                    {"temp_c": metrics.temp_c, "threshold": self.config.temp_warn_c},
                    severity=AlertSeverity.MEDIUM,  # Temperature is important
                )
            )

        # Publish alerts
        for alert in alerts:
            await self.event_bus.publish(alert)
            logger.warning(f"Health alert: {alert.rationale}")

    def _create_health_alert(
        self,
        tag: str,
        rationale: str,
        entities: dict[str, Any],
        severity: AlertSeverity = AlertSeverity.LOW,
    ) -> DetectionAlert:
        """Create a health-related detection alert.

        Args:
            tag: Alert tag.
            rationale: Human-readable rationale.
            entities: Alert entities dictionary.
            severity: Alert severity level.

        Returns:
            DetectionAlert for the health issue.
        """
        return DetectionAlert(
            severity=severity,
            category=AlertCategory.HEALTH,
            tag=tag,
            entities=entities,
            confidence=1.0,  # Health metrics are definitive
            rationale=rationale,
            provenance=ProvenanceInfo(
                file="health_monitor.md",
                section="healthdegradationcombov1",
                lines="7-12",
            ),
            suggested_actions=[
                "Check system resource usage",
                "Identify processes consuming high resources",
                "Consider system optimization or hardware upgrade",
            ],
        )

    def get_current_metrics(self) -> HealthMetric | None:
        """Get the most recent health metrics.

        Returns:
            Last collected HealthMetric or None if not available.
        """
        return self._last_metrics

    def get_stats(self) -> dict[str, Any]:
        """Get monitoring statistics.

        Returns:
            Dictionary with monitoring statistics.
        """
        stats = {
            "enabled": self.config.enabled,
            "running": self._running,
            "cpu_warn_threshold": self.config.cpu_warn,
            "ram_warn_threshold": self.config.ram_warn,
            "disk_warn_threshold": self.config.disk_warn_pct_free,
            "temp_warn_threshold": self.config.temp_warn_c,
        }

        # Include current metrics if available
        if self._last_metrics:
            stats.update(
                {
                    "current_cpu_pct": self._last_metrics.cpu_pct,
                    "current_ram_pct": self._last_metrics.ram_pct,
                    "current_disk_pct_free": self._last_metrics.disk_pct_free,
                    "current_temp_c": self._last_metrics.temp_c,
                }
            )

        return stats

    def get_system_info(self) -> dict[str, Any]:
        """Get comprehensive system information.

        Returns:
            Dictionary with detailed system information.
        """
        try:
            # CPU info
            cpu_info = {
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            }

            # Memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_info = {
                "total_memory_gb": round(memory.total / (1024**3), 2),
                "available_memory_gb": round(memory.available / (1024**3), 2),
                "memory_percent": memory.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
            }

            # Disk info
            disk_info: list[dict[str, Any]] = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                            "percent_used": round((usage.used / usage.total) * 100, 1),
                        }
                    )
                except PermissionError:
                    continue

            # Boot time
            boot_time = psutil.boot_time()

            return {
                "cpu": cpu_info,
                "memory": memory_info,
                "disks": disk_info,
                "boot_time": boot_time,
                "uptime_seconds": time.time() - boot_time,
            }

        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}
