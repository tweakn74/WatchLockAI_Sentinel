# File: tests/test_config_migrate.py
# Purpose: Unit tests for configuration migration utility (P3-001)

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.config_migrate import ConfigMigrator


class TestConfigMigrator(unittest.TestCase):
    """Test configuration migrator functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        self.migrator = ConfigMigrator(str(self.config_file))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_migration_rules_loaded(self):
        """Test that migration rules are loaded"""
        rules = self.migrator.migration_rules
        
        self.assertIsInstance(rules, dict)
        self.assertIn("ENABLE_HEALTH", rules)
        self.assertEqual(rules["ENABLE_HEALTH"], "HEALTH_ENDPOINT_ENABLED")
        self.assertIn("AUTH_ENABLE", rules)
        self.assertEqual(rules["AUTH_ENABLE"], "CONSOLE_AUTH_ENABLED")
    
    @patch.dict(os.environ, {
        "ENABLE_HEALTH": "1",
        "DEBUG_METRICS": "1", 
        "AUTH_ENABLE": "1",
        "MODERN_FLAG": "1"
    })
    def test_scan_environment(self):
        """Test scanning environment variables"""
        env_vars = self.migrator.scan_environment()
        
        # Should find legacy variables
        self.assertIn("ENABLE_HEALTH", env_vars)
        self.assertIn("DEBUG_METRICS", env_vars)
        self.assertIn("AUTH_ENABLE", env_vars)
        
        # Should also find non-legacy variables
        self.assertIn("MODERN_FLAG", env_vars)
    
    @patch.dict(os.environ, {
        "ENABLE_HEALTH": "1",
        "DEBUG_METRICS": "0",
        "UNKNOWN_VAR": "test"
    })
    def test_identify_migrations(self):
        """Test identifying required migrations"""
        migrations = self.migrator.identify_migrations()
        
        # Should identify known migrations
        expected_migrations = [
            ("ENABLE_HEALTH", "HEALTH_ENDPOINT_ENABLED", "1"),
            ("DEBUG_METRICS", "METRICS_DEBUG_ENABLED", "0")
        ]
        
        for old_key, new_key, value in expected_migrations:
            self.assertIn((old_key, new_key, value), migrations)
        
        # Should not include unknown variables
        unknown_found = any(old_key == "UNKNOWN_VAR" for old_key, _, _ in migrations)
        self.assertFalse(unknown_found)
    
    def test_create_backup_directory(self):
        """Test backup directory creation"""
        backup_dir = self.migrator.create_backup_directory()
        
        self.assertTrue(backup_dir.exists())
        self.assertTrue(backup_dir.is_dir())
        self.assertTrue(str(backup_dir).startswith(str(self.migrator.backup_dir)))
    
    def test_backup_environment_file(self):
        """Test backing up environment file"""
        # Create a test .env file
        env_file = Path(self.temp_dir) / ".env"
        env_content = "ENABLE_HEALTH=1\nDEBUG_METRICS=0\n"
        env_file.write_text(env_content)
        
        backup_dir = self.migrator.create_backup_directory()
        backup_path = self.migrator.backup_environment_file(str(env_file), backup_dir)
        
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.read_text(), env_content)
    
    def test_backup_environment_file_missing(self):
        """Test backing up non-existent environment file"""
        backup_dir = self.migrator.create_backup_directory()
        backup_path = self.migrator.backup_environment_file("nonexistent.env", backup_dir)
        
        self.assertIsNone(backup_path)
    
    def test_update_environment_file(self):
        """Test updating environment file"""
        # Create test .env file
        env_file = Path(self.temp_dir) / ".env"
        original_content = "ENABLE_HEALTH=1\nDEBUG_METRICS=0\nOTHER_VAR=test\n"
        env_file.write_text(original_content)
        
        migrations = [
            ("ENABLE_HEALTH", "HEALTH_ENDPOINT_ENABLED", "1"),
            ("DEBUG_METRICS", "METRICS_DEBUG_ENABLED", "0")
        ]
        
        result = self.migrator.update_environment_file(str(env_file), migrations)
        
        self.assertTrue(result)
        
        # Check updated content
        updated_content = env_file.read_text()
        self.assertIn("HEALTH_ENDPOINT_ENABLED=1", updated_content)
        self.assertIn("METRICS_DEBUG_ENABLED=0", updated_content)
        self.assertIn("OTHER_VAR=test", updated_content)  # Should preserve other vars
        self.assertNotIn("ENABLE_HEALTH=1", updated_content)  # Should remove old
        self.assertNotIn("DEBUG_METRICS=0", updated_content)
    
    def test_migrate_file_system_wide(self):
        """Test system-wide file migration"""
        # Create test environment files
        env1 = Path(self.temp_dir) / ".env"
        env2 = Path(self.temp_dir) / "config" / ".env"
        env2.parent.mkdir(parents=True, exist_ok=True)
        
        env1.write_text("ENABLE_HEALTH=1\n")
        env2.write_text("DEBUG_METRICS=0\n")
        
        with patch.dict(os.environ, {"ENABLE_HEALTH": "1", "DEBUG_METRICS": "0"}):
            result = self.migrator.migrate(scan_filesystem=True, search_paths=[self.temp_dir])
            
            self.assertTrue(result["success"])
            self.assertGreater(result["files_updated"], 0)
            self.assertGreater(result["migrations_applied"], 0)
    
    def test_migrate_environment_only(self):
        """Test environment-only migration"""
        with patch.dict(os.environ, {"ENABLE_HEALTH": "1"}, clear=True):
            with patch('builtins.print') as mock_print:  # Capture print output
                result = self.migrator.migrate(scan_filesystem=False, update_environment=False)
                
                self.assertTrue(result["success"])
                self.assertGreater(result["migrations_identified"], 0)
                
                # Should have printed migration suggestions
                printed_output = " ".join([call[0][0] for call in mock_print.call_args_list])
                self.assertIn("ENABLE_HEALTH", printed_output)
                self.assertIn("HEALTH_ENDPOINT_ENABLED", printed_output)
    
    def test_generate_migration_script(self):
        """Test generating migration script"""
        migrations = [
            ("ENABLE_HEALTH", "HEALTH_ENDPOINT_ENABLED", "1"),
            ("DEBUG_METRICS", "METRICS_DEBUG_ENABLED", "0")
        ]
        
        script_path = Path(self.temp_dir) / "migrate.sh"
        result = self.migrator.generate_migration_script(migrations, str(script_path))
        
        self.assertTrue(result)
        self.assertTrue(script_path.exists())
        
        script_content = script_path.read_text()
        self.assertIn("export HEALTH_ENDPOINT_ENABLED=1", script_content)
        self.assertIn("export METRICS_DEBUG_ENABLED=0", script_content)
        self.assertIn("unset ENABLE_HEALTH", script_content)
        self.assertIn("unset DEBUG_METRICS", script_content)
    
    def test_validate_migrations(self):
        """Test migration validation"""
        valid_migrations = [
            ("ENABLE_HEALTH", "HEALTH_ENDPOINT_ENABLED", "1"),
            ("DEBUG_METRICS", "METRICS_DEBUG_ENABLED", "0")
        ]
        
        invalid_migrations = [
            ("UNKNOWN_OLD", "UNKNOWN_NEW", "1"),
            ("ENABLE_HEALTH", "WRONG_TARGET", "1")
        ]
        
        # Valid migrations should pass
        is_valid, errors = self.migrator.validate_migrations(valid_migrations)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid migrations should fail
        is_valid, errors = self.migrator.validate_migrations(invalid_migrations)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_preview_mode(self):
        """Test migration in preview mode"""
        with patch.dict(os.environ, {"ENABLE_HEALTH": "1"}):
            result = self.migrator.migrate(preview_only=True)
            
            self.assertTrue(result["success"])
            self.assertGreater(result["migrations_identified"], 0)
            self.assertEqual(result["migrations_applied"], 0)  # No actual changes
            self.assertEqual(result["files_updated"], 0)


if __name__ == "__main__":
    unittest.main()
