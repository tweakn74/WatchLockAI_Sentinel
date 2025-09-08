# File: tests/test_auth.py
# Purpose: Comprehensive unit tests for P2-003 console authentication system

from __future__ import annotations
import unittest
import tempfile
import os
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import-safe test class
class TestAuthSystemImportSafe(unittest.TestCase):
    """Test auth system availability and import safety"""
    
    def test_auth_module_import_safe(self):
        """Test auth module can be imported safely"""
        try:
            from console import auth as auth_mod
            self.assertTrue(hasattr(auth_mod, 'ConsoleAuth'))
            self.assertTrue(hasattr(auth_mod, 'get_auth'))
        except ImportError:
            self.skipTest("Auth module not available")
    
    def test_auth_disabled_by_default(self):
        """Test authentication is disabled by default"""
        try:
            from console import auth as auth_mod
            
            # Clear auth environment variables
            old_env = {}
            for key in ["CONSOLE_AUTH_ENABLED", "CONSOLE_AUTH_SESSION_KEY", "CONSOLE_AUTH_USER_DB"]:
                old_env[key] = os.environ.pop(key, None)
            
            try:
                auth = auth_mod.ConsoleAuth()
                self.assertFalse(auth.enabled)
            finally:
                # Restore environment
                for key, value in old_env.items():
                    if value is not None:
                        os.environ[key] = value
                        
        except ImportError:
            self.skipTest("Auth module not available")


class TestAuthConfiguration(unittest.TestCase):
    """Test authentication configuration"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from console import auth as auth_mod
            self.auth_mod = auth_mod
        except ImportError:
            self.skipTest("Auth module not available")
            
        # Clean environment
        self.old_env = {}
        for key in ["CONSOLE_AUTH_ENABLED", "CONSOLE_AUTH_SESSION_KEY", "CONSOLE_AUTH_USER_DB"]:
            self.old_env[key] = os.environ.pop(key, None)
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore environment
        for key, value in self.old_env.items():
            if value is not None:
                os.environ[key] = value
    
    def test_config_validation_enabled_without_key(self):
        """Test configuration validation when enabled without session key"""
        os.environ["CONSOLE_AUTH_ENABLED"] = "1"
        # No session key set
        
        with self.assertRaises(ValueError) as cm:
            self.auth_mod.AuthConfig()
        
        self.assertIn("console_auth_session_key", str(cm.exception).lower())
    
    def test_config_validation_short_key(self):
        """Test configuration validation with short session key"""
        os.environ["CONSOLE_AUTH_ENABLED"] = "1"
        os.environ["CONSOLE_AUTH_SESSION_KEY"] = "short"  # Too short
        
        with self.assertRaises(ValueError) as cm:
            self.auth_mod.AuthConfig()
        
        self.assertIn("32+ bytes", str(cm.exception))
    
    def test_config_validation_valid(self):
        """Test configuration validation with valid settings"""
        os.environ["CONSOLE_AUTH_ENABLED"] = "1"
        os.environ["CONSOLE_AUTH_SESSION_KEY"] = "a" * 64  # Valid 32 byte hex
        os.environ["CONSOLE_AUTH_USER_DB"] = "test_users.json"
        
        config = self.auth_mod.AuthConfig()
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.session_key, "a" * 64)
        self.assertEqual(config.user_db_path, "test_users.json")


class TestUserDatabase(unittest.TestCase):
    """Test user database functionality"""
    
    def setUp(self):
        """Set up test environment with temporary database"""
        try:
            from console import auth as auth_mod
            self.auth_mod = auth_mod
        except ImportError:
            self.skipTest("Auth module not available")
            
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_users.json")
        self.user_db = self.auth_mod.UserDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up temporary files"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_creation(self):
        """Test database file creation"""
        self.assertTrue(os.path.exists(self.db_path))
        
        # Check initial empty database
        with open(self.db_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, {})
    
    def test_add_user_success(self):
        """Test successful user addition"""
        result = self.user_db.add_user("testuser", "testpass123")
        self.assertTrue(result)
        
        # Verify user was added
        self.assertTrue(self.user_db.user_exists("testuser"))
    
    def test_add_user_duplicate(self):
        """Test adding duplicate user"""
        self.user_db.add_user("testuser", "testpass123")
        result = self.user_db.add_user("testuser", "different_pass")
        
        self.assertFalse(result)  # Should fail on duplicate
    
    def test_password_hashing_format(self):
        """Test password hash format"""
        self.user_db.add_user("testuser", "testpass123")
        
        # Load users to check hash format
        users = self.user_db._load_users()
        pw_hash = users["testuser"]
        
        # Check PBKDF2 format: pbkdf2$sha256$iterations$salt$hash
        parts = pw_hash.split('$')
        self.assertEqual(len(parts), 5)
        self.assertEqual(parts[0], "pbkdf2")
        self.assertEqual(parts[1], "sha256")
        self.assertGreaterEqual(int(parts[2]), 100000)  # Min iterations
        self.assertEqual(len(parts[3]), 32)  # 16 byte salt hex = 32 chars
        self.assertEqual(len(parts[4]), 64)  # 32 byte hash hex = 64 chars
    
    def test_password_verification_correct(self):
        """Test password verification with correct password"""
        self.user_db.add_user("testuser", "testpass123")
        result = self.user_db.verify_user("testuser", "testpass123")
        self.assertTrue(result)
    
    def test_password_verification_incorrect(self):
        """Test password verification with incorrect password"""
        self.user_db.add_user("testuser", "testpass123")
        result = self.user_db.verify_user("testuser", "wrongpass")
        self.assertFalse(result)
    
    def test_password_verification_nonexistent_user(self):
        """Test password verification for non-existent user"""
        result = self.user_db.verify_user("nonexistent", "anypass")
        self.assertFalse(result)
    
    def test_password_verification_malformed_hash(self):
        """Test password verification handles malformed hash"""
        # Manually add user with malformed hash
        users = {"testuser": "invalid_hash_format"}
        self.user_db._save_users(users)
        
        result = self.user_db.verify_user("testuser", "anypass")
        self.assertFalse(result)


class TestSessionManager(unittest.TestCase):
    """Test session management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from console import auth as auth_mod
            self.auth_mod = auth_mod
        except ImportError:
            self.skipTest("Auth module not available")
            
        self.session_key = "a" * 64  # 32 bytes hex
        self.session_manager = self.auth_mod.SessionManager(self.session_key)
    
    def test_session_token_creation(self):
        """Test session token creation"""
        token = self.session_manager.create_session_token("testuser")
        
        # Token should have format: username:timestamp:signature
        parts = token.split(':')
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], "testuser")
        self.assertTrue(parts[1].isdigit())  # timestamp
        self.assertEqual(len(parts[2]), 64)  # SHA256 hex signature
    
    def test_session_token_verification_valid(self):
        """Test valid session token verification"""
        token = self.session_manager.create_session_token("testuser")
        username = self.session_manager.verify_session_token(token)
        
        self.assertEqual(username, "testuser")
    
    def test_session_token_verification_invalid_format(self):
        """Test session token verification with invalid format"""
        invalid_tokens = [
            "invalid",
            "too:few",
            "too:many:parts:here",
            "",
        ]
        
        for token in invalid_tokens:
            result = self.session_manager.verify_session_token(token)
            self.assertIsNone(result)
    
    def test_session_token_verification_wrong_signature(self):
        """Test session token verification with wrong signature"""
        token = self.session_manager.create_session_token("testuser")
        parts = token.split(':')
        
        # Tamper with signature
        tampered_token = f"{parts[0]}:{parts[1]}:{'x' * 64}"
        result = self.session_manager.verify_session_token(tampered_token)
        
        self.assertIsNone(result)
    
    def test_session_token_verification_expired(self):
        """Test session token verification with expired token"""
        # Create token with old timestamp
        old_timestamp = str(int(time.time()) - 90000)  # 25 hours ago
        message = f"testuser:{old_timestamp}"
        
        import hmac
        import hashlib
        signature = hmac.new(
            bytes.fromhex(self.session_key), 
            message.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        expired_token = f"{message}:{signature}"
        result = self.session_manager.verify_session_token(expired_token)
        
        self.assertIsNone(result)
    
    def test_cookie_config(self):
        """Test cookie configuration"""
        config = self.session_manager.get_cookie_config()
        
        self.assertTrue(config["httponly"])
        self.assertTrue(config["secure"])
        self.assertEqual(config["samesite"], "strict")
        self.assertEqual(config["max_age"], 86400)


class TestConsoleAuth(unittest.TestCase):
    """Test main ConsoleAuth class"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from console import auth as auth_mod
            self.auth_mod = auth_mod
        except ImportError:
            self.skipTest("Auth module not available")
            
        # Clean environment
        self.old_env = {}
        for key in ["CONSOLE_AUTH_ENABLED", "CONSOLE_AUTH_SESSION_KEY", "CONSOLE_AUTH_USER_DB"]:
            self.old_env[key] = os.environ.pop(key, None)
        
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore environment
        for key, value in self.old_env.items():
            if value is not None:
                os.environ[key] = value
                
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_auth_disabled_by_default(self):
        """Test auth is disabled when not configured"""
        auth = self.auth_mod.ConsoleAuth()
        
        self.assertFalse(auth.enabled)
        self.assertIsNone(auth.user_db)
        self.assertIsNone(auth.session_manager)
    
    def test_auth_enabled_with_config(self):
        """Test auth is enabled with proper configuration"""
        os.environ["CONSOLE_AUTH_ENABLED"] = "1"
        os.environ["CONSOLE_AUTH_SESSION_KEY"] = "b" * 64
        os.environ["CONSOLE_AUTH_USER_DB"] = os.path.join(self.temp_dir, "users.json")
        
        auth = self.auth_mod.ConsoleAuth()
        
        self.assertTrue(auth.enabled)
        self.assertIsNotNone(auth.user_db)
        self.assertIsNotNone(auth.session_manager)
    
    def test_auth_operations_when_disabled(self):
        """Test auth operations when authentication disabled"""
        auth = self.auth_mod.ConsoleAuth()
        
        # Should return False/None for disabled auth
        self.assertFalse(auth.authenticate_user("user", "pass"))
        self.assertIsNone(auth.verify_session("token"))
        
        with self.assertRaises(ValueError):
            auth.create_session("user")


# Import time inside test to avoid issues during module import
import time

if __name__ == "__main__":
    unittest.main()
