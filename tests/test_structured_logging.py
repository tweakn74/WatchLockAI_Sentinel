# File: tests/test_structured_logging.py
import os
import unittest
import importlib.util

def _has(mod: str) -> bool:
    return bool(importlib.util.find_spec(mod))

class TestStructuredLogging(unittest.TestCase):
    def test_metrics_snapshot_endpoint(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        # Enable debug metrics for snapshot endpoint
        os.environ["METRICS_DEBUG_ENABLED"] = "1"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Test snapshot endpoint
        r = client.get("/api/metrics/snapshot")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        
        # Check expected structure
        self.assertIn("timestamp", data)
        self.assertIn("uptime_s", data)
        self.assertIn("metrics", data)
        self.assertIn("event_bus", data["metrics"])
        self.assertIn("service", data["metrics"])

    def test_health_endpoint_logging(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        # Health endpoint should be default ON
        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Test health endpoint (should not fail due to logging)
        r = client.get("/api/metrics/health")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        
        # Check expected structure remains unchanged (non-breaking)
        self.assertIn("ok", data)
        self.assertIn("components", data)
        self.assertIn("uptime_s", data)

    def test_event_bus_metrics_logging(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        # Enable debug metrics
        os.environ["METRICS_DEBUG_ENABLED"] = "1"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Test event bus metrics endpoint (should not fail due to logging)
        r = client.get("/api/metrics/event_bus")
        self.assertEqual(r.status_code, 503, r.text)  # Expected since no real event bus service

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestStructuredLogging)
    runner = unittest.TextTestRunner(verbosity=2)
    import sys
    sys.exit(0 if runner.run(suite).wasSuccessful() else 1)
