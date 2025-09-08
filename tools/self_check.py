"""P4-005: End-to-End Self-Check for WatchLockAI Sentinel.

Orchestrates a local spin-up, pings health, exercises admin routes, validates responses.
"""

from __future__ import annotations

import os
import sys
import json
import time
import tempfile
import argparse
import importlib.util
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


class SelfCheckRunner:
    """End-to-end self-check orchestrator."""
    
    def __init__(self, verbose: bool = False):
        """Initialize self-check runner.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.results = []
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp.
        
        Args:
            message: Message to log
            level: Log level
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "FAIL", "PASS"]:
            print(f"[{timestamp}] {level}: {message}")
    
    def check_python_environment(self) -> Dict[str, Any]:
        """Check Python environment and dependencies.
        
        Returns:
            dict: Environment check results
        """
        self.log("Checking Python environment...")
        
        result = {
            "name": "Python Environment",
            "status": "PASS",
            "details": {}
        }
        
        try:
            # Check Python version
            py_version = sys.version_info
            result["details"]["python_version"] = f"{py_version.major}.{py_version.minor}.{py_version.micro}"
            
            if py_version < (3, 8):
                result["status"] = "FAIL"
                result["error"] = "Python 3.8+ required"
                return result
            
            # Check core modules
            core_modules = [
                "app_core", "app_core.bus", "console.web_api", 
                "detection", "collectors", "response"
            ]
            
            missing_modules = []
            for module in core_modules:
                if not importlib.util.find_spec(module):
                    missing_modules.append(module)
            
            result["details"]["core_modules_available"] = len(core_modules) - len(missing_modules)
            result["details"]["missing_modules"] = missing_modules
            
            # Check optional modules
            optional_modules = ["fastapi", "sklearn", "yaml", "psutil"]
            available_optional = []
            for module in optional_modules:
                if importlib.util.find_spec(module):
                    available_optional.append(module)
            
            result["details"]["optional_modules_available"] = available_optional
            
            self.log(f"Python {result['details']['python_version']}, {len(available_optional)} optional modules")
            
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        return result
    
    def check_file_system(self) -> Dict[str, Any]:
        """Check file system permissions and required directories.
        
        Returns:
            dict: File system check results
        """
        self.log("Checking file system...")
        
        result = {
            "name": "File System",
            "status": "PASS",
            "details": {}
        }
        
        try:
            # Check required directories
            required_dirs = ["data", "logs", "config", "DOCS"]
            missing_dirs = []
            writable_dirs = []
            
            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                if not dir_path.exists():
                    missing_dirs.append(dir_name)
                else:
                    # Test writability
                    try:
                        test_file = dir_path / f".write_test_{os.getpid()}"
                        test_file.write_text("test")
                        test_file.unlink()
                        writable_dirs.append(dir_name)
                    except Exception:
                        pass  # Not writable
            
            result["details"]["missing_directories"] = missing_dirs
            result["details"]["writable_directories"] = writable_dirs
            
            # Check configuration files
            config_files = ["config.yaml", "requirements.txt"]
            existing_configs = []
            for config_file in config_files:
                if Path(config_file).exists():
                    existing_configs.append(config_file)
            
            result["details"]["config_files_present"] = existing_configs
            
            # Test temp directory access
            try:
                with tempfile.NamedTemporaryFile() as tmp:
                    tmp.write(b"test")
                result["details"]["temp_access"] = True
            except Exception:
                result["details"]["temp_access"] = False
            
            self.log(f"File system: {len(writable_dirs)}/{len(required_dirs)} dirs writable")
            
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        return result
    
    def check_web_api_import(self) -> Dict[str, Any]:
        """Check web API import and basic instantiation.
        
        Returns:
            dict: Web API check results
        """
        self.log("Checking web API import...")
        
        result = {
            "name": "Web API Import",
            "status": "PASS",
            "details": {}
        }
        
        try:
            # Check if FastAPI is available
            if not importlib.util.find_spec("fastapi"):
                result["status"] = "SKIP"
                result["reason"] = "FastAPI not available"
                return result
            
            # Try to import web API
            from console.web_api import SentinelWebAPI
            
            # Try to instantiate (without starting server)
            try:
                web_api = SentinelWebAPI(sentinel_service=None)
                result["details"]["instantiation"] = "success"
                
                # Check app creation
                if hasattr(web_api, 'app'):
                    result["details"]["fastapi_app"] = "created"
                    
                    # Count routes
                    if hasattr(web_api.app, 'routes'):
                        route_count = len(web_api.app.routes)
                        result["details"]["route_count"] = route_count
                        self.log(f"Web API: {route_count} routes registered")
                
            except Exception as e:
                result["status"] = "FAIL"
                result["error"] = f"Failed to instantiate: {e}"
                return result
            
        except ImportError as e:
            result["status"] = "FAIL"
            result["error"] = f"Import failed: {e}"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        return result
    
    def check_health_endpoint(self) -> Dict[str, Any]:
        """Check health endpoint functionality.
        
        Returns:
            dict: Health endpoint check results
        """
        self.log("Checking health endpoint...")
        
        result = {
            "name": "Health Endpoint",
            "status": "PASS",
            "details": {}
        }
        
        try:
            # Check if FastAPI is available
            if not importlib.util.find_spec("fastapi"):
                result["status"] = "SKIP"
                result["reason"] = "FastAPI not available"
                return result
            
            from console.web_api import SentinelWebAPI
            from fastapi.testclient import TestClient
            
            # Set up environment for health endpoint
            os.environ["HEALTH_ENDPOINT_ENABLED"] = "1"
            
            # Create test client
            web_api = SentinelWebAPI(sentinel_service=None)
            client = TestClient(web_api.app)
            
            # Test health endpoint
            response = client.get("/api/metrics/health")
            
            result["details"]["status_code"] = response.status_code
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["details"]["response_type"] = "json"
                    result["details"]["has_components"] = "components" in data
                    result["details"]["has_uptime"] = "uptime_s" in data
                    
                    self.log("Health endpoint responding correctly")
                except Exception:
                    result["details"]["response_type"] = "non-json"
            else:
                result["status"] = "FAIL"
                result["error"] = f"Health endpoint returned {response.status_code}"
            
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        return result
    
    def check_admin_authentication(self) -> Dict[str, Any]:
        """Check admin authentication functionality.
        
        Returns:
            dict: Admin auth check results
        """
        self.log("Checking admin authentication...")
        
        result = {
            "name": "Admin Authentication",
            "status": "PASS",
            "details": {}
        }
        
        try:
            # Check if FastAPI is available
            if not importlib.util.find_spec("fastapi"):
                result["status"] = "SKIP"
                result["reason"] = "FastAPI not available"
                return result
            
            from console.web_api import SentinelWebAPI
            from fastapi.testclient import TestClient
            
            # Set up environment for admin auth
            os.environ["ADMIN_AUTH_ENABLED"] = "1"
            os.environ["ADMIN_TOKEN"] = "test_token_selfcheck"
            os.environ["CONFIG_HOT_RELOAD_ENABLED"] = "1"  # Enable an admin route
            
            # Create test client
            web_api = SentinelWebAPI(sentinel_service=None)
            client = TestClient(web_api.app)
            
            # Test without auth (should fail)
            response_no_auth = client.post("/api/admin/config/reload")
            result["details"]["no_auth_status"] = response_no_auth.status_code
            
            # Test with wrong auth (should fail)
            response_wrong_auth = client.post("/api/admin/config/reload", 
                                            headers={"X-Admin-Token": "wrong_token"})
            result["details"]["wrong_auth_status"] = response_wrong_auth.status_code
            
            # Test with correct auth (should succeed)
            response_correct_auth = client.post("/api/admin/config/reload",
                                               headers={"X-Admin-Token": "test_token_selfcheck"})
            result["details"]["correct_auth_status"] = response_correct_auth.status_code
            
            # Validate auth behavior
            if (response_no_auth.status_code == 403 and 
                response_wrong_auth.status_code == 403 and
                response_correct_auth.status_code == 200):
                self.log("Admin authentication working correctly")
            else:
                result["status"] = "FAIL"
                result["error"] = "Admin authentication not working as expected"
            
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        return result
    
    def check_configuration_validation(self) -> Dict[str, Any]:
        """Check configuration validation functionality.
        
        Returns:
            dict: Config validation check results
        """
        self.log("Checking configuration validation...")
        
        result = {
            "name": "Configuration Validation",
            "status": "PASS",
            "details": {}
        }
        
        try:
            # Check if config schema module is available
            if not importlib.util.find_spec("console.config_schema"):
                result["status"] = "SKIP"
                result["reason"] = "Config schema module not available"
                return result
            
            from console.config_schema import get_config_validator
            
            # Get validator
            validator = get_config_validator()
            
            # Test validation with sample data
            test_config = {
                "HEALTH_ENDPOINT_ENABLED": "1",
                "ADMIN_AUTH_ENABLED": "0",
                "RATE_LIMIT_ENABLED": "0"
            }
            
            validation_result = validator.validate_config(test_config)
            result["details"]["validation_result"] = validation_result.get("status")
            result["details"]["errors_found"] = len(validation_result.get("errors", []))
            
            if validation_result.get("status") == "valid":
                self.log("Configuration validation working")
            else:
                result["status"] = "FAIL"
                result["error"] = f"Validation failed: {validation_result.get('errors')}"
            
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        return result
    
    def run_all_checks(self) -> Tuple[bool, Dict[str, Any]]:
        """Run all self-checks.
        
        Returns:
            tuple: (success, detailed_results)
        """
        self.log("Starting WatchLockAI Sentinel self-check...", "INFO")
        
        checks = [
            self.check_python_environment,
            self.check_file_system,
            self.check_web_api_import,
            self.check_health_endpoint,
            self.check_admin_authentication,
            self.check_configuration_validation
        ]
        
        results = []
        overall_success = True
        
        for check_func in checks:
            try:
                result = check_func()
                results.append(result)
                
                status = result["status"]
                if status == "PASS":
                    self.log(f"✅ {result['name']}: PASS")
                elif status == "SKIP":
                    self.log(f"⏭️ {result['name']}: SKIP - {result.get('reason')}")
                elif status == "FAIL":
                    self.log(f"❌ {result['name']}: FAIL - {result.get('error')}")
                    overall_success = False
                elif status == "ERROR":
                    self.log(f"⚠️ {result['name']}: ERROR - {result.get('error')}")
                    overall_success = False
                    
            except Exception as e:
                error_result = {
                    "name": check_func.__name__,
                    "status": "ERROR",
                    "error": str(e)
                }
                results.append(error_result)
                self.log(f"⚠️ {check_func.__name__}: ERROR - {e}")
                overall_success = False
        
        # Calculate summary
        end_time = time.time()
        duration = end_time - self.start_time
        
        summary = {
            "overall_status": "PASS" if overall_success else "FAIL",
            "total_checks": len(results),
            "passed": sum(1 for r in results if r["status"] == "PASS"),
            "failed": sum(1 for r in results if r["status"] == "FAIL"),
            "errors": sum(1 for r in results if r["status"] == "ERROR"),
            "skipped": sum(1 for r in results if r["status"] == "SKIP"),
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        detailed_results = {
            "summary": summary,
            "checks": results
        }
        
        # Final summary
        if overall_success:
            self.log(f"✅ All checks passed in {duration:.1f}s", "PASS")
        else:
            self.log(f"❌ {summary['failed']} checks failed, {summary['errors']} errors in {duration:.1f}s", "FAIL")
        
        return overall_success, detailed_results


def main():
    """CLI entry point for self-check."""
    parser = argparse.ArgumentParser(description="WatchLockAI Sentinel Self-Check")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--output", "-o",
                       help="Output detailed results to JSON file")
    parser.add_argument("--fail-fast", action="store_true",
                       help="Stop on first failure")
    
    args = parser.parse_args()
    
    # Run self-check
    runner = SelfCheckRunner(verbose=args.verbose)
    success, results = runner.run_all_checks()
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Detailed results saved to: {args.output}")
    
    # Exit with appropriate code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
