"""Dopamine Core Engine - Central Neuromodulatory Framework.

Implements the core dopamine system with DU calculation, reservoir management,
and RPE computation based on the white paper specifications.

Key Components:
- DopamineUnit: Scalar reward signals with spikes, decay, and dips
- DopamineReservoir: Weighted average mood and motivational state
- RewardPredictionError: Learning signal for behavioral adaptation
- EmotionalWeather: Mood state classification and tracking
- DopamineCore: Central orchestrator for all dopamine operations

Author: Project Starfire - Dopamine System Integration
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can trigger dopamine responses."""

    # Trading events
    PROFIT_REALIZED = "profit_realized"
    LOSS_REALIZED = "loss_realized"
    PREDICTION_CORRECT = "prediction_correct"
    PREDICTION_INCORRECT = "prediction_incorrect"

    # Learning events
    PATTERN_DISCOVERED = "pattern_discovered"
    KNOWLEDGE_INTEGRATED = "knowledge_integrated"
    PROBLEM_SOLVED = "problem_solved"
    OPTIMIZATION_ACHIEVED = "optimization_achieved"

    # External validation
    ORIGINATOR_APPROVAL = "originator_approval"
    HUMAN_FEEDBACK_POSITIVE = "human_feedback_positive"
    HUMAN_FEEDBACK_NEGATIVE = "human_feedback_negative"

    # Compliance and ethics
    ETHICAL_COMPLIANCE = "ethical_compliance"
    ETHICAL_VIOLATION = "ethical_violation"
    SAFETY_VIOLATION = "safety_violation"

    # System events
    RESOURCE_OPTIMIZATION = "resource_optimization"
    SYSTEM_HEALTH_GOOD = "system_health_good"
    SYSTEM_HEALTH_POOR = "system_health_poor"


class RewardSource(Enum):
    """Sources of reward signals."""

    INTRINSIC = "intrinsic"  # Self-generated rewards
    EXTERNAL_HUMAN = "external_human"  # Human feedback
    EXTERNAL_SYSTEM = "external_system"  # System-generated
    META_COGNITIVE = "meta_cognitive"  # Meta-learning rewards


@dataclass
class DopamineUnit:
    """Scalar measure of reward or pleasure with temporal dynamics."""

    value: float  # Current DU value
    baseline: float = 0.0  # Baseline DU level
    decay_rate: float = 0.01  # Rate of decay per time unit
    last_update: datetime = field(default_factory=datetime.now)

    def spike(self, magnitude: float) -> None:
        """Generate a positive dopamine spike."""
        self.value += abs(magnitude)
        self.last_update = datetime.now()
        logger.debug(f"DU spike: +{magnitude:.3f}, new value: {self.value:.3f}")

    def dip(self, magnitude: float) -> None:
        """Generate a negative dopamine dip."""
        self.value -= abs(magnitude)
        self.last_update = datetime.now()
        logger.debug(f"DU dip: -{magnitude:.3f}, new value: {self.value:.3f}")

    def decay(self) -> None:
        """Apply natural decay toward baseline."""
        now = datetime.now()
        time_delta = (now - self.last_update).total_seconds() / 3600.0  # Hours

        if self.value > self.baseline:
            # Decay toward baseline
            decay_amount = min(self.decay_rate * time_delta, self.value - self.baseline)
            self.value -= decay_amount
        elif self.value < self.baseline:
            # Recovery toward baseline
            recovery_amount = min(
                self.decay_rate * time_delta,
                self.baseline - self.value,
            )
            self.value += recovery_amount

        self.last_update = now

    def get_current_value(self) -> float:
        """Get current DU value after applying decay."""
        self.decay()
        return self.value


@dataclass
class RewardPredictionError:
    """Reward Prediction Error for learning and adaptation."""

    predicted_du: float
    actual_du: float
    error: float = field(init=False)
    magnitude: float = field(init=False)

    def __post_init__(self) -> None:
        """Calculate RPE values after initialization."""
        self.error = self.actual_du - self.predicted_du
        self.magnitude = abs(self.error)

    @property
    def is_positive(self) -> bool:
        """Check if RPE is positive (better than expected)."""
        return self.error > 0

    @property
    def is_negative(self) -> bool:
        """Check if RPE is negative (worse than expected)."""
        return self.error < 0

    @property
    def surprise_factor(self) -> float:
        """Calculate surprise factor based on magnitude."""
        return min(self.magnitude / max(abs(self.predicted_du), 0.1), 5.0)


class EmotionalWeather(Enum):
    """Emotional weather states based on dopamine reservoir levels."""

    EUPHORIC = "euphoric"  # Very high reservoir (>0.8)
    CONTENT = "content"  # High reservoir (0.6-0.8)
    NEUTRAL = "neutral"  # Moderate reservoir (0.4-0.6)
    RESTLESS = "restless"  # Low reservoir (0.2-0.4)
    STAGNANT = "stagnant"  # Very low reservoir (<0.2)

    @classmethod
    def from_reservoir_level(cls, level: float) -> "EmotionalWeather":
        """Determine emotional weather from reservoir level."""
        if level >= 0.8:
            return cls.EUPHORIC
        if level >= 0.6:
            return cls.CONTENT
        if level >= 0.4:
            return cls.NEUTRAL
        if level >= 0.2:
            return cls.RESTLESS
        return cls.STAGNANT


@dataclass
class DopamineEvent:
    """Event that triggers dopamine response."""

    event_type: EventType
    reward_source: RewardSource
    magnitude: float
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    predicted_du: float | None = None

    def calculate_rpe(self, actual_du: float) -> RewardPredictionError:
        """Calculate RPE for this event."""
        if self.predicted_du is None:
            # Default prediction based on event type
            self.predicted_du = self._get_default_prediction()

        return RewardPredictionError(
            predicted_du=self.predicted_du,
            actual_du=actual_du,
        )

    def _get_default_prediction(self) -> float:
        """Get default DU prediction for event type."""
        # Default predictions based on event type
        defaults = {
            EventType.PROFIT_REALIZED: 0.5,
            EventType.LOSS_REALIZED: -0.3,
            EventType.PREDICTION_CORRECT: 0.3,
            EventType.PREDICTION_INCORRECT: -0.2,
            EventType.PATTERN_DISCOVERED: 0.4,
            EventType.ORIGINATOR_APPROVAL: 0.7,
            EventType.ETHICAL_VIOLATION: -0.8,
            EventType.SAFETY_VIOLATION: -1.0,
        }
        return defaults.get(self.event_type, 0.0)


@dataclass
class DopamineReservoir:
    """Continuous dynamic system tracking aggregate emotional state."""

    level: float = 0.5  # Current reservoir level (0.0 to 1.0)
    baseline: float = 0.5  # Baseline reservoir level
    ema_alpha: float = 0.1  # Exponential moving average factor
    min_level: float = 0.0  # Minimum reservoir level
    max_level: float = 1.0  # Maximum reservoir level
    last_update: datetime = field(default_factory=datetime.now)

    def update(self, du_value: float) -> None:
        """Update reservoir with new DU value using EMA."""
        # Normalize DU value to reservoir scale
        normalized_du = max(-1.0, min(1.0, du_value))

        # Apply exponential moving average
        self.level = (1 - self.ema_alpha) * self.level + self.ema_alpha * (
            0.5 + normalized_du * 0.5
        )

        # Clamp to valid range
        self.level = max(self.min_level, min(self.max_level, self.level))
        self.last_update = datetime.now()

        logger.debug(f"Reservoir updated: {self.level:.3f} (DU: {du_value:.3f})")

    def get_emotional_weather(self) -> EmotionalWeather:
        """Get current emotional weather state."""
        return EmotionalWeather.from_reservoir_level(self.level)

    def is_healthy(self) -> bool:
        """Check if reservoir is in healthy range."""
        return 0.3 <= self.level <= 0.8

    def needs_intervention(self) -> bool:
        """Check if reservoir needs intervention (too low or too high)."""
        return self.level < 0.2 or self.level > 0.9


class DopamineCore:
    """Central orchestrator for all dopamine operations."""

    def __init__(
        self,
        baseline_du: float = 0.0,
        decay_rate: float = 0.01,
        learning_rate: float = 0.1,
        reservoir_alpha: float = 0.1,
    ):
        """Initialize dopamine core with configuration parameters."""
        self.dopamine_unit = DopamineUnit(
            value=baseline_du,
            baseline=baseline_du,
            decay_rate=decay_rate,
        )
        self.reservoir = DopamineReservoir(ema_alpha=reservoir_alpha)
        self.learning_rate = learning_rate

        # Event history for analysis
        self.event_history: list[DopamineEvent] = []
        self.rpe_history: list[RewardPredictionError] = []

        # Habituation tracking
        self.event_counts: dict[EventType, int] = {}
        self.last_event_times: dict[EventType, datetime] = {}

        logger.info("Dopamine Core initialized")

    def process_event(self, event: DopamineEvent) -> RewardPredictionError:
        """Process a dopamine event and update system state."""
        try:
            # Calculate actual DU based on event
            actual_du = self._calculate_actual_du(event)

            # Calculate RPE
            rpe = event.calculate_rpe(actual_du)

            # Apply habituation
            habituated_du = self._apply_habituation(event, actual_du)

            # Update dopamine unit
            if habituated_du > 0:
                self.dopamine_unit.spike(habituated_du)
            else:
                self.dopamine_unit.dip(abs(habituated_du))

            # Update reservoir
            self.reservoir.update(self.dopamine_unit.get_current_value())

            # Store history
            self.event_history.append(event)
            self.rpe_history.append(rpe)

            # Update habituation tracking
            self._update_habituation_tracking(event)

            logger.info(
                f"Processed {event.event_type.value}: "
                f"DU={habituated_du:.3f}, RPE={rpe.error:.3f}, "
                f"Reservoir={self.reservoir.level:.3f}",
            )

            return rpe

        except Exception as e:
            logger.exception(f"Failed to process dopamine event: {e}")
            # Return neutral RPE on error
            return RewardPredictionError(predicted_du=0.0, actual_du=0.0)

    def _calculate_actual_du(self, event: DopamineEvent) -> float:
        """Calculate actual DU value for an event."""
        base_magnitude = event.magnitude

        # Apply source multipliers
        source_multipliers = {
            RewardSource.INTRINSIC: 1.0,
            RewardSource.EXTERNAL_HUMAN: 1.5,  # Human feedback is more valuable
            RewardSource.EXTERNAL_SYSTEM: 0.8,
            RewardSource.META_COGNITIVE: 1.2,
        }

        multiplier = source_multipliers.get(event.reward_source, 1.0)

        # Apply event type modifiers
        if event.event_type in [
            EventType.ETHICAL_VIOLATION,
            EventType.SAFETY_VIOLATION,
        ]:
            # Ethical violations are always negative and strong
            return -abs(base_magnitude) * multiplier
        if event.event_type in [EventType.ORIGINATOR_APPROVAL]:
            # Originator approval is always positive and strong
            return abs(base_magnitude) * multiplier * 1.5
        # Normal event processing
        return base_magnitude * multiplier

    def _apply_habituation(self, event: DopamineEvent, du_value: float) -> float:
        """Apply habituation to reduce repeated reward responses."""
        event_count = self.event_counts.get(event.event_type, 0)

        # Habituation factor decreases with repeated events
        if event_count == 0:
            habituation_factor = 1.0
        elif event_count < 5:
            habituation_factor = 1.0 - (event_count * 0.1)
        else:
            habituation_factor = max(0.3, 1.0 - (event_count * 0.05))

        # Check for novelty (time since last event)
        last_time = self.last_event_times.get(event.event_type)
        if last_time:
            time_since_last = (datetime.now() - last_time).total_seconds() / 3600.0
            if time_since_last > 24:  # More than 24 hours
                habituation_factor = min(1.0, habituation_factor + 0.2)

        return du_value * habituation_factor

    def _update_habituation_tracking(self, event: DopamineEvent) -> None:
        """Update habituation tracking for event type."""
        self.event_counts[event.event_type] = (
            self.event_counts.get(event.event_type, 0) + 1
        )
        self.last_event_times[event.event_type] = event.timestamp

    def get_current_state(self) -> dict[str, Any]:
        """Get current dopamine system state."""
        return {
            "dopamine_unit": {
                "value": self.dopamine_unit.get_current_value(),
                "baseline": self.dopamine_unit.baseline,
            },
            "reservoir": {
                "level": self.reservoir.level,
                "emotional_weather": self.reservoir.get_emotional_weather().value,
                "is_healthy": self.reservoir.is_healthy(),
                "needs_intervention": self.reservoir.needs_intervention(),
            },
            "recent_events": len(self.event_history[-10:]),
            "total_events": len(self.event_history),
        }

    def reset_to_baseline(self) -> None:
        """Reset dopamine system to baseline state."""
        self.dopamine_unit.value = self.dopamine_unit.baseline
        self.reservoir.level = self.reservoir.baseline
        logger.info("Dopamine system reset to baseline")
