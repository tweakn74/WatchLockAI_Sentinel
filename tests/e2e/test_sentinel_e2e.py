"""End-to-end test implementing test_e2e.md specifications.

Goal: Prove pipeline wiring without destructive actions.
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path

import pytest

from app_core.bus import EventBus
from app_core.config import AlertsConfig, FileSystemConfig, HealthConfig
from app_core.schemas import DetectionAlert, FileEvent, HealthMetric
from collectors.fs_monitor import FileSystemMonitor
from collectors.health_monitor import HealthMonitor
from detection.rules_engine import RulesEngine
from response.alerts import AlertManager


class E2ETestCollector:
    """Helper class to collect events and alerts during E2E testing."""

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize test collector.

        Args:
            event_bus: Event bus to monitor.
        """
        self.event_bus = event_bus
        self.file_events: list[FileEvent] = []
        self.health_metrics: list[HealthMetric] = []
        self.alerts: list[DetectionAlert] = []
        self.subscriptions = []

    async def start(self) -> None:
        """Start collecting events."""
        # Subscribe to events
        file_sub = self.event_bus.subscribe(
            FileEvent,
            self._handle_file_event,
            "E2ETestCollector.FileHandler",
        )

        health_sub = self.event_bus.subscribe(
            HealthMetric,
            self._handle_health_metric,
            "E2ETestCollector.HealthHandler",
        )

        alert_sub = self.event_bus.subscribe(
            DetectionAlert,
            self._handle_alert,
            "E2ETestCollector.AlertHandler",
        )

        self.subscriptions = [file_sub, health_sub, alert_sub]

    async def stop(self) -> None:
        """Stop collecting events."""
        for subscription in self.subscriptions:
            self.event_bus.unsubscribe(subscription)
        self.subscriptions.clear()

    def _handle_file_event(self, event: FileEvent) -> None:
        """Handle file events."""
        self.file_events.append(event)

    def _handle_health_metric(self, event: HealthMetric) -> None:
        """Handle health metrics."""
        self.health_metrics.append(event)

    def _handle_alert(self, event: DetectionAlert) -> None:
        """Handle detection alerts."""
        self.alerts.append(event)

    def get_stats(self) -> dict[str, int]:
        """Get collection statistics."""
        return {
            "file_events": len(self.file_events),
            "health_metrics": len(self.health_metrics),
            "alerts": len(self.alerts),
        }


@pytest.fixture()
async def test_environment():
    """Set up E2E test environment."""
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp(prefix="sentinel_e2e_test_")
    temp_path = Path(temp_dir)

    # Create event bus
    event_bus = EventBus(max_history=1000)
    await event_bus.start()

    # Create test collector
    collector = E2ETestCollector(event_bus)
    await collector.start()

    yield {
        "temp_dir": temp_path,
        "event_bus": event_bus,
        "collector": collector,
    }

    # Cleanup
    await collector.stop()
    await event_bus.stop()

    # Clean up temp directory
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio()
async def test_e2e_scenario_per_spec(test_environment):
    """Test E2E scenario per test_e2e.md specifications.

    Scenario:
    1) Start app in non-service mode with default config (file_monitor on a temp directory).
    2) Create 10 small files in temp dir over 2 seconds, then modify 5 of them.
    3) Expect:
       - FileEvent@v1 count >= 15 in logs
       - No ransomware alert (threshold is 120 in 10s)
       - 1 health metric observed
    4) Verify an alert of type 'health' can be forced by setting cpu_warn=0 in a test config.
    """
    temp_dir = test_environment["temp_dir"]
    event_bus = test_environment["event_bus"]
    collector = test_environment["collector"]

    # Step 1: Configure file system monitor for temp directory
    fs_config = FileSystemConfig(
        enabled=True,
        paths=[str(temp_dir)],
        exclude_globs=[],
        method="polling",  # Use polling for reliable testing
        compute_entropy=False,
        compute_hash_small_files=False,
        small_file_threshold_bytes=1024,
        burst_window_sec=10,
    )

    fs_monitor = FileSystemMonitor(fs_config, event_bus)
    await fs_monitor.start()

    # Configure health monitor
    health_config = HealthConfig(
        enabled=True,
        cpu_warn=90,  # Normal threshold first
        ram_warn=90,
        disk_warn_pct_free=5,
    )

    health_monitor = HealthMonitor(health_config, event_bus)
    await health_monitor.start()

    # Initialize rules engine
    rules_engine = RulesEngine(event_bus)
    await rules_engine.start()

    try:
        # Wait for monitors to initialize
        await asyncio.sleep(1)

        # Step 2: Create 10 small files over 2 seconds
        print("Creating 10 test files...")
        for i in range(10):
            test_file = temp_dir / f"test_file_{i:02d}.txt"
            test_file.write_text(f"Test content for file {i}")
            await asyncio.sleep(0.2)  # 200ms between files = 2 seconds total

        # Modify 5 of them
        print("Modifying 5 test files...")
        for i in range(5):
            test_file = temp_dir / f"test_file_{i:02d}.txt"
            test_file.write_text(f"Modified content for file {i}")
            await asyncio.sleep(0.1)

        # Wait for file system events to be processed
        await asyncio.sleep(3)

        # Step 3: Verify expectations
        stats = collector.get_stats()
        print(f"Collected events: {stats}")

        # Check file events count (should be >= 15: 10 creates + 5 modifies)
        assert stats["file_events"] >= 15, f"Expected >= 15 file events, got {stats['file_events']}"
        print(f"✓ File events count: {stats['file_events']} >= 15")

        # Check health metrics (should have at least 1)
        assert stats["health_metrics"] >= 1, f"Expected >= 1 health metric, got {stats['health_metrics']}"
        print(f"✓ Health metrics count: {stats['health_metrics']} >= 1")

        # Check no ransomware alert (threshold is 120 events in 10 seconds)
        ransomware_alerts = [
            alert for alert in collector.alerts
            if alert.tag == "ransomware-io-burst"
        ]
        assert len(ransomware_alerts) == 0, f"Unexpected ransomware alert: {ransomware_alerts}"
        print("✓ No ransomware alert triggered (as expected)")

        # Step 4: Test health alert by setting cpu_warn=0
        print("Testing health alert with cpu_warn=0...")

        # Reconfigure health monitor with cpu_warn=0
        await health_monitor.stop()

        health_config_strict = HealthConfig(
            enabled=True,
            cpu_warn=0,  # This should trigger an alert
            ram_warn=90,
            disk_warn_pct_free=5,
        )

        health_monitor_strict = HealthMonitor(health_config_strict, event_bus)
        await health_monitor_strict.start()

        # Wait for health metric that should trigger alert
        await asyncio.sleep(6)  # Health monitor samples every 5 seconds

        # Check for health alert
        health_alerts = [
            alert for alert in collector.alerts
            if alert.category == "health"
        ]

        assert len(health_alerts) >= 1, f"Expected health alert with cpu_warn=0, got {len(health_alerts)} alerts"
        print(f"✓ Health alert triggered: {health_alerts[0].rationale}")

        await health_monitor_strict.stop()

    finally:
        # Cleanup
        await rules_engine.stop()
        await health_monitor.stop()
        await fs_monitor.stop()

    # Final verification
    final_stats = collector.get_stats()
    print(f"Final test stats: {final_stats}")

    # Save results to build manifest location
    results = {
        "test_name": "E2E Smoke Test per test_e2e.md",
        "timestamp": time.time(),
        "results": {
            "file_events_collected": final_stats["file_events"],
            "health_metrics_collected": final_stats["health_metrics"],
            "alerts_generated": final_stats["alerts"],
            "ransomware_alerts": len([a for a in collector.alerts if a.tag == "ransomware-io-burst"]),
            "health_alerts": len([a for a in collector.alerts if a.category == "health"]),
        },
        "expectations_met": {
            "file_events_ge_15": final_stats["file_events"] >= 15,
            "health_metrics_ge_1": final_stats["health_metrics"] >= 1,
            "no_ransomware_alert": len([a for a in collector.alerts if a.tag == "ransomware-io-burst"]) == 0,
            "health_alert_triggered": len([a for a in collector.alerts if a.category == "health"]) >= 1,
        },
        "status": "PASSED",
    }

    # Save to DOCS directory
    docs_dir = Path("DOCS")
    docs_dir.mkdir(exist_ok=True)

    with open(docs_dir / "E2E_Test_Results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✓ E2E test completed successfully!")
    print(f"Results saved to {docs_dir / 'E2E_Test_Results.json'}")

    return results


@pytest.mark.asyncio()
async def test_alert_manager_integration(test_environment):
    """Test alert manager integration in E2E scenario."""
    event_bus = test_environment["event_bus"]

    # Create alert manager
    alerts_config = AlertsConfig(
        toast_notifications=False,  # Disable for testing
        log_jsonl="logs/test_alerts.jsonl",
    )

    alert_manager = AlertManager(alerts_config, event_bus)
    await alert_manager.start()

    try:
        # Create a test alert
        from app_core.schemas import AlertCategory, AlertSeverity, ProvenanceInfo

        test_alert = DetectionAlert(
            severity=AlertSeverity.MEDIUM,
            category=AlertCategory.GENERAL,
            tag="test-integration",
            entities={"test": True},
            confidence=0.8,
            rationale="Test alert for integration testing",
            provenance=ProvenanceInfo(
                file="test_e2e.md",
                section="integration_test",
                lines="N/A",
            ),
            suggested_actions=["Verify alert system integration"],
        )

        # Publish alert
        await event_bus.publish(test_alert)

        # Wait for processing
        await asyncio.sleep(0.5)

        # Verify alert was processed
        tray_alerts = alert_manager.get_tray_alerts()
        assert len(tray_alerts) >= 1, "Alert should be in tray buffer"

        # Check alert content
        found_alert = None
        for alert in tray_alerts:
            if alert.tag == "test-integration":
                found_alert = alert
                break

        assert found_alert is not None, "Test alert not found in tray buffer"
        assert found_alert.rationale == "Test alert for integration testing"

        print("✓ Alert manager integration test passed")

    finally:
        await alert_manager.stop()


@pytest.mark.asyncio()
async def test_rules_engine_integration(test_environment):
    """Test rules engine integration with file events."""
    event_bus = test_environment["event_bus"]
    collector = test_environment["collector"]

    # Initialize rules engine
    rules_engine = RulesEngine(event_bus)
    await rules_engine.start()

    try:
        # Create file events that should NOT trigger ransomware alert
        # (below threshold of 120 events)
        for i in range(10):
            file_event = FileEvent(
                event_type="created",
                path=f"test_file_{i}.txt",
                size_bytes=100,
                entropy=6.0,  # Below ransomware threshold of 7.2
            )
            await event_bus.publish(file_event)

        # Wait for processing
        await asyncio.sleep(1)

        # Should not trigger ransomware alert
        ransomware_alerts = [
            alert for alert in collector.alerts
            if alert.tag == "ransomware-io-burst"
        ]

        assert len(ransomware_alerts) == 0, "Should not trigger ransomware alert with low file count"

        print("✓ Rules engine integration test passed (no false positives)")

    finally:
        await rules_engine.stop()


if __name__ == "__main__":
    # Allow running this test directly
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
