# File: tests/test_preflight_checks.py
# Purpose: Unit tests for preflight checks system (P3-004)

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import socket

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from console.preflight_checks import (
    PreflightResult, PreflightSummary, PreflightChecker,
    run_preflight_checks
)


class TestPreflightResult(unittest.TestCase):
    """Test preflight result data structure"""
    
    def test_preflight_result_creation(self):
        """Test creating preflight result"""
        result = PreflightResult(
            check_name="test_check",
            status="pass",
            message="Test passed",
            details={"test": "data"},
            severity="info"
        )
        
        self.assertEqual(result.check_name, "test_check")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.message, "Test passed")
        self.assertEqual(result.details, {"test": "data"})
        self.assertEqual(result.severity, "info")
    
    def test_preflight_result_defaults(self):
        """Test preflight result with defaults"""
        result = PreflightResult(
            check_name="test_check",
            status="warn",
            message="Test warning"
        )
        
        self.assertIsNone(result.details)
        self.assertEqual(result.severity, "info")


class TestPreflightChecker(unittest.TestCase):
    """Test preflight checker functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.checker = PreflightChecker()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_check_python_environment_compatible(self):
        """Test Python environment check with compatible version"""
        with patch('sys.version_info', (3, 9, 0)):
            result = self.checker.check_python_environment()
            
            self.assertEqual(result.check_name, "python_version")
            self.assertEqual(result.status, "pass")
            self.assertIn("3.9.0", result.message)
    
    def test_check_python_environment_old_supported(self):
        """Test Python environment check with old but supported version"""
        with patch('sys.version_info', (3, 8, 5)):
            result = self.checker.check_python_environment()
            
            self.assertEqual(result.check_name, "python_version")
            self.assertEqual(result.status, "warn")
            self.assertIn("3.8.5", result.message)
            self.assertEqual(result.severity, "warning")
    
    def test_check_python_environment_too_old(self):
        """Test Python environment check with unsupported version"""
        with patch('sys.version_info', (3, 7, 0)):
            result = self.checker.check_python_environment()
            
            self.assertEqual(result.check_name, "python_version")
            self.assertEqual(result.status, "fail")
            self.assertIn("too old", result.message)
            self.assertEqual(result.severity, "critical")
    
    @patch('importlib.util.find_spec')
    def test_check_required_modules_all_present(self, mock_find_spec):
        """Test required modules check with all modules present"""
        mock_find_spec.return_value = MagicMock()  # All modules found
        
        result = self.checker.check_required_modules()
        
        self.assertEqual(result.check_name, "required_modules")
        self.assertEqual(result.status, "pass")
        self.assertIn("All required modules available", result.message)
    
    @patch('importlib.util.find_spec')
    def test_check_required_modules_missing_required(self, mock_find_spec):
        """Test required modules check with missing required modules"""
        def find_spec_side_effect(module):
            if module in ["json", "os"]:  # These are "required"
                return MagicMock()
            return None
        
        mock_find_spec.side_effect = find_spec_side_effect
        
        result = self.checker.check_required_modules()
        
        self.assertEqual(result.check_name, "required_modules")
        self.assertEqual(result.status, "fail")
        self.assertIn("Missing required modules", result.message)
        self.assertEqual(result.severity, "critical")
    
    @patch('importlib.util.find_spec')
    def test_check_required_modules_missing_optional(self, mock_find_spec):
        """Test required modules check with missing optional modules"""
        required_modules = [
            "json", "os", "sys", "logging", "pathlib", "typing",
            "hashlib", "base64", "datetime", "time", "re", "uuid",
            "urllib", "http", "socket", "ssl", "threading", "subprocess"
        ]
        
        def find_spec_side_effect(module):
            if module in required_modules:
                return MagicMock()
            return None  # Optional modules not found
        
        mock_find_spec.side_effect = find_spec_side_effect
        
        result = self.checker.check_required_modules()
        
        self.assertEqual(result.check_name, "required_modules")
        self.assertEqual(result.status, "warn")
        self.assertIn("Missing optional modules", result.message)
        self.assertEqual(result.severity, "warning")
    
    def test_check_file_permissions_success(self):
        """Test file permissions check with adequate permissions"""
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'), \
             patch('pathlib.Path.unlink'), \
             patch('pathlib.Path.rmdir'):
            
            result = self.checker.check_file_permissions()
            
            self.assertEqual(result.check_name, "file_permissions")
            self.assertEqual(result.status, "pass")
            self.assertIn("adequate", result.message)
    
    @patch('pathlib.Path.mkdir')
    def test_check_file_permissions_failure(self, mock_mkdir):
        """Test file permissions check with permission errors"""
        mock_mkdir.side_effect = PermissionError("Access denied")
        
        result = self.checker.check_file_permissions()
        
        self.assertEqual(result.check_name, "file_permissions")
        self.assertEqual(result.status, "fail")
        self.assertIn("permission issues", result.message)
        self.assertEqual(result.severity, "critical")
    
    @patch('socket.socket')
    def test_check_network_connectivity_success(self, mock_socket):
        """Test network connectivity check with available port"""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 1  # Port not in use
        mock_socket.return_value = mock_sock
        
        with patch('socket.gethostbyname'):
            result = self.checker.check_network_connectivity()
            
            self.assertEqual(result.check_name, "network_connectivity")
            self.assertEqual(result.status, "pass")
            self.assertIn("connectivity OK", result.message)
    
    @patch('socket.socket')
    def test_check_network_connectivity_port_in_use(self, mock_socket):
        """Test network connectivity check with port in use"""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0  # Port in use
        mock_socket.return_value = mock_sock
        
        with patch('socket.gethostbyname'):
            result = self.checker.check_network_connectivity()
            
            self.assertEqual(result.check_name, "network_connectivity")
            self.assertEqual(result.status, "warn")
            self.assertIn("already in use", result.message)
            self.assertEqual(result.severity, "warning")
    
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_check_system_resources_adequate(self, mock_disk, mock_memory):
        """Test system resources check with adequate resources"""
        # Mock adequate memory (200MB available)
        mock_memory_obj = MagicMock()
        mock_memory_obj.available = 200 * 1024 * 1024
        mock_memory.return_value = mock_memory_obj
        
        # Mock adequate disk (200MB free)
        mock_disk_obj = MagicMock()
        mock_disk_obj.free = 200 * 1024 * 1024
        mock_disk.return_value = mock_disk_obj
        
        result = self.checker.check_system_resources()
        
        self.assertEqual(result.check_name, "system_resources")
        self.assertEqual(result.status, "pass")
        self.assertIn("adequate", result.message)
    
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_check_system_resources_low_memory(self, mock_disk, mock_memory):
        """Test system resources check with low memory"""
        # Mock low memory (50MB available)
        mock_memory_obj = MagicMock()
        mock_memory_obj.available = 50 * 1024 * 1024
        mock_memory.return_value = mock_memory_obj
        
        # Mock adequate disk
        mock_disk_obj = MagicMock()
        mock_disk_obj.free = 200 * 1024 * 1024
        mock_disk.return_value = mock_disk_obj
        
        result = self.checker.check_system_resources()
        
        self.assertEqual(result.check_name, "system_resources")
        self.assertEqual(result.status, "fail")
        self.assertIn("Very low memory", result.message)
        self.assertEqual(result.severity, "critical")
    
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_check_system_resources_warnings(self, mock_disk, mock_memory):
        """Test system resources check with warning conditions"""
        # Mock borderline memory (100MB available)
        mock_memory_obj = MagicMock()
        mock_memory_obj.available = 100 * 1024 * 1024
        mock_memory.return_value = mock_memory_obj
        
        # Mock adequate disk
        mock_disk_obj = MagicMock()
        mock_disk_obj.free = 200 * 1024 * 1024
        mock_disk.return_value = mock_disk_obj
        
        result = self.checker.check_system_resources()
        
        self.assertEqual(result.check_name, "system_resources")
        self.assertEqual(result.status, "warn")
        self.assertIn("Low memory", result.message)
        self.assertEqual(result.severity, "warning")
    
    def test_check_system_resources_psutil_missing(self):
        """Test system resources check without psutil"""
        with patch('console.preflight_checks.psutil', side_effect=ImportError):
            result = self.checker.check_system_resources()
            
            self.assertEqual(result.check_name, "system_resources")
            self.assertEqual(result.status, "warn")
            self.assertIn("psutil not available", result.message)
            self.assertEqual(result.severity, "warning")
    
    @patch.dict(os.environ, {"CONSOLE_AUTH_ENABLED": "1", "CONSOLE_AUTH_SESSION_KEY": "short"})
    def test_check_configuration_integrity_warnings(self):
        """Test configuration integrity check with warnings"""
        result = self.checker.check_configuration_integrity()
        
        self.assertEqual(result.check_name, "configuration_integrity")
        self.assertEqual(result.status, "warn")
        self.assertIn("at least 16 characters", result.message)
        self.assertEqual(result.severity, "warning")
    
    @patch.dict(os.environ, {"CONSOLE_AUTH_ENABLED": "1"})
    def test_check_configuration_integrity_errors(self):
        """Test configuration integrity check with errors"""
        # Missing required session key
        result = self.checker.check_configuration_integrity()
        
        self.assertEqual(result.check_name, "configuration_integrity")
        self.assertEqual(result.status, "fail")
        self.assertIn("SESSION_KEY required", result.message)
        self.assertEqual(result.severity, "error")
    
    @patch.dict(os.environ, {"DEBUG": "1"})
    def test_check_security_settings_warnings(self):
        """Test security settings check with warnings"""
        result = self.checker.check_security_settings()
        
        self.assertEqual(result.check_name, "security_settings")
        self.assertEqual(result.status, "warn")
        self.assertIn("Debug mode", result.message)
        self.assertEqual(result.severity, "warning")
    
    def test_check_security_settings_pass(self):
        """Test security settings check with good settings"""
        with patch.dict(os.environ, {"LOG_REDACT_SECRETS": "1"}, clear=False):
            result = self.checker.check_security_settings()
            
            # Should pass or warn, but not fail
            self.assertIn(result.status, ["pass", "warn"])
    
    def test_run_all_checks(self):
        """Test running all preflight checks"""
        with patch.object(self.checker, 'check_python_environment') as mock_python, \
             patch.object(self.checker, 'check_required_modules') as mock_modules, \
             patch.object(self.checker, 'check_file_permissions') as mock_files, \
             patch.object(self.checker, 'check_network_connectivity') as mock_network, \
             patch.object(self.checker, 'check_system_resources') as mock_resources, \
             patch.object(self.checker, 'check_configuration_integrity') as mock_config, \
             patch.object(self.checker, 'check_security_settings') as mock_security:
            
            # Mock all checks to pass
            mock_python.return_value = PreflightResult("python", "pass", "OK")
            mock_modules.return_value = PreflightResult("modules", "pass", "OK")
            mock_files.return_value = PreflightResult("files", "pass", "OK")
            mock_network.return_value = PreflightResult("network", "pass", "OK")
            mock_resources.return_value = PreflightResult("resources", "pass", "OK")
            mock_config.return_value = PreflightResult("config", "pass", "OK")
            mock_security.return_value = PreflightResult("security", "pass", "OK")
            
            summary = self.checker.run_all_checks()
            
            self.assertEqual(summary.total_checks, 7)
            self.assertEqual(summary.passed, 7)
            self.assertEqual(summary.warnings, 0)
            self.assertEqual(summary.failures, 0)
            self.assertEqual(summary.overall_status, "pass")
    
    def test_run_all_checks_with_failures(self):
        """Test running all checks with some failures"""
        with patch.object(self.checker, 'check_python_environment') as mock_python, \
             patch.object(self.checker, 'check_required_modules') as mock_modules, \
             patch.object(self.checker, 'check_file_permissions') as mock_files, \
             patch.object(self.checker, 'check_network_connectivity') as mock_network, \
             patch.object(self.checker, 'check_system_resources') as mock_resources, \
             patch.object(self.checker, 'check_configuration_integrity') as mock_config, \
             patch.object(self.checker, 'check_security_settings') as mock_security:
            
            # Mix of pass, warn, and fail
            mock_python.return_value = PreflightResult("python", "pass", "OK")
            mock_modules.return_value = PreflightResult("modules", "warn", "Warning")
            mock_files.return_value = PreflightResult("files", "fail", "Error")
            mock_network.return_value = PreflightResult("network", "pass", "OK")
            mock_resources.return_value = PreflightResult("resources", "warn", "Warning")
            mock_config.return_value = PreflightResult("config", "fail", "Error")
            mock_security.return_value = PreflightResult("security", "pass", "OK")
            
            summary = self.checker.run_all_checks()
            
            self.assertEqual(summary.total_checks, 7)
            self.assertEqual(summary.passed, 3)
            self.assertEqual(summary.warnings, 2)
            self.assertEqual(summary.failures, 2)
            self.assertEqual(summary.overall_status, "fail")


class TestPreflightFunctions(unittest.TestCase):
    """Test module-level functions"""
    
    @patch.object(PreflightChecker, 'run_all_checks')
    def test_run_preflight_checks(self, mock_run_checks):
        """Test run_preflight_checks function"""
        mock_summary = PreflightSummary(
            total_checks=5,
            passed=4,
            warnings=1,
            failures=0,
            results=[],
            overall_status="warn",
            execution_time_seconds=1.5
        )
        mock_run_checks.return_value = mock_summary
        
        summary = run_preflight_checks(verbose=False)
        
        self.assertEqual(summary.overall_status, "warn")
        self.assertEqual(summary.total_checks, 5)


if __name__ == "__main__":
    unittest.main()
