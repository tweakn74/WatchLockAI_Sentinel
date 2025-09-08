"""Tests for quarantine system (P2-002).

Tests file quarantine, restore, ACL hardening, and audit logging functionality.
"""

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Test with environment override to ensure testing works
os.environ["QUARANTINE_ENABLED"] = "1"

try:
    from console.quarantine import (
        QuarantineManager, QuarantineError, compute_file_sha256,
        apply_windows_acl_hardening, write_audit_log,
        quarantine_file, restore_file, list_quarantined_files,
        get_quarantine_status, get_manager,
        QUARANTINE_ENABLED
    )
    QUARANTINE_MODULE_AVAILABLE = True
except ImportError:
    QUARANTINE_MODULE_AVAILABLE = False


class TestQuarantineUtilities(unittest.TestCase):
    """Test quarantine utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QUARANTINE_MODULE_AVAILABLE:
            self.skipTest("Quarantine module not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test_file.txt"
        self.test_content = b"This is a test file for quarantine testing."
        
        # Create test file
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_compute_file_sha256(self):
        """Test SHA256 computation."""
        expected_hash = hashlib.sha256(self.test_content).hexdigest()
        computed_hash = compute_file_sha256(self.test_file)
        
        self.assertEqual(computed_hash, expected_hash)
        self.assertEqual(len(computed_hash), 64)  # SHA256 is 64 hex chars
    
    def test_compute_file_sha256_nonexistent(self):
        """Test SHA256 computation on non-existent file."""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.txt"
        
        with self.assertRaises(QuarantineError):
            compute_file_sha256(nonexistent_file)
    
    def test_write_audit_log(self):
        """Test audit log writing."""
        audit_log = Path(self.temp_dir) / "audit.jsonl"
        
        with mock.patch('console.quarantine.AUDIT_LOG_FILE', audit_log):
            write_audit_log(
                action="test_action",
                source_path="/test/source",
                dest_path="/test/dest",
                sha256="abc123"
            )
            
            # Check log file was created and contains expected data
            self.assertTrue(audit_log.exists())
            
            with open(audit_log, 'r', encoding='utf-8') as f:
                log_line = f.readline().strip()
                log_entry = json.loads(log_line)
            
            self.assertEqual(log_entry["action"], "test_action")
            self.assertEqual(log_entry["path_src"], "/test/source")
            self.assertEqual(log_entry["path_dst"], "/test/dest")
            self.assertEqual(log_entry["sha256"], "abc123")
            self.assertIn("timestamp", log_entry)
    
    def test_write_audit_log_error(self):
        """Test audit log writing with error."""
        audit_log = Path(self.temp_dir) / "audit.jsonl"
        
        with mock.patch('console.quarantine.AUDIT_LOG_FILE', audit_log):
            write_audit_log(
                action="test_error",
                source_path="/test/source",
                error="Test error message"
            )
            
            with open(audit_log, 'r', encoding='utf-8') as f:
                log_entry = json.loads(f.readline().strip())
            
            self.assertEqual(log_entry["error"], "Test error message")
    
    @mock.patch('os.name', 'nt')  # Mock Windows OS
    @mock.patch('subprocess.run')
    def test_apply_windows_acl_hardening_success(self, mock_run):
        """Test Windows ACL hardening success."""
        mock_run.return_value = mock.Mock(returncode=0)
        
        result = apply_windows_acl_hardening(self.test_file)
        
        self.assertTrue(result)
        mock_run.assert_called_once()
        
        # Check icacls command structure
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], "icacls")
        self.assertIn("/inheritance:r", call_args)
        self.assertIn("/grant:r", call_args)
    
    @mock.patch('os.name', 'posix')  # Mock non-Windows OS
    def test_apply_windows_acl_hardening_non_windows(self):
        """Test Windows ACL hardening on non-Windows OS."""
        result = apply_windows_acl_hardening(self.test_file)
        
        self.assertFalse(result)  # Should fail gracefully on non-Windows
    
    @mock.patch('os.name', 'nt')
    @mock.patch('subprocess.run', side_effect=FileNotFoundError)
    def test_apply_windows_acl_hardening_icacls_unavailable(self, mock_run):
        """Test Windows ACL hardening when icacls unavailable."""
        result = apply_windows_acl_hardening(self.test_file)
        
        self.assertFalse(result)  # Should fail gracefully
    
    def test_apply_windows_acl_hardening_nonexistent_file(self):
        """Test Windows ACL hardening on non-existent file."""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.txt"
        
        result = apply_windows_acl_hardening(nonexistent_file)
        
        self.assertFalse(result)


class TestQuarantineManager(unittest.TestCase):
    """Test QuarantineManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QUARANTINE_MODULE_AVAILABLE:
            self.skipTest("Quarantine module not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.quarantine_dir = Path(self.temp_dir) / "quarantine"
        self.audit_log = self.quarantine_dir / "audit_log.jsonl"
        
        # Mock quarantine directory
        self.quarantine_patcher = mock.patch('console.quarantine.QUARANTINE_DIR', self.quarantine_dir)
        self.audit_patcher = mock.patch('console.quarantine.AUDIT_LOG_FILE', self.audit_log)
        
        self.quarantine_patcher.start()
        self.audit_patcher.start()
        
        self.manager = QuarantineManager()
        
        # Create test file
        self.test_file = Path(self.temp_dir) / "test_file.txt"
        self.test_content = b"This is a test file for quarantine."
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)
        
        self.expected_sha256 = hashlib.sha256(self.test_content).hexdigest()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'quarantine_patcher'):
            self.quarantine_patcher.stop()
        if hasattr(self, 'audit_patcher'):
            self.audit_patcher.stop()
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_quarantine_file_success(self):
        """Test successful file quarantine."""
        result = self.manager.quarantine_file(str(self.test_file))
        
        self.assertEqual(result["status"], "quarantined")
        self.assertEqual(result["sha256"], self.expected_sha256)
        self.assertIn("dst", result)
        self.assertTrue(result["enabled"])
        
        # Check original file was moved
        self.assertFalse(self.test_file.exists())
        
        # Check quarantined file exists
        quarantined_path = Path(result["dst"])
        self.assertTrue(quarantined_path.exists())
        
        # Verify file content integrity
        with open(quarantined_path, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.test_content)
        
        # Check mapping was created
        self.assertIn(self.expected_sha256, self.manager._quarantine_mapping)
        mapping_entry = self.manager._quarantine_mapping[self.expected_sha256]
        self.assertEqual(mapping_entry["original_path"], str(self.test_file))
        self.assertEqual(mapping_entry["sha256"], self.expected_sha256)
    
    def test_quarantine_file_nonexistent(self):
        """Test quarantining non-existent file."""
        nonexistent_file = str(Path(self.temp_dir) / "nonexistent.txt")
        
        result = self.manager.quarantine_file(nonexistent_file)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("does not exist", result["error"])
    
    def test_quarantine_file_not_regular_file(self):
        """Test quarantining non-regular file (directory)."""
        test_dir = Path(self.temp_dir) / "test_directory"
        test_dir.mkdir()
        
        result = self.manager.quarantine_file(str(test_dir))
        
        self.assertEqual(result["status"], "error")
        self.assertIn("not a regular file", result["error"])
    
    @mock.patch('console.quarantine.QUARANTINE_ENABLED', False)
    def test_quarantine_file_disabled(self):
        """Test quarantine when disabled."""
        manager = QuarantineManager()
        result = manager.quarantine_file(str(self.test_file))
        
        self.assertEqual(result["status"], "disabled")
        self.assertFalse(result["enabled"])
    
    def test_restore_file_success(self):
        """Test successful file restore."""
        # First quarantine a file
        quarantine_result = self.manager.quarantine_file(str(self.test_file))
        sha256 = quarantine_result["sha256"]
        
        # Now restore it
        restore_result = self.manager.restore_file(sha256)
        
        self.assertEqual(restore_result["status"], "restored")
        self.assertEqual(restore_result["sha256"], sha256)
        self.assertEqual(restore_result["restored_to"], str(self.test_file))
        self.assertTrue(restore_result["enabled"])
        
        # Check file was restored to original location
        self.assertTrue(self.test_file.exists())
        
        # Verify content integrity
        with open(self.test_file, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.test_content)
        
        # Check mapping was removed
        self.assertNotIn(sha256, self.manager._quarantine_mapping)
    
    def test_restore_file_custom_path(self):
        """Test file restore to custom path."""
        # First quarantine a file
        quarantine_result = self.manager.quarantine_file(str(self.test_file))
        sha256 = quarantine_result["sha256"]
        
        # Restore to custom path
        custom_path = str(Path(self.temp_dir) / "custom_restore.txt")
        restore_result = self.manager.restore_file(sha256, custom_path)
        
        self.assertEqual(restore_result["status"], "restored")
        self.assertEqual(restore_result["restored_to"], custom_path)
        
        # Check file was restored to custom location
        self.assertTrue(Path(custom_path).exists())
    
    def test_restore_file_not_found(self):
        """Test restoring non-existent quarantined file."""
        fake_sha256 = "a" * 64  # Valid format but not in quarantine
        
        result = self.manager.restore_file(fake_sha256)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("not found in quarantine", result["error"])
    
    def test_restore_file_quarantine_missing(self):
        """Test restoring when quarantined file missing from disk."""
        # Manually add to mapping without actual file
        fake_sha256 = "b" * 64
        self.manager._quarantine_mapping[fake_sha256] = {
            "original_path": "/fake/path",
            "quarantine_path": str(Path(self.temp_dir) / "missing.txt"),
            "timestamp": "2025-01-01T00:00:00Z",
            "sha256": fake_sha256
        }
        
        result = self.manager.restore_file(fake_sha256)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("not found on disk", result["error"])
    
    def test_restore_file_destination_exists(self):
        """Test restore when destination already exists."""
        # First quarantine a file
        quarantine_result = self.manager.quarantine_file(str(self.test_file))
        sha256 = quarantine_result["sha256"]
        
        # Create file at original location
        with open(self.test_file, "w") as f:
            f.write("Different content")
        
        # Attempt restore
        result = self.manager.restore_file(sha256)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("already exists", result["error"])
    
    def test_restore_file_integrity_check_failure(self):
        """Test restore with integrity check failure."""
        # First quarantine a file
        quarantine_result = self.manager.quarantine_file(str(self.test_file))
        sha256 = quarantine_result["sha256"]
        quarantined_path = Path(quarantine_result["dst"])
        
        # Corrupt the quarantined file
        with open(quarantined_path, "w") as f:
            f.write("Corrupted content")
        
        # Attempt restore
        result = self.manager.restore_file(sha256)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("integrity check failed", result["error"])
    
    @mock.patch('console.quarantine.QUARANTINE_ENABLED', False)
    def test_restore_file_disabled(self):
        """Test restore when disabled."""
        manager = QuarantineManager()
        result = manager.restore_file("a" * 64)
        
        self.assertEqual(result["status"], "disabled")
        self.assertFalse(result["enabled"])
    
    def test_list_quarantined_files(self):
        """Test listing quarantined files."""
        # Initially should be empty
        files = self.manager.list_quarantined_files()
        self.assertEqual(len(files), 0)
        
        # Quarantine a file
        quarantine_result = self.manager.quarantine_file(str(self.test_file))
        sha256 = quarantine_result["sha256"]
        
        # Now should have one file
        files = self.manager.list_quarantined_files()
        self.assertEqual(len(files), 1)
        
        file_info = files[0]
        self.assertEqual(file_info["sha256"], sha256)
        self.assertEqual(file_info["original_path"], str(self.test_file))
        self.assertIn("timestamp", file_info)
        self.assertIn("acl_hardened", file_info)
    
    def test_get_quarantine_status(self):
        """Test quarantine status."""
        status = self.manager.get_quarantine_status()
        
        self.assertTrue(status["enabled"])
        self.assertEqual(status["quarantine_dir"], str(self.quarantine_dir))
        self.assertEqual(status["quarantined_files"], 0)
        self.assertIn("audit_log", status)
        
        # Quarantine a file and check count
        self.manager.quarantine_file(str(self.test_file))
        status = self.manager.get_quarantine_status()
        self.assertEqual(status["quarantined_files"], 1)
    
    def test_mapping_persistence(self):
        """Test quarantine mapping persistence."""
        # Quarantine a file
        quarantine_result = self.manager.quarantine_file(str(self.test_file))
        sha256 = quarantine_result["sha256"]
        
        # Create new manager (simulates restart)
        new_manager = QuarantineManager()
        
        # Should load the mapping
        self.assertIn(sha256, new_manager._quarantine_mapping)
        
        # Should be able to restore using new manager
        restore_result = new_manager.restore_file(sha256)
        self.assertEqual(restore_result["status"], "restored")


class TestQuarantineFunctions(unittest.TestCase):
    """Test module-level functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QUARANTINE_MODULE_AVAILABLE:
            self.skipTest("Quarantine module not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.quarantine_dir = Path(self.temp_dir) / "quarantine"
        
        # Mock quarantine directory
        self.quarantine_patcher = mock.patch('console.quarantine.QUARANTINE_DIR', self.quarantine_dir)
        self.quarantine_patcher.start()
        
        # Create test file
        self.test_file = Path(self.temp_dir) / "test_file.txt"
        with open(self.test_file, "w") as f:
            f.write("Test content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'quarantine_patcher'):
            self.quarantine_patcher.stop()
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_global_manager(self):
        """Test global manager singleton."""
        manager1 = get_manager()
        manager2 = get_manager()
        self.assertIs(manager1, manager2)  # Should be the same instance
    
    def test_quarantine_file_function(self):
        """Test module-level quarantine_file function."""
        result = quarantine_file(str(self.test_file))
        
        self.assertIn("status", result)
        if result["status"] == "quarantined":
            self.assertIn("sha256", result)
            self.assertIn("dst", result)
    
    def test_restore_file_function(self):
        """Test module-level restore_file function."""
        # First quarantine a file
        quarantine_result = quarantine_file(str(self.test_file))
        
        if quarantine_result["status"] == "quarantined":
            sha256 = quarantine_result["sha256"]
            restore_result = restore_file(sha256)
            self.assertIn("status", restore_result)
    
    def test_list_quarantined_files_function(self):
        """Test module-level list_quarantined_files function."""
        files = list_quarantined_files()
        self.assertIsInstance(files, list)
    
    def test_get_quarantine_status_function(self):
        """Test module-level get_quarantine_status function."""
        status = get_quarantine_status()
        
        self.assertIn("enabled", status)
        self.assertIn("quarantine_dir", status)
        self.assertIn("quarantined_files", status)


class TestQuarantineConfiguration(unittest.TestCase):
    """Test quarantine configuration."""
    
    def test_feature_flags(self):
        """Test feature flag parsing."""
        # QUARANTINE_ENABLED should be True due to setUp
        self.assertTrue(QUARANTINE_ENABLED)
    
    def test_paths_configuration(self):
        """Test paths are properly configured."""
        from console.quarantine import QUARANTINE_DIR, AUDIT_LOG_FILE
        
        self.assertEqual(QUARANTINE_DIR, Path("data/quarantine"))
        self.assertEqual(AUDIT_LOG_FILE, QUARANTINE_DIR / "audit_log.jsonl")


if __name__ == "__main__":
    unittest.main()
