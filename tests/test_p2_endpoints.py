# File: tests/test_p2_endpoints.py
# Purpose: Integration tests for P2-003 and P2-004 web API endpoints

from __future__ import annotations
import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import-safe test class
class TestP2EndpointsImportSafe(unittest.TestCase):
    """Test P2 endpoints availability and import safety"""
    
    def test_web_api_import_safe(self):
        """Test web API module can be imported safely"""
        try:
            from console import web_api as web_api_mod
            self.assertTrue(hasattr(web_api_mod, 'SentinelWebAPI'))
        except ImportError:
            self.skipTest("Web API module not available")
    
    def test_fastapi_graceful_degradation(self):
        """Test system works gracefully without FastAPI"""
        try:
            import fastapi
            # If FastAPI is available, we can test endpoint functionality
            self.assertTrue(hasattr(fastapi, 'FastAPI'))
        except ImportError:
            # System should still work without FastAPI (just no web endpoints)
            self.skipTest("FastAPI not available - P2 endpoints will be disabled")


class TestAuthEndpoints(unittest.TestCase):
    """Test P2-003 authentication endpoints integration"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            import fastapi
            from fastapi.testclient import TestClient
            from console.web_api import SentinelWebAPI
        except ImportError:
            self.skipTest("FastAPI not available")
        
        # Clean environment
        self.old_env = {}
        for key in ["CONSOLE_AUTH_ENABLED", "CONSOLE_AUTH_SESSION_KEY", 
                   "CONSOLE_AUTH_USER_DB", "RATE_LIMIT_ENABLED"]:
            self.old_env[key] = os.environ.pop(key, None)
        
        # Set up temporary directory and database
        self.temp_dir = tempfile.mkdtemp()
        self.user_db_path = os.path.join(self.temp_dir, "test_users.json")
        
        # Configure authentication
        os.environ["CONSOLE_AUTH_ENABLED"] = "1"
        os.environ["CONSOLE_AUTH_SESSION_KEY"] = "d" * 64  # 32 bytes hex
        os.environ["CONSOLE_AUTH_USER_DB"] = self.user_db_path
        os.environ["RATE_LIMIT_ENABLED"] = "0"  # Disable for testing
        
        # Reload module to pick up environment changes
        import importlib
        from console import web_api as web_api_mod
        importlib.reload(web_api_mod)
        
        # Create test service and web API
        self.mock_service = MagicMock()
        self.web_api = web_api_mod.SentinelWebAPI(self.mock_service)
        self.client = TestClient(self.web_api.app)
        
        # Create test user
        from console import auth as auth_mod
        auth = auth_mod.get_auth()
        if auth.user_db:
            auth.user_db.add_user("testuser", "testpass123")
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore environment
        for key, value in self.old_env.items():
            if value is not None:
                os.environ[key] = value
        
        # Clean up temp directory
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_auth_endpoints_exist(self):
        """Test authentication endpoints are registered"""
        routes = [route.path for route in self.web_api.app.routes]
        
        expected_routes = ["/api/auth/login", "/api/auth/logout", "/api/auth/me"]
        for route in expected_routes:
            self.assertIn(route, routes)
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        
        # Should set session cookie
        cookies = response.cookies
        self.assertIn("sentinel_session", cookies)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("invalid credentials", data["detail"].lower())
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "anypass"
        })
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("invalid credentials", data["detail"].lower())
    
    def test_login_invalid_request_format(self):
        """Test login with invalid request format"""
        # Missing password
        response = self.client.post("/api/auth/login", json={
            "username": "testuser"
        })
        
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_logout_success(self):
        """Test successful logout"""
        response = self.client.post("/api/auth/logout")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        
        # Should clear session cookie (check in set-cookie header)
        set_cookie_header = response.headers.get("set-cookie", "")
        self.assertIn("sentinel_session=", set_cookie_header)
    
    def test_auth_me_with_valid_session(self):
        """Test /auth/me with valid session"""
        # First login to get session
        login_response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        # Extract session cookie
        session_cookie = login_response.cookies.get("sentinel_session")
        self.assertIsNotNone(session_cookie)
        
        # Test /auth/me with session
        response = self.client.get("/api/auth/me", cookies={"sentinel_session": session_cookie})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user"], "testuser")
    
    def test_auth_me_without_session(self):
        """Test /auth/me without session"""
        response = self.client.get("/api/auth/me")
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("not authenticated", data["detail"].lower())
    
    def test_auth_me_with_invalid_session(self):
        """Test /auth/me with invalid session"""
        response = self.client.get("/api/auth/me", cookies={"sentinel_session": "invalid_token"})
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("not authenticated", data["detail"].lower())


class TestAuthEndpointsDisabled(unittest.TestCase):
    """Test P2-003 authentication endpoints when disabled"""
    
    def setUp(self):
        """Set up test environment with auth disabled"""
        try:
            import fastapi
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("FastAPI not available")
        
        # Clean environment (auth disabled by default)
        self.old_env = {}
        for key in ["CONSOLE_AUTH_ENABLED", "CONSOLE_AUTH_SESSION_KEY", "CONSOLE_AUTH_USER_DB"]:
            self.old_env[key] = os.environ.pop(key, None)
        
        # Reload module with auth disabled
        import importlib
        from console import web_api as web_api_mod
        importlib.reload(web_api_mod)
        
        # Create web API with auth disabled
        mock_service = MagicMock()
        self.web_api = web_api_mod.SentinelWebAPI(mock_service)
        self.client = TestClient(self.web_api.app)
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore environment
        for key, value in self.old_env.items():
            if value is not None:
                os.environ[key] = value
    
    def test_auth_endpoints_not_registered_when_disabled(self):
        """Test auth endpoints are not registered when auth disabled"""
        routes = [route.path for route in self.web_api.app.routes]
        
        auth_routes = ["/api/auth/login", "/api/auth/logout", "/api/auth/me"]
        for route in auth_routes:
            self.assertNotIn(route, routes)


class TestStreamingEndpoints(unittest.TestCase):
    """Test P2-004 streaming endpoints integration"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            import fastapi
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("FastAPI not available")
        
        # Clean environment
        self.old_env = {}
        for key in ["STREAM_ENABLED", "STREAM_TYPE", "STREAM_HEALTH_INTERVAL_MS", 
                   "STREAM_REQUIRE_AUTH"]:
            self.old_env[key] = os.environ.pop(key, None)
        
        # Enable streaming
        os.environ["STREAM_ENABLED"] = "1"
        os.environ["STREAM_TYPE"] = "sse"
        os.environ["STREAM_HEALTH_INTERVAL_MS"] = "100"  # Fast for testing
        
        # Reload module
        import importlib
        from console import web_api as web_api_mod
        importlib.reload(web_api_mod)
        
        # Create web API
        mock_service = MagicMock()
        mock_service.start_time = 1000000
        self.web_api = web_api_mod.SentinelWebAPI(mock_service)
        self.client = TestClient(self.web_api.app)
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore environment
        for key, value in self.old_env.items():
            if value is not None:
                os.environ[key] = value
    
    def test_streaming_endpoint_exists(self):
        """Test streaming endpoint is registered"""
        routes = [route.path for route in self.web_api.app.routes]
        self.assertIn("/api/stream/health", routes)
    
    def test_streaming_endpoint_disabled(self):
        """Test streaming endpoint when disabled"""
        # Create web API with streaming disabled
        os.environ["STREAM_ENABLED"] = "0"
        
        import importlib
        from console import web_api as web_api_mod
        importlib.reload(web_api_mod)
        
        mock_service = MagicMock()
        disabled_web_api = web_api_mod.SentinelWebAPI(mock_service)
        disabled_client = TestClient(disabled_web_api.app)
        
        routes = [route.path for route in disabled_web_api.app.routes]
        self.assertNotIn("/api/stream/health", routes)


class TestP2IntegrationWithExistingFeatures(unittest.TestCase):
    """Test P2-003/P2-004 integration with existing admin features"""
    
    def setUp(self):
        """Set up test environment with both auth and existing features"""
        try:
            import fastapi
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("FastAPI not available")
        
        # Clean environment
        self.old_env = {}
        for key in ["CONSOLE_AUTH_ENABLED", "CONSOLE_AUTH_SESSION_KEY", 
                   "CONSOLE_AUTH_USER_DB", "ADMIN_AUTH_ENABLED", "ADMIN_TOKEN",
                   "CONFIG_HOT_RELOAD_ENABLED", "ANOMALY_ENABLED", "QUARANTINE_ENABLED"]:
            self.old_env[key] = os.environ.pop(key, None)
        
        # Set up temporary directory and database
        self.temp_dir = tempfile.mkdtemp()
        self.user_db_path = os.path.join(self.temp_dir, "test_users.json")
        
        # Configure both authentication systems
        os.environ["CONSOLE_AUTH_ENABLED"] = "1"
        os.environ["CONSOLE_AUTH_SESSION_KEY"] = "e" * 64
        os.environ["CONSOLE_AUTH_USER_DB"] = self.user_db_path
        os.environ["ADMIN_AUTH_ENABLED"] = "1" 
        os.environ["ADMIN_TOKEN"] = "test_admin_token"
        os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"  # Enable admin endpoint
        
        # Reload module
        import importlib
        from console import web_api as web_api_mod
        importlib.reload(web_api_mod)
        
        # Create web API
        mock_service = MagicMock()
        self.web_api = web_api_mod.SentinelWebAPI(mock_service)
        self.client = TestClient(self.web_api.app)
        
        # Create test user
        from console import auth as auth_mod
        auth = auth_mod.get_auth()
        if auth.user_db:
            auth.user_db.add_user("admin", "adminpass123")
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore environment
        for key, value in self.old_env.items():
            if value is not None:
                os.environ[key] = value
        
        # Clean up temp directory
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_admin_endpoint_accepts_session_auth(self):
        """Test admin endpoints accept session authentication"""
        # Login to get session
        login_response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "adminpass123"
        })
        
        session_cookie = login_response.cookies.get("sentinel_session")
        self.assertIsNotNone(session_cookie)
        
        # Test admin endpoint with session (should work)
        response = self.client.post("/api/admin/config/reload", 
                                  cookies={"sentinel_session": session_cookie})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "reloading")
    
    def test_admin_endpoint_accepts_token_auth(self):
        """Test admin endpoints still accept token authentication"""
        # Test admin endpoint with X-Admin-Token (should work)
        response = self.client.post("/api/admin/config/reload",
                                  headers={"X-Admin-Token": "test_admin_token"})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "reloading")
    
    def test_admin_endpoint_rejects_no_auth(self):
        """Test admin endpoints reject requests without authentication"""
        # Test admin endpoint without auth (should fail)
        response = self.client.post("/api/admin/config/reload")
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("admin authentication", data["detail"].lower())
    
    def test_admin_endpoint_rejects_wrong_token(self):
        """Test admin endpoints reject wrong token"""
        # Test admin endpoint with wrong token (should fail)
        response = self.client.post("/api/admin/config/reload",
                                  headers={"X-Admin-Token": "wrong_token"})
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("admin authentication", data["detail"].lower())
    
    def test_admin_endpoint_rejects_invalid_session(self):
        """Test admin endpoints reject invalid session"""
        # Test admin endpoint with invalid session (should fail)
        response = self.client.post("/api/admin/config/reload",
                                  cookies={"sentinel_session": "invalid_session"})
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("admin authentication", data["detail"].lower())


if __name__ == "__main__":
    unittest.main()
