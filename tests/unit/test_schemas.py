"""Unit tests for Pydantic schemas."""

from datetime import datetime, timezone

import pytest

from app_core.schemas import (
    AlertCategory,
    AlertSeverity,
    DetectionAlert,
    EventType,
    FileEvent,
    HealthMetric,
    NetworkEvent,
    NetworkEventType,
    NetworkProtocol,
    ProcessEvent,
    ProcessEventType,
    ProvenanceInfo,
    RegistryEvent,
    RegistryEventType,
    RegistryHive,
)


def test_file_event_creation():
    """Test FileEvent creation and validation."""
    event = FileEvent(
        event_type=EventType.CREATED,
        path="C:\\test\\file.txt",
        size_bytes=1024,
        entropy=7.5,
    )

    assert event.event_type == EventType.CREATED
    assert event.path == "C:\\test\\file.txt"
    assert event.size_bytes == 1024
    assert event.entropy == 7.5
    assert event.host_id is not None
    assert event.sentinel_version == "1.0.0"
    assert event.ts is not None


def test_file_event_entropy_validation():
    """Test entropy validation in FileEvent."""
    # Valid entropy
    event = FileEvent(
        event_type=EventType.CREATED,
        path="test.txt",
        entropy=5.0,
    )
    assert event.entropy == 5.0

    # Invalid entropy (too high)
    with pytest.raises(ValueError):
        FileEvent(
            event_type=EventType.CREATED,
            path="test.txt",
            entropy=10.0,
        )

    # Invalid entropy (negative)
    with pytest.raises(ValueError):
        FileEvent(
            event_type=EventType.CREATED,
            path="test.txt",
            entropy=-1.0,
        )


def test_process_event_creation():
    """Test ProcessEvent creation."""
    event = ProcessEvent(
        event_type=ProcessEventType.STARTED,
        pid=1234,
        ppid=5678,
        exe="C:\\Windows\\System32\\notepad.exe",
        cmdline="notepad.exe test.txt",
        username="user",
    )

    assert event.event_type == ProcessEventType.STARTED
    assert event.pid == 1234
    assert event.ppid == 5678
    assert event.exe == "C:\\Windows\\System32\\notepad.exe"


def test_registry_event_creation():
    """Test RegistryEvent creation."""
    event = RegistryEvent(
        event_type=RegistryEventType.CREATED,
        hive=RegistryHive.HKCU,
        key_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name="TestApp",
        value_type="REG_SZ",
        data_preview="C:\\test\\app.exe",
    )

    assert event.event_type == RegistryEventType.CREATED
    assert event.hive == RegistryHive.HKCU
    assert event.key_path == "Software\\Microsoft\\Windows\\CurrentVersion\\Run"


def test_network_event_creation():
    """Test NetworkEvent creation."""
    event = NetworkEvent(
        event_type=NetworkEventType.CONNECTION,
        pid=1234,
        proc_name="chrome.exe",
        laddr_ip="192.168.1.100",
        laddr_port=12345,
        raddr_ip="93.184.216.34",
        raddr_port=443,
        proto=NetworkProtocol.TCP,
        status="ESTABLISHED",
    )

    assert event.event_type == NetworkEventType.CONNECTION
    assert event.proto == NetworkProtocol.TCP
    assert event.laddr_port == 12345
    assert event.raddr_port == 443


def test_network_event_port_validation():
    """Test port number validation in NetworkEvent."""
    # Valid ports
    event = NetworkEvent(
        event_type=NetworkEventType.CONNECTION,
        laddr_port=80,
        raddr_port=65535,
        proto=NetworkProtocol.TCP,
    )
    assert event.laddr_port == 80
    assert event.raddr_port == 65535

    # Invalid port (too high)
    with pytest.raises(ValueError):
        NetworkEvent(
            event_type=NetworkEventType.CONNECTION,
            laddr_port=70000,
            proto=NetworkProtocol.TCP,
        )


def test_health_metric_creation():
    """Test HealthMetric creation."""
    metric = HealthMetric(
        cpu_pct=45.5,
        ram_pct=67.2,
        disk_pct_free=25.8,
        temp_c=55.0,
    )

    assert metric.cpu_pct == 45.5
    assert metric.ram_pct == 67.2
    assert metric.disk_pct_free == 25.8
    assert metric.temp_c == 55.0


def test_health_metric_validation():
    """Test HealthMetric validation."""
    # Valid percentages
    metric = HealthMetric(
        cpu_pct=0.0,
        ram_pct=100.0,
        disk_pct_free=50.0,
    )
    assert metric.cpu_pct == 0.0
    assert metric.ram_pct == 100.0

    # Invalid percentage (negative)
    with pytest.raises(ValueError):
        HealthMetric(
            cpu_pct=-5.0,
            ram_pct=50.0,
            disk_pct_free=50.0,
        )

    # Invalid percentage (too high)
    with pytest.raises(ValueError):
        HealthMetric(
            cpu_pct=150.0,
            ram_pct=50.0,
            disk_pct_free=50.0,
        )


def test_detection_alert_creation():
    """Test DetectionAlert creation."""
    provenance = ProvenanceInfo(
        file="rules_engine_spec.md",
        section="test_rule",
        lines="1-10",
    )

    alert = DetectionAlert(
        severity=AlertSeverity.HIGH,
        category=AlertCategory.RANSOMWARE,
        tag="test-alert",
        entities={"test": True, "count": 5},
        confidence=0.95,
        rationale="Test alert for unit testing",
        provenance=provenance,
        suggested_actions=["Test action 1", "Test action 2"],
    )

    assert alert.severity == AlertSeverity.HIGH
    assert alert.category == AlertCategory.RANSOMWARE
    assert alert.tag == "test-alert"
    assert alert.confidence == 0.95
    assert alert.rationale == "Test alert for unit testing"
    assert alert.provenance.file == "rules_engine_spec.md"
    assert len(alert.suggested_actions) == 2
    assert alert.id is not None  # UUID should be generated


def test_alert_confidence_validation():
    """Test confidence validation in DetectionAlert."""
    provenance = ProvenanceInfo(file="test.md", section="test")

    # Valid confidence
    alert = DetectionAlert(
        severity=AlertSeverity.LOW,
        category=AlertCategory.GENERAL,
        tag="test",
        confidence=0.5,
        rationale="Test",
        provenance=provenance,
    )
    assert alert.confidence == 0.5

    # Invalid confidence (too high)
    with pytest.raises(ValueError):
        DetectionAlert(
            severity=AlertSeverity.LOW,
            category=AlertCategory.GENERAL,
            tag="test",
            confidence=1.5,
            rationale="Test",
            provenance=provenance,
        )

    # Invalid confidence (negative)
    with pytest.raises(ValueError):
        DetectionAlert(
            severity=AlertSeverity.LOW,
            category=AlertCategory.GENERAL,
            tag="test",
            confidence=-0.1,
            rationale="Test",
            provenance=provenance,
        )


def test_timestamp_fields():
    """Test that timestamp fields are properly generated."""
    event = FileEvent(
        event_type=EventType.CREATED,
        path="test.txt",
    )

    # Check timestamp format
    assert event.ts is not None

    # Should be able to parse as ISO format
    parsed_time = datetime.fromisoformat(event.ts.replace("Z", "+00:00"))
    assert parsed_time.tzinfo == timezone.utc

    # Should be recent (within last minute)
    now = datetime.now(timezone.utc)
    time_diff = (now - parsed_time).total_seconds()
    assert time_diff < 60


def test_enum_values():
    """Test that enum values are properly set."""
    event = FileEvent(
        event_type=EventType.MODIFIED,
        path="test.txt",
    )

    # Should use enum values in serialization
    event_dict = event.model_dump()
    assert event_dict["event_type"] == "modified"


def test_optional_fields():
    """Test handling of optional fields."""
    # Minimal FileEvent
    event = FileEvent(
        event_type=EventType.CREATED,
        path="test.txt",
    )

    assert event.old_path is None
    assert event.size_bytes is None
    assert event.sha256 is None
    assert event.entropy is None
    assert event.proc_pid is None
    assert event.proc_name is None

    # Event dict should include None values
    event_dict = event.model_dump()
    assert "old_path" in event_dict
    assert event_dict["old_path"] is None
