"""Tests for P4-002: Secret Rotation functionality."""

import os
import unittest
import json
from unittest.mock import patch, MagicMock

# Import the module under test
try:
    from tools.rotate_secrets import SecretRotator, get_secret_rotator
except ImportError:
    SecretRotator = None
    get_secret_rotator = None


@unittest.skipUnless(SecretRotator, "Secret rotation module not available")
class TestSecretRotation(unittest.TestCase):
    """Test secret rotation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.rotator = SecretRotator()
    
    def test_rotation_disabled(self):
        """Test rotation functionality when disabled."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', False):
            result = self.rotator.rotate_console_auth_session_key()
            
            self.assertEqual(result["status"], "disabled")
            self.assertFalse(result["enabled"])
    
    def test_rotate_console_auth_session_key(self):
        """Test console auth session key rotation."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            result = self.rotator.rotate_console_auth_session_key()
            
            self.assertEqual(result["status"], "generated")
            self.assertEqual(result["secret_type"], "CONSOLE_AUTH_SESSION_KEY")
            self.assertEqual(result["new_key_length"], 64)  # 32 bytes as hex
            self.assertIn("new_key_preview", result)
            self.assertIn("timestamp", result)
            self.assertTrue(result["enabled"])
            
            # Verify key preview format
            preview = result["new_key_preview"]
            self.assertTrue(preview.startswith("..." + ".")) 
            self.assertTrue(preview.endswith("..."))
    
    def test_rotate_admin_token(self):
        """Test admin token rotation."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            result = self.rotator.rotate_admin_token()
            
            self.assertEqual(result["status"], "generated")
            self.assertEqual(result["secret_type"], "ADMIN_TOKEN")
            self.assertIn("new_token_length", result)
            self.assertIn("new_token_preview", result)
            self.assertIn("timestamp", result)
            self.assertTrue(result["enabled"])
            
            # Verify token is base64 encoded
            preview = result["new_token_preview"]
            self.assertTrue(len(preview) > 16)  # Should have reasonable length
    
    def test_generate_salt(self):
        """Test salt generation."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            result = self.rotator.generate_salt("test_salt", 16)
            
            self.assertEqual(result["status"], "generated")
            self.assertEqual(result["secret_type"], "SALT")
            self.assertEqual(result["name"], "test_salt")
            self.assertEqual(result["salt_length"], 16)
            self.assertIn("salt_hex", result)
            self.assertIn("salt_preview", result)
            self.assertTrue(result["enabled"])
            
            # Verify salt hex format
            salt_hex = result["salt_hex"]
            self.assertEqual(len(salt_hex), 32)  # 16 bytes = 32 hex chars
            
            # Verify all hex characters
            try:
                int(salt_hex, 16)
            except ValueError:
                self.fail("Salt is not valid hex")
    
    def test_generate_salt_invalid_length(self):
        """Test salt generation with invalid length."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            # Too short
            result = self.rotator.generate_salt("test", 4)
            self.assertEqual(result["status"], "error")
            
            # Too long
            result = self.rotator.generate_salt("test", 128)
            self.assertEqual(result["status"], "error")
    
    def test_preview_rotation_plan(self):
        """Test rotation plan preview."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            # Mock environment variables
            with patch.dict(os.environ, {
                'CONSOLE_AUTH_SESSION_KEY': 'existing_key',
                'ADMIN_TOKEN': 'existing_token'
            }):
                result = self.rotator.preview_rotation_plan()
                
                self.assertEqual(result["status"], "preview")
                self.assertIn("plan", result)
                self.assertEqual(result["secrets_count"], 2)
                self.assertTrue(result["enabled"])
                
                # Check plan structure
                plan = result["plan"]
                self.assertEqual(len(plan), 2)
                
                # Verify session key plan
                session_plan = next(p for p in plan if p["secret_type"] == "CONSOLE_AUTH_SESSION_KEY")
                self.assertTrue(session_plan["current_exists"])
                self.assertEqual(session_plan["recommended_action"], "rotate")
                
                # Verify admin token plan
                token_plan = next(p for p in plan if p["secret_type"] == "ADMIN_TOKEN")
                self.assertTrue(token_plan["current_exists"])
                self.assertEqual(token_plan["recommended_action"], "rotate")
    
    def test_execute_rotation_all_secrets(self):
        """Test execution of rotation for all secrets."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            result = self.rotator.execute_rotation()
            
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["successful_count"], 2)
            self.assertEqual(result["failed_count"], 0)
            self.assertIn("results", result)
            self.assertTrue(result["enabled"])
            
            # Verify results structure
            results = result["results"]
            self.assertEqual(len(results), 2)
            
            for secret_result in results:
                self.assertEqual(secret_result["status"], "generated")
    
    def test_execute_rotation_specific_secrets(self):
        """Test execution of rotation for specific secrets."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            result = self.rotator.execute_rotation(["ADMIN_TOKEN"])
            
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["successful_count"], 1)
            self.assertEqual(result["failed_count"], 0)
            self.assertTrue(result["enabled"])
            
            # Verify only admin token was rotated
            results = result["results"]
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["secret_type"], "ADMIN_TOKEN")
    
    def test_get_rotation_history(self):
        """Test rotation history retrieval."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            # Perform some rotations
            self.rotator.rotate_admin_token()
            self.rotator.generate_salt("test_salt")
            
            result = self.rotator.get_rotation_history()
            
            self.assertEqual(result["status"], "ok")
            self.assertIn("history", result)
            self.assertEqual(result["entries_count"], 2)
            self.assertTrue(result["enabled"])
            
            # Verify history entries
            history = result["history"]
            self.assertEqual(len(history), 2)
            
            for entry in history:
                self.assertIn("secret_type", entry)
                self.assertIn("action", entry)
                self.assertIn("timestamp", entry)
    
    def test_rotation_history_disabled(self):
        """Test rotation history when disabled."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', False):
            result = self.rotator.get_rotation_history()
            
            self.assertEqual(result["status"], "disabled")
            self.assertEqual(result["history"], [])
            self.assertFalse(result["enabled"])
    
    def test_key_uniqueness(self):
        """Test that generated keys are unique."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            # Generate multiple session keys
            result1 = self.rotator.rotate_console_auth_session_key()
            result2 = self.rotator.rotate_console_auth_session_key()
            
            # Keys should be different (extremely low probability of collision)
            self.assertNotEqual(
                result1["new_key_preview"],
                result2["new_key_preview"]
            )
            
            # Generate multiple admin tokens
            token1 = self.rotator.rotate_admin_token()
            token2 = self.rotator.rotate_admin_token()
            
            self.assertNotEqual(
                token1["new_token_preview"],
                token2["new_token_preview"]
            )
    
    def test_salt_uniqueness(self):
        """Test that generated salts are unique."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            salt1 = self.rotator.generate_salt("salt1")
            salt2 = self.rotator.generate_salt("salt2")
            
            self.assertNotEqual(
                salt1["salt_hex"],
                salt2["salt_hex"]
            )
    
    def test_secret_rotator_singleton(self):
        """Test secret rotator singleton pattern."""
        if get_secret_rotator:
            rotator1 = get_secret_rotator()
            rotator2 = get_secret_rotator()
            
            self.assertIs(rotator1, rotator2)
    
    def test_rotation_with_existing_environment(self):
        """Test rotation behavior with existing environment variables."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            with patch.dict(os.environ, {
                'CONSOLE_AUTH_SESSION_KEY': 'old_session_key',
                'ADMIN_TOKEN': 'old_admin_token'
            }):
                # Rotate session key
                result = self.rotator.rotate_console_auth_session_key()
                self.assertTrue(result["key_changed"])  # Should detect change
                
                # Rotate admin token
                result = self.rotator.rotate_admin_token()
                self.assertTrue(result["token_changed"])  # Should detect change
    
    def test_error_handling(self):
        """Test error handling in rotation functions."""
        with patch('tools.rotate_secrets.ROTATE_ENABLED', True):
            # Mock secrets.token_hex to raise an exception
            with patch('secrets.token_hex', side_effect=Exception("Mock error")):
                result = self.rotator.rotate_console_auth_session_key()
                
                self.assertEqual(result["status"], "error")
                self.assertIn("error", result)
                self.assertTrue(result["enabled"])


if __name__ == '__main__':
    unittest.main()
