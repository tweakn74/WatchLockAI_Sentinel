# File: tests/test_rate_limit.py
import os
import unittest
import importlib.util

def _has(mod: str) -> bool:
    return bool(importlib.util.find_spec(mod))

class TestRateLimit(unittest.TestCase):
    def test_admin_reload_rate_limited(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        # Enable admin route + rate limit
        os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"
        os.environ["RATE_LIMIT_ENABLED"] = "1"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Default limit: 5 per minute for admin_config_reload
        for _ in range(5):
            r = client.post("/api/admin/config/reload")
            self.assertEqual(r.status_code, 200, r.text)
            self.assertEqual(r.json().get("status"), "reloading")

        sixth = client.post("/api/admin/config/reload")
        self.assertEqual(sixth.status_code, 429, sixth.text)

    def test_debounce_ms_validation(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"
        # rate limit off for this test
        os.environ["RATE_LIMIT_ENABLED"] = "0"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Invalid negative -> clamped to 0 but response remains reloading
        r = client.post("/api/admin/config/reload?debounce_ms=-10")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json().get("status"), "reloading")

        # Excessively large -> clamped to 60000
        r2 = client.post("/api/admin/config/reload?debounce_ms=999999")
        self.assertEqual(r2.status_code, 200, r2.text)
        self.assertEqual(r2.json().get("status"), "reloading")

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestRateLimit)
    runner = unittest.TextTestRunner(verbosity=2)
    import sys
    sys.exit(0 if runner.run(suite).wasSuccessful() else 1)
