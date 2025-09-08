"""Dopamine System for Project Starfire - Synthetic Neuromodulatory Framework.

This module implements the Dopamine Core as specified in the white paper:
"The Dopamine Core: A Synthetic Neuromodulatory Framework for Sentient AI in vibe_trading_app Systems"

The Dopamine System provides:
- Dopamine Units (DU) for scalar reward signals
- Dopamine Reservoir for mood and motivational state tracking
- Reward Prediction Error (RPE) for learning and adaptation
- Behavioral modulation based on emotional weather
- Integration with Trading Brain performance tracking

Author: Project Starfire - Dopamine System Integration
"""

from .behavioral_modulation import (
    BehavioralBias,
    BehavioralModulator,
    ExplorationState,
)
from .dopamine_calculator import (
    DopamineCalculator,
    TradingOutcome,
)
from .dopamine_core import (
    DopamineCore,
    DopamineEvent,
    DopamineReservoir,
    DopamineUnit,
    EmotionalWeather,
    EventType,
    RewardPredictionError,
    RewardSource,
)
from .safety_monitor import (
    AddictionDetector,
    BurnoutDetector,
    CorruptionDetector,
    DopamineSafetyMonitor,
    InterventionType,
    SafetyAlert,
    SafetyLevel,
)

__all__ = [
    # Core components
    "DopamineCore",
    "DopamineUnit",
    "DopamineReservoir",
    "DopamineEvent",
    "RewardPredictionError",
    "EmotionalWeather",
    "EventType",
    "RewardSource",
    # Calculator and event processing
    "DopamineCalculator",
    "TradingOutcome",
    # Behavioral modulation
    "BehavioralModulator",
    "BehavioralBias",
    "ExplorationState",
    # Safety and monitoring
    "DopamineSafetyMonitor",
    "AddictionDetector",
    "BurnoutDetector",
    "CorruptionDetector",
    "SafetyAlert",
    "SafetyLevel",
    "InterventionType",
]

__version__ = "1.0.0"
