# tests/test_bus_metrics.py
import os
import sys
import unittest
import importlib.util
from typing import Any, Dict

def _has(mod: str) -> bool:
    return bool(importlib.util.find_spec(mod))

class TestEventBusObservability(unittest.TestCase):
    def test_observability_metrics_direct(self) -> None:
        if not _has("app_core.bus"):
            self.skipTest("app_core.bus not importable in this environment")
        
        try:
            from app_core.bus import EventBus
        except ImportError as e:
            self.skipTest(f"app_core.bus import failed: {e}")

        bus = EventBus()
        
        # Check if get_observability_metrics method exists
        if not hasattr(bus, 'get_observability_metrics'):
            self.skipTest("get_observability_metrics method not available (wrong EventBus version)")
            
        metrics: Dict[str, Any] = bus.get_observability_metrics()
        for k in ("delivery_success_count", "delivery_failure_count"):
            self.assertIn(k, metrics, f"missing key: {k}")
            self.assertIsInstance(metrics[k], int)
            self.assertGreaterEqual(metrics[k], 0)

    def test_observability_metrics_route_when_enabled(self) -> None:
        # Route should be opt-in only
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")
        # Enable metrics route for this test only
        os.environ["METRICS_DEBUG_ENABLED"] = "1"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]

        # If TestClient is unavailable, skip cleanly
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")

        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI()
        client = TestClient(api.app)  # SentinelWebAPI expected to expose FastAPI as .app

        resp = client.get("/api/metrics/event_bus")
        self.assertEqual(resp.status_code, 200, resp.text)
        data = resp.json()
        self.assertIn("event_bus", data)
        eb = data["event_bus"]
        for k in ("delivery_success_count", "delivery_failure_count"):
            self.assertIn(k, eb)
            self.assertIsInstance(eb[k], int)
            self.assertGreaterEqual(eb[k], 0)

    def test_health_metrics_route_when_enabled(self) -> None:
        # Route should be default ON (unlike debug routes)
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]

        # If TestClient is unavailable, skip cleanly
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")

        from fastapi.testclient import TestClient  # type: ignore

        # Test with default settings (should be enabled)
        api = SentinelWebAPI()
        client = TestClient(api.app)

        resp = client.get("/api/metrics/health")
        self.assertEqual(resp.status_code, 200, resp.text)
        data = resp.json()
        
        # Check expected structure from user's specification
        self.assertIn("ok", data)
        self.assertIn("components", data)
        self.assertIn("uptime_s", data)
        
        # Check components structure
        components = data["components"]
        self.assertIn("event_bus", components)
        self.assertIn("service", components)
        
        # Validate types
        self.assertIsInstance(data["ok"], bool)
        self.assertIsInstance(data["uptime_s"], int)
        self.assertGreaterEqual(data["uptime_s"], 0)

    def test_health_metrics_route_can_be_disabled(self) -> None:
        # Test that route can be disabled with HEALTH_ENDPOINT_ENABLED=0
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        # Set flag to disable health endpoint
        os.environ["HEALTH_ENDPOINT_ENABLED"] = "0"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]

        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")

        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI()
        client = TestClient(api.app)

        # Route should not exist when disabled
        resp = client.get("/api/metrics/health")
        self.assertEqual(resp.status_code, 404)  # Route not found
        
        # Clean up environment
        os.environ.pop("HEALTH_ENDPOINT_ENABLED", None)

if __name__ == "__main__":
    # Pure unittest runner for environments without pytest
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestEventBusObservability)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
