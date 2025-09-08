"""Rules Engine implementing rules_engine_spec.md specifications with RAG-backed detection."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

from app_core.schemas import (
    AlertCategory,
    AlertSeverity,
    DetectionAlert,
    FileEvent,
    HealthMetric,
    NetworkEvent,
    ProcessEvent,
    ProvenanceInfo,
    RegistryEvent,
    SentinelEvent,
)

if TYPE_CHECKING:
    from app_core.bus import EventBus, EventSubscription
    from detection.knowledge.loader import KnowledgeLoader


class RollingWindow:
    """Rolling time window for event aggregation."""

    def __init__(self, window_seconds: int) -> None:
        """Initialize rolling window.

        Args:
            window_seconds: Window duration in seconds.
        """
        self.window_seconds = window_seconds
        self.events: deque[tuple[float, SentinelEvent]] = deque()

    def add_event(self, event: SentinelEvent) -> None:
        """Add event to window.

        Args:
            event: Event to add.
        """
        timestamp = datetime.fromisoformat(event.ts.replace("Z", "+00:00")).timestamp()
        self.events.append((timestamp, event))
        self._cleanup_old_events()

    def _cleanup_old_events(self) -> None:
        """Remove events outside the window."""
        current_time = datetime.now(timezone.utc).timestamp()
        cutoff_time = current_time - self.window_seconds

        while self.events and self.events[0][0] < cutoff_time:
            self.events.popleft()

    def get_events(self, event_type: type | None = None) -> list[SentinelEvent]:
        """Get events in current window.

        Args:
            event_type: Optional event type filter.

        Returns:
            List of events in window.
        """
        self._cleanup_old_events()

        if event_type:
            return [event for _, event in self.events if isinstance(event, event_type)]
        else:
            return [event for _, event in self.events]

    def count_events(self, event_type: type | None = None) -> int:
        """Count events in current window.

        Args:
            event_type: Optional event type filter.

        Returns:
            Number of events in window.
        """
        return len(self.get_events(event_type))


class RansomwareBurstDetector:
    """Implements RansomwareBurstV1 rule from rules_engine_spec.md."""

    def __init__(self) -> None:
        """Initialize ransomware burst detector."""
        self.file_window = RollingWindow(10)  # burst_window_sec: 10
        self.min_suspicious_events = 120
        self.min_entropy = 7.2
        self.min_diverse_extensions = 15

    def check_file_event(self, event: FileEvent) -> DetectionAlert | None:
        """Check file event for ransomware-like behavior.

        Args:
            event: File event to analyze.

        Returns:
            DetectionAlert if suspicious pattern detected, None otherwise.
        """
        # Only check created/modified events
        if event.event_type not in ["created", "modified"]:
            return None

        self.file_window.add_event(event)

        # Count suspicious events in window
        suspicious_events = self.file_window.get_events(FileEvent)
        suspicious_count = len([e for e in suspicious_events if e.event_type in ["created", "modified"]])

        if suspicious_count < self.min_suspicious_events:
            return None

        # Check entropy criterion if available
        high_entropy_events = [e for e in suspicious_events if e.entropy and e.entropy >= self.min_entropy]
        if suspicious_events and not any(e.entropy for e in suspicious_events):
            # No entropy data available, skip entropy check
            pass
        elif len(high_entropy_events) == 0:
            return None

        # Check diverse extensions
        extensions = set()
        for event in suspicious_events:
            if event.path:
                ext = Path(event.path).suffix.lower()
                if ext:
                    extensions.add(ext)

        if len(extensions) < self.min_diverse_extensions:
            return None

        # Create alert
        return DetectionAlert(
            severity=AlertSeverity.HIGH,
            category=AlertCategory.RANSOMWARE,
            tag="ransomware-io-burst",
            entities={
                "suspicious_events": suspicious_count,
                "high_entropy_events": len(high_entropy_events),
                "diverse_extensions": len(extensions),
                "window_seconds": 10,
                "sample_paths": [e.path for e in suspicious_events[:5]],
            },
            confidence=0.9,
            rationale="High-rate file churn with high-entropy writes across diverse extensions.",
            provenance=ProvenanceInfo(
                file="rules_engine_spec.md",
                section="ransomwareburstv1",
                lines="8-18",
            ),
            suggested_actions=[
                "Immediately isolate the affected system",
                "Identify and terminate suspicious processes",
                "Check for backup integrity",
                "Consider network isolation",
            ],
        )


class AutostartPersistenceDetector:
    """Implements NewAutostartPersistenceV1 rule from rules_engine_spec.md."""

    def __init__(self) -> None:
        """Initialize autostart persistence detector."""
        self.autostart_keys = {
            "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
            "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        }

    def check_registry_event(self, event: RegistryEvent) -> DetectionAlert | None:
        """Check registry event for autostart persistence.

        Args:
            event: Registry event to analyze.

        Returns:
            DetectionAlert if persistence detected, None otherwise.
        """
        if event.event_type not in ["created", "modified"]:
            return None

        # Check if it's an autostart key
        full_key_path = f"{event.hive.value}\\{event.key_path}"
        if full_key_path not in self.autostart_keys:
            return None

        return DetectionAlert(
            severity=AlertSeverity.MEDIUM,
            category=AlertCategory.PERSISTENCE,
            tag="persistence-autostart",
            entities={
                "hive": event.hive.value,
                "key_path": event.key_path,
                "value_name": event.value_name,
                "value_type": event.value_type,
                "data_preview": event.data_preview,
            },
            confidence=0.8,
            rationale="Autostart location modified.",
            provenance=ProvenanceInfo(
                file="rules_engine_spec.md",
                section="newautostartpersistencev1",
                lines="20-26",
            ),
            suggested_actions=[
                "Review the new autostart entry for legitimacy",
                "Verify the associated executable is trusted",
                "Check process ancestry for suspicious parent",
            ],
        )


class SuspiciousParentChildDetector:
    """Implements SuspiciousParentChildV1 rule from rules_engine_spec.md."""

    def __init__(self, process_monitor: Any | None = None) -> None:
        """Initialize suspicious parent-child detector.

        Args:
            process_monitor: Process monitor for ancestry lookups.
        """
        self.process_monitor = process_monitor
        self.suspicious_parents = ["office", "winword", "excel", "powerpnt"]
        self.suspicious_children = ["cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe", "mshta.exe", "rundll32.exe"]

    def check_process_event(self, event: ProcessEvent) -> DetectionAlert | None:
        """Check process event for suspicious parent-child relationships.

        Args:
            event: Process event to analyze.

        Returns:
            DetectionAlert if suspicious spawn detected, None otherwise.
        """
        if event.event_type != "started" or not event.exe or not event.ppid:
            return None

        # Check if child is suspicious
        child_exe = Path(event.exe).name.lower()
        if child_exe not in self.suspicious_children:
            return None

        # Get parent process info
        parent_info = None
        if self.process_monitor:
            parent_info = self.process_monitor.get_process_info(event.ppid)

        # Check parent executable (basic check if no process monitor)
        parent_suspicious = False
        if parent_info and "exe" in parent_info:
            parent_exe = Path(parent_info["exe"]).name.lower()
            parent_suspicious = any(parent in parent_exe for parent in self.suspicious_parents)

        if not parent_suspicious:
            return None

        return DetectionAlert(
            severity=AlertSeverity.HIGH,
            category=AlertCategory.PROCESS,
            tag="macro-spawn-shell",
            entities={
                "child_pid": event.pid,
                "parent_pid": event.ppid,
                "child_exe": event.exe,
                "child_cmdline": event.cmdline,
                "parent_info": parent_info,
            },
            confidence=0.85,
            rationale="Office app spawned a scripting shell.",
            provenance=ProvenanceInfo(
                file="rules_engine_spec.md",
                section="suspiciousparentchildv1",
                lines="28-37",
            ),
            suggested_actions=[
                "Immediately investigate the parent Office process",
                "Check for malicious documents or macros",
                "Consider terminating the child process",
                "Scan for additional malware",
            ],
        )


class EgressAnomalyDetector:
    """Implements RareEgressSpikeV1 rule from rules_engine_spec.md."""

    def __init__(self) -> None:
        """Initialize egress anomaly detector."""
        self.network_window = RollingWindow(60)  # window_sec: 60
        self.high_risk_ports = {4444, 4445, 8081, 8443}
        self.distinct_ip_threshold = 50
        self.pid_connections: dict[int, set[str]] = defaultdict(set)

    def check_network_event(self, event: NetworkEvent) -> DetectionAlert | None:
        """Check network event for egress anomalies.

        Args:
            event: Network event to analyze.

        Returns:
            DetectionAlert if anomaly detected, None otherwise.
        """
        if event.event_type != "connection" or not event.pid or not event.raddr_ip:
            return None

        self.network_window.add_event(event)

        # Check for high-risk port
        if event.raddr_port in self.high_risk_ports:
            return DetectionAlert(
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.NETWORK,
                tag="egress-anomaly",
                entities={
                    "pid": event.pid,
                    "proc_name": event.proc_name,
                    "raddr_ip": event.raddr_ip,
                    "raddr_port": event.raddr_port,
                    "reason": "high_risk_port",
                },
                confidence=0.7,
                rationale="Unusual egress pattern for process.",
                provenance=ProvenanceInfo(
                    file="rules_engine_spec.md",
                    section="rareegressspikev1",
                    lines="39-48",
                ),
                suggested_actions=[
                    "Investigate the process making the connection",
                    "Check if the destination is known malicious",
                    "Monitor for additional suspicious network activity",
                ],
            )

        # Track distinct IPs per PID
        if event.raddr_ip:
            self.pid_connections[event.pid].add(event.raddr_ip)

            # Check for too many distinct IPs
            if len(self.pid_connections[event.pid]) >= self.distinct_ip_threshold:
                return DetectionAlert(
                    severity=AlertSeverity.MEDIUM,
                    category=AlertCategory.NETWORK,
                    tag="egress-anomaly",
                    entities={
                        "pid": event.pid,
                        "proc_name": event.proc_name,
                        "distinct_ips": len(self.pid_connections[event.pid]),
                        "threshold": self.distinct_ip_threshold,
                        "reason": "too_many_destinations",
                    },
                    confidence=0.75,
                    rationale="Unusual egress pattern for process.",
                    provenance=ProvenanceInfo(
                        file="rules_engine_spec.md",
                        section="rareegressspikev1",
                        lines="39-48",
                    ),
                    suggested_actions=[
                        "Investigate process for potential C2 communication",
                        "Check network logs for patterns",
                        "Consider process termination if confirmed malicious",
                    ],
                )

        return None


class HealthDegradationDetector:
    """Implements HealthDegradationComboV1 rule from rules_engine_spec.md."""

    def __init__(self) -> None:
        """Initialize health degradation detector."""
        self.file_window = RollingWindow(10)  # 10 second window
        self.last_health_metric: HealthMetric | None = None

    def check_health_metric(self, event: HealthMetric) -> None:
        """Check health metric for CPU degradation.

        Args:
            event: Health metric event.
        """
        self.last_health_metric = event

    def check_file_event(self, event: FileEvent) -> DetectionAlert | None:
        """Check file event in context of health metrics.

        Args:
            event: File event to analyze.

        Returns:
            DetectionAlert if health degradation with file churn detected, None otherwise.
        """
        if not self.last_health_metric or self.last_health_metric.cpu_pct <= 95:
            return None

        self.file_window.add_event(event)

        # Count file operations in window
        file_ops = self.file_window.count_events(FileEvent)

        if file_ops > 200:
            return DetectionAlert(
                severity=AlertSeverity.LOW,
                category=AlertCategory.HEALTH,
                tag="resource-burn-file-churn",
                entities={
                    "cpu_pct": self.last_health_metric.cpu_pct,
                    "file_ops_count": file_ops,
                    "window_seconds": 10,
                },
                confidence=0.6,
                rationale="CPU pinned coincident with file churn.",
                provenance=ProvenanceInfo(
                    file="rules_engine_spec.md",
                    section="healthdegradationcombov1",
                    lines="50-55",
                ),
                suggested_actions=[
                    "Identify processes consuming high CPU",
                    "Check for runaway processes or malware",
                    "Monitor system performance",
                ],
            )

        return None


class RulesEngine:
    """Main rules engine implementing rules_engine_spec.md specifications."""

    def __init__(self, event_bus: EventBus, knowledge_loader: KnowledgeLoader | None = None, process_monitor: Any | None = None) -> None:
        """Initialize rules engine.

        Args:
            event_bus: Event bus for subscribing to events and publishing alerts.
            knowledge_loader: Knowledge loader for RAG queries.
            process_monitor: Process monitor for ancestry information.
        """
        self.event_bus = event_bus
        self.knowledge_loader = knowledge_loader
        self.process_monitor = process_monitor

        # Initialize detectors
        self.ransomware_detector = RansomwareBurstDetector()
        self.persistence_detector = AutostartPersistenceDetector()
        self.parent_child_detector = SuspiciousParentChildDetector(process_monitor)
        self.egress_detector = EgressAnomalyDetector()
        self.health_detector = HealthDegradationDetector()

        # Subscriptions
        self._subscriptions: list[EventSubscription] = []
        self._running = False

        logger.info("RulesEngine initialized with all detection rules")

    async def start(self) -> None:
        """Start rules engine by subscribing to events."""
        if self._running:
            logger.warning("RulesEngine already running")
            return

        self._running = True

        # Subscribe to relevant event types
        subscriptions = [
            self.event_bus.subscribe(FileEvent, self._handle_file_event, "RulesEngine.FileHandler"),
            self.event_bus.subscribe(ProcessEvent, self._handle_process_event, "RulesEngine.ProcessHandler"),
            self.event_bus.subscribe(RegistryEvent, self._handle_registry_event, "RulesEngine.RegistryHandler"),
            self.event_bus.subscribe(NetworkEvent, self._handle_network_event, "RulesEngine.NetworkHandler"),
            self.event_bus.subscribe(HealthMetric, self._handle_health_metric, "RulesEngine.HealthHandler"),
        ]

        self._subscriptions = subscriptions
        logger.info("RulesEngine started and subscribed to events")

    async def stop(self) -> None:
        """Stop rules engine by unsubscribing from events."""
        if not self._running:
            return

        self._running = False

        # Unsubscribe from events
        for subscription in self._subscriptions:
            self.event_bus.unsubscribe(subscription)

        self._subscriptions.clear()
        logger.info("RulesEngine stopped")

    async def _handle_file_event(self, event: FileEvent) -> None:
        """Handle file events for rule evaluation.

        Args:
            event: File event to process.
        """
        try:
            # Check ransomware burst rule
            alert = self.ransomware_detector.check_file_event(event)
            if alert:
                await self.event_bus.publish(alert)
                logger.warning(f"Ransomware alert: {alert.rationale}")

            # Check health degradation rule
            alert = self.health_detector.check_file_event(event)
            if alert:
                await self.event_bus.publish(alert)
                logger.warning(f"Health degradation alert: {alert.rationale}")

        except Exception as e:
            logger.error(f"Error processing file event: {e}")

    async def _handle_process_event(self, event: ProcessEvent) -> None:
        """Handle process events for rule evaluation.

        Args:
            event: Process event to process.
        """
        try:
            # Check suspicious parent-child rule
            alert = self.parent_child_detector.check_process_event(event)
            if alert:
                await self.event_bus.publish(alert)
                logger.warning(f"Suspicious process spawn alert: {alert.rationale}")

        except Exception as e:
            logger.error(f"Error processing process event: {e}")

    async def _handle_registry_event(self, event: RegistryEvent) -> None:
        """Handle registry events for rule evaluation.

        Args:
            event: Registry event to process.
        """
        try:
            # Check autostart persistence rule
            alert = self.persistence_detector.check_registry_event(event)
            if alert:
                await self.event_bus.publish(alert)
                logger.warning(f"Persistence alert: {alert.rationale}")

        except Exception as e:
            logger.error(f"Error processing registry event: {e}")

    async def _handle_network_event(self, event: NetworkEvent) -> None:
        """Handle network events for rule evaluation.

        Args:
            event: Network event to process.
        """
        try:
            # Check egress anomaly rule
            alert = self.egress_detector.check_network_event(event)
            if alert:
                await self.event_bus.publish(alert)
                logger.warning(f"Network anomaly alert: {alert.rationale}")

        except Exception as e:
            logger.error(f"Error processing network event: {e}")

    async def _handle_health_metric(self, event: HealthMetric) -> None:
        """Handle health metrics for rule evaluation.

        Args:
            event: Health metric to process.
        """
        try:
            # Update health degradation detector
            self.health_detector.check_health_metric(event)

        except Exception as e:
            logger.error(f"Error processing health metric: {e}")

    def get_stats(self) -> dict[str, any]:
        """Get rules engine statistics.

        Returns:
            Dictionary with rules engine statistics.
        """
        return {
            "running": self._running,
            "active_subscriptions": len(self._subscriptions),
            "rules": {
                "ransomware_burst": {
                    "window_events": self.ransomware_detector.file_window.count_events(),
                    "threshold": self.ransomware_detector.min_suspicious_events,
                },
                "egress_anomaly": {
                    "window_events": self.egress_detector.network_window.count_events(),
                    "tracked_pids": len(self.egress_detector.pid_connections),
                },
                "health_degradation": {
                    "window_events": self.health_detector.file_window.count_events(),
                    "last_cpu_pct": self.health_detector.last_health_metric.cpu_pct if self.health_detector.last_health_metric else None,
                },
            },
        }

    def query_knowledge(self, query: str) -> list[dict[str, any]]:
        """Query knowledge base for rule information.

        Args:
            query: Query string.

        Returns:
            List of knowledge hits.
        """
        if not self.knowledge_loader:
            return []

        try:
            hits = self.knowledge_loader.query_knowledge(query)
            return [
                {
                    "content": hit.content,
                    "filename": hit.filename,
                    "section": hit.section,
                    "lines": hit.lines,
                    "confidence": hit.confidence,
                }
                for hit in hits
            ]
        except Exception as e:
            logger.error(f"Knowledge query failed: {e}")
            return []
