"""System tray application for WatchLockAI Sentinel."""

from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    logger.warning("System tray not available (pystray/PIL not installed)")
    TRAY_AVAILABLE = False


if TYPE_CHECKING:
    from response.actions import ResponseActionsManager
    from response.alerts import AlertManager


def create_default_icon(size: int = 64) -> Image.Image | None:
    """Create a default icon for the tray application.

    Args:
        size: Icon size in pixels.

    Returns:
        PIL Image object or None if PIL not available.
    """
    if not TRAY_AVAILABLE:
        return None

    try:
        # Create a simple shield icon
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw shield shape
        padding = size // 8
        shield_points = [
            (size // 2, padding),  # Top
            (size - padding, padding + size // 4),  # Top right
            (size - padding, size - padding - size // 4),  # Bottom right
            (size // 2, size - padding),  # Bottom
            (padding, size - padding - size // 4),  # Bottom left
            (padding, padding + size // 4),  # Top left
        ]

        # Fill shield
        draw.polygon(shield_points, fill=(70, 130, 180, 255))

        # Draw border
        draw.polygon(shield_points, outline=(25, 25, 112, 255), width=2)

        # Add "S" for Sentinel
        size // 3
        text_bbox = draw.textbbox((0, 0), "S")
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2

        draw.text((text_x, text_y), "S", fill=(255, 255, 255, 255))

        return image

    except Exception as e:
        logger.error(f"Failed to create default icon: {e}")
        return None


class TrayApplication:
    """System tray application for Sentinel monitoring and control."""

    def __init__(
        self,
        alert_manager: AlertManager | None = None,
        actions_manager: ResponseActionsManager | None = None,
    ) -> None:
        """Initialize tray application.

        Args:
            alert_manager: Alert manager for getting recent alerts.
            actions_manager: Actions manager for monitoring control.
        """
        self.alert_manager = alert_manager
        self.actions_manager = actions_manager
        self.icon: pystray.Icon | None = None
        self.running = False

        # Status tracking
        self._monitoring_status = "Unknown"
        self._last_alert_count = 0

        if not TRAY_AVAILABLE:
            logger.warning("Tray application disabled: required dependencies not available")
        else:
            logger.info("TrayApplication initialized")

    def create_menu(self) -> pystray.Menu | None:
        """Create tray context menu.

        Returns:
            pystray.Menu object or None if not available.
        """
        if not TRAY_AVAILABLE:
            return None

        try:
            # Get current status
            is_paused = (
                self.actions_manager.is_monitoring_paused()
                if self.actions_manager else False
            )

            # Get recent alerts
            alert_items = self._create_alert_menu_items()

            # Create menu items
            menu_items = [
                pystray.MenuItem("WatchLockAI Sentinel", lambda: None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(f"Status: {self._monitoring_status}", lambda: None, enabled=False),
            ]

            # Add pause/resume option
            if is_paused:
                remaining = self.actions_manager.get_monitoring_pause_remaining()
                pause_text = f"Paused ({remaining}s remaining)" if remaining else "Paused"
                menu_items.extend([
                    pystray.MenuItem(pause_text, lambda: None, enabled=False),
                    pystray.MenuItem("Resume Monitoring", self._resume_monitoring),
                ])
            else:
                menu_items.extend([
                    pystray.MenuItem("Monitoring: Active", lambda: None, enabled=False),
                    pystray.MenuItem("Pause 1 min", lambda: self._pause_monitoring(60)),
                    pystray.MenuItem("Pause 5 min", lambda: self._pause_monitoring(300)),
                    pystray.MenuItem("Pause 15 min", lambda: self._pause_monitoring(900)),
                ])

            menu_items.append(pystray.Menu.SEPARATOR)

            # Add alerts section
            if alert_items:
                menu_items.extend([
                    pystray.MenuItem("Recent Alerts", lambda: None, enabled=False),
                    *alert_items,
                    pystray.Menu.SEPARATOR,
                ])
            else:
                menu_items.extend([
                    pystray.MenuItem("No Recent Alerts", lambda: None, enabled=False),
                    pystray.Menu.SEPARATOR,
                ])

            # Add utility options
            menu_items.extend([
                pystray.MenuItem("Open Console", self._open_console),
                pystray.MenuItem("Policies...", self._open_policies),
                pystray.MenuItem("Open Logs", self._open_logs),
                pystray.MenuItem("Test Notification", self._test_notification),
                pystray.MenuItem("Settings", self._open_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("About", self._show_about),
                pystray.MenuItem("Exit", self._exit_application),
            ])

            return pystray.Menu(*menu_items)

        except Exception as e:
            logger.error(f"Error creating tray menu: {e}")
            return None

    def _create_alert_menu_items(self) -> list[pystray.MenuItem]:
        """Create menu items for recent alerts.

        Returns:
            List of menu items for recent alerts.
        """
        if not TRAY_AVAILABLE or not self.alert_manager:
            return []

        try:
            alerts = self.alert_manager.get_tray_alerts()
            if not alerts:
                return []

            # Show last 5 alerts
            recent_alerts = alerts[-5:]
            menu_items = []

            for alert in reversed(recent_alerts):  # Most recent first
                # Format alert time
                try:
                    alert_time = datetime.fromisoformat(alert.ts.replace("Z", "+00:00"))
                    time_str = alert_time.strftime("%H:%M")
                except Exception:
                    time_str = "??:??"

                # Create alert menu item
                alert_text = f"{time_str} [{alert.severity.upper()}] {alert.tag}"
                if len(alert_text) > 50:
                    alert_text = alert_text[:47] + "..."

                menu_items.append(
                    pystray.MenuItem(
                        alert_text,
                        lambda icon, item, alert_id=alert.id: self._show_alert_details(alert_id),
                        enabled=True,
                    ),
                )

            return menu_items

        except Exception as e:
            logger.error(f"Error creating alert menu items: {e}")
            return []

    def _pause_monitoring(self, duration_seconds: int) -> None:
        """Pause monitoring for specified duration.

        Args:
            duration_seconds: Duration to pause in seconds.
        """
        if not self.actions_manager:
            logger.warning("Cannot pause monitoring: actions manager not available")
            return

        try:
            result = self.actions_manager.pause_monitoring(duration_seconds)
            logger.info(f"Monitoring pause requested: {result.message}")

            # Update menu
            if self.icon:
                self.icon.menu = self.create_menu()
                self.icon.update_menu()

        except Exception as e:
            logger.error(f"Error pausing monitoring: {e}")

    def _resume_monitoring(self) -> None:
        """Resume monitoring if paused."""
        if not self.actions_manager:
            logger.warning("Cannot resume monitoring: actions manager not available")
            return

        try:
            result = self.actions_manager.resume_monitoring()
            logger.info(f"Monitoring resume requested: {result.message}")

            # Update menu
            if self.icon:
                self.icon.menu = self.create_menu()
                self.icon.update_menu()

        except Exception as e:
            logger.error(f"Error resuming monitoring: {e}")

    def _open_console(self) -> None:
        """Open web console in default browser."""
        try:
            import webbrowser
            console_url = "http://127.0.0.1:8080"
            webbrowser.open(console_url)
            logger.info(f"Opening web console: {console_url}")
        except Exception as e:
            logger.error(f"Error opening web console: {e}")

    def _open_policies(self) -> None:
        """Open policies page in default browser."""
        try:
            import webbrowser
            policies_url = "http://127.0.0.1:8080/policies"
            webbrowser.open(policies_url)
            logger.info(f"Opening policies page: {policies_url}")
        except Exception as e:
            logger.error(f"Error opening policies page: {e}")

    def _open_logs(self) -> None:
        """Open logs directory in file explorer."""
        try:
            logs_dir = Path("logs")
            if logs_dir.exists():
                import os
                import subprocess

                if os.name == "nt":  # Windows
                    subprocess.run(["explorer", str(logs_dir.absolute())], check=False)
                else:
                    logger.warning("Log directory opening only supported on Windows")
            else:
                logger.warning("Logs directory not found")

        except Exception as e:
            logger.error(f"Error opening logs: {e}")

    def _test_notification(self) -> None:
        """Send a test notification."""
        if not self.alert_manager:
            logger.warning("Cannot send test notification: alert manager not available")
            return

        try:
            import asyncio

            # Run test notification in thread-safe way
            def run_test() -> None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.alert_manager.test_notification())
                finally:
                    loop.close()

            threading.Thread(target=run_test, daemon=True).start()

        except Exception as e:
            logger.error(f"Error sending test notification: {e}")

    def _open_settings(self) -> None:
        """Open settings (placeholder for future implementation)."""
        logger.info("Settings requested (not yet implemented)")
        # TODO: Implement settings dialog

    def _show_about(self) -> None:
        """Show about dialog (placeholder for future implementation)."""
        logger.info("About dialog requested")
        # TODO: Implement about dialog with version info

    def _show_alert_details(self, alert_id: str) -> None:
        """Show details for specific alert.

        Args:
            alert_id: ID of alert to show details for.
        """
        logger.info(f"Alert details requested: {alert_id}")
        # TODO: Implement alert details dialog

    def _exit_application(self) -> None:
        """Exit the tray application."""
        logger.info("Tray application exit requested")
        self.stop()

    def start(self) -> None:
        """Start the tray application."""
        if not TRAY_AVAILABLE:
            logger.warning("Cannot start tray application: dependencies not available")
            return

        if self.running:
            logger.warning("Tray application already running")
            return

        try:
            # Create icon
            icon_image = create_default_icon()
            if not icon_image:
                logger.error("Failed to create tray icon")
                return

            # Create tray icon
            self.icon = pystray.Icon(
                "WatchLockAI_Sentinel",
                icon_image,
                "WatchLockAI Sentinel",
                menu=self.create_menu(),
            )

            self.running = True
            logger.info("Starting tray application...")

            # Run tray icon (blocking call)
            self.icon.run()

        except Exception as e:
            logger.error(f"Error starting tray application: {e}")
            self.running = False

    def stop(self) -> None:
        """Stop the tray application."""
        if not self.running or not self.icon:
            return

        self.running = False

        try:
            self.icon.stop()
            logger.info("Tray application stopped")
        except Exception as e:
            logger.error(f"Error stopping tray application: {e}")

    def update_status(self, status: str) -> None:
        """Update monitoring status display.

        Args:
            status: Current monitoring status.
        """
        self._monitoring_status = status

        # Update menu if icon is available
        if self.icon and self.running:
            try:
                self.icon.menu = self.create_menu()
                self.icon.update_menu()
            except Exception as e:
                logger.error(f"Error updating tray menu: {e}")

    def notify_new_alert(self) -> None:
        """Notify about new alert (could change icon color/state)."""
        if not self.running:
            return

        try:
            # Update alert count
            if self.alert_manager:
                current_count = len(self.alert_manager.get_tray_alerts())
                if current_count > self._last_alert_count:
                    logger.debug("New alert detected in tray")
                    # TODO: Could change icon to indicate new alert
                    self._last_alert_count = current_count

                    # Update menu
                    if self.icon:
                        self.icon.menu = self.create_menu()
                        self.icon.update_menu()

        except Exception as e:
            logger.error(f"Error handling new alert notification: {e}")

    def run_in_thread(self) -> threading.Thread:
        """Run tray application in a separate thread.

        Returns:
            Thread object running the tray application.
        """
        def run_tray() -> None:
            try:
                self.start()
            except Exception as e:
                logger.error(f"Tray application thread error: {e}")

        thread = threading.Thread(target=run_tray, daemon=True, name="TrayApp")
        thread.start()
        logger.info("Tray application started in background thread")
        return thread

    def get_stats(self) -> dict[str, Any]:
        """Get tray application statistics.

        Returns:
            Dictionary with tray application stats.
        """
        return {
            "available": TRAY_AVAILABLE,
            "running": self.running,
            "monitoring_status": self._monitoring_status,
            "last_alert_count": self._last_alert_count,
        }


def create_tray_app(
    alert_manager: AlertManager | None = None,
    actions_manager: ResponseActionsManager | None = None,
) -> TrayApplication:
    """Create and configure tray application.

    Args:
        alert_manager: Alert manager instance.
        actions_manager: Actions manager instance.

    Returns:
        Configured TrayApplication instance.
    """
    return TrayApplication(alert_manager, actions_manager)
