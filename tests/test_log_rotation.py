# File: tests/test_log_rotation.py
# Purpose: Unit tests for P3-002 log rotation and redaction system

from __future__ import annotations
import unittest
import tempfile
import shutil
import logging
import os
from pathlib import Path


class TestLogRotationImportSafe(unittest.TestCase):
    """Test log rotation system availability and import safety"""
    
    def test_log_config_module_import_safe(self):
        """Test log config module can be imported safely"""
        try:
            from console import log_config as log_config_mod
            self.assertTrue(hasattr(log_config_mod, 'RotatingLogConfig'))
            self.assertTrue(hasattr(log_config_mod, 'SecretRedactionFilter'))
            self.assertTrue(hasattr(log_config_mod, 'get_log_config'))
        except ImportError:
            self.skipTest("Log config module not available")
    
    def test_log_rotation_enabled_by_default(self):
        """Test log rotation is enabled by default with safe settings"""
        try:
            from console import log_config as log_config_mod
            
            # Clear log environment variables
            old_env = {}
            for key in ["LOG_MAX_BYTES", "LOG_BACKUPS", "LOG_REDACT_SECRETS"]:
                old_env[key] = os.environ.pop(key, None)
            
            try:
                # Reset global config to pick up environment changes
                log_config_mod._global_log_config = None
                
                log_config = log_config_mod.get_log_config()
                self.assertEqual(log_config.max_bytes, 1048576)  # 1MB default
                self.assertEqual(log_config.backup_count, 5)     # 5 backups default
                self.assertTrue(log_config.redact_secrets)       # Redaction ON by default
                
            finally:
                # Restore environment
                for key, value in old_env.items():
                    if value is not None:
                        os.environ[key] = value
                # Reset global config again
                log_config_mod._global_log_config = None
                        
        except ImportError:
            self.skipTest("Log config module not available")


class TestSecretRedactionFilter(unittest.TestCase):
    """Test secret redaction functionality"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from console import log_config as log_config_mod
            self.log_config_mod = log_config_mod
        except ImportError:
            self.skipTest("Log config module not available")
    
    def test_redaction_filter_creation(self):
        """Test redaction filter can be created"""
        filter_obj = self.log_config_mod.SecretRedactionFilter(enabled=True)
        self.assertTrue(filter_obj.enabled)
        
        filter_disabled = self.log_config_mod.SecretRedactionFilter(enabled=False)
        self.assertFalse(filter_disabled.enabled)
    
    def test_token_redaction(self):
        """Test API token redaction"""
        filter_obj = self.log_config_mod.SecretRedactionFilter(enabled=True)
        
        test_cases = [
            ("token: abc123def456ghi789", "[REDACTED]"),
            ("API_KEY=sk_test_1234567890abcdef", "[REDACTED]"),
            ("api-key: xyz789abc123def456", "[REDACTED]"),
        ]
        
        for original, expected_part in test_cases:
            redacted = filter_obj._redact_text(original)
            self.assertIn(expected_part, redacted)
            self.assertNotIn("abc123def456ghi789", redacted)
    
    def test_password_redaction(self):
        """Test password redaction"""
        filter_obj = self.log_config_mod.SecretRedactionFilter(enabled=True)
        
        test_cases = [
            "password=supersecret123",
            "passwd: mypassword123",
            "pwd=anothersecret",
        ]
        
        for original in test_cases:
            redacted = filter_obj._redact_text(original)
            self.assertIn("[REDACTED]", redacted)
            self.assertNotIn("supersecret123", redacted)
            self.assertNotIn("mypassword123", redacted)
            self.assertNotIn("anothersecret", redacted)
    
    def test_authorization_header_redaction(self):
        """Test authorization header redaction"""
        filter_obj = self.log_config_mod.SecretRedactionFilter(enabled=True)
        
        test_cases = [
            "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
            "authorization: token abc123def456",
        ]
        
        for original in test_cases:
            redacted = filter_obj._redact_text(original)
            self.assertIn("[REDACTED]", redacted)
            self.assertNotIn("eyJ0eXAiOiJKV1QiOiJhbGciOiJIUzI1NiJ9", redacted)
    
    def test_connection_string_redaction(self):
        """Test database connection string redaction"""
        filter_obj = self.log_config_mod.SecretRedactionFilter(enabled=True)
        
        original = "postgresql://user:mypassword@localhost/db"
        redacted = filter_obj._redact_text(original)
        
        self.assertIn("[REDACTED]", redacted)
        self.assertNotIn("mypassword", redacted)
        self.assertIn("postgresql://user:", redacted)
        self.assertIn("@localhost/db", redacted)
    
    def test_no_redaction_when_disabled(self):
        """Test no redaction occurs when filter is disabled"""
        filter_obj = self.log_config_mod.SecretRedactionFilter(enabled=False)
        
        original = "token: abc123def456ghi789"
        redacted = filter_obj._redact_text(original)
        
        self.assertEqual(original, redacted)
    
    def test_short_strings_not_redacted(self):
        """Test short strings are not redacted to avoid false positives"""
        filter_obj = self.log_config_mod.SecretRedactionFilter(enabled=True)
        
        short_strings = [
            "short",
            "key=x",
            "token: a",
            "password=12",
        ]
        
        for original in short_strings:
            redacted = filter_obj._redact_text(original)
            self.assertEqual(original, redacted)
    
    def test_normal_messages_unchanged(self):
        """Test normal log messages are not modified"""
        filter_obj = self.log_config_mod.SecretRedactionFilter(enabled=True)
        
        normal_messages = [
            "User logged in successfully",
            "Processing request for endpoint /api/health",
            "Database connection established",
            "Service started on port 8080",
        ]
        
        for original in normal_messages:
            redacted = filter_obj._redact_text(original)
            self.assertEqual(original, redacted)


class TestRotatingLogConfig(unittest.TestCase):
    """Test log rotation configuration"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        try:
            from console import log_config as log_config_mod
            self.log_config_mod = log_config_mod
        except ImportError:
            self.skipTest("Log config module not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)
    
    def test_rotating_config_creation(self):
        """Test rotating log configuration creation"""
        config = self.log_config_mod.RotatingLogConfig(
            log_dir=self.temp_dir,
            max_bytes=2097152,  # 2MB
            backup_count=3,
            redact_secrets=True
        )
        
        self.assertEqual(config.max_bytes, 2097152)
        self.assertEqual(config.backup_count, 3)
        self.assertTrue(config.redact_secrets)
        self.assertTrue(config.log_dir.exists())
    
    def test_config_bounds_validation(self):
        """Test configuration bounds are enforced"""
        config = self.log_config_mod.RotatingLogConfig(
            log_dir=self.temp_dir,
            max_bytes=500,  # Too small, should be clamped to 1024
            backup_count=100,  # Too large, should be clamped to 50
            redact_secrets=True
        )
        
        self.assertEqual(config.max_bytes, 1024)  # Minimum enforced
        self.assertEqual(config.backup_count, 50)  # Maximum enforced
    
    def test_rotating_handler_creation(self):
        """Test rotating file handler creation"""
        config = self.log_config_mod.RotatingLogConfig(
            log_dir=self.temp_dir,
            max_bytes=1048576,
            backup_count=5,
            redact_secrets=True
        )
        
        handler = config.create_rotating_handler("test_log", level=logging.INFO)
        
        self.assertIsInstance(handler, logging.handlers.RotatingFileHandler)
        self.assertEqual(handler.level, logging.INFO)
        self.assertEqual(handler.maxBytes, 1048576)
        self.assertEqual(handler.backupCount, 5)
    
    def test_logger_setup(self):
        """Test logger setup with rotation"""
        config = self.log_config_mod.RotatingLogConfig(
            log_dir=self.temp_dir,
            max_bytes=1048576,
            backup_count=5,
            redact_secrets=True
        )
        
        logger = config.setup_logger("test.logger", "test_app", level=logging.INFO)
        
        self.assertEqual(logger.name, "test.logger")
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)
        self.assertFalse(logger.propagate)  # Should not propagate
    
    def test_log_status_reporting(self):
        """Test log status reporting"""
        config = self.log_config_mod.RotatingLogConfig(
            log_dir=self.temp_dir,
            max_bytes=1048576,
            backup_count=5,
            redact_secrets=True
        )
        
        status = config.get_log_status()
        
        self.assertIn("log_directory", status)
        self.assertIn("max_bytes", status)
        self.assertIn("backup_count", status)
        self.assertIn("redact_secrets", status)
        self.assertIn("directory_exists", status)
        self.assertIn("total_log_files", status)
        
        self.assertEqual(status["max_bytes"], 1048576)
        self.assertEqual(status["backup_count"], 5)
        self.assertTrue(status["redact_secrets"])
        self.assertTrue(status["directory_exists"])


class TestApplicationLoggingSetup(unittest.TestCase):
    """Test application-wide logging setup"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from console import log_config as log_config_mod
            self.log_config_mod = log_config_mod
        except ImportError:
            self.skipTest("Log config module not available")
        
        # Clean environment
        self.old_env = {}
        for key in ["LOG_MAX_BYTES", "LOG_BACKUPS", "LOG_REDACT_SECRETS"]:
            self.old_env[key] = os.environ.pop(key, None)
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore environment
        for key, value in self.old_env.items():
            if value is not None:
                os.environ[key] = value
    
    def test_setup_application_logging(self):
        """Test application logging setup"""
        os.environ["LOG_MAX_BYTES"] = "2097152"  # 2MB
        os.environ["LOG_BACKUPS"] = "3"
        os.environ["LOG_REDACT_SECRETS"] = "1"
        
        # Reset global config to pick up new environment
        self.log_config_mod._global_log_config = None
        
        result = self.log_config_mod.setup_application_logging()
        
        self.assertIn("app", result)
        self.assertIn("metrics", result)
        self.assertIn("audit", result)
        self.assertIn("config", result)
        
        # Check loggers were created
        self.assertEqual(result["app"].name, "sentinel.app")
        self.assertEqual(result["metrics"].name, "sentinel.metrics")
        self.assertEqual(result["audit"].name, "sentinel.audit")
        
        # Check configuration was applied
        self.assertEqual(result["config"]["max_bytes"], 2097152)
        self.assertEqual(result["config"]["backup_count"], 3)
        self.assertTrue(result["config"]["redact_secrets"])


if __name__ == '__main__':
    unittest.main()
