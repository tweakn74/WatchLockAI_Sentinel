"""Unit tests for alert manager."""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app_core.bus import EventBus
from app_core.config import AlertsConfig
from app_core.schemas import (
    AlertCategory,
    AlertSeverity,
    DetectionAlert,
    ProvenanceInfo,
)
from response.alerts import AlertManager


@pytest.fixture()
async def event_bus():
    """Create event bus for testing."""
    bus = EventBus(max_history=100)
    await bus.start()
    yield bus
    await bus.stop()


@pytest.fixture()
def temp_log_file():
    """Create temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        temp_file = f.name

    yield temp_file

    # Cleanup
    Path(temp_file).unlink(missing_ok=True)


@pytest.fixture()
async def alert_manager(event_bus, temp_log_file):
    """Create alert manager for testing."""
    config = AlertsConfig(
        toast_notifications=False,  # Disable for testing
        log_jsonl=temp_log_file,
        max_tray_history=5,
    )

    manager = AlertManager(config, event_bus)
    await manager.start()
    yield manager
    await manager.stop()


def create_test_alert(severity=AlertSeverity.MEDIUM, category=AlertCategory.GENERAL, tag="test-alert"):
    """Helper to create test alerts."""
    provenance = ProvenanceInfo(
        file="test_rule.md",
        section="test_section",
        lines="1-10",
    )

    return DetectionAlert(
        severity=severity,
        category=category,
        tag=tag,
        entities={"test_key": "test_value"},
        confidence=0.8,
        rationale="Test alert for unit testing",
        provenance=provenance,
        suggested_actions=["Test action"],
    )


@pytest.mark.asyncio()
async def test_alert_manager_initialization(event_bus, temp_log_file):
    """Test alert manager initialization."""
    config = AlertsConfig(log_jsonl=temp_log_file)
    manager = AlertManager(config, event_bus)

    assert not manager.running

    await manager.start()
    assert manager.running

    await manager.stop()
    assert not manager.running


@pytest.mark.asyncio()
async def test_alert_processing(alert_manager, event_bus, temp_log_file):
    """Test basic alert processing."""
    # Create and publish test alert
    test_alert = create_test_alert()
    await event_bus.publish(test_alert)

    # Wait for processing
    await asyncio.sleep(0.2)

    # Check that alert was logged to JSONL
    log_path = Path(temp_log_file)
    assert log_path.exists()

    with open(log_path) as f:
        lines = f.readlines()

    assert len(lines) >= 1

    # Parse the JSON log entry
    log_entry = json.loads(lines[0])
    assert log_entry["severity"] == "medium"
    assert log_entry["category"] == "general"
    assert log_entry["tag"] == "test-alert"
    assert log_entry["rationale"] == "Test alert for unit testing"


@pytest.mark.asyncio()
async def test_tray_history_management(alert_manager, event_bus):
    """Test tray alert history management."""
    # Create multiple alerts (more than max_tray_history)
    for i in range(8):  # More than max_tray_history=5
        alert = create_test_alert(tag=f"test-alert-{i}")
        await event_bus.publish(alert)

    await asyncio.sleep(0.2)

    # Get tray history
    history = alert_manager.get_tray_history()

    # Should be limited to max_tray_history
    assert len(history) <= 5

    # Should be most recent alerts (reverse chronological)
    assert "test-alert-7" in history[0]["tag"]  # Most recent first


@pytest.mark.asyncio()
async def test_alert_severity_filtering(alert_manager, event_bus, temp_log_file):
    """Test that all severity levels are processed."""
    # Create alerts of different severities
    severities = [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH]

    for severity in severities:
        alert = create_test_alert(severity=severity, tag=f"test-{severity.value}")
        await event_bus.publish(alert)

    await asyncio.sleep(0.2)

    # Check all were logged
    with open(temp_log_file) as f:
        lines = f.readlines()

    assert len(lines) >= 3

    # Verify all severity levels present
    log_severities = []
    for line in lines:
        entry = json.loads(line)
        log_severities.append(entry["severity"])

    assert "low" in log_severities
    assert "medium" in log_severities
    assert "high" in log_severities


@pytest.mark.asyncio()
async def test_alert_category_handling(alert_manager, event_bus, temp_log_file):
    """Test handling of different alert categories."""
    categories = [
        AlertCategory.RANSOMWARE,
        AlertCategory.PERSISTENCE,
        AlertCategory.PROCESS,
        AlertCategory.NETWORK,
        AlertCategory.HEALTH,
        AlertCategory.GENERAL,
    ]

    for category in categories:
        alert = create_test_alert(category=category, tag=f"test-{category.value}")
        await event_bus.publish(alert)

    await asyncio.sleep(0.2)

    # Check all categories were logged
    with open(temp_log_file) as f:
        lines = f.readlines()

    assert len(lines) >= 6

    # Verify all categories present
    log_categories = []
    for line in lines:
        entry = json.loads(line)
        log_categories.append(entry["category"])

    for category in categories:
        assert category.value in log_categories


@pytest.mark.asyncio()
async def test_alert_provenance_logging(alert_manager, event_bus, temp_log_file):
    """Test that alert provenance is properly logged."""
    provenance = ProvenanceInfo(
        file="rules_engine_spec.md",
        section="RansomwareBurstV1",
        lines="10-25",
    )

    alert = DetectionAlert(
        severity=AlertSeverity.HIGH,
        category=AlertCategory.RANSOMWARE,
        tag="ransomware-burst",
        entities={"file_count": 150, "time_window": 10},
        confidence=0.95,
        rationale="High-rate file activity detected",
        provenance=provenance,
        suggested_actions=["Investigate file activity", "Check for encryption"],
    )

    await event_bus.publish(alert)
    await asyncio.sleep(0.2)

    # Check provenance in log
    with open(temp_log_file) as f:
        log_entry = json.loads(f.readline())

    assert "provenance" in log_entry
    assert log_entry["provenance"]["file"] == "rules_engine_spec.md"
    assert log_entry["provenance"]["section"] == "RansomwareBurstV1"
    assert log_entry["provenance"]["lines"] == "10-25"


@pytest.mark.asyncio()
async def test_alert_entities_serialization(alert_manager, event_bus, temp_log_file):
    """Test that alert entities are properly serialized."""
    complex_entities = {
        "file_paths": ["/path/1", "/path/2", "/path/3"],
        "process_info": {
            "pid": 1234,
            "name": "suspicious.exe",
            "parent_pid": 5678,
        },
        "network_connections": [
            {"ip": "1.2.3.4", "port": 80},
            {"ip": "5.6.7.8", "port": 443},
        ],
        "metrics": {
            "cpu_pct": 95.5,
            "file_count": 150,
        },
    }

    alert = create_test_alert()
    alert.entities = complex_entities

    await event_bus.publish(alert)
    await asyncio.sleep(0.2)

    # Check entities serialization
    with open(temp_log_file) as f:
        log_entry = json.loads(f.readline())

    assert "entities" in log_entry
    entities = log_entry["entities"]

    assert entities["file_paths"] == ["/path/1", "/path/2", "/path/3"]
    assert entities["process_info"]["pid"] == 1234
    assert entities["metrics"]["cpu_pct"] == 95.5


@pytest.mark.asyncio()
async def test_suggested_actions_handling(alert_manager, event_bus, temp_log_file):
    """Test handling of suggested actions."""
    alert = create_test_alert()
    alert.suggested_actions = [
        "Isolate affected system",
        "Review file system changes",
        "Check for lateral movement",
        "Update security rules",
    ]

    await event_bus.publish(alert)
    await asyncio.sleep(0.2)

    # Check actions in log
    with open(temp_log_file) as f:
        log_entry = json.loads(f.readline())

    assert "suggested_actions" in log_entry
    actions = log_entry["suggested_actions"]

    assert len(actions) == 4
    assert "Isolate affected system" in actions
    assert "Update security rules" in actions


@pytest.mark.asyncio()
async def test_toast_notification_handling(event_bus, temp_log_file):
    """Test toast notification handling (mocked)."""
    config = AlertsConfig(
        toast_notifications=True,  # Enable for this test
        log_jsonl=temp_log_file,
    )

    with patch("response.alerts.show_toast_notification") as mock_toast:
        manager = AlertManager(config, event_bus)
        await manager.start()

        try:
            # Create high severity alert (should trigger toast)
            alert = create_test_alert(severity=AlertSeverity.HIGH)
            await event_bus.publish(alert)
            await asyncio.sleep(0.2)

            # Verify toast was called
            mock_toast.assert_called_once()

        finally:
            await manager.stop()


@pytest.mark.asyncio()
async def test_alert_manager_stats(alert_manager, event_bus):
    """Test alert manager statistics."""
    # Initially should have no stats
    stats = alert_manager.get_stats()
    initial_count = stats.get("alerts_processed", 0)

    # Process some alerts
    for i in range(3):
        alert = create_test_alert(tag=f"test-{i}")
        await event_bus.publish(alert)

    await asyncio.sleep(0.2)

    # Check updated stats
    stats = alert_manager.get_stats()
    assert stats["alerts_processed"] >= initial_count + 3


@pytest.mark.asyncio()
async def test_log_file_creation(event_bus):
    """Test that log file is created if it doesn't exist."""
    # Use a path that doesn't exist
    temp_dir = tempfile.mkdtemp()
    log_path = Path(temp_dir) / "new_dir" / "alerts.jsonl"

    try:
        config = AlertsConfig(log_jsonl=str(log_path))
        manager = AlertManager(config, event_bus)
        await manager.start()

        # Publish an alert
        alert = create_test_alert()
        await event_bus.publish(alert)
        await asyncio.sleep(0.2)

        # Log file should be created
        assert log_path.exists()

        await manager.stop()

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio()
async def test_error_handling_in_alert_processing(alert_manager, event_bus):
    """Test error handling during alert processing."""
    # Create alert with problematic data (should not crash manager)
    alert = create_test_alert()

    # Mock a failure in logging
    with patch.object(alert_manager, "_log_alert_jsonl", side_effect=Exception("Test error")):
        await event_bus.publish(alert)
        await asyncio.sleep(0.2)

        # Manager should still be running despite error
        assert alert_manager.running


@pytest.mark.asyncio()
async def test_clear_tray_history(alert_manager, event_bus):
    """Test clearing tray history."""
    # Add some alerts to history
    for i in range(3):
        alert = create_test_alert(tag=f"test-{i}")
        await event_bus.publish(alert)

    await asyncio.sleep(0.2)

    # Verify history has alerts
    history = alert_manager.get_tray_history()
    assert len(history) == 3

    # Clear history
    alert_manager.clear_tray_history()

    # Verify history is empty
    history = alert_manager.get_tray_history()
    assert len(history) == 0
