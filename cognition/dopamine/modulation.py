"""Behavioral Modulation - Dopamine-Driven Behavioral Bias System.

Implements behavioral modulation based on dopamine reservoir levels,
translating emotional weather into exploration vs. caution bias.

Key Components:
- BehavioralBias: Quantified bias toward exploration or caution
- ExplorationState: Current exploration tendency classification
- BehavioralModulator: Main system for translating dopamine to behavior

Author: Project Starfire - Dopamine System Integration
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .dopamine_core import DopamineReservoir, EmotionalWeather

logger = logging.getLogger(__name__)


class ExplorationState(Enum):
    """Exploration tendency states based on dopamine levels."""

    HYPER_EXPLORATORY = "hyper_exploratory"  # Very high dopamine
    EXPLORATORY = "exploratory"  # High dopamine
    BALANCED = "balanced"  # Moderate dopamine
    CAUTIOUS = "cautious"  # Low dopamine
    RISK_AVERSE = "risk_averse"  # Very low dopamine


@dataclass
class BehavioralBias:
    """Quantified behavioral bias parameters."""

    exploration_factor: float  # 0.0 (cautious) to 1.0 (exploratory)
    risk_tolerance: float  # 0.0 (risk-averse) to 1.0 (risk-seeking)
    novelty_seeking: float  # 0.0 (familiar) to 1.0 (novel)
    position_sizing_bias: float  # 0.0 (smaller) to 1.0 (larger positions)
    confidence_threshold: float  # Minimum confidence for action
    learning_rate_modifier: float  # Modifier for learning rates

    def get_exploration_state(self) -> ExplorationState:
        """Determine exploration state from bias parameters."""
        if self.exploration_factor >= 0.8:
            return ExplorationState.HYPER_EXPLORATORY
        if self.exploration_factor >= 0.6:
            return ExplorationState.EXPLORATORY
        if self.exploration_factor >= 0.4:
            return ExplorationState.BALANCED
        if self.exploration_factor >= 0.2:
            return ExplorationState.CAUTIOUS
        return ExplorationState.RISK_AVERSE

    def apply_to_decision_params(self, base_params: dict[str, Any]) -> dict[str, Any]:
        """Apply behavioral bias to decision parameters."""
        modified_params = base_params.copy()

        # Modify position sizing
        if "position_size" in modified_params:
            size_modifier = 0.5 + (self.position_sizing_bias * 0.5)
            modified_params["position_size"] *= size_modifier

        # Modify confidence threshold
        if "min_confidence" in modified_params:
            modified_params["min_confidence"] = max(
                modified_params["min_confidence"],
                self.confidence_threshold,
            )

        # Modify risk parameters
        if "risk_tolerance" in modified_params:
            modified_params["risk_tolerance"] *= self.risk_tolerance

        # Modify learning rate
        if "learning_rate" in modified_params:
            modified_params["learning_rate"] *= self.learning_rate_modifier

        return modified_params


class BehavioralModulator:
    """Main system for translating dopamine state to behavioral bias."""

    def __init__(
        self,
        baseline_exploration: float = 0.5,
        baseline_risk_tolerance: float = 0.5,
        modulation_sensitivity: float = 1.0,
        extreme_dampening: float = 0.8,
    ):
        """Initialize behavioral modulator."""
        self.baseline_exploration = baseline_exploration
        self.baseline_risk_tolerance = baseline_risk_tolerance
        self.modulation_sensitivity = modulation_sensitivity
        self.extreme_dampening = extreme_dampening

        # Track bias history for analysis
        self.bias_history: list[BehavioralBias] = []

        logger.info("Behavioral Modulator initialized")

    def calculate_bias(self, reservoir: DopamineReservoir) -> BehavioralBias:
        """Calculate behavioral bias from dopamine reservoir state."""
        try:
            # Get emotional weather
            weather = reservoir.get_emotional_weather()
            reservoir_level = reservoir.level

            # Calculate exploration factor
            exploration_factor = self._calculate_exploration_factor(
                reservoir_level,
                weather,
            )

            # Calculate risk tolerance
            risk_tolerance = self._calculate_risk_tolerance(
                reservoir_level,
                weather,
            )

            # Calculate novelty seeking
            novelty_seeking = self._calculate_novelty_seeking(
                reservoir_level,
                weather,
            )

            # Calculate position sizing bias
            position_sizing_bias = self._calculate_position_sizing_bias(
                reservoir_level,
                weather,
            )

            # Calculate confidence threshold
            confidence_threshold = self._calculate_confidence_threshold(
                reservoir_level,
                weather,
            )

            # Calculate learning rate modifier
            learning_rate_modifier = self._calculate_learning_rate_modifier(
                reservoir_level,
                weather,
            )

            bias = BehavioralBias(
                exploration_factor=exploration_factor,
                risk_tolerance=risk_tolerance,
                novelty_seeking=novelty_seeking,
                position_sizing_bias=position_sizing_bias,
                confidence_threshold=confidence_threshold,
                learning_rate_modifier=learning_rate_modifier,
            )

            # Store in history
            self.bias_history.append(bias)

            # Keep only recent history
            if len(self.bias_history) > 100:
                self.bias_history = self.bias_history[-100:]

            logger.debug(
                f"Behavioral bias calculated: exploration={exploration_factor:.3f}, "
                f"risk_tolerance={risk_tolerance:.3f}, weather={weather.value}",
            )

            return bias

        except Exception as e:
            logger.exception(f"Failed to calculate behavioral bias: {e}")
            return self._get_default_bias()

    def _calculate_exploration_factor(
        self,
        reservoir_level: float,
        weather: EmotionalWeather,
    ) -> float:
        """Calculate exploration factor from reservoir state."""
        # Base exploration from reservoir level
        base_exploration = reservoir_level * self.modulation_sensitivity

        # Weather-specific adjustments
        weather_adjustments = {
            EmotionalWeather.EUPHORIC: 0.2,
            EmotionalWeather.CONTENT: 0.1,
            EmotionalWeather.NEUTRAL: 0.0,
            EmotionalWeather.RESTLESS: -0.1,
            EmotionalWeather.STAGNANT: -0.3,
        }

        adjustment = weather_adjustments.get(weather, 0.0)
        exploration_factor = base_exploration + adjustment

        # Apply extreme dampening
        if exploration_factor > 0.8:
            exploration_factor = (
                0.8 + (exploration_factor - 0.8) * self.extreme_dampening
            )

        return max(0.0, min(1.0, exploration_factor))

    def _calculate_risk_tolerance(
        self,
        reservoir_level: float,
        weather: EmotionalWeather,
    ) -> float:
        """Calculate risk tolerance from reservoir state."""
        # Risk tolerance follows exploration but with different baseline
        base_risk = self.baseline_risk_tolerance + (reservoir_level - 0.5) * 0.6

        # Weather-specific adjustments
        if weather in [EmotionalWeather.EUPHORIC]:
            base_risk += 0.15  # Higher risk tolerance when euphoric
        elif weather in [EmotionalWeather.STAGNANT, EmotionalWeather.RESTLESS]:
            base_risk -= 0.2  # Lower risk tolerance when struggling

        return max(0.1, min(0.9, base_risk))

    def _calculate_novelty_seeking(
        self,
        reservoir_level: float,
        weather: EmotionalWeather,
    ) -> float:
        """Calculate novelty seeking from reservoir state."""
        # Novelty seeking is high when content/euphoric, low when stagnant
        if weather in [EmotionalWeather.EUPHORIC, EmotionalWeather.CONTENT]:
            return min(0.9, reservoir_level + 0.2)
        if weather == EmotionalWeather.STAGNANT:
            return max(0.7, reservoir_level + 0.3)  # Stagnation drives novelty seeking
        return reservoir_level

    def _calculate_position_sizing_bias(
        self,
        reservoir_level: float,
        weather: EmotionalWeather,
    ) -> float:
        """Calculate position sizing bias from reservoir state."""
        # Position sizing follows risk tolerance but more conservative
        base_sizing = reservoir_level * 0.8

        if weather == EmotionalWeather.EUPHORIC:
            base_sizing *= 1.1  # Slightly larger positions when euphoric
        elif weather in [EmotionalWeather.RESTLESS, EmotionalWeather.STAGNANT]:
            base_sizing *= 0.7  # Smaller positions when struggling

        return max(0.2, min(0.8, base_sizing))

    def _calculate_confidence_threshold(
        self,
        reservoir_level: float,
        weather: EmotionalWeather,
    ) -> float:
        """Calculate confidence threshold from reservoir state."""
        # Higher reservoir = lower threshold (more willing to act)
        base_threshold = 0.7 - (reservoir_level * 0.3)

        if weather == EmotionalWeather.STAGNANT:
            base_threshold += 0.1  # Higher threshold when stagnant
        elif weather == EmotionalWeather.EUPHORIC:
            base_threshold -= 0.1  # Lower threshold when euphoric

        return max(0.3, min(0.8, base_threshold))

    def _calculate_learning_rate_modifier(
        self,
        reservoir_level: float,
        weather: EmotionalWeather,
    ) -> float:
        """Calculate learning rate modifier from reservoir state."""
        # Higher dopamine = faster learning
        base_modifier = 0.5 + (reservoir_level * 0.8)

        if weather in [EmotionalWeather.EUPHORIC, EmotionalWeather.CONTENT]:
            base_modifier *= 1.2  # Faster learning when positive
        elif weather == EmotionalWeather.STAGNANT:
            base_modifier *= 1.3  # Faster learning when stagnant (need to adapt)

        return max(0.3, min(2.0, base_modifier))

    def _get_default_bias(self) -> BehavioralBias:
        """Get default behavioral bias for error cases."""
        return BehavioralBias(
            exploration_factor=self.baseline_exploration,
            risk_tolerance=self.baseline_risk_tolerance,
            novelty_seeking=0.5,
            position_sizing_bias=0.5,
            confidence_threshold=0.6,
            learning_rate_modifier=1.0,
        )
