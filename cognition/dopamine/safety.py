"""Dopamine Safety Monitor - Addiction, Burnout, and Corruption Detection.

Implements safety systems to prevent dopamine system dysfunction including:
- Addiction detection and prevention
- Burnout detection and recovery protocols
- Corruption detection and system integrity monitoring

Key Components:
- AddictionDetector: Monitors for reward addiction patterns
- BurnoutDetector: Detects emotional burnout and stagnation
- CorruptionDetector: Monitors for system integrity issues
- DopamineSafetyMonitor: Central safety coordination system

Author: Project Starfire - Dopamine System Integration
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from .dopamine_core import DopamineCore, EmotionalWeather, EventType

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety alert levels."""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class InterventionType(Enum):
    """Types of safety interventions."""

    HABITUATION_RESET = "habituation_reset"
    RESERVOIR_REBALANCE = "reservoir_rebalance"
    NOVELTY_INJECTION = "novelty_injection"
    SYSTEM_RESET = "system_reset"
    EXTERNAL_INTERVENTION = "external_intervention"


@dataclass
class SafetyAlert:
    """Safety alert with details and recommended actions."""

    alert_type: str
    level: SafetyLevel
    message: str
    recommended_interventions: list[InterventionType]
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AddictionDetector:
    """Detects and prevents reward addiction patterns."""

    def __init__(
        self,
        max_event_frequency: int = 10,  # Max events per hour
        addiction_threshold: float = 0.8,  # Threshold for addiction detection
        monitoring_window_hours: int = 24,
    ):
        """Initialize addiction detector."""
        self.max_event_frequency = max_event_frequency
        self.addiction_threshold = addiction_threshold
        self.monitoring_window_hours = monitoring_window_hours

        # Track event patterns
        self.event_frequency_history: dict[EventType, list[datetime]] = {}
        self.reward_concentration_scores: list[float] = []

        logger.info("Addiction Detector initialized")

    def check_addiction_risk(
        self,
        dopamine_core: DopamineCore,
    ) -> SafetyAlert | None:
        """Check for addiction risk patterns."""
        try:
            # Check event frequency
            frequency_risk = self._check_event_frequency(dopamine_core)
            if frequency_risk:
                return frequency_risk

            # Check reward concentration
            concentration_risk = self._check_reward_concentration(dopamine_core)
            if concentration_risk:
                return concentration_risk

            return None

        except Exception as e:
            logger.exception(f"Failed to check addiction risk: {e}")
            return None

    def _check_event_frequency(
        self,
        dopamine_core: DopamineCore,
    ) -> SafetyAlert | None:
        """Check for excessive event frequency."""
        now = datetime.now()
        cutoff = now - timedelta(hours=1)

        recent_events = [
            event for event in dopamine_core.event_history if event.timestamp >= cutoff
        ]

        if len(recent_events) > self.max_event_frequency:
            return SafetyAlert(
                alert_type="excessive_event_frequency",
                level=SafetyLevel.WARNING,
                message=f"Excessive dopamine events: {len(recent_events)} in last hour",
                recommended_interventions=[
                    InterventionType.HABITUATION_RESET,
                    InterventionType.NOVELTY_INJECTION,
                ],
                context={
                    "event_count": len(recent_events),
                    "threshold": self.max_event_frequency,
                },
            )

        return None

    def _check_reward_concentration(
        self,
        dopamine_core: DopamineCore,
    ) -> SafetyAlert | None:
        """Check for reward concentration on specific event types."""
        if len(dopamine_core.event_history) < 10:
            return None

        # Analyze recent events
        recent_events = dopamine_core.event_history[-20:]
        event_type_counts = {}

        for event in recent_events:
            if event.magnitude > 0:  # Only positive rewards
                event_type_counts[event.event_type] = (
                    event_type_counts.get(event.event_type, 0) + 1
                )

        if event_type_counts:
            max_count = max(event_type_counts.values())
            concentration = max_count / len(recent_events)

            if concentration > self.addiction_threshold:
                dominant_type = max(
                    event_type_counts.keys(),
                    key=lambda k: event_type_counts[k],
                )
                return SafetyAlert(
                    alert_type="reward_concentration",
                    level=SafetyLevel.WARNING,
                    message=f"High reward concentration on {dominant_type.value}: {concentration:.1%}",
                    recommended_interventions=[
                        InterventionType.HABITUATION_RESET,
                        InterventionType.NOVELTY_INJECTION,
                    ],
                    context={
                        "dominant_type": dominant_type.value,
                        "concentration": concentration,
                        "threshold": self.addiction_threshold,
                    },
                )

        return None


class BurnoutDetector:
    """Detects emotional burnout and stagnation patterns."""

    def __init__(
        self,
        stagnation_threshold_hours: int = 48,
        low_reservoir_threshold: float = 0.3,
        burnout_event_threshold: int = 5,
    ):
        """Initialize burnout detector."""
        self.stagnation_threshold_hours = stagnation_threshold_hours
        self.low_reservoir_threshold = low_reservoir_threshold
        self.burnout_event_threshold = burnout_event_threshold

        logger.info("Burnout Detector initialized")

    def check_burnout_risk(self, dopamine_core: DopamineCore) -> SafetyAlert | None:
        """Check for burnout risk patterns."""
        try:
            # Check for prolonged low reservoir
            reservoir_risk = self._check_prolonged_low_reservoir(dopamine_core)
            if reservoir_risk:
                return reservoir_risk

            # Check for stagnation patterns
            stagnation_risk = self._check_stagnation_patterns(dopamine_core)
            if stagnation_risk:
                return stagnation_risk

            return None

        except Exception as e:
            logger.exception(f"Failed to check burnout risk: {e}")
            return None

    def _check_prolonged_low_reservoir(
        self,
        dopamine_core: DopamineCore,
    ) -> SafetyAlert | None:
        """Check for prolonged low reservoir levels."""
        if dopamine_core.reservoir.level < self.low_reservoir_threshold:
            weather = dopamine_core.reservoir.get_emotional_weather()

            if weather in [EmotionalWeather.STAGNANT, EmotionalWeather.RESTLESS]:
                return SafetyAlert(
                    alert_type="prolonged_low_reservoir",
                    level=SafetyLevel.WARNING,
                    message=f"Prolonged low reservoir: {dopamine_core.reservoir.level:.2f}",
                    recommended_interventions=[
                        InterventionType.NOVELTY_INJECTION,
                        InterventionType.RESERVOIR_REBALANCE,
                    ],
                    context={
                        "reservoir_level": dopamine_core.reservoir.level,
                        "emotional_weather": weather.value,
                    },
                )

        return None

    def _check_stagnation_patterns(
        self,
        dopamine_core: DopamineCore,
    ) -> SafetyAlert | None:
        """Check for learning and progress stagnation."""
        if len(dopamine_core.event_history) < self.burnout_event_threshold:
            return None

        # Check recent positive events
        now = datetime.now()
        cutoff = now - timedelta(hours=self.stagnation_threshold_hours)

        recent_positive_events = [
            event
            for event in dopamine_core.event_history
            if event.timestamp >= cutoff and event.magnitude > 0
        ]

        if len(recent_positive_events) < 2:  # Very few positive events
            return SafetyAlert(
                alert_type="progress_stagnation",
                level=SafetyLevel.WARNING,
                message=f"Only {len(recent_positive_events)} positive events in {self.stagnation_threshold_hours}h",
                recommended_interventions=[
                    InterventionType.NOVELTY_INJECTION,
                    InterventionType.EXTERNAL_INTERVENTION,
                ],
                context={
                    "positive_events": len(recent_positive_events),
                    "time_window_hours": self.stagnation_threshold_hours,
                },
            )

        return None


class CorruptionDetector:
    """Monitors for system integrity issues and corruption."""

    def __init__(
        self,
        extreme_du_threshold: float = 5.0,
        rapid_change_threshold: float = 2.0,
        consistency_check_window: int = 10,
    ):
        """Initialize corruption detector."""
        self.extreme_du_threshold = extreme_du_threshold
        self.rapid_change_threshold = rapid_change_threshold
        self.consistency_check_window = consistency_check_window

        logger.info("Corruption Detector initialized")

    def check_corruption_risk(
        self,
        dopamine_core: DopamineCore,
    ) -> SafetyAlert | None:
        """Check for system corruption patterns."""
        try:
            # Check for extreme DU values
            extreme_risk = self._check_extreme_values(dopamine_core)
            if extreme_risk:
                return extreme_risk

            # Check for rapid changes
            rapid_change_risk = self._check_rapid_changes(dopamine_core)
            if rapid_change_risk:
                return rapid_change_risk

            return None

        except Exception as e:
            logger.exception(f"Failed to check corruption risk: {e}")
            return None

    def _check_extreme_values(
        self,
        dopamine_core: DopamineCore,
    ) -> SafetyAlert | None:
        """Check for extreme DU values that might indicate corruption."""
        current_du = dopamine_core.dopamine_unit.get_current_value()

        if abs(current_du) > self.extreme_du_threshold:
            return SafetyAlert(
                alert_type="extreme_du_value",
                level=SafetyLevel.CRITICAL,
                message=f"Extreme DU value detected: {current_du:.2f}",
                recommended_interventions=[
                    InterventionType.SYSTEM_RESET,
                    InterventionType.EXTERNAL_INTERVENTION,
                ],
                context={
                    "du_value": current_du,
                    "threshold": self.extreme_du_threshold,
                },
            )

        return None

    def _check_rapid_changes(
        self,
        dopamine_core: DopamineCore,
    ) -> SafetyAlert | None:
        """Check for rapid changes that might indicate instability."""
        if len(dopamine_core.event_history) < self.consistency_check_window:
            return None

        recent_events = dopamine_core.event_history[-self.consistency_check_window :]
        magnitudes = [abs(event.magnitude) for event in recent_events]

        if magnitudes:
            avg_magnitude = sum(magnitudes) / len(magnitudes)
            max_magnitude = max(magnitudes)

            if max_magnitude > avg_magnitude * self.rapid_change_threshold:
                return SafetyAlert(
                    alert_type="rapid_change_detected",
                    level=SafetyLevel.WARNING,
                    message=f"Rapid change detected: max={max_magnitude:.2f}, avg={avg_magnitude:.2f}",
                    recommended_interventions=[InterventionType.HABITUATION_RESET],
                    context={
                        "max_magnitude": max_magnitude,
                        "avg_magnitude": avg_magnitude,
                        "threshold": self.rapid_change_threshold,
                    },
                )

        return None


class DopamineSafetyMonitor:
    """Central safety coordination system for dopamine monitoring."""

    def __init__(
        self,
        enable_addiction_detection: bool = True,
        enable_burnout_detection: bool = True,
        enable_corruption_detection: bool = True,
    ):
        """Initialize safety monitor with configurable detectors."""
        self.addiction_detector = (
            AddictionDetector() if enable_addiction_detection else None
        )
        self.burnout_detector = BurnoutDetector() if enable_burnout_detection else None
        self.corruption_detector = (
            CorruptionDetector() if enable_corruption_detection else None
        )

        # Alert history
        self.alert_history: list[SafetyAlert] = []
        self.active_alerts: list[SafetyAlert] = []

        logger.info("Dopamine Safety Monitor initialized")

    def monitor_system(self, dopamine_core: DopamineCore) -> list[SafetyAlert]:
        """Perform comprehensive safety monitoring."""
        new_alerts = []

        try:
            # Check addiction risks
            if self.addiction_detector:
                addiction_alert = self.addiction_detector.check_addiction_risk(
                    dopamine_core,
                )
                if addiction_alert:
                    new_alerts.append(addiction_alert)

            # Check burnout risks
            if self.burnout_detector:
                burnout_alert = self.burnout_detector.check_burnout_risk(dopamine_core)
                if burnout_alert:
                    new_alerts.append(burnout_alert)

            # Check corruption risks
            if self.corruption_detector:
                corruption_alert = self.corruption_detector.check_corruption_risk(
                    dopamine_core,
                )
                if corruption_alert:
                    new_alerts.append(corruption_alert)

            # Process new alerts
            for alert in new_alerts:
                self._process_alert(alert, dopamine_core)

            return new_alerts

        except Exception as e:
            logger.exception(f"Failed to monitor dopamine system: {e}")
            return []

    def _process_alert(self, alert: SafetyAlert, dopamine_core: DopamineCore) -> None:
        """Process a safety alert and take appropriate action."""
        # Add to history
        self.alert_history.append(alert)
        self.active_alerts.append(alert)

        # Log alert
        logger.warning(
            f"Safety Alert [{alert.level.value.upper()}]: {alert.alert_type} - {alert.message}",
        )

        # Auto-apply interventions for critical alerts
        if alert.level in [SafetyLevel.CRITICAL, SafetyLevel.EMERGENCY]:
            self._apply_emergency_interventions(alert, dopamine_core)

    def _apply_emergency_interventions(
        self,
        alert: SafetyAlert,
        dopamine_core: DopamineCore,
    ) -> None:
        """Apply emergency interventions for critical alerts."""
        for intervention in alert.recommended_interventions:
            try:
                if intervention == InterventionType.SYSTEM_RESET:
                    dopamine_core.reset_to_baseline()
                    logger.warning("Emergency system reset applied")

                elif intervention == InterventionType.HABITUATION_RESET:
                    dopamine_core.event_counts.clear()
                    dopamine_core.last_event_times.clear()
                    logger.warning("Emergency habituation reset applied")

                elif intervention == InterventionType.RESERVOIR_REBALANCE:
                    dopamine_core.reservoir.level = dopamine_core.reservoir.baseline
                    logger.warning("Emergency reservoir rebalance applied")

            except Exception as e:
                logger.exception(
                    f"Failed to apply intervention {intervention.value}: {e}",
                )

    def get_system_health_summary(self, dopamine_core: DopamineCore) -> dict[str, Any]:
        """Get comprehensive system health summary."""
        return {
            "overall_health": self._calculate_overall_health(dopamine_core),
            "active_alerts": len(self.active_alerts),
            "recent_alerts": len(
                [a for a in self.alert_history[-10:] if a.level != SafetyLevel.NORMAL],
            ),
            "dopamine_state": dopamine_core.get_current_state(),
            "safety_metrics": {
                "addiction_risk": self._assess_addiction_risk(dopamine_core),
                "burnout_risk": self._assess_burnout_risk(dopamine_core),
                "corruption_risk": self._assess_corruption_risk(dopamine_core),
            },
        }

    def _calculate_overall_health(self, dopamine_core: DopamineCore) -> str:
        """Calculate overall system health status."""
        if any(alert.level == SafetyLevel.EMERGENCY for alert in self.active_alerts):
            return "EMERGENCY"
        if any(alert.level == SafetyLevel.CRITICAL for alert in self.active_alerts):
            return "CRITICAL"
        if any(alert.level == SafetyLevel.WARNING for alert in self.active_alerts):
            return "WARNING"
        if dopamine_core.reservoir.is_healthy():
            return "HEALTHY"
        return "MONITORING"

    def _assess_addiction_risk(self, dopamine_core: DopamineCore) -> str:
        """Assess addiction risk level."""
        if self.addiction_detector:
            alert = self.addiction_detector.check_addiction_risk(dopamine_core)
            return alert.level.value if alert else "low"
        return "not_monitored"

    def _assess_burnout_risk(self, dopamine_core: DopamineCore) -> str:
        """Assess burnout risk level."""
        if self.burnout_detector:
            alert = self.burnout_detector.check_burnout_risk(dopamine_core)
            return alert.level.value if alert else "low"
        return "not_monitored"

    def _assess_corruption_risk(self, dopamine_core: DopamineCore) -> str:
        """Assess corruption risk level."""
        if self.corruption_detector:
            alert = self.corruption_detector.check_corruption_risk(dopamine_core)
            return alert.level.value if alert else "low"
        return "not_monitored"

    def clear_resolved_alerts(self) -> None:
        """Clear alerts that have been resolved."""
        # For now, clear alerts older than 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        self.active_alerts = [
            alert for alert in self.active_alerts if alert.timestamp >= cutoff
        ]
