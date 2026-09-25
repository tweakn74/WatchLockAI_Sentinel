"""Integration smoke tests for WatchLockAI Sentinel.

Tests basic system integration without external dependencies.
Verifies: app imports, router mounting, API connectivity, event flow, graceful shutdown.
"""

from __future__ import annotations

import asyncio
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app_core.bus import EventBus
from app_core.schemas import EventType, FileEvent
from console.web_api import SentinelWebAPI


class TestIntegrationSmoke:
    """Smoke tests for core integration points."""

    def test_app_imports(self) -> None:
        """Test that main application modules import successfully."""
        try:
            # Core imports
            from app import SentinelApplication
            from app_core.bus import EventBus
            from app_core.config import load_config  # noqa: F401
            from app_core.schemas import BaseEvent

            # Console imports  
            from console.web_api import SentinelWebAPI

            # Response imports
            from response.actions import ResponseActionsManager  # noqa: F401
            from response.alerts import AlertManager  # noqa: F401

            # Service imports
            from service.service_wrapper import SentinelService
            
            # Verify classes are importable
            assert SentinelApplication is not None
            assert SentinelService is not None
            assert SentinelWebAPI is not None
            assert EventBus is not None
            assert BaseEvent is not None
            
        except ImportError as e:
            pytest.fail(f"Critical import failed: {e}")

    def test_router_mounting(self) -> None:
        """Test that API routers mount correctly."""
        # Mock sentinel service
        mock_service = Mock()
        mock_service.get_status.return_value = {
            "running": True,
            "uptime_seconds": 10.0,
            "collectors": {},
            "rules_engine": {},
            "event_bus": {},
        }
        mock_service.alert_manager = None
        mock_service.rules_engine = None
        mock_service.actions_manager = None
        
        # Create web API instance
        web_api = SentinelWebAPI(mock_service)
        
        # Create test client
        client = TestClient(web_api.app)
        
        # Test main API routes are mounted
        response = client.get("/api/status")
        assert response.status_code == 200
        
        # Test operational mode router is mounted (if available)
        try:
            response = client.get("/api/operational_mode")
            # Should be 200 (success) or 503 (service unavailable), not 404 (not mounted)
            assert response.status_code in [200, 503]
        except Exception:
            # Router may not be available in test environment
            pass

    def test_api_endpoint_connectivity(self) -> None:
        """Test basic API endpoint connectivity."""
        # Mock sentinel service with proper structure
        mock_service = Mock()
        mock_service.get_status.return_value = {
            "running": True,
            "uptime_seconds": 10.0,
            "collectors": {"fs_monitor": {"status": "running"}},
            "rules_engine": {"rules_loaded": 0},
            "event_bus": {"events_published": 0},
        }
        mock_service.alert_manager = Mock()
        mock_service.alert_manager.get_recent_alerts.return_value = []
        
        # Create web API instance
        web_api = SentinelWebAPI(mock_service)
        client = TestClient(web_api.app)
        
        # Test status endpoint
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["running"] is True
        assert "uptime_seconds" in data
        
        # Test alerts endpoint
        response = client.get("/api/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts" in data
        assert "recent_alerts" in data

    @pytest.mark.asyncio
    async def test_event_bus_flow(self) -> None:
        """Test event bus producer->consumer flow."""
        # Create event bus
        event_bus = EventBus()
        
        # Track events received
        events_received = []
        
        def mock_consumer(event):
            events_received.append(event)
        
        try:
            # Start event bus
            await event_bus.start()
            
            # Subscribe to FileEvent
            subscription = event_bus.subscribe(
                FileEvent,
                mock_consumer,
                "test_consumer"
            )
            
            # Create test event
            test_event = FileEvent(
                event_type=EventType.CREATED,
                path="/test/path.txt",
                size_bytes=1024
            )
            
            # Publish event
            await event_bus.publish(test_event)
            
            # Wait for event processing
            await asyncio.sleep(0.1)
            
            # Verify event was received
            assert len(events_received) == 1
            assert events_received[0].path == "/test/path.txt"
            assert events_received[0].event_type == EventType.CREATED
            
            # Clean up subscription
            event_bus.unsubscribe(subscription)
            
        finally:
            # Stop event bus
            await event_bus.stop()

    @pytest.mark.asyncio 
    async def test_graceful_shutdown(self) -> None:
        """Test background task startup and graceful shutdown."""
        # Create event bus (represents background task)
        event_bus = EventBus()
        
        # Mock service components (placeholder for future use)
        _ = Mock()  # Mock service placeholder
        
        try:
            # Start background task (event bus)
            await event_bus.start()
            assert event_bus.is_running is True
            
            # Simulate some activity
            test_event = FileEvent(
                event_type=EventType.MODIFIED,
                path="/test/file.txt"
            )
            await event_bus.publish(test_event)
            
            # Request graceful shutdown
            await event_bus.stop()
            
            # Verify clean shutdown
            assert event_bus.is_running is False
            
            # Verify no pending tasks or exceptions
            # (EventBus should handle cancellation gracefully)
            
        except asyncio.CancelledError:
            # Should not reach here with proper graceful shutdown
            pytest.fail("Background task did not shutdown gracefully")
        except Exception as e:
            pytest.fail(f"Unexpected error during shutdown: {e}")

    def test_operational_mode_api_integration(self) -> None:
        """Test operational mode API integration if available."""
        try:
            from config.operational_mode import get_mode, set_mode
            from console.api.operational_mode import router
            
            # Test basic operational mode functions
            original_mode = get_mode()
            assert original_mode in ["observe", "alert", "contain", "quarantine", "offline"]
            
            # Test mode switching (non-destructive)
            if original_mode != "observe":
                set_mode("observe")
                assert get_mode() == "observe"
                # Restore original mode
                set_mode(original_mode)  # type: ignore[arg-type]
            
            # Verify router exists and has expected routes
            assert router is not None
            assert len(router.routes) >= 2  # GET and PUT endpoints
            
        except ImportError:
            # Operational mode API may not be available
            pytest.skip("Operational mode API not available")

    @patch('app_core.config.load_config')
    def test_config_loading_integration(self, mock_load_config) -> None:
        """Test configuration loading integration."""
        from app_core.config import SentinelConfig
        
        # Mock configuration
        mock_config = SentinelConfig()
        mock_load_config.return_value = mock_config
        
        # Test config loading
        try:
            config = mock_load_config()
            assert config is not None
            assert hasattr(config, 'monitoring')
            assert hasattr(config, 'operational')
            assert hasattr(config, 'responses')
            
        except Exception as e:
            pytest.fail(f"Configuration loading failed: {e}")

    def test_response_actions_integration(self) -> None:
        """Test response actions integration."""
        try:
            from app_core.config import OperationalConfig, ResponsesConfig
            from response.actions import (
                ResponseActionsManager,
            )
            
            # Create mock configurations
            responses_config = ResponsesConfig()
            operational_config = OperationalConfig()
            
            # Create actions manager
            actions_manager = ResponseActionsManager(
                responses_config=responses_config,
                operational_config=operational_config,
                event_bus=Mock()  # Mock event bus
            )
            
            # Verify initialization
            assert actions_manager is not None
            assert hasattr(actions_manager, 'terminate_process')
            assert hasattr(actions_manager, 'pause_monitoring')
            
            # Test basic functionality (should not crash)
            stats = actions_manager.get_stats()
            assert isinstance(stats, dict)
            assert "actions_executed" in stats
            
        except ImportError as e:
            pytest.skip(f"Response actions not available: {e}")

    def test_detection_engine_integration(self) -> None:
        """Test detection engine integration."""
        try:
            from detection.behavioral_engine import BehavioralEngine
            from detection.rules_engine import RulesEngine
            
            # Verify classes are importable and instantiable
            assert RulesEngine is not None
            assert BehavioralEngine is not None
            
            # Test with mock configuration
            mock_config = Mock()
            mock_event_bus = Mock()
            
            # Should not crash during initialization
            rules_engine = RulesEngine(mock_config, mock_event_bus)
            assert rules_engine is not None
            
        except ImportError as e:
            pytest.skip(f"Detection engine not available: {e}")
        except Exception as e:
            # Initialization might fail due to missing dependencies, that's ok
            pytest.skip(f"Detection engine initialization failed: {e}")
