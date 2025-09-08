"""Tests for operational mode storage, API, and enforcement.

Comprehensive test suite covering:
- Storage round-trip operations
- API GET/PUT endpoints
- Enforcement behavior across all modes
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

try:
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TestClient = None

from app_core.config import OperationalConfig, ResponsesConfig

# Test the storage module
from config.operational_mode import (
    DEFAULT_MODE,
    VALID_MODES,
    _invalidate_cache,
    get_mode,
    get_valid_modes,
    is_valid_mode,
    set_mode,
)

# Test the API
from console.api.operational_mode import router

# Test enforcement
from response.actions import ActionResult, ResponseActionsManager


class TestOperationalModeStorage(unittest.TestCase):
    """Test the storage module functionality."""
    
    def setUp(self):
        """Set up test environment"""
        if not FASTAPI_AVAILABLE:
            self.skipTest("FastAPI not available")
        """Setup for each test."""
        # Invalidate cache before each test
        _invalidate_cache()

    def test_default_mode(self):
        """Test default mode is returned when no file exists."""
        with patch('config.operational_mode._get_config_file_path') as mock_path:
            # Mock a non-existent file
            mock_path.return_value = Path('/nonexistent/operational_mode.json')
            
            mode = get_mode()
            assert mode == DEFAULT_MODE

    def test_valid_modes(self):
        """Test valid modes list and validation."""
        valid_modes = get_valid_modes()
        assert len(valid_modes) == 5
        assert set(valid_modes) == VALID_MODES
        
        # Test validation
        for mode in VALID_MODES:
            assert is_valid_mode(mode)
            
        assert not is_valid_mode("invalid_mode")
        assert not is_valid_mode("")

    def test_set_get_mode_round_trip(self):
        """Test setting and getting modes with file persistence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "operational_mode.json"
            
            with patch('config.operational_mode._get_config_file_path') as mock_path:
                mock_path.return_value = config_file
                
                # Test each valid mode
                for test_mode in VALID_MODES:
                    _invalidate_cache()  # Force reload from file
                    set_mode(test_mode)  # type: ignore[arg-type]
                    retrieved_mode = get_mode()
                    assert retrieved_mode == test_mode
                    
                    # Verify file was created and contains correct data
                    assert config_file.exists()
                    with config_file.open('r') as f:
                        data = json.load(f)
                    assert data["mode"] == test_mode
                    assert "last_updated" in data

    def test_invalid_mode_raises_error(self):
        """Test that setting invalid modes raises ValueError."""
        with pytest.raises(ValueError, match="Invalid operational mode"):
            set_mode("invalid_mode")  # type: ignore[arg-type]

    def test_atomic_write(self):
        """Test that writes are atomic (temp file approach)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "operational_mode.json"
            
            with patch('config.operational_mode._get_config_file_path') as mock_path:
                mock_path.return_value = config_file
                
                # Set initial mode
                set_mode("observe")  # type: ignore[arg-type]
                
                # Verify no .tmp file remains
                temp_files = list(Path(temp_dir).glob("*.tmp"))
                assert len(temp_files) == 0

    def test_thread_safety(self):
        """Test thread-safe operations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(mode_suffix):
            try:
                test_mode = "alert" if mode_suffix % 2 == 0 else "contain"
                set_mode(test_mode)  # type: ignore[arg-type]
                time.sleep(0.01)  # Small delay
                retrieved = get_mode()
                results.append(retrieved)
            except Exception as e:
                errors.append(e)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "operational_mode.json"
            
            with patch('config.operational_mode._get_config_file_path') as mock_path:
                mock_path.return_value = config_file
                
                # Create multiple threads
                threads = []
                for i in range(10):
                    thread = threading.Thread(target=worker, args=(i,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads
                for thread in threads:
                    thread.join()
                
                # Check results
                self.assertEqual(len(errors), 0, f"Thread errors: {errors}")
                self.assertEqual(len(results), 10)
                
                # All results should be valid modes
                for result in results:
                    self.assertIn(result, VALID_MODES)


class TestOperationalModeAPI(unittest.TestCase):
    """Test the FastAPI endpoints."""
    
    def setUp(self):
        """Set up test environment"""
        if not FASTAPI_AVAILABLE:
            self.skipTest("FastAPI not available")
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def test_get_operational_mode(self, client):
        """Test GET /api/operational_mode endpoint."""
        with patch('config.operational_mode.get_mode') as mock_get:
            mock_get.return_value = "alert"
            
            response = client.get("/api/operational_mode")
            
            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == "alert"
            assert "timestamp" in data

    def test_get_operational_mode_error(self, client):
        """Test GET endpoint error handling."""
        with patch('config.operational_mode.get_mode') as mock_get:
            mock_get.side_effect = Exception("Storage error")
            
            response = client.get("/api/operational_mode")
            
            assert response.status_code == 500
            assert "Failed to get operational mode" in response.json()["detail"]

    def test_put_operational_mode_success(self, client):
        """Test successful PUT /api/operational_mode."""
        with patch('config.operational_mode.set_mode') as mock_set, \
             patch('config.operational_mode.is_valid_mode') as mock_valid, \
             patch('config.operational_mode.get_valid_modes') as mock_modes:
            
            mock_valid.return_value = True
            mock_modes.return_value = list(VALID_MODES)
            
            response = client.put("/api/operational_mode", json={"mode": "contain"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["mode"] == "contain"
            assert "successfully set" in data["message"]
            assert "timestamp" in data
            
            mock_set.assert_called_once_with("contain")

    def test_put_operational_mode_invalid(self, client):
        """Test PUT with invalid mode."""
        with patch('config.operational_mode.is_valid_mode') as mock_valid, \
             patch('config.operational_mode.get_valid_modes') as mock_modes:
            
            mock_valid.return_value = False
            mock_modes.return_value = list(VALID_MODES)
            
            response = client.put("/api/operational_mode", json={"mode": "invalid"})
            
            assert response.status_code == 400
            assert "Invalid operational mode 'invalid'" in response.json()["detail"]

    def test_put_operational_mode_storage_error(self, client):
        """Test PUT with storage error."""
        with patch('config.operational_mode.set_mode') as mock_set, \
             patch('config.operational_mode.is_valid_mode') as mock_valid:
            
            mock_valid.return_value = True
            mock_set.side_effect = OSError("Disk full")
            
            response = client.put("/api/operational_mode", json={"mode": "alert"})
            
            assert response.status_code == 500
            assert "Failed to persist operational mode" in response.json()["detail"]

    @pytest.mark.parametrize("mode", VALID_MODES)
    def test_put_all_valid_modes(self, client, mode):
        """Test PUT with all valid modes."""
        with patch('config.operational_mode.set_mode') as mock_set, \
             patch('config.operational_mode.is_valid_mode') as mock_valid:
            
            mock_valid.return_value = True
            
            response = client.put("/api/operational_mode", json={"mode": mode})
            
            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == mode
            mock_set.assert_called_once_with(mode)


class TestOperationalModeEnforcement:
    """Test enforcement logic in ResponseActionsManager."""

    def setup_method(self):
        """Setup for each test."""
        self.config = ResponsesConfig(allow_destructive_actions=True)
        self.operational_config = OperationalConfig()
        
    @pytest.fixture
    def manager(self):
        """Create a ResponseActionsManager instance."""
        return ResponseActionsManager(self.config, self.operational_config)

    @pytest.mark.parametrize("mode,expected_result", [
        ("offline", ActionResult.UNAUTHORIZED),
        ("observe", ActionResult.UNAUTHORIZED),
        ("alert", ActionResult.UNAUTHORIZED),
        ("contain", ActionResult.SUCCESS),  # Allowed but would need user consent
        ("quarantine", ActionResult.SUCCESS),  # Allowed but would need user consent
    ])
    def test_terminate_process_enforcement(self, manager, mode, expected_result):
        """Test process termination enforcement across modes."""
        with patch.object(manager, '_get_current_operational_mode') as mock_mode:
            mock_mode.return_value = mode
            
            # Test without user consent to focus on mode enforcement
            result = manager.terminate_process(pid=1234, user_consent=False, force=False)
            
            if expected_result == ActionResult.UNAUTHORIZED:
                # Should be blocked by mode enforcement or consent requirement
                assert result.result == ActionResult.UNAUTHORIZED
            else:
                # Should fail due to lack of user consent, not mode enforcement
                assert result.result == ActionResult.UNAUTHORIZED
                assert "consent" in result.message.lower()

    @pytest.mark.parametrize("mode,expected_result", [
        ("offline", ActionResult.UNAUTHORIZED),
        ("observe", ActionResult.UNAUTHORIZED),
        ("alert", ActionResult.UNAUTHORIZED),
        ("contain", ActionResult.FAILED),  # Allowed through but stub fails
        ("quarantine", ActionResult.FAILED),  # Allowed through but stub fails
    ])
    def test_quarantine_directory_enforcement(self, manager, mode, expected_result):
        """Test directory quarantine enforcement across modes."""
        with patch.object(manager, '_get_current_operational_mode') as mock_mode:
            mock_mode.return_value = mode
            
            result = manager.quarantine_directory(path="/test/path", user_consent=True)
            
            assert result.result == expected_result

    def test_pause_monitoring_allowed_all_modes(self, manager):
        """Test that pause monitoring is allowed in all modes."""
        for mode in VALID_MODES:
            with patch.object(manager, '_get_current_operational_mode') as mock_mode:
                mock_mode.return_value = mode
                
                result = manager.pause_monitoring(duration_seconds=10)
                
                # Should succeed regardless of mode
                assert result.result == ActionResult.SUCCESS

    def test_mode_enforcement_logging(self, manager):
        """Test that mode enforcement generates appropriate log messages."""
        with patch.object(manager, '_get_current_operational_mode') as mock_mode, \
             patch('response.actions.logger') as mock_logger:
            
            # Test offline mode logging
            mock_mode.return_value = "offline"
            manager.terminate_process(pid=1234, user_consent=True, force=False)
            
            # Should log the intent
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args[0][0]
            assert "[OFFLINE MODE]" in log_call
            assert "Would perform" in log_call

    def test_get_current_operational_mode_fallback(self, manager):
        """Test fallback behavior when operational mode storage fails."""
        with patch('config.operational_mode.get_mode') as mock_get:
            mock_get.side_effect = Exception("Storage unavailable")
            
            mode = manager._get_current_operational_mode()
            
            assert mode == "observe"  # Default fallback

    def test_enforcement_with_user_consent_in_quarantine_mode(self, manager):
        """Test that actions succeed with user consent in quarantine mode."""
        with patch.object(manager, '_get_current_operational_mode') as mock_mode:
            mock_mode.return_value = "quarantine"
            
            # Terminate process should succeed with consent (but would fail due to invalid PID)
            with patch.object(manager.process_terminator, 'terminate_process') as mock_terminate:
                mock_terminate.return_value = Mock(result=ActionResult.SUCCESS, user_consent=True)
                
                result = manager.terminate_process(pid=1234, user_consent=True, force=False)
                
                # Should reach the terminator (not blocked by enforcement)
                mock_terminate.assert_called_once()
                # Verify the result is successful
                assert result.result == ActionResult.SUCCESS

    def test_mode_enforcement_action_history(self, manager):
        """Test that blocked actions are recorded in action history."""
        with patch.object(manager, '_get_current_operational_mode') as mock_mode:
            mock_mode.return_value = "observe"
            
            initial_history_length = len(manager.action_history)
            
            result = manager.terminate_process(pid=1234, user_consent=True, force=False)
            
            # Should be blocked and recorded
            assert result.result == ActionResult.UNAUTHORIZED
            assert len(manager.action_history) == initial_history_length + 1
            assert manager.action_history[-1].result == ActionResult.UNAUTHORIZED


if __name__ == "__main__":
    pytest.main([__file__])
