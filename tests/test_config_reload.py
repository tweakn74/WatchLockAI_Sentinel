# tests/test_config_reload.py
import os
import unittest
import importlib.util

def _has(mod: str) -> bool:
    return bool(importlib.util.find_spec(mod))

class TestConfigHotReload(unittest.TestCase):
    def test_config_reload_route_when_enabled(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")
        os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"
        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore
        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)
        r = client.post("/api/admin/config/reload")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json().get("status"), "reloading")

    def test_config_reload_route_default_off(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")
        # Ensure disabled
        os.environ.pop("CONFIG_HOT_RELOAD_ENABLED", None)
        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore
        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)
        # Route should not exist; safest assertion: 404
        resp = client.post("/api/admin/config/reload")
        self.assertIn(resp.status_code, (404, 405, 403))  # depends on router shape; non-200 proves gating

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestConfigHotReload)
    runner = unittest.TextTestRunner(verbosity=2)
    import sys
    sys.exit(0 if runner.run(suite).wasSuccessful() else 1)
