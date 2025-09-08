"""ML Scoring module implementing ml_scoring.md specifications.

This module provides a typed interface for ML-based behavior scoring.
No model artifact is provided in the Knowledge Pack, so this is implemented as a stub.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from loguru import logger


class MLScoringEngine:
    """ML scoring engine with typed interface per ml_scoring.md specifications."""

    def __init__(self, model_path: str | None = None) -> None:
        """Initialize ML scoring engine.

        Args:
            model_path: Path to model file (e.g., models/model.pkl). If None or file doesn't exist,
                       scoring will be disabled.
        """
        self.model_path = model_path
        self.model: Any | None = None
        self.model_loaded = False
        self.model_info: dict[str, Any] = {}

        if model_path:
            self._try_load_model(model_path)

        logger.info(f"MLScoringEngine initialized: model_loaded={self.model_loaded}, path={model_path}")

    def _try_load_model(self, model_path: str) -> None:
        """Attempt to load ML model from file.

        Args:
            model_path: Path to model file.
        """
        try:
            model_file = Path(model_path)

            if not model_file.exists():
                logger.info(f"ML model file not found: {model_path}")
                return

            logger.info(f"Loading ML model from: {model_path}")

            # Try to load pickle model
            with open(model_file, "rb") as f:
                self.model = pickle.load(f)

            self.model_loaded = True

            # Try to extract model metadata
            self.model_info = {
                "file_path": str(model_file.absolute()),
                "file_size_mb": round(model_file.stat().st_size / (1024 * 1024), 2),
                "model_type": type(self.model).__name__,
            }

            # Check for common model attributes
            if hasattr(self.model, "feature_names_in_"):
                self.model_info["feature_names"] = list(self.model.feature_names_in_)

            if hasattr(self.model, "classes_"):
                self.model_info["classes"] = list(self.model.classes_)

            logger.info(f"ML model loaded successfully: {self.model_info}")

        except Exception as e:
            logger.warning(f"Failed to load ML model from {model_path}: {e}")
            self.model = None
            self.model_loaded = False

    def score_behavior(self, signal: dict[str, Any]) -> tuple[float, str] | None:
        """Score behavior signal using loaded ML model.

        Args:
            signal: Dictionary containing behavior signal features.
                   Expected keys depend on the specific model used.

        Returns:
            Tuple of (score, rationale) where score is 0.0-1.0 confidence,
            or None if no model is available or scoring fails.

        Note:
            This is the main interface specified in ml_scoring.md.
            Implementation is model-dependent and requires a trained model artifact.
        """
        if not self.model_loaded or not self.model:
            logger.debug("ML scoring requested but no model available")
            return None

        try:
            # This is a generic implementation - actual behavior depends on model type
            score, rationale = self._score_with_model(signal)

            logger.debug(f"ML scoring result: score={score:.3f}, rationale='{rationale}'")
            return score, rationale

        except Exception as e:
            logger.error(f"ML scoring failed: {e}")
            return None

    def _score_with_model(self, signal: dict[str, Any]) -> tuple[float, str]:
        """Internal method to score signal with loaded model.

        Args:
            signal: Signal dictionary to score.

        Returns:
            Tuple of (score, rationale).

        Raises:
            ValueError: If signal format is invalid for the model.
            RuntimeError: If model prediction fails.
        """
        # This is a placeholder implementation since no specific model is provided
        # Real implementation would depend on the model type and expected input format

        # Example for scikit-learn style models:
        if hasattr(self.model, "predict_proba"):
            # Extract features based on model expectations
            features = self._extract_features(signal)

            # Get prediction probabilities
            probabilities = self.model.predict_proba([features])[0]

            # Assume binary classification (benign/malicious)
            if len(probabilities) >= 2:
                malicious_score = probabilities[1]  # Probability of malicious class
                rationale = f"ML model confidence: {malicious_score:.3f}"
                return float(malicious_score), rationale
            return None

        # Example for custom models with score method
        elif hasattr(self.model, "score"):
            score = self.model.score(signal)
            rationale = f"Custom model score: {score:.3f}"
            return float(score), rationale

        # Fallback for unknown model types
        else:
            logger.warning(f"Unknown model type: {type(self.model).__name__}")
            return 0.5, "Unknown model type - neutral score"

    def _extract_features(self, signal: dict[str, Any]) -> list[float]:
        """Extract numerical features from signal dictionary.

        Args:
            signal: Signal dictionary containing raw behavior data.

        Returns:
            List of numerical features for model input.

        Note:
            This is a placeholder implementation. Real feature extraction
            would depend on the specific model's training data format.
        """
        # Example feature extraction (placeholder)
        features = []

        # File-related features
        if "file_ops_count" in signal:
            features.append(float(signal["file_ops_count"]))

        if "entropy_avg" in signal:
            features.append(float(signal["entropy_avg"]))

        if "distinct_extensions" in signal:
            features.append(float(signal["distinct_extensions"]))

        # Process-related features
        if "process_count" in signal:
            features.append(float(signal["process_count"]))

        if "suspicious_children" in signal:
            features.append(float(signal["suspicious_children"]))

        # Network-related features
        if "network_connections" in signal:
            features.append(float(signal["network_connections"]))

        if "distinct_ips" in signal:
            features.append(float(signal["distinct_ips"]))

        # Health-related features
        if "cpu_usage" in signal:
            features.append(float(signal["cpu_usage"]))

        if "memory_usage" in signal:
            features.append(float(signal["memory_usage"]))

        # Ensure we have the expected number of features
        # This would be determined by the specific trained model
        expected_features = getattr(self.model, "n_features_in_", 10)

        # Pad or truncate to expected size
        if len(features) < expected_features:
            features.extend([0.0] * (expected_features - len(features)))
        elif len(features) > expected_features:
            features = features[:expected_features]

        return features

    def is_available(self) -> bool:
        """Check if ML scoring is available.

        Returns:
            True if model is loaded and scoring is available.
        """
        return self.model_loaded and self.model is not None

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the loaded model.

        Returns:
            Dictionary with model metadata and capabilities.
        """
        info = {
            "available": self.is_available(),
            "model_path": self.model_path,
            "model_loaded": self.model_loaded,
        }

        if self.model_loaded:
            info.update(self.model_info)

        return info

    def validate_signal(self, signal: dict[str, Any]) -> bool:
        """Validate that signal contains required features for scoring.

        Args:
            signal: Signal dictionary to validate.

        Returns:
            True if signal is valid for scoring.
        """
        if not self.is_available():
            return False

        # Basic validation - signal should be a non-empty dictionary
        if not isinstance(signal, dict) or not signal:
            return False

        # Check for numeric values
        try:
            features = self._extract_features(signal)
            return len(features) > 0 and all(isinstance(f, int | float) for f in features)
        except Exception:
            return False


# Factory function for easy instantiation
def create_ml_scorer(model_path: str | None = None) -> MLScoringEngine:
    """Create ML scoring engine with optional model path.

    Args:
        model_path: Path to model file. If None, checks default location.

    Returns:
        MLScoringEngine instance.
    """
    if model_path is None:
        # Check default model location
        default_path = Path("models/model.pkl")
        if default_path.exists():
            model_path = str(default_path)

    return MLScoringEngine(model_path)


# Global instance (lazy initialization)
_ml_scorer: MLScoringEngine | None = None


def get_ml_scorer() -> MLScoringEngine:
    """Get global ML scoring engine instance.

    Returns:
        Global MLScoringEngine instance.
    """
    global _ml_scorer
    if _ml_scorer is None:
        _ml_scorer = create_ml_scorer()
    return _ml_scorer
