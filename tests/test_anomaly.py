"""Tests for anomaly detection system (P2-001).

Tests both Tier A (stdlib-only) and Tier B (sklearn optional) functionality.
"""

import json
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

# Test with environment override to ensure testing works
os.environ["ANOMALY_ENABLED"] = "1"

try:
    from console.anomaly import (
        AnomalyDetector, AnomalyState, add_observation, 
        compute_anomaly_score, train_isolation_forest,
        get_detector, ANOMALY_ENABLED, ANOMALY_SKLEARN_ENABLED
    )
    ANOMALY_MODULE_AVAILABLE = True
except ImportError:
    ANOMALY_MODULE_AVAILABLE = False


class TestAnomalyState(unittest.TestCase):
    """Test AnomalyState class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not ANOMALY_MODULE_AVAILABLE:
            self.skipTest("Anomaly detection module not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "test_state.json"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_state_serialization(self):
        """Test state serialization and deserialization."""
        state = AnomalyState()
        
        # Add some test data
        test_data = {
            "timestamp": time.time(),
            "features": {"cpu_usage": 50.0, "memory_usage": 75.0}
        }
        state.window_data.append(test_data)
        state.feature_stats["cpu_usage"] = {"mean": 45.0, "std": 10.0, "count": 5}
        
        # Test to_dict
        data = state.to_dict()
        self.assertIn("window_data", data)
        self.assertIn("feature_stats", data)
        self.assertIn("last_updated", data)
        self.assertEqual(len(data["window_data"]), 1)
        
        # Test from_dict
        new_state = AnomalyState()
        new_state.from_dict(data)
        self.assertEqual(len(new_state.window_data), 1)
        self.assertIn("cpu_usage", new_state.feature_stats)
        self.assertEqual(new_state.feature_stats["cpu_usage"]["mean"], 45.0)
    
    def test_state_persistence(self):
        """Test state file persistence."""
        state = AnomalyState()
        
        # Mock the state file path
        with mock.patch('console.anomaly.ANOMALY_STATE_FILE', self.state_file):
            # Add test data
            test_data = {"timestamp": time.time(), "features": {"test_feature": 123.0}}
            state.window_data.append(test_data)
            
            # Save to file
            state.save_to_file()
            self.assertTrue(self.state_file.exists())
            
            # Load from file
            new_state = AnomalyState()
            new_state.load_from_file()
            self.assertEqual(len(new_state.window_data), 1)
            self.assertEqual(new_state.window_data[0]["features"]["test_feature"], 123.0)


class TestAnomalyDetector(unittest.TestCase):
    """Test AnomalyDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not ANOMALY_MODULE_AVAILABLE:
            self.skipTest("Anomaly detection module not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "test_state.json"
        self.models_dir = Path(self.temp_dir) / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        # Mock paths
        self.state_patcher = mock.patch('console.anomaly.ANOMALY_STATE_FILE', self.state_file)
        self.models_patcher = mock.patch('console.anomaly.IFOREST_MODEL_FILE', self.models_dir / "test_model.pkl")
        
        self.state_patcher.start()
        self.models_patcher.start()
        
        self.detector = AnomalyDetector(max_window_size=10)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'state_patcher'):
            self.state_patcher.stop()
        if hasattr(self, 'models_patcher'):
            self.models_patcher.stop()
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_feature_extraction(self):
        """Test feature extraction."""
        features = self.detector.extract_features()
        
        # Check basic features are present
        self.assertIn("hour_of_day", features)
        self.assertIn("day_of_week", features)
        self.assertIn("cpu_usage_pct", features)
        self.assertIn("memory_usage_pct", features)
        
        # Check feature value ranges
        self.assertGreaterEqual(features["hour_of_day"], 0)
        self.assertLessEqual(features["hour_of_day"], 23)
        self.assertGreaterEqual(features["day_of_week"], 0)
        self.assertLessEqual(features["day_of_week"], 6)
    
    def test_feature_extraction_with_events(self):
        """Test feature extraction with event data."""
        event_data = {
            "events": [
                {"level": "info", "source": "collector1"},
                {"level": "error", "source": "collector2"},
                {"level": "warning", "source": "collector1"}
            ]
        }
        
        features = self.detector.extract_features(event_data)
        
        self.assertEqual(features["event_count"], 3)
        self.assertEqual(features["error_count"], 1)
        self.assertEqual(features["unique_sources"], 2)
    
    def test_z_score_calculation(self):
        """Test z-score calculation."""
        # Add some observations to build statistics
        for i in range(5):
            self.detector.update_feature_stats({"test_feature": 10.0 + i})
        
        z_score = self.detector.calculate_z_score("test_feature", 20.0)
        self.assertGreater(z_score, 0)  # Should be anomalous
        
        z_score_normal = self.detector.calculate_z_score("test_feature", 12.0)
        self.assertLess(z_score_normal, z_score)  # Should be less anomalous
    
    def test_mad_score_calculation(self):
        """Test MAD (Median Absolute Deviation) score calculation."""
        # Add observations to the window
        test_values = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        for value in test_values:
            observation = {
                "timestamp": time.time(),
                "features": {"test_feature": float(value)}
            }
            self.detector.state.window_data.append(observation)
        
        mad_score = self.detector.calculate_mad_score("test_feature", 25.0)
        self.assertGreater(mad_score, 0)  # Should be anomalous
        
        mad_score_normal = self.detector.calculate_mad_score("test_feature", 15.0)
        self.assertLess(mad_score_normal, mad_score)  # Should be less anomalous
    
    def test_add_observation(self):
        """Test adding observations."""
        initial_count = len(self.detector.state.window_data)
        
        self.detector.add_observation()
        self.assertEqual(len(self.detector.state.window_data), initial_count + 1)
        
        # Test with event data
        event_data = {"events": [{"level": "info", "source": "test"}]}
        self.detector.add_observation(event_data)
        self.assertEqual(len(self.detector.state.window_data), initial_count + 2)
    
    def test_window_size_limit(self):
        """Test window size is properly limited."""
        # Add more observations than the max window size
        for i in range(15):  # Max window size is 10
            self.detector.add_observation()
        
        self.assertEqual(len(self.detector.state.window_data), 10)
    
    def test_compute_anomaly_score(self):
        """Test anomaly score computation."""
        # Add some normal observations
        for i in range(10):
            event_data = {"events": [{"level": "info", "source": f"source_{i % 3}"}]}
            self.detector.add_observation(event_data)
        
        result = self.detector.compute_anomaly_score(window_minutes=60)
        
        self.assertIn("score", result)
        self.assertIn("n", result)
        self.assertIn("enabled", result)
        self.assertTrue(result["enabled"])
        self.assertGreaterEqual(result["score"], 0.0)
        self.assertGreater(result["n"], 0)
    
    def test_compute_anomaly_score_disabled(self):
        """Test anomaly score when disabled."""
        with mock.patch('console.anomaly.ANOMALY_ENABLED', False):
            detector = AnomalyDetector()
            result = detector.compute_anomaly_score()
            
            self.assertFalse(result["enabled"])
            self.assertEqual(result["score"], 0.0)
    
    def test_compute_anomaly_score_insufficient_data(self):
        """Test anomaly score with insufficient data."""
        result = self.detector.compute_anomaly_score()
        
        # Should handle empty data gracefully
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["n"], 0)
    
    @mock.patch('console.anomaly.ANOMALY_SKLEARN_ENABLED', True)
    def test_train_isolation_forest_sklearn_unavailable(self):
        """Test Isolation Forest training when sklearn unavailable."""
        with mock.patch.object(self.detector, '_sklearn_available', False):
            result = self.detector.train_isolation_forest()
            
            self.assertEqual(result["status"], "sklearn_unavailable")
            self.assertFalse(result["sklearn_available"])
    
    @mock.patch('console.anomaly.ANOMALY_SKLEARN_ENABLED', True)
    def test_train_isolation_forest_insufficient_data(self):
        """Test Isolation Forest training with insufficient data."""
        with mock.patch.object(self.detector, '_sklearn_available', True):
            result = self.detector.train_isolation_forest()
            
            self.assertEqual(result["status"], "insufficient_data")
    
    def test_feature_stats_update(self):
        """Test feature statistics updates."""
        features = {"test_feature": 10.0}
        self.detector.update_feature_stats(features)
        
        stats = self.detector.state.feature_stats["test_feature"]
        self.assertEqual(stats["mean"], 10.0)
        self.assertEqual(stats["count"], 1)
        
        # Add another observation
        self.detector.update_feature_stats({"test_feature": 20.0})
        stats = self.detector.state.feature_stats["test_feature"]
        self.assertEqual(stats["mean"], 15.0)  # (10 + 20) / 2
        self.assertEqual(stats["count"], 2)


class TestAnomalyFunctions(unittest.TestCase):
    """Test module-level functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not ANOMALY_MODULE_AVAILABLE:
            self.skipTest("Anomaly detection module not available")
    
    def test_global_detector(self):
        """Test global detector singleton."""
        detector1 = get_detector()
        detector2 = get_detector()
        self.assertIs(detector1, detector2)  # Should be the same instance
    
    def test_add_observation_function(self):
        """Test module-level add_observation function."""
        detector = get_detector()
        initial_count = len(detector.state.window_data)
        
        add_observation()
        self.assertEqual(len(detector.state.window_data), initial_count + 1)
    
    def test_compute_anomaly_score_function(self):
        """Test module-level compute_anomaly_score function."""
        result = compute_anomaly_score(window_minutes=30)
        
        self.assertIn("score", result)
        self.assertIn("n", result)
        self.assertIn("enabled", result)
    
    def test_train_isolation_forest_function(self):
        """Test module-level train_isolation_forest function."""
        result = train_isolation_forest()
        
        self.assertIn("status", result)
        # Status will depend on sklearn availability and data


class TestAnomalyConfiguration(unittest.TestCase):
    """Test anomaly detection configuration."""
    
    def test_feature_flags(self):
        """Test feature flag parsing."""
        # ANOMALY_ENABLED should be True due to setUp
        self.assertTrue(ANOMALY_ENABLED)
        
        # ANOMALY_SKLEARN_ENABLED should default to False
        self.assertFalse(ANOMALY_SKLEARN_ENABLED)
    
    def test_paths_configuration(self):
        """Test paths are properly configured."""
        from console.anomaly import ANOMALY_STATE_DIR, ANOMALY_STATE_FILE, MODELS_DIR
        
        self.assertEqual(ANOMALY_STATE_DIR, Path("data/anomaly"))
        self.assertEqual(ANOMALY_STATE_FILE, ANOMALY_STATE_DIR / "state.json")
        self.assertEqual(MODELS_DIR, Path("models"))


if __name__ == "__main__":
    unittest.main()
