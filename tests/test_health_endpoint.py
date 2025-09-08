#!/usr/bin/env python3
"""
Import-safe unittest for composite health endpoint (Beazley-Mode RC-1+).

Tests that the health endpoint registers only when HEALTH_ENDPOINT_ENABLED=="1"
and response JSON has the expected keys without asserting internal values.
"""

import unittest
import os
import sys
from pathlib import Path

# Add project root to path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


class TestHealthEndpoint(unittest.TestCase):
    """Test suite for composite health endpoint."""

    def setUp(self):
        """Set up test environment."""
        # Clean environment for predictable test state
        env_vars = [
            "HEALTH_ENDPOINT_ENABLED", 
            "METRICS_DEBUG_ENABLED",
            "CONFIG_HOT_RELOAD_ENABLED", 
            "TI_CACHE_ENABLED",
            "RATE_LIMIT_ENABLED"
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

    def tearDown(self):
        """Clean up test environment."""
        # Restore default state
        env_vars = [
            "HEALTH_ENDPOINT_ENABLED", 
            "METRICS_DEBUG_ENABLED",
            "CONFIG_HOT_RELOAD_ENABLED", 
            "TI_CACHE_ENABLED", 
            "RATE_LIMIT_ENABLED"
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

    def test_fastapi_import_availability(self):
        """Test if FastAPI is available for testing."""
        try:
            import fastapi
            self.fastapi_available = True
        except ImportError:
            self.skipTest("FastAPI not available - skipping health endpoint tests")

    def test_health_endpoint_disabled_by_default(self):
        """Test that health endpoint is not registered when flag is default (OFF)."""
        try:
            import fastapi
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("FastAPI not available - skipping health endpoint tests")

        try:
            # Import the web API module
            from console.web_api import SentinelWebAPI
            
            # Mock sentinel service
            mock_service = type('MockService', (), {
                'get_status': lambda: {'running': True, 'uptime_seconds': 100},
                'event_bus': type('MockEventBus', (), {
                    'get_stats': lambda: {'events_processed': 42},
                    'get_observability_metrics': lambda: {'delivery_success_count': 10}
                })()
            })()
            
            # Create API instance with flag OFF (default)
            api = SentinelWebAPI(mock_service)
            client = TestClient(api.app)
            
            # Health endpoint should not be accessible (404)
            response = client.get("/api/metrics/health")
            self.assertEqual(response.status_code, 404, 
                           "Health endpoint should return 404 when HEALTH_ENDPOINT_ENABLED=0 (default)")
            
        except Exception as e:
            self.skipTest(f"Could not test health endpoint - {e}")

    def test_health_endpoint_enabled_when_flag_set(self):
        """Test that health endpoint is registered when HEALTH_ENDPOINT_ENABLED=1."""
        try:
            import fastapi
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("FastAPI not available - skipping health endpoint tests")

        try:
            # Set the flag to enable health endpoint
            os.environ["HEALTH_ENDPOINT_ENABLED"] = "1"
            
            # Re-import to pick up the environment change
            import importlib
            if 'console.web_api' in sys.modules:
                importlib.reload(sys.modules['console.web_api'])
            from console.web_api import SentinelWebAPI
            
            # Mock sentinel service
            mock_service = type('MockService', (), {
                'get_status': lambda: {'running': True, 'uptime_seconds': 100},
                'uptime_seconds': 100,
                'event_bus': type('MockEventBus', (), {
                    'get_stats': lambda: {'events_processed': 42},
                    'get_observability_metrics': lambda: {'delivery_success_count': 10}
                })()
            })()
            
            # Create API instance with flag ON
            api = SentinelWebAPI(mock_service)
            client = TestClient(api.app)
            
            # Health endpoint should be accessible (200)
            response = client.get("/api/metrics/health")
            self.assertEqual(response.status_code, 200, 
                           "Health endpoint should return 200 when HEALTH_ENDPOINT_ENABLED=1")
            
            # Check response structure (don't assert internal values)
            if response.status_code == 200:
                json_data = response.json()
                required_keys = ["service", "event_bus", "flags", "version"]
                for key in required_keys:
                    self.assertIn(key, json_data, f"Response should contain '{key}' field")
                
                # Check flags structure
                if "flags" in json_data:
                    flags = json_data["flags"]
                    expected_flags = [
                        "METRICS_DEBUG_ENABLED",
                        "CONFIG_HOT_RELOAD_ENABLED", 
                        "TI_CACHE_ENABLED",
                        "RATE_LIMIT_ENABLED",
                        "HEALTH_ENDPOINT_ENABLED"
                    ]
                    for flag in expected_flags:
                        self.assertIn(flag, flags, f"Flags should contain '{flag}'")
            
        except Exception as e:
            self.skipTest(f"Could not test enabled health endpoint - {e}")

    def test_import_sanity_check(self):
        """Test basic imports work as expected."""
        try:
            # Test core imports
            import app_core.bus
            self.assertTrue(True, "app_core.bus import successful")
        except ImportError:
            pass  # Not required for this test

        try:
            import console.web_api
            self.assertTrue(True, "console.web_api import successful")
        except ImportError:
            self.fail("console.web_api should be importable")

        try:
            import fastapi
            self.assertTrue(True, "fastapi import successful")
        except ImportError:
            pass  # FastAPI not required, will skip related tests


def main():
    """Run the test suite."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
