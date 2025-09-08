"""Alerts system implementing alerts.md specifications."""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    logger.warning("Toast notifications not available (plyer not installed)")
    NOTIFICATIONS_AVAILABLE = False

from app_core.schemas import DetectionAlert

if TYPE_CHECKING:
    from app_core.bus import EventBus, EventSubscription
    from app_core.config import AlertsConfig


class ToastNotificationHandler:
    """Windows toast notification handler using plyer."""

    def __init__(self, enabled: bool = True) -> None:
        """Initialize toast notification handler.

        Args:
            enabled: Whether toast notifications are enabled.
        """
        self.enabled = enabled and NOTIFICATIONS_AVAILABLE

        if not NOTIFICATIONS_AVAILABLE:
            logger.warning("Toast notifications disabled: plyer not available")
        elif not enabled:
            logger.info("Toast notifications disabled by configuration")
        else:
            logger.info("Toast notifications enabled")

    async def send_notification(self, alert: DetectionAlert) -> bool:
        """Send toast notification for alert.

        Args:
            alert: Detection alert to notify about.

        Returns:
            True if notification was sent successfully.
        """
        if not self.enabled:
            return False

        try:
            # Format notification content
            title = f"Sentinel Alert [{alert.severity.upper()}]"
            message = f"{alert.tag}: {alert.rationale}"

            # Truncate long messages
            if len(message) > 100:
                message = message[:97] + "..."

            # Send notification
            notification.notify(
                title=title,
                message=message,
                app_name="WatchLockAI Sentinel",
                timeout=10,  # 10 seconds
            )

            logger.debug(f"Toast notification sent: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send toast notification: {e}")
            return False


class JSONLAlertLogger:
    """JSONL alert logger for persistent storage."""

    def __init__(self, log_path: str) -> None:
        """Initialize JSONL alert logger.

        Args:
            log_path: Path to JSONL log file.
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"JSONL alert logging to: {self.log_path}")

    async def log_alert(self, alert: DetectionAlert) -> bool:
        """Log alert to JSONL file.

        Args:
            alert: Detection alert to log.

        Returns:
            True if logging was successful.
        """
        try:
            # Prepare alert data
            alert_data = alert.model_dump()
            alert_data["logged_at"] = datetime.now(timezone.utc).isoformat()

            # Write to JSONL file
            with open(self.log_path, "a", encoding="utf-8") as f:
                json.dump(alert_data, f, ensure_ascii=False)
                f.write("\n")

            logger.debug(f"Alert logged to JSONL: {alert.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to log alert to JSONL: {e}")
            return False

    def get_recent_alerts(self, count: int = 10) -> list[dict[str, Any]]:
        """Get recent alerts from JSONL log.

        Args:
            count: Number of recent alerts to retrieve.

        Returns:
            List of recent alert dictionaries.
        """
        alerts = []

        try:
            if not self.log_path.exists():
                return alerts

            # Read last N lines efficiently
            with open(self.log_path, encoding="utf-8") as f:
                lines = deque(f, maxlen=count)

            # Parse JSONL
            for line in lines:
                line = line.strip()
                if line:
                    try:
                        alert_data = json.loads(line)
                        alerts.append(alert_data)
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            logger.error(f"Failed to read recent alerts: {e}")

        return alerts


class TrayAlertBuffer:
    """In-memory buffer for tray UI alert display."""

    def __init__(self, max_alerts: int = 10) -> None:
        """Initialize tray alert buffer.

        Args:
            max_alerts: Maximum number of alerts to keep in memory.
        """
        self.max_alerts = max_alerts
        self.alerts: deque[DetectionAlert] = deque(maxlen=max_alerts)

        logger.debug(f"Tray alert buffer initialized: max_alerts={max_alerts}")

    def add_alert(self, alert: DetectionAlert) -> None:
        """Add alert to tray buffer.

        Args:
            alert: Detection alert to add.
        """
        self.alerts.append(alert)
        logger.debug(f"Alert added to tray buffer: {alert.id}")

    def get_alerts(self) -> list[DetectionAlert]:
        """Get all alerts in tray buffer.

        Returns:
            List of alerts in chronological order (oldest first).
        """
        return list(self.alerts)

    def get_recent_alerts(self, count: int = 5) -> list[DetectionAlert]:
        """Get most recent alerts.

        Args:
            count: Number of recent alerts to get.

        Returns:
            List of most recent alerts.
        """
        return list(self.alerts)[-count:]

    def clear(self) -> None:
        """Clear all alerts from buffer."""
        self.alerts.clear()
        logger.debug("Tray alert buffer cleared")


class AlertManager:
    """Main alert manager implementing alerts.md specifications."""

    def __init__(self, config: AlertsConfig, event_bus: EventBus) -> None:
        """Initialize alert manager.

        Args:
            config: Alerts configuration.
            event_bus: Event bus for subscribing to DetectionAlert events.
        """
        self.config = config
        self.event_bus = event_bus

        # Initialize handlers
        self.toast_handler = ToastNotificationHandler(config.toast_notifications)
        self.jsonl_logger = JSONLAlertLogger(config.log_jsonl)
        self.tray_buffer = TrayAlertBuffer()

        # Subscription tracking
        self._subscription: EventSubscription | None = None
        self._running = False

        # Statistics
        self._stats = {
            "alerts_processed": 0,
            "toast_notifications_sent": 0,
            "jsonl_logs_written": 0,
            "started_at": None,
        }

        logger.info(f"AlertManager initialized: toast={config.toast_notifications}, jsonl={config.log_jsonl}")

    async def start(self) -> None:
        """Start alert manager by subscribing to DetectionAlert events."""
        if self._running:
            logger.warning("AlertManager already running")
            return

        self._running = True
        self._stats["started_at"] = datetime.now(timezone.utc).isoformat()

        # Subscribe to detection alerts
        self._subscription = self.event_bus.subscribe(
            DetectionAlert,
            self._handle_alert,
            "AlertManager",
        )

        logger.info("AlertManager started and subscribed to alerts")

    async def stop(self) -> None:
        """Stop alert manager by unsubscribing from events."""
        if not self._running:
            return

        self._running = False

        if self._subscription:
            self.event_bus.unsubscribe(self._subscription)
            self._subscription = None

        logger.info("AlertManager stopped")

    async def _handle_alert(self, alert: DetectionAlert) -> None:
        """Handle incoming detection alert.

        Args:
            alert: Detection alert to process.
        """
        try:
            logger.info(f"Processing alert: {alert.id} [{alert.severity.upper()}] {alert.tag}")

            # Update statistics
            self._stats["alerts_processed"] += 1

            # Add to tray buffer
            self.tray_buffer.add_alert(alert)

            # Send toast notification
            if self.config.toast_notifications:
                success = await self.toast_handler.send_notification(alert)
                if success:
                    self._stats["toast_notifications_sent"] += 1

            # Log to JSONL
            success = await self.jsonl_logger.log_alert(alert)
            if success:
                self._stats["jsonl_logs_written"] += 1

            # Log alert details
            logger.warning(
                f"ALERT [{alert.severity.upper()}] {alert.tag}: {alert.rationale} "
                f"(confidence: {alert.confidence:.2f}, source: {alert.provenance.file}#{alert.provenance.section})",
            )

            # Log suggested actions
            if alert.suggested_actions:
                logger.info(f"Suggested actions for {alert.id}: {', '.join(alert.suggested_actions)}")

        except Exception as e:
            logger.error(f"Error processing alert {alert.id}: {e}")

    def get_tray_alerts(self) -> list[DetectionAlert]:
        """Get alerts for tray UI display.

        Returns:
            List of recent alerts for tray display.
        """
        return self.tray_buffer.get_alerts()

    def get_recent_alerts_from_log(self, count: int = 10) -> list[dict[str, Any]]:
        """Get recent alerts from persistent log.

        Args:
            count: Number of recent alerts to retrieve.

        Returns:
            List of recent alert dictionaries from JSONL log.
        """
        return self.jsonl_logger.get_recent_alerts(count)

    def clear_tray_alerts(self) -> None:
        """Clear alerts from tray buffer."""
        self.tray_buffer.clear()
        logger.info("Tray alerts cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get alert manager statistics.

        Returns:
            Dictionary with alert statistics.
        """
        stats = self._stats.copy()
        stats.update({
            "running": self._running,
            "tray_buffer_size": len(self.tray_buffer.alerts),
            "config": {
                "toast_notifications": self.config.toast_notifications,
                "log_jsonl": self.config.log_jsonl,
            },
        })

        return stats

    def get_alert_summary(self) -> dict[str, Any]:
        """Get summary of recent alert activity.

        Returns:
            Dictionary with alert activity summary.
        """
        tray_alerts = self.get_tray_alerts()

        # Count by severity
        severity_counts = {"low": 0, "medium": 0, "high": 0}
        category_counts = {}

        for alert in tray_alerts:
            severity_counts[alert.severity] += 1
            category_counts[alert.category] = category_counts.get(alert.category, 0) + 1

        return {
            "total_alerts": len(tray_alerts),
            "by_severity": severity_counts,
            "by_category": category_counts,
            "most_recent": tray_alerts[-1].model_dump() if tray_alerts else None,
        }

    async def test_notification(self) -> bool:
        """Send a test notification to verify functionality.

        Returns:
            True if test notification was sent successfully.
        """
        if not self.config.toast_notifications:
            logger.warning("Cannot send test notification: toast notifications disabled")
            return False

        # Create test alert
        from app_core.schemas import AlertCategory, AlertSeverity, ProvenanceInfo

        test_alert = DetectionAlert(
            severity=AlertSeverity.LOW,
            category=AlertCategory.GENERAL,
            tag="test-notification",
            entities={"test": True},
            confidence=1.0,
            rationale="This is a test notification from WatchLockAI Sentinel.",
            provenance=ProvenanceInfo(
                file="alerts.py",
                section="test",
                lines="N/A",
            ),
            suggested_actions=["Verify notification system is working"],
        )

        success = await self.toast_handler.send_notification(test_alert)

        if success:
            logger.info("Test notification sent successfully")
        else:
            logger.error("Failed to send test notification")

        return success
