# File: tests/test_rbac.py
import os
import unittest
import importlib.util

def _has(mod: str) -> bool:
    return bool(importlib.util.find_spec(mod))

class TestRBAC(unittest.TestCase):
    def setUp(self):
        # Clean environment
        os.environ.pop("ADMIN_AUTH_ENABLED", None)
        os.environ.pop("ADMIN_TOKEN", None)
        os.environ.pop("CONFIG_HOT_RELOAD_ENABLED", None)
        os.environ.pop("RATE_LIMIT_ENABLED", None)

    def test_admin_auth_default_off(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        # Enable admin route but leave auth disabled (default)
        os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"
        # ADMIN_AUTH_ENABLED defaults to OFF

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Should work without any auth headers (existing behavior preserved)
        r = client.post("/api/admin/config/reload")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json().get("status"), "reloading")

    def test_admin_auth_enabled_missing_header(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        # Enable admin route and auth
        os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"
        os.environ["ADMIN_AUTH_ENABLED"] = "1"
        os.environ["ADMIN_TOKEN"] = "test-secret-token"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Should fail with 403 when no header provided
        r = client.post("/api/admin/config/reload")
        self.assertEqual(r.status_code, 403, r.text)

    def test_admin_auth_enabled_wrong_token(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"
        os.environ["ADMIN_AUTH_ENABLED"] = "1"
        os.environ["ADMIN_TOKEN"] = "test-secret-token"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Should fail with 403 when wrong token provided
        r = client.post("/api/admin/config/reload", headers={"X-Admin-Token": "wrong-token"})
        self.assertEqual(r.status_code, 403, r.text)

    def test_admin_auth_enabled_correct_token(self) -> None:
        if not (_has("console.web_api") and _has("fastapi")):
            self.skipTest("console.web_api or fastapi not importable")

        os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"
        os.environ["ADMIN_AUTH_ENABLED"] = "1"
        os.environ["ADMIN_TOKEN"] = "test-secret-token"

        from console.web_api import SentinelWebAPI  # type: ignore[attr-defined]
        if not _has("fastapi.testclient"):
            self.skipTest("fastapi.testclient not importable")
        from fastapi.testclient import TestClient  # type: ignore

        api = SentinelWebAPI(sentinel_service=None)
        client = TestClient(api.app)

        # Should succeed with correct token
        r = client.post("/api/admin/config/reload", headers={"X-Admin-Token": "test-secret-token"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json().get("status"), "reloading")

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestRBAC)
    runner = unittest.TextTestRunner(verbosity=2)
    import sys
    sys.exit(0 if runner.run(suite).wasSuccessful() else 1)
