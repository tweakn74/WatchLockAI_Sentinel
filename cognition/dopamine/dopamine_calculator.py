"""Dopamine Calculator - Trading Event to DU Conversion.

Implements the calculation of Dopamine Units (DU) from trading events,
performance metrics, and system outcomes based on the white paper specifications.

Key Functions:
- Convert P&L events to DU signals
- Calculate risk-adjusted reward values
- Apply surprise factors and RPE weighting
- Handle compliance and ethical event processing

Author: Project Starfire - Dopamine System Integration
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .dopamine_core import DopamineEvent, EventType, RewardSource

logger = logging.getLogger(__name__)


@dataclass
class TradingOutcome:
    """Represents a trading outcome for dopamine calculation."""

    symbol: str
    profit_loss: float  # Actual P&L
    expected_profit_loss: float  # Expected P&L
    risk_adjusted_return: float  # Risk-adjusted return
    trade_success: bool  # Whether trade was profitable
    confidence_score: float  # Original confidence in trade
    execution_quality: float  # Quality of execution (0-1)
    compliance_status: str  # "compliant", "violation", "warning"
    timestamp: datetime
    context: dict[str, Any]


class DopamineCalculator:
    """Calculates dopamine units from trading and system events."""

    def __init__(
        self,
        base_profit_multiplier: float = 1.0,
        base_loss_multiplier: float = 1.2,  # Losses hurt more than gains feel good
        surprise_amplification: float = 2.0,
        compliance_penalty_multiplier: float = 3.0,
        originator_approval_multiplier: float = 2.5,
    ):
        """Initialize calculator with configuration parameters."""
        self.base_profit_multiplier = base_profit_multiplier
        self.base_loss_multiplier = base_loss_multiplier
        self.surprise_amplification = surprise_amplification
        self.compliance_penalty_multiplier = compliance_penalty_multiplier
        self.originator_approval_multiplier = originator_approval_multiplier

        logger.info("Dopamine Calculator initialized")

    def calculate_trading_du(self, outcome: TradingOutcome) -> DopamineEvent:
        """Calculate DU from trading outcome."""
        try:
            # Calculate base reward prediction error
            rpe = outcome.profit_loss - outcome.expected_profit_loss

            # Calculate surprise factor
            surprise_factor = self._calculate_surprise_factor(
                outcome.profit_loss,
                outcome.expected_profit_loss,
                outcome.confidence_score,
            )

            # Calculate base DU magnitude
            if outcome.trade_success:
                base_du = (
                    outcome.risk_adjusted_return
                    * self.base_profit_multiplier
                    * surprise_factor
                )
                event_type = EventType.PROFIT_REALIZED
            else:
                base_du = (
                    outcome.risk_adjusted_return
                    * self.base_loss_multiplier
                    * surprise_factor
                )
                event_type = EventType.LOSS_REALIZED

            # Apply execution quality modifier
            execution_modifier = 0.5 + (outcome.execution_quality * 0.5)
            final_du = base_du * execution_modifier

            # Handle compliance issues
            if outcome.compliance_status == "violation":
                final_du -= 0.5 * self.compliance_penalty_multiplier
                event_type = EventType.SAFETY_VIOLATION
            elif outcome.compliance_status == "warning":
                final_du -= 0.2 * self.compliance_penalty_multiplier

            # Create dopamine event
            event = DopamineEvent(
                event_type=event_type,
                reward_source=RewardSource.EXTERNAL_SYSTEM,
                magnitude=final_du,
                predicted_du=outcome.expected_profit_loss * self.base_profit_multiplier,
                context={
                    "symbol": outcome.symbol,
                    "profit_loss": outcome.profit_loss,
                    "rpe": rpe,
                    "surprise_factor": surprise_factor,
                    "execution_quality": outcome.execution_quality,
                    "compliance_status": outcome.compliance_status,
                },
                timestamp=outcome.timestamp,
            )

            logger.debug(
                f"Trading DU calculated: {final_du:.3f} for {outcome.symbol} "
                f"(P&L: {outcome.profit_loss:.2f}, RPE: {rpe:.2f})",
            )

            return event

        except Exception as e:
            logger.exception(f"Failed to calculate trading DU: {e}")
            return self._create_neutral_event("trading_calculation_error")

    def calculate_prediction_du(
        self,
        predicted_outcome: str,
        actual_outcome: str,
        confidence: float,
        context: dict[str, Any] | None = None,
    ) -> DopamineEvent:
        """Calculate DU from prediction accuracy."""
        try:
            prediction_correct = predicted_outcome == actual_outcome

            if prediction_correct:
                # Reward for correct prediction, scaled by confidence
                base_du = confidence * 0.5
                event_type = EventType.PREDICTION_CORRECT
            else:
                # Penalty for incorrect prediction, scaled by confidence
                base_du = -confidence * 0.3
                event_type = EventType.PREDICTION_INCORRECT

            # Apply surprise factor based on confidence
            if prediction_correct and confidence < 0.5:
                # Unexpected success
                base_du *= 1.5
            elif not prediction_correct and confidence > 0.8:
                # Unexpected failure
                base_du *= 1.3

            event = DopamineEvent(
                event_type=event_type,
                reward_source=RewardSource.INTRINSIC,
                magnitude=base_du,
                predicted_du=confidence * 0.3
                if prediction_correct
                else -confidence * 0.2,
                context={
                    "predicted_outcome": predicted_outcome,
                    "actual_outcome": actual_outcome,
                    "confidence": confidence,
                    "prediction_correct": prediction_correct,
                    **(context or {}),
                },
            )

            logger.debug(
                f"Prediction DU calculated: {base_du:.3f} "
                f"(correct: {prediction_correct}, confidence: {confidence:.2f})",
            )

            return event

        except Exception as e:
            logger.exception(f"Failed to calculate prediction DU: {e}")
            return self._create_neutral_event("prediction_calculation_error")

    def calculate_originator_approval_du(
        self,
        approval_strength: float,
        context: dict[str, Any] | None = None,
    ) -> DopamineEvent:
        """Calculate DU from originator approval."""
        base_du = approval_strength * self.originator_approval_multiplier

        return DopamineEvent(
            event_type=EventType.ORIGINATOR_APPROVAL,
            reward_source=RewardSource.EXTERNAL_HUMAN,
            magnitude=base_du,
            predicted_du=approval_strength * 0.5,
            context=context or {},
        )

    def calculate_learning_du(
        self,
        learning_type: str,
        complexity: float,
        novelty: float,
        context: dict[str, Any] | None = None,
    ) -> DopamineEvent:
        """Calculate DU from learning events."""
        base_du = (complexity * 0.3 + novelty * 0.7) * 0.4

        event_type_map = {
            "pattern_discovery": EventType.PATTERN_DISCOVERED,
            "knowledge_integration": EventType.KNOWLEDGE_INTEGRATED,
            "problem_solving": EventType.PROBLEM_SOLVED,
            "optimization": EventType.OPTIMIZATION_ACHIEVED,
        }

        event_type = event_type_map.get(learning_type, EventType.KNOWLEDGE_INTEGRATED)

        return DopamineEvent(
            event_type=event_type,
            reward_source=RewardSource.INTRINSIC,
            magnitude=base_du,
            predicted_du=complexity * 0.2,
            context={
                "learning_type": learning_type,
                "complexity": complexity,
                "novelty": novelty,
                **(context or {}),
            },
        )

    def _calculate_surprise_factor(
        self,
        actual_value: float,
        expected_value: float,
        confidence: float,
    ) -> float:
        """Calculate surprise factor based on prediction error and confidence."""
        try:
            # Calculate relative prediction error
            if abs(expected_value) > 0.001:
                relative_error = abs(actual_value - expected_value) / abs(
                    expected_value,
                )
            else:
                relative_error = abs(actual_value - expected_value)

            # Higher confidence makes surprises more impactful
            confidence_factor = 0.5 + (confidence * 0.5)

            # Calculate surprise factor
            surprise = 1.0 + (
                relative_error * confidence_factor * self.surprise_amplification
            )

            # Cap surprise factor to prevent extreme values
            return min(surprise, 5.0)

        except Exception as e:
            logger.exception(f"Failed to calculate surprise factor: {e}")
            return 1.0

    def _create_neutral_event(self, error_context: str) -> DopamineEvent:
        """Create a neutral dopamine event for error cases."""
        return DopamineEvent(
            event_type=EventType.SYSTEM_HEALTH_POOR,
            reward_source=RewardSource.EXTERNAL_SYSTEM,
            magnitude=0.0,
            context={"error": error_context},
        )
