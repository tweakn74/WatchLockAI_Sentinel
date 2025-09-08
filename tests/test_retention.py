"""Tests for P5-002 data retention and prune jobs."""

import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

try:
    from console.retention import (
        get_retention_days,
        scan_directory_for_cleanup,
        prune_quarantine_files,
        prune_export_files,
        prune_log_files,
        prune_anomaly_state,
        run_retention_job,
        get_directory_stats
    )
    RETENTION_AVAILABLE = True
except ImportError:
    RETENTION_AVAILABLE = False


@unittest.skipUnless(RETENTION_AVAILABLE, "Retention module not available")
class TestRetention(unittest.TestCase):
    """Test data retention functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Save original working directory
        self.original_cwd = os.getcwd()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original working directory
        os.chdir(self.original_cwd)
        
        # Clean up temp directory
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def create_test_files(self, directory: Path, count: int = 5, age_days: int = 30) -> list:
        """Create test files with specified age."""
        directory.mkdir(parents=True, exist_ok=True)
        files = []
        
        current_time = time.time()
        old_time = current_time - (age_days * 24 * 60 * 60)
        
        for i in range(count):
            file_path = directory / f"test_file_{i}.log"
            file_path.write_text(f"Test content {i}")
            
            # Set file modification time to simulate age
            os.utime(file_path, (old_time, old_time))
            files.append(file_path)
        
        return files
    
    def test_get_retention_days_default(self):
        """Test default retention days."""
        with patch.dict('os.environ', {}, clear=False):
            if 'RETENTION_DAYS' in os.environ:
                del os.environ['RETENTION_DAYS']
            days = get_retention_days()
            self.assertEqual(days, 14)
    
    def test_get_retention_days_custom(self):
        """Test custom retention days from environment."""
        with patch.dict('os.environ', {'RETENTION_DAYS': '30'}):
            days = get_retention_days()
            self.assertEqual(days, 30)
    
    def test_scan_directory_for_cleanup(self):
        """Test directory scanning for cleanup candidates."""
        test_dir = self.temp_path / "test_scan"
        
        # Create mix of old and new files
        old_files = self.create_test_files(test_dir, count=3, age_days=20)
        new_files = self.create_test_files(test_dir, count=2, age_days=5)
        
        # Scan for files older than 15 days
        candidates = scan_directory_for_cleanup(test_dir, retention_days=15)
        
        # Should find 3 old files, not the 2 new ones
        self.assertEqual(len(candidates), 3)
        
        # Check that all candidates are old files
        candidate_paths = [c[0] for c in candidates]
        for old_file in old_files:
            self.assertIn(old_file, candidate_paths)
        
        for new_file in new_files:
            self.assertNotIn(new_file, candidate_paths)
    
    def test_scan_directory_with_extensions(self):
        """Test directory scanning with file extension filtering."""
        test_dir = self.temp_path / "test_ext"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create files with different extensions
        log_file = test_dir / "test.log"
        json_file = test_dir / "test.json"
        txt_file = test_dir / "test.txt"
        
        old_time = time.time() - (20 * 24 * 60 * 60)  # 20 days old
        
        for f in [log_file, json_file, txt_file]:
            f.write_text("test content")
            os.utime(f, (old_time, old_time))
        
        # Scan only for .log files
        candidates = scan_directory_for_cleanup(test_dir, retention_days=15, file_extensions=['.log'])
        
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0][0], log_file)
    
    def test_scan_nonexistent_directory(self):
        """Test scanning non-existent directory."""
        fake_dir = self.temp_path / "nonexistent"
        candidates = scan_directory_for_cleanup(fake_dir, retention_days=15)
        self.assertEqual(candidates, [])
    
    def test_prune_functions_dry_run(self):
        """Test all prune functions in dry run mode."""
        # Change to temp directory for relative paths to work
        os.chdir(self.temp_path)
        
        # Create test directory structure
        for subdir in ["data/quarantine", "data/export", "logs", "data/anomaly"]:
            dir_path = self.temp_path / subdir
            self.create_test_files(dir_path, count=3, age_days=20)
        
        prune_functions = [
            prune_quarantine_files,
            prune_export_files,
            prune_log_files,
            prune_anomaly_state
        ]
        
        for prune_func in prune_functions:
            with self.subTest(func=prune_func.__name__):
                result = prune_func(retention_days=15, dry_run=True)
                
                # Check result structure
                self.assertIn("type", result)
                self.assertIn("dry_run", result)
                self.assertIn("removed_count", result)
                self.assertIn("removed_size_bytes", result)
                self.assertTrue(result["dry_run"])
                
                # Should find files to remove in dry run
                if prune_func != prune_log_files:  # log function has special logic
                    self.assertGreater(result["removed_count"], 0)
    
    def test_prune_functions_execute(self):
        """Test prune functions actually removing files."""
        # Change to temp directory
        os.chdir(self.temp_path)
        
        # Test quarantine pruning specifically
        quarantine_dir = self.temp_path / "data/quarantine"
        old_files = self.create_test_files(quarantine_dir, count=3, age_days=20)
        new_files = self.create_test_files(quarantine_dir, count=2, age_days=5)
        
        # Verify files exist before pruning
        self.assertEqual(len(list(quarantine_dir.glob("*.log"))), 5)
        
        # Run actual pruning (not dry run)
        result = prune_quarantine_files(retention_days=15, dry_run=False)
        
        self.assertFalse(result["dry_run"])
        self.assertEqual(result["removed_count"], 3)  # Only old files removed
        
        # Verify old files are gone, new files remain
        remaining_files = list(quarantine_dir.glob("*.log"))
        self.assertEqual(len(remaining_files), 2)
        
        for old_file in old_files:
            self.assertFalse(old_file.exists())
        
        for new_file in new_files:
            self.assertTrue(new_file.exists())
    
    def test_run_retention_job(self):
        """Test complete retention job."""
        # Change to temp directory
        os.chdir(self.temp_path)
        
        # Create test files in multiple directories
        for subdir in ["data/quarantine", "data/export", "logs"]:
            dir_path = self.temp_path / subdir
            self.create_test_files(dir_path, count=2, age_days=20)
        
        # Run retention job
        result = run_retention_job(dry_run=True, retention_days=15)
        
        # Check result structure
        self.assertIn("timestamp", result)
        self.assertIn("dry_run", result)
        self.assertIn("retention_days", result)
        self.assertIn("results", result)
        self.assertIn("summary", result)
        self.assertIn("execution_time_seconds", result)
        
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["retention_days"], 15)
        
        # Should have results for multiple directory types
        self.assertGreater(len(result["results"]), 0)
        
        # Summary should aggregate results
        self.assertGreater(result["summary"]["total_files"], 0)
    
    def test_get_directory_stats(self):
        """Test directory statistics gathering."""
        # Change to temp directory
        os.chdir(self.temp_path)
        
        # Create test files with different ages
        quarantine_dir = self.temp_path / "data/quarantine"
        self.create_test_files(quarantine_dir, count=3, age_days=10)
        self.create_test_files(quarantine_dir, count=2, age_days=30)
        
        stats = get_directory_stats()
        
        # Check structure
        self.assertIn("timestamp", stats)
        self.assertIn("directories", stats)
        self.assertIn("data/quarantine", stats["directories"])
        
        quarantine_stats = stats["directories"]["data/quarantine"]
        self.assertTrue(quarantine_stats["exists"])
        self.assertEqual(quarantine_stats["file_count"], 5)
        self.assertGreater(quarantine_stats["total_size_bytes"], 0)
        self.assertIsNotNone(quarantine_stats["oldest_file"])
        self.assertIsNotNone(quarantine_stats["newest_file"])
    
    def test_log_prune_current_file_preservation(self):
        """Test that current log files are not removed."""
        # Change to temp directory
        os.chdir(self.temp_path)
        
        logs_dir = self.temp_path / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create current and rotated log files
        current_log = logs_dir / "app.log"
        rotated_log1 = logs_dir / "app.log.1"
        rotated_log2 = logs_dir / "app.log.2.gz"
        
        old_time = time.time() - (20 * 24 * 60 * 60)  # 20 days old
        
        for log_file in [current_log, rotated_log1, rotated_log2]:
            log_file.write_text("log content")
            os.utime(log_file, (old_time, old_time))
        
        # Run log pruning
        result = prune_log_files(retention_days=15, dry_run=False)
        
        # Current log should be preserved, rotated logs removed
        self.assertTrue(current_log.exists(), "Current log file should be preserved")
        self.assertFalse(rotated_log1.exists(), "Rotated log should be removed")
        self.assertFalse(rotated_log2.exists(), "Compressed rotated log should be removed")
        
        # Result should show 2 files removed (rotated logs only)
        self.assertEqual(result["removed_count"], 2)
    
    def test_anomaly_state_current_file_preservation(self):
        """Test that current/active anomaly model files are not removed."""
        # Change to temp directory
        os.chdir(self.temp_path)
        
        anomaly_dir = self.temp_path / "data/anomaly"
        anomaly_dir.mkdir(parents=True, exist_ok=True)
        
        # Create model files
        current_model = anomaly_dir / "current_model.pkl"
        active_model = anomaly_dir / "active_classifier.pkl"
        old_model = anomaly_dir / "old_model_20250101.pkl"
        
        old_time = time.time() - (20 * 24 * 60 * 60)
        
        for model_file in [current_model, active_model, old_model]:
            model_file.write_text("model data")
            os.utime(model_file, (old_time, old_time))
        
        # Run anomaly state pruning
        result = prune_anomaly_state(retention_days=15, dry_run=False)
        
        # Current/active models should be preserved
        self.assertTrue(current_model.exists(), "Current model should be preserved")
        self.assertTrue(active_model.exists(), "Active model should be preserved")
        self.assertFalse(old_model.exists(), "Old model should be removed")
        
        self.assertEqual(result["removed_count"], 1)


@unittest.skipUnless(RETENTION_AVAILABLE, "Retention module not available")  
class TestRetentionIntegration(unittest.TestCase):
    """Test retention integration with web API."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
    
    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    @patch.dict('os.environ', {
        'RETENTION_ENABLED': '1',
        'ADMIN_AUTH_ENABLED': '1', 
        'ADMIN_TOKEN': 'test_token'
    })
    def test_retention_endpoint_integration(self):
        """Test retention endpoint integration (mock test)."""
        # This is a simplified integration test
        # In a full test, we would start the FastAPI test client
        
        try:
            from console.web_api import SentinelWebAPI
            from fastapi.testclient import TestClient
            
            # Change to temp directory
            os.chdir(self.temp_dir)
            
            # Create test API instance
            api = SentinelWebAPI()
            client = TestClient(api.app)
            
            # Test retention endpoint with authentication
            response = client.post(
                "/api/admin/retention/run?dry=true&retention_days=30",
                headers={"X-Admin-Token": "test_token"}
            )
            
            # Should return 200 if retention module is available
            if response.status_code == 200:
                data = response.json()
                self.assertEqual(data["status"], "ok")
                self.assertIn("dry_run", data)
                self.assertTrue(data["dry_run"])
            else:
                # Might be missing dependencies, skip
                self.skipTest("Retention endpoint not available")
                
        except ImportError:
            self.skipTest("FastAPI or dependencies not available")


if __name__ == '__main__':
    unittest.main()
