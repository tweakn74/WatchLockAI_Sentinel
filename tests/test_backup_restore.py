"""Tests for P4-001: Backup & Restore functionality."""

import os
import tempfile
import unittest
import json
import zipfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module under test
try:
    from console.backup_restore import BackupManager, get_backup_manager
except ImportError:
    BackupManager = None
    get_backup_manager = None


@unittest.skipUnless(BackupManager, "Backup module not available")
class TestBackupRestore(unittest.TestCase):
    """Test backup and restore functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create test files to backup
        self.test_data_dir = Path(self.test_dir) / "data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Create test config file
        config_file = Path(self.test_dir) / "config.yaml"
        config_file.write_text("test: configuration")
        
        # Create test data files
        (self.test_data_dir / "test.json").write_text('{"test": "data"}')
        
        # Change to test directory
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create backup manager
        self.backup_manager = BackupManager(backup_dir=str(self.backup_dir))
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_backup_disabled(self):
        """Test backup functionality when disabled."""
        with patch('console.backup_restore.BACKUP_ENABLED', False):
            result = self.backup_manager.create_backup("test backup")
            
            self.assertEqual(result["status"], "disabled")
            self.assertFalse(result["enabled"])
    
    def test_create_backup_success(self):
        """Test successful backup creation."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            result = self.backup_manager.create_backup("Test backup")
            
            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["enabled"])
            self.assertIn("path", result)
            self.assertIn("sha256", result)
            self.assertIn("timestamp", result)
            
            # Verify backup file exists
            backup_path = Path(result["path"])
            self.assertTrue(backup_path.exists())
            
            # Verify it's a valid zip file
            with zipfile.ZipFile(backup_path, 'r') as zf:
                file_list = zf.namelist()
                self.assertIn("metadata.json", file_list)
    
    def test_backup_with_custom_targets(self):
        """Test backup with custom backup targets."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            # Override backup targets
            self.backup_manager.backup_targets = ["config.yaml", "data"]
            
            result = self.backup_manager.create_backup("Custom backup")
            
            self.assertEqual(result["status"], "ok")
            
            # Verify backup contents
            backup_path = Path(result["path"])
            with zipfile.ZipFile(backup_path, 'r') as zf:
                file_list = zf.namelist()
                self.assertIn("metadata.json", file_list)
                self.assertIn("config.yaml", file_list)
    
    def test_restore_backup_disabled(self):
        """Test restore functionality when disabled."""
        with patch('console.backup_restore.BACKUP_ENABLED', False):
            result = self.backup_manager.restore_backup("fake_backup.zip")
            
            self.assertEqual(result["status"], "disabled")
            self.assertFalse(result["enabled"])
    
    def test_restore_nonexistent_backup(self):
        """Test restore with non-existent backup file."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            result = self.backup_manager.restore_backup("nonexistent.zip")
            
            self.assertEqual(result["status"], "error")
            self.assertIn("not found", result["error"])
    
    def test_restore_dry_run(self):
        """Test restore dry-run functionality."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            # First create a backup
            backup_result = self.backup_manager.create_backup("Test backup")
            backup_path = backup_result["path"]
            
            # Test dry-run restore
            restore_result = self.backup_manager.restore_backup(backup_path, confirm=False)
            
            self.assertEqual(restore_result["status"], "dry_run")
            self.assertIn("plan", restore_result)
            self.assertIn("metadata", restore_result)
            self.assertTrue(restore_result["enabled"])
    
    def test_restore_backup_success(self):
        """Test successful backup restore."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            # Create a backup
            backup_result = self.backup_manager.create_backup("Test backup")
            backup_path = backup_result["path"]
            
            # Remove original file
            os.remove("config.yaml")
            
            # Restore backup
            restore_result = self.backup_manager.restore_backup(backup_path, confirm=True)
            
            self.assertEqual(restore_result["status"], "restored")
            self.assertIn("restored_files", restore_result)
            self.assertTrue(restore_result["enabled"])
            
            # Verify file was restored
            self.assertTrue(Path("config.yaml").exists())
    
    def test_list_backups_disabled(self):
        """Test list backups when disabled."""
        with patch('console.backup_restore.BACKUP_ENABLED', False):
            result = self.backup_manager.list_backups()
            
            self.assertEqual(result["status"], "disabled")
            self.assertEqual(result["backups"], [])
            self.assertFalse(result["enabled"])
    
    def test_list_backups_empty(self):
        """Test list backups with no existing backups."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            result = self.backup_manager.list_backups()
            
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["count"], 0)
            self.assertEqual(result["backups"], [])
            self.assertTrue(result["enabled"])
    
    def test_list_backups_with_existing(self):
        """Test list backups with existing backup files."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            # Create a couple of backups
            backup1 = self.backup_manager.create_backup("Backup 1")
            backup2 = self.backup_manager.create_backup("Backup 2")
            
            result = self.backup_manager.list_backups()
            
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["count"], 2)
            self.assertTrue(result["enabled"])
            
            # Verify backup info
            backup_info = result["backups"]
            self.assertEqual(len(backup_info), 2)
            
            for backup in backup_info:
                self.assertIn("path", backup)
                self.assertIn("name", backup)
                self.assertIn("size_bytes", backup)
                self.assertIn("created", backup)
    
    def test_backup_manager_singleton(self):
        """Test backup manager singleton pattern."""
        if get_backup_manager:
            manager1 = get_backup_manager()
            manager2 = get_backup_manager()
            
            self.assertIs(manager1, manager2)
    
    def test_invalid_zip_restore(self):
        """Test restore with invalid zip file."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            # Create invalid zip file
            invalid_zip = self.backup_dir / "invalid.zip"
            invalid_zip.write_text("not a zip file")
            
            result = self.backup_manager.restore_backup(str(invalid_zip))
            
            self.assertEqual(result["status"], "error")
            self.assertTrue(result["enabled"])
    
    def test_backup_metadata(self):
        """Test backup metadata content."""
        with patch('console.backup_restore.BACKUP_ENABLED', True):
            backup_result = self.backup_manager.create_backup("Metadata test")
            backup_path = Path(backup_result["path"])
            
            # Read metadata from backup
            with zipfile.ZipFile(backup_path, 'r') as zf:
                metadata_content = zf.read("metadata.json").decode('utf-8')
                metadata = json.loads(metadata_content)
                
                self.assertIn("timestamp", metadata)
                self.assertIn("description", metadata)
                self.assertIn("version", metadata)
                self.assertIn("targets", metadata)
                self.assertEqual(metadata["description"], "Metadata test")
                self.assertEqual(metadata["version"], "P4-001")


if __name__ == '__main__':
    unittest.main()
