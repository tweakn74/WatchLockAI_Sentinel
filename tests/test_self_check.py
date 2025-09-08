"""Tests for P4-005: Self-Check functionality."""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module under test
try:
    from tools.self_check import SelfCheckRunner
except ImportError:
    SelfCheckRunner = None


@unittest.skipUnless(SelfCheckRunner, "Self-check module not available")
class TestSelfCheck(unittest.TestCase):
    """Test self-check functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.runner = SelfCheckRunner(verbose=False)
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test directory structure
        os.chdir(self.test_dir)
        for dirname in ["data", "logs", "config", "DOCS"]:
            Path(dirname).mkdir(exist_ok=True)
        
        # Create test files
        Path("config.yaml").write_text("test: config")
        Path("requirements.txt").write_text("fastapi\nuvicorn")
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_check_python_environment_success(self):
        """Test successful Python environment check."""
        result = self.runner.check_python_environment()
        
        self.assertEqual(result["name"], "Python Environment")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("python_version", result["details"])
        self.assertIn("core_modules_available", result["details"])
        self.assertIn("optional_modules_available", result["details"])
        
        # Verify Python version format
        version = result["details"]["python_version"]
        self.assertRegex(version, r'\d+\.\d+\.\d+')
    
    def test_check_python_environment_old_version(self):
        """Test Python environment check with old version."""
        # Mock sys.version_info to simulate old Python
        with patch('sys.version_info', (3, 7, 0)):
            result = self.runner.check_python_environment()
            
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("Python 3.8+ required", result["error"])
    
    def test_check_file_system_success(self):
        """Test successful file system check."""
        result = self.runner.check_file_system()
        
        self.assertEqual(result["name"], "File System")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("missing_directories", result["details"])
        self.assertIn("writable_directories", result["details"])
        self.assertIn("config_files_present", result["details"])
        self.assertIn("temp_access", result["details"])
        
        # Should find our test directories
        writable_dirs = result["details"]["writable_directories"]
        self.assertIn("data", writable_dirs)
        self.assertIn("logs", writable_dirs)
        
        # Should find our test config files
        config_files = result["details"]["config_files_present"]
        self.assertIn("config.yaml", config_files)
        self.assertIn("requirements.txt", config_files)
    
    def test_check_file_system_missing_directories(self):
        """Test file system check with missing directories."""
        # Remove some directories
        shutil.rmtree("data")
        shutil.rmtree("logs")
        
        result = self.runner.check_file_system()
        
        self.assertEqual(result["status"], "PASS")  # Still passes, just reports missing
        missing_dirs = result["details"]["missing_directories"]
        self.assertIn("data", missing_dirs)
        self.assertIn("logs", missing_dirs)
    
    def test_check_web_api_import_no_fastapi(self):
        """Test web API import check when FastAPI is not available."""
        with patch('importlib.util.find_spec') as mock_find_spec:
            mock_find_spec.return_value = None
            
            result = self.runner.check_web_api_import()
            
            self.assertEqual(result["status"], "SKIP")
            self.assertEqual(result["reason"], "FastAPI not available")
    
    def test_check_web_api_import_success(self):
        """Test successful web API import check."""
        # Mock the imports to succeed
        mock_web_api = MagicMock()
        mock_web_api.app = MagicMock()
        mock_web_api.app.routes = [1, 2, 3]  # Mock 3 routes
        
        with patch('importlib.util.find_spec') as mock_find_spec, \
             patch('tools.self_check.SentinelWebAPI', return_value=mock_web_api):
            
            # Mock FastAPI availability
            mock_find_spec.return_value = MagicMock()
            
            result = self.runner.check_web_api_import()
            
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["details"]["instantiation"], "success")
            self.assertEqual(result["details"]["fastapi_app"], "created")
            self.assertEqual(result["details"]["route_count"], 3)
    
    def test_check_web_api_import_instantiation_failure(self):
        """Test web API import check with instantiation failure."""
        with patch('importlib.util.find_spec') as mock_find_spec, \
             patch('tools.self_check.SentinelWebAPI', side_effect=Exception("Mock error")):
            
            mock_find_spec.return_value = MagicMock()
            
            result = self.runner.check_web_api_import()
            
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("Failed to instantiate", result["error"])
    
    def test_check_health_endpoint_no_fastapi(self):
        """Test health endpoint check when FastAPI is not available."""
        with patch('importlib.util.find_spec') as mock_find_spec:
            mock_find_spec.return_value = None
            
            result = self.runner.check_health_endpoint()
            
            self.assertEqual(result["status"], "SKIP")
            self.assertEqual(result["reason"], "FastAPI not available")
    
    def test_check_health_endpoint_success(self):
        """Test successful health endpoint check."""
        # Mock FastAPI and TestClient
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ok": True,
            "components": {"event_bus": {}},
            "uptime_s": 123
        }
        
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        
        mock_web_api = MagicMock()
        mock_web_api.app = MagicMock()
        
        with patch('importlib.util.find_spec') as mock_find_spec, \
             patch('tools.self_check.SentinelWebAPI', return_value=mock_web_api), \
             patch('tools.self_check.TestClient', return_value=mock_client):
            
            mock_find_spec.return_value = MagicMock()
            
            result = self.runner.check_health_endpoint()
            
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["details"]["status_code"], 200)
            self.assertEqual(result["details"]["response_type"], "json")
            self.assertTrue(result["details"]["has_components"])
            self.assertTrue(result["details"]["has_uptime"])
    
    def test_check_health_endpoint_failure(self):
        """Test health endpoint check with failure."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        
        mock_web_api = MagicMock()
        
        with patch('importlib.util.find_spec') as mock_find_spec, \
             patch('tools.self_check.SentinelWebAPI', return_value=mock_web_api), \
             patch('tools.self_check.TestClient', return_value=mock_client):
            
            mock_find_spec.return_value = MagicMock()
            
            result = self.runner.check_health_endpoint()
            
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("returned 500", result["error"])
    
    def test_check_admin_authentication_success(self):
        """Test successful admin authentication check."""
        # Mock responses for different auth scenarios
        mock_responses = {
            'no_auth': MagicMock(status_code=403),
            'wrong_auth': MagicMock(status_code=403),
            'correct_auth': MagicMock(status_code=200)
        }
        
        def mock_post(url, headers=None):
            if not headers or headers.get("X-Admin-Token") != "test_token_selfcheck":
                if not headers:
                    return mock_responses['no_auth']
                else:
                    return mock_responses['wrong_auth']
            else:
                return mock_responses['correct_auth']
        
        mock_client = MagicMock()
        mock_client.post.side_effect = mock_post
        
        mock_web_api = MagicMock()
        
        with patch('importlib.util.find_spec') as mock_find_spec, \
             patch('tools.self_check.SentinelWebAPI', return_value=mock_web_api), \
             patch('tools.self_check.TestClient', return_value=mock_client):
            
            mock_find_spec.return_value = MagicMock()
            
            result = self.runner.check_admin_authentication()
            
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["details"]["no_auth_status"], 403)
            self.assertEqual(result["details"]["wrong_auth_status"], 403)
            self.assertEqual(result["details"]["correct_auth_status"], 200)
    
    def test_check_admin_authentication_failure(self):
        """Test admin authentication check with failure."""
        # Mock incorrect behavior (no auth returns 200)
        mock_response = MagicMock(status_code=200)
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        
        mock_web_api = MagicMock()
        
        with patch('importlib.util.find_spec') as mock_find_spec, \
             patch('tools.self_check.SentinelWebAPI', return_value=mock_web_api), \
             patch('tools.self_check.TestClient', return_value=mock_client):
            
            mock_find_spec.return_value = MagicMock()
            
            result = self.runner.check_admin_authentication()
            
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("not working as expected", result["error"])
    
    def test_check_configuration_validation_no_module(self):
        """Test configuration validation check when module is not available."""
        with patch('importlib.util.find_spec') as mock_find_spec:
            mock_find_spec.return_value = None
            
            result = self.runner.check_configuration_validation()
            
            self.assertEqual(result["status"], "SKIP")
            self.assertEqual(result["reason"], "Config schema module not available")
    
    def test_check_configuration_validation_success(self):
        """Test successful configuration validation check."""
        mock_validator = MagicMock()
        mock_validator.validate_config.return_value = {
            "status": "valid",
            "errors": []
        }
        
        with patch('importlib.util.find_spec') as mock_find_spec, \
             patch('tools.self_check.get_config_validator', return_value=mock_validator):
            
            mock_find_spec.return_value = MagicMock()
            
            result = self.runner.check_configuration_validation()
            
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["details"]["validation_result"], "valid")
            self.assertEqual(result["details"]["errors_found"], 0)
    
    def test_check_configuration_validation_failure(self):
        """Test configuration validation check with validation errors."""
        mock_validator = MagicMock()
        mock_validator.validate_config.return_value = {
            "status": "invalid",
            "errors": ["Test error 1", "Test error 2"]
        }
        
        with patch('importlib.util.find_spec') as mock_find_spec, \
             patch('tools.self_check.get_config_validator', return_value=mock_validator):
            
            mock_find_spec.return_value = MagicMock()
            
            result = self.runner.check_configuration_validation()
            
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("Validation failed", result["error"])
    
    def test_run_all_checks_success(self):
        """Test running all checks successfully."""
        # Mock all individual check methods to return success
        with patch.object(self.runner, 'check_python_environment', return_value={"name": "Python Environment", "status": "PASS"}) as mock1, \
             patch.object(self.runner, 'check_file_system', return_value={"name": "File System", "status": "PASS"}) as mock2, \
             patch.object(self.runner, 'check_web_api_import', return_value={"name": "Web API Import", "status": "PASS"}) as mock3, \
             patch.object(self.runner, 'check_health_endpoint', return_value={"name": "Health Endpoint", "status": "PASS"}) as mock4, \
             patch.object(self.runner, 'check_admin_authentication', return_value={"name": "Admin Authentication", "status": "PASS"}) as mock5, \
             patch.object(self.runner, 'check_configuration_validation', return_value={"name": "Configuration Validation", "status": "PASS"}) as mock6:
            
            success, results = self.runner.run_all_checks()
            
            self.assertTrue(success)
            self.assertEqual(results["summary"]["overall_status"], "PASS")
            self.assertEqual(results["summary"]["total_checks"], 6)
            self.assertEqual(results["summary"]["passed"], 6)
            self.assertEqual(results["summary"]["failed"], 0)
            self.assertEqual(results["summary"]["errors"], 0)
            self.assertEqual(results["summary"]["skipped"], 0)
    
    def test_run_all_checks_with_failures(self):
        """Test running all checks with some failures."""
        # Mock some checks to fail
        with patch.object(self.runner, 'check_python_environment', return_value={"name": "Python Environment", "status": "PASS"}) as mock1, \
             patch.object(self.runner, 'check_file_system', return_value={"name": "File System", "status": "FAIL", "error": "Test error"}) as mock2, \
             patch.object(self.runner, 'check_web_api_import', return_value={"name": "Web API Import", "status": "SKIP", "reason": "Not available"}) as mock3, \
             patch.object(self.runner, 'check_health_endpoint', return_value={"name": "Health Endpoint", "status": "ERROR", "error": "Test error"}) as mock4, \
             patch.object(self.runner, 'check_admin_authentication', return_value={"name": "Admin Authentication", "status": "PASS"}) as mock5, \
             patch.object(self.runner, 'check_configuration_validation', return_value={"name": "Configuration Validation", "status": "PASS"}) as mock6:
            
            success, results = self.runner.run_all_checks()
            
            self.assertFalse(success)
            self.assertEqual(results["summary"]["overall_status"], "FAIL")
            self.assertEqual(results["summary"]["total_checks"], 6)
            self.assertEqual(results["summary"]["passed"], 3)
            self.assertEqual(results["summary"]["failed"], 1)
            self.assertEqual(results["summary"]["errors"], 1)
            self.assertEqual(results["summary"]["skipped"], 1)
    
    def test_run_all_checks_with_exception(self):
        """Test running all checks with exceptions in check methods."""
        # Mock one check to raise an exception
        with patch.object(self.runner, 'check_python_environment', side_effect=Exception("Test exception")) as mock1, \
             patch.object(self.runner, 'check_file_system', return_value={"name": "File System", "status": "PASS"}) as mock2, \
             patch.object(self.runner, 'check_web_api_import', return_value={"name": "Web API Import", "status": "PASS"}) as mock3, \
             patch.object(self.runner, 'check_health_endpoint', return_value={"name": "Health Endpoint", "status": "PASS"}) as mock4, \
             patch.object(self.runner, 'check_admin_authentication', return_value={"name": "Admin Authentication", "status": "PASS"}) as mock5, \
             patch.object(self.runner, 'check_configuration_validation', return_value={"name": "Configuration Validation", "status": "PASS"}) as mock6:
            
            success, results = self.runner.run_all_checks()
            
            self.assertFalse(success)
            self.assertEqual(results["summary"]["total_checks"], 6)
            self.assertEqual(results["summary"]["errors"], 1)
            
            # Find the error result
            error_result = next(r for r in results["checks"] if r["status"] == "ERROR")
            self.assertIn("Test exception", error_result["error"])
    
    def test_logging_functionality(self):
        """Test logging functionality in verbose mode."""
        verbose_runner = SelfCheckRunner(verbose=True)
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            verbose_runner.log("Test message", "INFO")
            
            # Should have printed the message
            mock_print.assert_called_once()
            args = mock_print.call_args[0][0]
            self.assertIn("INFO: Test message", args)
    
    def test_logging_non_verbose(self):
        """Test logging in non-verbose mode."""
        non_verbose_runner = SelfCheckRunner(verbose=False)
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            non_verbose_runner.log("Test message", "INFO")
            
            # Should not have printed for INFO level
            mock_print.assert_not_called()
    
    def test_logging_error_level_always_prints(self):
        """Test that error level messages always print."""
        non_verbose_runner = SelfCheckRunner(verbose=False)
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            non_verbose_runner.log("Error message", "ERROR")
            
            # Should have printed even in non-verbose mode
            mock_print.assert_called_once()


if __name__ == '__main__':
    unittest.main()
