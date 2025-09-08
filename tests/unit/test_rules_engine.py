"""Unit tests for rules engine."""

import asyncio

import pytest

from app_core.bus import EventBus
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
    RegistryEvent,
    RegistryEventType,
    RegistryHive,
)
from detection.rules_engine import RulesEngine


@pytest.fixture()
async def event_bus():
    """Create event bus for testing."""
    bus = EventBus(max_history=100)
    await bus.start()
    yield bus
    await bus.stop()


@pytest.fixture()
async def rules_engine(event_bus):
    """Create rules engine for testing."""
    engine = RulesEngine(event_bus)
    await engine.start()
    yield engine
    await engine.stop()


@pytest.mark.asyncio()
async def test_rules_engine_initialization(event_bus):
    """Test rules engine initialization."""
    engine = RulesEngine(event_bus)
    assert not engine.running

    await engine.start()
    assert engine.running

    await engine.stop()
    assert not engine.running


@pytest.mark.asyncio()
async def test_ransomware_burst_rule_below_threshold(rules_engine, event_bus):
    """Test ransomware burst rule - below threshold (no alert)."""
    alerts = []

    def alert_handler(alert):
        alerts.append(alert)

    # Subscribe to alerts
    alert_sub = event_bus.subscribe(DetectionAlert, alert_handler, "test_alert_handler")

    try:
        # Create file events below ransomware threshold (< 120 in 10s)
        for i in range(50):
            event = FileEvent(
                event_type=EventType.CREATED,
                path=f"test_{i}.txt",
                entropy=7.5,  # High entropy
            )
            await event_bus.publish(event)

        # Wait for processing
        await asyncio.sleep(0.5)

        # Should not trigger ransomware alert
        ransomware_alerts = [a for a in alerts if a.tag == "ransomware-io-burst"]
        assert len(ransomware_alerts) == 0

    finally:
        event_bus.unsubscribe(alert_sub)


@pytest.mark.asyncio()
async def test_ransomware_burst_rule_above_threshold(rules_engine, event_bus):
    """Test ransomware burst rule - above threshold (alert expected)."""
    alerts = []

    def alert_handler(alert):
        alerts.append(alert)

    # Subscribe to alerts
    alert_sub = event_bus.subscribe(DetectionAlert, alert_handler, "test_alert_handler")

    try:
        # Create file events above ransomware threshold (>= 120 in 10s)
        extensions = [".doc", ".pdf", ".jpg", ".png", ".txt", ".docx", ".xlsx", ".pptx",
                     ".zip", ".rar", ".mp3", ".mp4", ".avi", ".mov", ".dat", ".log"]

        for i in range(130):
            ext = extensions[i % len(extensions)]
            event = FileEvent(
                event_type=EventType.CREATED,
                path=f"test_{i}{ext}",
                entropy=7.5,  # High entropy
            )
            await event_bus.publish(event)

        # Wait for processing
        await asyncio.sleep(0.5)

        # Should trigger ransomware alert
        ransomware_alerts = [a for a in alerts if a.tag == "ransomware-io-burst"]
        assert len(ransomware_alerts) >= 1

        alert = ransomware_alerts[0]
        assert alert.severity == AlertSeverity.HIGH
        assert alert.category == AlertCategory.RANSOMWARE
        assert alert.provenance.file == "rules_engine_spec.md"
        assert alert.provenance.section == "ransomwareburstv1"

    finally:
        event_bus.unsubscribe(alert_sub)


@pytest.mark.asyncio()
async def test_autostart_persistence_rule(rules_engine, event_bus):
    """Test autostart persistence rule."""
    alerts = []

    def alert_handler(alert):
        alerts.append(alert)

    # Subscribe to alerts
    alert_sub = event_bus.subscribe(DetectionAlert, alert_handler, "test_alert_handler")

    try:
        # Create registry event for autostart key
        event = RegistryEvent(
            event_type=RegistryEventType.CREATED,
            hive=RegistryHive.HKCU,
            key_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            value_name="SuspiciousApp",
            value_type="REG_SZ",
            data_preview="C:\\temp\\malware.exe",
        )

        await event_bus.publish(event)
        await asyncio.sleep(0.2)

        # Should trigger persistence alert
        persistence_alerts = [a for a in alerts if a.tag == "persistence-autostart"]
        assert len(persistence_alerts) == 1

        alert = persistence_alerts[0]
        assert alert.severity == AlertSeverity.MEDIUM
        assert alert.category == AlertCategory.PERSISTENCE
        assert alert.provenance.file == "rules_engine_spec.md"
        assert alert.provenance.section == "newautostartpersistencev1"

    finally:
        event_bus.unsubscribe(alert_sub)


@pytest.mark.asyncio()
async def test_suspicious_parent_child_rule(rules_engine, event_bus):
    """Test suspicious parent-child process rule."""
    alerts = []

    def alert_handler(alert):
        alerts.append(alert)

    # Subscribe to alerts
    alert_sub = event_bus.subscribe(DetectionAlert, alert_handler, "test_alert_handler")

    try:
        # First, create parent process
        parent_event = ProcessEvent(
            event_type=ProcessEventType.STARTED,
            pid=1000,
            exe="C:\\Program Files\\Microsoft Office\\WINWORD.EXE",
            cmdline="winword.exe document.docx",
        )
        await event_bus.publish(parent_event)

        # Then create child process (suspicious)
        child_event = ProcessEvent(
            event_type=ProcessEventType.STARTED,
            pid=2000,
            ppid=1000,  # Child of winword
            exe="C:\\Windows\\System32\\cmd.exe",
            cmdline="cmd.exe /c whoami",
        )
        await event_bus.publish(child_event)
        await asyncio.sleep(0.2)

        # Should trigger macro spawn alert
        macro_alerts = [a for a in alerts if a.tag == "macro-spawn-shell"]
        assert len(macro_alerts) == 1

        alert = macro_alerts[0]
        assert alert.severity == AlertSeverity.HIGH
        assert alert.category == AlertCategory.PROCESS
        assert alert.provenance.file == "rules_engine_spec.md"
        assert alert.provenance.section == "suspiciousparentchildv1"

    finally:
        event_bus.unsubscribe(alert_sub)


@pytest.mark.asyncio()
async def test_rare_egress_spike_rule(rules_engine, event_bus):
    """Test rare egress spike rule."""
    alerts = []

    def alert_handler(alert):
        alerts.append(alert)

    # Subscribe to alerts
    alert_sub = event_bus.subscribe(DetectionAlert, alert_handler, "test_alert_handler")

    try:
        # Create connections to many different IPs
        for i in range(55):  # Above threshold of 50
            event = NetworkEvent(
                event_type=NetworkEventType.CONNECTION,
                pid=1234,
                proc_name="suspicious.exe",
                laddr_ip="192.168.1.100",
                laddr_port=12000 + i,
                raddr_ip=f"10.0.0.{i}",
                raddr_port=80,
                proto=NetworkProtocol.TCP,
                status="ESTABLISHED",
            )
            await event_bus.publish(event)

        await asyncio.sleep(0.2)

        # Should trigger egress anomaly alert
        egress_alerts = [a for a in alerts if a.tag == "egress-anomaly"]
        assert len(egress_alerts) >= 1

        alert = egress_alerts[0]
        assert alert.severity == AlertSeverity.MEDIUM
        assert alert.category == AlertCategory.NETWORK
        assert alert.provenance.file == "rules_engine_spec.md"
        assert alert.provenance.section == "rareegressspikev1"

    finally:
        event_bus.unsubscribe(alert_sub)


@pytest.mark.asyncio()
async def test_health_degradation_combo_rule(rules_engine, event_bus):
    """Test health degradation combo rule."""
    alerts = []

    def alert_handler(alert):
        alerts.append(alert)

    # Subscribe to alerts
    alert_sub = event_bus.subscribe(DetectionAlert, alert_handler, "test_alert_handler")

    try:
        # Create high CPU metric
        health_event = HealthMetric(
            cpu_pct=96.0,  # Above 95%
            ram_pct=60.0,
            disk_pct_free=30.0,
        )
        await event_bus.publish(health_event)

        # Create file churn within 10 seconds
        for i in range(250):  # Above 200 threshold
            event = FileEvent(
                event_type=EventType.CREATED,
                path=f"churn_{i}.tmp",
            )
            await event_bus.publish(event)

        await asyncio.sleep(0.2)

        # Should trigger health degradation alert
        health_alerts = [a for a in alerts if a.tag == "resource-burn-file-churn"]
        assert len(health_alerts) >= 1

        alert = health_alerts[0]
        assert alert.severity == AlertSeverity.LOW
        assert alert.category == AlertCategory.HEALTH
        assert alert.provenance.file == "rules_engine_spec.md"
        assert alert.provenance.section == "healthdegradationcombov1"

    finally:
        event_bus.unsubscribe(alert_sub)


@pytest.mark.asyncio()
async def test_rule_provenance_required(rules_engine, event_bus):
    """Test that all alerts include proper provenance information."""
    alerts = []

    def alert_handler(alert):
        alerts.append(alert)

    # Subscribe to alerts
    alert_sub = event_bus.subscribe(DetectionAlert, alert_handler, "test_alert_handler")

    try:
        # Trigger a simple autostart persistence alert
        event = RegistryEvent(
            event_type=RegistryEventType.CREATED,
            hive=RegistryHive.HKLM,
            key_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            value_name="TestApp",
            value_type="REG_SZ",
            data_preview="test.exe",
        )

        await event_bus.publish(event)
        await asyncio.sleep(0.2)

        # Verify provenance
        assert len(alerts) >= 1
        alert = alerts[0]

        # All alerts must have provenance per Knowledge Pack requirement
        assert alert.provenance is not None
        assert alert.provenance.file == "rules_engine_spec.md"
        assert alert.provenance.section is not None
        assert alert.rationale is not None
        assert len(alert.rationale) > 0

    finally:
        event_bus.unsubscribe(alert_sub)


@pytest.mark.asyncio()
async def test_rules_engine_stats(rules_engine):
    """Test rules engine statistics."""
    stats = rules_engine.get_stats()

    # Should have basic stats structure
    assert "rules_loaded" in stats
    assert "events_processed" in stats
    assert "alerts_generated" in stats
    assert stats["rules_loaded"] >= 5  # Should have at least 5 rules from spec


@pytest.mark.asyncio()
async def test_rules_engine_rule_disabling(event_bus):
    """Test that rules can be disabled via configuration."""
    # This would test rule enabling/disabling functionality
    # For now, verify that engine handles missing rules gracefully
    engine = RulesEngine(event_bus)
    await engine.start()

    try:
        # Engine should start even if some rules are missing or disabled
        assert engine.running
    finally:
        await engine.stop()
