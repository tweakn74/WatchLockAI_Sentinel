"""Behavioral anomaly detection system (two-tier: stdlib-only + optional sklearn).

Tier A: Standard library only with z-score/MAD-based scoring and rolling windows
Tier B: Optional sklearn integration with IsolationForest when available

Feature flags:
- ANOMALY_ENABLED=0 (default OFF)
- ANOMALY_SKLEARN_ENABLED=0 (optional, OFF)
"""

from __future__ import annotations

import json
import os
import pickle
import statistics
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Feature flags
ANOMALY_ENABLED = os.getenv("ANOMALY_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
ANOMALY_SKLEARN_ENABLED = os.getenv("ANOMALY_SKLEARN_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}

# Data persistence paths
ANOMALY_STATE_DIR = Path("data/anomaly")
ANOMALY_STATE_FILE = ANOMALY_STATE_DIR / "state.json"
MODELS_DIR = Path("models")
IFOREST_MODEL_FILE = MODELS_DIR / "anomaly_iforest.pkl"


class AnomalyState:
    """Persistent state for anomaly detection."""
    
    def __init__(self):
        self.window_data: List[Dict[str, Any]] = []
        self.feature_stats: Dict[str, Dict[str, float]] = {}
        self.last_updated: float = time.time()
        self._lock = threading.Lock()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        with self._lock:
            return {
                "window_data": self.window_data,
                "feature_stats": self.feature_stats,
                "last_updated": self.last_updated
            }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize state from dictionary."""
        with self._lock:
            self.window_data = data.get("window_data", [])
            self.feature_stats = data.get("feature_stats", {})
            self.last_updated = data.get("last_updated", time.time())
    
    def save_to_file(self) -> None:
        """Persist state to JSON file."""
        try:
            ANOMALY_STATE_DIR.mkdir(parents=True, exist_ok=True)
            with open(ANOMALY_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception:
            # Swallow errors to maintain stability
            pass
    
    def load_from_file(self) -> None:
        """Load state from JSON file."""
        try:
            if ANOMALY_STATE_FILE.exists():
                with open(ANOMALY_STATE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.from_dict(data)
        except Exception:
            # Initialize with empty state on error
            self.from_dict({})


class AnomalyDetector:
    """Behavioral anomaly detection with two-tier approach."""
    
    def __init__(self, max_window_size: int = 100):
        self.max_window_size = max_window_size
        self.state = AnomalyState()
        self.state.load_from_file()
        self._isolation_forest = None
        self._sklearn_available = False
        
        # Check sklearn availability if enabled
        if ANOMALY_SKLEARN_ENABLED:
            try:
                import sklearn.ensemble  # type: ignore
                self._sklearn_available = True
            except ImportError:
                self._sklearn_available = False
    
    def extract_features(self, event_data: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """Extract feature vector from current system state.
        
        Args:
            event_data: Optional event data to extract features from
            
        Returns:
            Dictionary of extracted features with numeric values
        """
        features = {}
        current_time = time.time()
        
        # Time-based features
        features["hour_of_day"] = datetime.now().hour
        features["day_of_week"] = datetime.now().weekday()
        
        # System load features (placeholder - would use actual system metrics)
        features["cpu_usage_pct"] = 0.0  # Would integrate with actual system monitoring
        features["memory_usage_pct"] = 0.0
        features["disk_io_rate"] = 0.0
        features["network_io_rate"] = 0.0
        
        # Event-based features (if event data provided)
        if event_data:
            features["event_count"] = len(event_data.get("events", []))
            features["error_count"] = len([e for e in event_data.get("events", []) if e.get("level") == "error"])
            features["unique_sources"] = len(set(e.get("source", "") for e in event_data.get("events", [])))
        else:
            features["event_count"] = 0.0
            features["error_count"] = 0.0
            features["unique_sources"] = 0.0
        
        # Activity pattern features
        features["time_since_last_activity"] = current_time - self.state.last_updated
        
        return features
    
    def calculate_z_score(self, feature_name: str, value: float) -> float:
        """Calculate z-score for a feature value."""
        stats = self.state.feature_stats.get(feature_name, {})
        mean = stats.get("mean", value)
        std = stats.get("std", 1.0)
        
        if std == 0:
            return 0.0
        
        return abs(value - mean) / std
    
    def calculate_mad_score(self, feature_name: str, value: float) -> float:
        """Calculate Modified Z-Score using Median Absolute Deviation."""
        with self.state._lock:
            # Get recent values for this feature
            recent_values = [
                record.get("features", {}).get(feature_name, value) 
                for record in self.state.window_data[-50:]  # Use last 50 values
                if feature_name in record.get("features", {})
            ]
            
            if len(recent_values) < 2:
                return 0.0
            
            median = statistics.median(recent_values)
            mad = statistics.median([abs(v - median) for v in recent_values])
            
            if mad == 0:
                return 0.0
            
            return abs(value - median) / (1.4826 * mad)
    
    def update_feature_stats(self, features: Dict[str, float]) -> None:
        """Update rolling statistics for features."""
        with self.state._lock:
            for feature_name, value in features.items():
                if feature_name not in self.state.feature_stats:
                    self.state.feature_stats[feature_name] = {
                        "mean": value,
                        "std": 1.0,
                        "count": 1
                    }
                else:
                    stats = self.state.feature_stats[feature_name]
                    count = stats["count"]
                    old_mean = stats["mean"]
                    
                    # Update running statistics
                    new_count = count + 1
                    new_mean = (old_mean * count + value) / new_count
                    
                    # Update variance (simplified)
                    if new_count > 1:
                        variance = stats.get("variance", 1.0)
                        new_variance = ((count * variance + (value - old_mean) * (value - new_mean)) / new_count)
                        stats["std"] = max(new_variance ** 0.5, 0.01)  # Minimum std to avoid division by zero
                    
                    stats["mean"] = new_mean
                    stats["count"] = new_count
    
    def add_observation(self, event_data: Optional[Dict[str, Any]] = None) -> None:
        """Add new observation to the rolling window."""
        features = self.extract_features(event_data)
        timestamp = time.time()
        
        observation = {
            "timestamp": timestamp,
            "features": features
        }
        
        with self.state._lock:
            self.state.window_data.append(observation)
            
            # Maintain window size
            if len(self.state.window_data) > self.max_window_size:
                self.state.window_data = self.state.window_data[-self.max_window_size:]
            
            self.state.last_updated = timestamp
        
        # Update feature statistics
        self.update_feature_stats(features)
        
        # Persist state
        self.state.save_to_file()
    
    def compute_anomaly_score(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Compute anomaly score using Tier A (stdlib-only) approach.
        
        Args:
            window_minutes: Time window in minutes to analyze
            
        Returns:
            Dictionary containing score, count, and details
        """
        if not ANOMALY_ENABLED:
            return {"score": 0.0, "n": 0, "enabled": False}
        
        current_time = time.time()
        cutoff_time = current_time - (window_minutes * 60)
        
        with self.state._lock:
            # Filter observations within window
            recent_observations = [
                obs for obs in self.state.window_data 
                if obs["timestamp"] >= cutoff_time
            ]
        
        if len(recent_observations) < 2:
            return {"score": 0.0, "n": len(recent_observations), "enabled": True}
        
        # Calculate anomaly scores for each observation
        anomaly_scores = []
        for obs in recent_observations:
            features = obs["features"]
            obs_scores = []
            
            for feature_name, value in features.items():
                # Use both z-score and MAD score
                z_score = self.calculate_z_score(feature_name, value)
                mad_score = self.calculate_mad_score(feature_name, value)
                
                # Combine scores (weighted average)
                combined_score = (z_score * 0.6) + (mad_score * 0.4)
                obs_scores.append(combined_score)
            
            if obs_scores:
                # Use max score as the observation's anomaly score
                anomaly_scores.append(max(obs_scores))
        
        if not anomaly_scores:
            final_score = 0.0
        else:
            # Use 95th percentile as final anomaly score
            anomaly_scores.sort()
            percentile_95_idx = int(len(anomaly_scores) * 0.95)
            final_score = anomaly_scores[min(percentile_95_idx, len(anomaly_scores) - 1)]
        
        return {
            "score": round(final_score, 3),
            "n": len(recent_observations),
            "enabled": True,
            "window_minutes": window_minutes,
            "sklearn_available": self._sklearn_available
        }
    
    def train_isolation_forest(self) -> Dict[str, Any]:
        """Train Isolation Forest model (Tier B - sklearn required).
        
        Returns:
            Training status and model information
        """
        if not ANOMALY_ENABLED or not ANOMALY_SKLEARN_ENABLED:
            return {"status": "disabled", "sklearn_available": self._sklearn_available}
        
        if not self._sklearn_available:
            return {"status": "sklearn_unavailable", "sklearn_available": False}
        
        with self.state._lock:
            if len(self.state.window_data) < 10:
                return {"status": "insufficient_data", "n_samples": len(self.state.window_data)}
        
        try:
            from sklearn.ensemble import IsolationForest  # type: ignore
            import numpy as np  # type: ignore
            
            # Prepare training data
            features_list = []
            for obs in self.state.window_data:
                features = obs["features"]
                feature_values = list(features.values())
                features_list.append(feature_values)
            
            if not features_list or not features_list[0]:
                return {"status": "no_features"}
            
            X = np.array(features_list)
            
            # Train Isolation Forest
            self._isolation_forest = IsolationForest(
                contamination=0.1,  # Assume 10% contamination
                random_state=42,
                n_estimators=100
            )
            self._isolation_forest.fit(X)
            
            # Save model to disk
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            with open(IFOREST_MODEL_FILE, 'wb') as f:
                pickle.dump(self._isolation_forest, f)
            
            return {
                "status": "training_complete",
                "n_samples": len(features_list),
                "n_features": len(features_list[0]),
                "model_saved": str(IFOREST_MODEL_FILE)
            }
            
        except Exception as e:
            return {"status": "training_failed", "error": str(e)}
    
    def load_isolation_forest(self) -> bool:
        """Load pre-trained Isolation Forest model."""
        if not self._sklearn_available or not IFOREST_MODEL_FILE.exists():
            return False
        
        try:
            with open(IFOREST_MODEL_FILE, 'rb') as f:
                self._isolation_forest = pickle.load(f)
            return True
        except Exception:
            return False
    
    def predict_with_isolation_forest(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict anomaly using Isolation Forest (if available)."""
        if not self._isolation_forest:
            return {"available": False}
        
        try:
            import numpy as np  # type: ignore
            
            feature_values = list(features.values())
            X = np.array([feature_values])
            
            # Get anomaly score (-1 for anomaly, 1 for normal)
            prediction = self._isolation_forest.predict(X)[0]
            anomaly_score = self._isolation_forest.decision_function(X)[0]
            
            return {
                "available": True,
                "prediction": int(prediction),
                "anomaly_score": float(anomaly_score),
                "is_anomaly": prediction == -1
            }
            
        except Exception as e:
            return {"available": True, "error": str(e)}


# Global detector instance
_detector: Optional[AnomalyDetector] = None


def get_detector() -> AnomalyDetector:
    """Get or create global anomaly detector instance."""
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
    return _detector


def add_observation(event_data: Optional[Dict[str, Any]] = None) -> None:
    """Add observation to anomaly detection system."""
    if ANOMALY_ENABLED:
        detector = get_detector()
        detector.add_observation(event_data)


def compute_anomaly_score(window_minutes: int = 60) -> Dict[str, Any]:
    """Compute current anomaly score."""
    detector = get_detector()
    return detector.compute_anomaly_score(window_minutes)


def train_isolation_forest() -> Dict[str, Any]:
    """Train Isolation Forest model."""
    detector = get_detector()
    return detector.train_isolation_forest()
