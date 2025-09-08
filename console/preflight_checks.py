# File: console/preflight_checks.py
# Purpose: Deepened preflight checks for configuration and environment sanity (P3-004)

from __future__ import annotations
import os
import sys
import json
import logging
import tempfile
import shutil
import subprocess
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import importlib.util
import socket
import psutil


logger = logging.getLogger(__name__)


@dataclass
class PreflightResult:
    """Result of a preflight check"""
    check_name: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = "info"  # "info", "warning", "error", "critical"


@dataclass
class PreflightSummary:
    """Summary of all preflight checks"""
    total_checks: int
    passed: int
    warnings: int
    failures: int
    results: List[PreflightResult]
    overall_status: str  # "pass", "warn", "fail"
    execution_time_seconds: float


class PreflightChecker:
    """Comprehensive preflight checks for system readiness"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize preflight checker
        
        Args:
            config: Optional configuration override
        """
        self.config = config or {}
        self.results = []
        
    def check_python_environment(self) -> PreflightResult:
        """Check Python environment compatibility
        
        Returns:
            PreflightResult: Python environment check result
        """
        try:
            version_info = sys.version_info
            python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
            
            # Check minimum Python version (3.8+)
            if version_info < (3, 8):
                return PreflightResult(
                    check_name="python_version",
                    status="fail",
                    message=f"Python {python_version} is too old (minimum 3.8 required)",
                    severity="critical"
                )
            
            # Check for deprecated Python versions
            if version_info < (3, 9):
                return PreflightResult(
                    check_name="python_version", 
                    status="warn",
                    message=f"Python {python_version} is supported but consider upgrading to 3.9+",
                    details={"version": python_version, "recommended": "3.9+"},
                    severity="warning"
                )
                
            return PreflightResult(
                check_name="python_version",
                status="pass",
                message=f"Python {python_version} is compatible",
                details={"version": python_version}
            )
            
        except Exception as e:
            return PreflightResult(
                check_name="python_version",
                status="fail", 
                message=f"Failed to check Python version: {e}",
                severity="error"
            )
    
    def check_required_modules(self) -> PreflightResult:
        """Check required Python modules are available
        
        Returns:
            PreflightResult: Required modules check result
        """
        required_modules = [
            "json", "os", "sys", "logging", "pathlib", "typing",
            "hashlib", "base64", "datetime", "time", "re", "uuid",
            "urllib", "http", "socket", "ssl", "threading", "subprocess"
        ]
        
        optional_modules = {
            "psutil": "System monitoring features",
            "flask": "Web API functionality", 
            "werkzeug": "Web server functionality"
        }
        
        missing_required = []
        missing_optional = []
        
        # Check required modules
        for module in required_modules:
            if not importlib.util.find_spec(module):
                missing_required.append(module)
        
        # Check optional modules
        for module, description in optional_modules.items():
            if not importlib.util.find_spec(module):
                missing_optional.append((module, description))
        
        if missing_required:
            return PreflightResult(
                check_name="required_modules",
                status="fail",
                message=f"Missing required modules: {', '.join(missing_required)}",
                details={"missing": missing_required},
                severity="critical"
            )
        
        if missing_optional:
            missing_descriptions = [f"{mod} ({desc})" for mod, desc in missing_optional]
            return PreflightResult(
                check_name="required_modules", 
                status="warn",
                message=f"Missing optional modules: {', '.join(missing_descriptions)}",
                details={"missing_optional": [mod for mod, _ in missing_optional]},
                severity="warning"
            )
            
        return PreflightResult(
            check_name="required_modules",
            status="pass",
            message="All required modules available"
        )
    
    def check_file_permissions(self) -> PreflightResult:
        """Check file system permissions
        
        Returns:
            PreflightResult: File permissions check result
        """
        issues = []
        
        # Check write access to logs directory
        log_dir = Path("logs")
        try:
            log_dir.mkdir(exist_ok=True)
            test_file = log_dir / ".permission_test"
            test_file.write_text("test")
            test_file.unlink()
        except (OSError, PermissionError) as e:
            issues.append(f"Cannot write to logs directory: {e}")
        
        # Check write access to data directory  
        data_dir = Path("data")
        try:
            data_dir.mkdir(exist_ok=True)
            (data_dir / "temp").mkdir(exist_ok=True)
            test_file = data_dir / "temp" / ".permission_test"
            test_file.write_text("test") 
            test_file.unlink()
            (data_dir / "temp").rmdir()
        except (OSError, PermissionError) as e:
            issues.append(f"Cannot write to data directory: {e}")
        
        # Check quarantine directory if enabled
        if os.getenv("QUARANTINE_ENABLED", "0") == "1":
            quarantine_dir = Path(os.getenv("QUARANTINE_DIR", "data/quarantine"))
            try:
                quarantine_dir.mkdir(parents=True, exist_ok=True)
                test_file = quarantine_dir / ".permission_test"
                test_file.write_text("test")
                test_file.unlink()
            except (OSError, PermissionError) as e:
                issues.append(f"Cannot write to quarantine directory: {e}")
        
        if issues:
            return PreflightResult(
                check_name="file_permissions",
                status="fail", 
                message=f"File permission issues: {'; '.join(issues)}",
                details={"issues": issues},
                severity="critical"
            )
            
        return PreflightResult(
            check_name="file_permissions",
            status="pass",
            message="File permissions are adequate"
        )
    
    def check_network_connectivity(self) -> PreflightResult:
        """Check network connectivity and port availability
        
        Returns:
            PreflightResult: Network connectivity check result
        """
        issues = []
        
        # Check if required ports are available
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8000"))
        
        try:
            # Test if port is already in use
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                issues.append(f"Port {port} is already in use")
                
        except Exception as e:
            issues.append(f"Cannot test port {port}: {e}")
        
        # Check DNS resolution (basic test)
        try:
            socket.gethostbyname("localhost")
        except socket.gaierror as e:
            issues.append(f"DNS resolution issues: {e}")
        
        if issues:
            return PreflightResult(
                check_name="network_connectivity",
                status="warn",
                message=f"Network issues detected: {'; '.join(issues)}",
                details={"issues": issues},
                severity="warning"
            )
            
        return PreflightResult(
            check_name="network_connectivity", 
            status="pass",
            message=f"Network connectivity OK (port {port} available)"
        )
    
    def check_system_resources(self) -> PreflightResult:
        """Check system resources (memory, disk, CPU)
        
        Returns:
            PreflightResult: System resources check result
        """
        warnings = []
        errors = []
        
        try:
            # Check available memory
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)
            
            if available_mb < 64:  # Less than 64MB
                errors.append(f"Very low memory: {available_mb:.1f}MB available")
            elif available_mb < 128:  # Less than 128MB
                warnings.append(f"Low memory: {available_mb:.1f}MB available")
            
            # Check disk space
            disk = psutil.disk_usage('.')
            free_mb = disk.free / (1024 * 1024)
            
            if free_mb < 10:  # Less than 10MB
                errors.append(f"Very low disk space: {free_mb:.1f}MB free")
            elif free_mb < 100:  # Less than 100MB  
                warnings.append(f"Low disk space: {free_mb:.1f}MB free")
            
            # Check CPU load (if available)
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                if cpu_percent > 95:
                    warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
            except:
                pass  # CPU check is non-critical
                
        except ImportError:
            return PreflightResult(
                check_name="system_resources",
                status="warn",
                message="psutil not available - cannot check system resources",
                severity="warning"
            )
        except Exception as e:
            return PreflightResult(
                check_name="system_resources", 
                status="warn",
                message=f"Failed to check system resources: {e}",
                severity="warning"
            )
        
        if errors:
            return PreflightResult(
                check_name="system_resources",
                status="fail",
                message=f"Resource issues: {'; '.join(errors + warnings)}",
                details={"errors": errors, "warnings": warnings},
                severity="critical"
            )
        elif warnings:
            return PreflightResult(
                check_name="system_resources",
                status="warn", 
                message=f"Resource warnings: {'; '.join(warnings)}",
                details={"warnings": warnings},
                severity="warning"
            )
        
        return PreflightResult(
            check_name="system_resources",
            status="pass",
            message="System resources are adequate"
        )
    
    def check_configuration_integrity(self) -> PreflightResult:
        """Check configuration file integrity and required values
        
        Returns:
            PreflightResult: Configuration integrity check result
        """
        issues = []
        warnings = []
        
        # Check for configuration schema validation
        try:
            from console.config_schema import ConfigSchema
            schema = ConfigSchema()
            
            # Validate current environment variables
            env_config = {k: v for k, v in os.environ.items() if k.isupper()}
            
            # This would need to be implemented in the ConfigSchema class
            # For now, just check critical settings
            
            # Check auth configuration
            if os.getenv("CONSOLE_AUTH_ENABLED", "0") == "1":
                session_key = os.getenv("CONSOLE_AUTH_SESSION_KEY", "")
                if not session_key:
                    issues.append("CONSOLE_AUTH_SESSION_KEY required when auth enabled")
                elif len(session_key) < 16:
                    warnings.append("CONSOLE_AUTH_SESSION_KEY should be at least 16 characters")
            
            # Check log configuration 
            log_max_bytes = os.getenv("LOG_MAX_BYTES", "10485760")  # 10MB default
            try:
                max_bytes = int(log_max_bytes)
                if max_bytes < 1024:  # Less than 1KB
                    warnings.append("LOG_MAX_BYTES is very small")
                elif max_bytes > 1024 * 1024 * 1024:  # More than 1GB
                    warnings.append("LOG_MAX_BYTES is very large")
            except ValueError:
                issues.append("LOG_MAX_BYTES must be a valid integer")
            
            # Check plugin directory if enabled
            if os.getenv("PLUGINS_ENABLED", "0") == "1":
                plugin_dir = Path(os.getenv("PLUGINS_DIR", "plugins"))
                if not plugin_dir.exists():
                    issues.append(f"Plugin directory does not exist: {plugin_dir}")
                else:
                    manifest_file = plugin_dir / "manifest.json"
                    if not manifest_file.exists():
                        issues.append("Plugin manifest.json not found")
            
        except ImportError:
            warnings.append("Configuration schema validator not available")
        except Exception as e:
            warnings.append(f"Configuration check failed: {e}")
        
        if issues:
            return PreflightResult(
                check_name="configuration_integrity",
                status="fail",
                message=f"Configuration issues: {'; '.join(issues)}",
                details={"errors": issues, "warnings": warnings},
                severity="error"
            )
        elif warnings:
            return PreflightResult(
                check_name="configuration_integrity",
                status="warn",
                message=f"Configuration warnings: {'; '.join(warnings)}",
                details={"warnings": warnings}, 
                severity="warning"
            )
            
        return PreflightResult(
            check_name="configuration_integrity",
            status="pass",
            message="Configuration integrity verified"
        )
    
    def check_security_settings(self) -> PreflightResult:
        """Check security-related settings and configurations
        
        Returns:
            PreflightResult: Security settings check result
        """
        warnings = []
        issues = []
        
        # Check debug settings in production
        debug_enabled = os.getenv("DEBUG", "0") == "1"
        if debug_enabled:
            warnings.append("Debug mode is enabled (not recommended for production)")
        
        # Check default credentials
        if os.getenv("CONSOLE_AUTH_ENABLED", "0") == "1":
            user_db = os.getenv("CONSOLE_AUTH_USER_DB", "data/auth/users.json")
            user_db_path = Path(user_db)
            if user_db_path.exists():
                try:
                    with open(user_db_path, 'r') as f:
                        users = json.load(f)
                    
                    # Check for default/weak credentials (basic check)
                    default_users = ['admin', 'test', 'demo', 'user']
                    for user in users.get('users', []):
                        if user.get('username', '').lower() in default_users:
                            warnings.append(f"Default username detected: {user['username']}")
                            
                except (json.JSONDecodeError, IOError):
                    pass  # Non-critical for preflight
        
        # Check log redaction
        if os.getenv("LOG_REDACT_SECRETS", "0") != "1":
            warnings.append("Log redaction is disabled (secrets may be logged)")
        
        # Check file permissions on sensitive files
        sensitive_files = [
            "data/auth/users.json",
            "logs/app.log", 
            ".env"
        ]
        
        for file_path in sensitive_files:
            path = Path(file_path)
            if path.exists():
                try:
                    stat = path.stat()
                    # Check if file is world-readable (basic check on Unix systems)
                    if hasattr(stat, 'st_mode') and (stat.st_mode & 0o044):
                        warnings.append(f"Sensitive file {file_path} may be world-readable")
                except:
                    pass  # Non-critical for preflight
        
        if issues:
            return PreflightResult(
                check_name="security_settings",
                status="fail",
                message=f"Security issues: {'; '.join(issues)}",
                details={"errors": issues, "warnings": warnings},
                severity="error"
            )
        elif warnings:
            return PreflightResult(
                check_name="security_settings",
                status="warn",
                message=f"Security warnings: {'; '.join(warnings)}",
                details={"warnings": warnings},
                severity="warning"
            )
            
        return PreflightResult(
            check_name="security_settings",
            status="pass",
            message="Security settings are appropriate"
        )
    
    def run_all_checks(self) -> PreflightSummary:
        """Run all preflight checks
        
        Returns:
            PreflightSummary: Summary of all check results
        """
        import time
        start_time = time.time()
        
        checks = [
            self.check_python_environment,
            self.check_required_modules,
            self.check_file_permissions, 
            self.check_network_connectivity,
            self.check_system_resources,
            self.check_configuration_integrity,
            self.check_security_settings
        ]
        
        results = []
        passed = 0
        warnings = 0
        failures = 0
        
        for check_func in checks:
            try:
                result = check_func()
                results.append(result)
                
                if result.status == "pass":
                    passed += 1
                elif result.status == "warn":
                    warnings += 1
                elif result.status == "fail":
                    failures += 1
                    
            except Exception as e:
                logger.error(f"Preflight check {check_func.__name__} failed: {e}")
                result = PreflightResult(
                    check_name=check_func.__name__,
                    status="fail",
                    message=f"Check execution failed: {e}",
                    severity="error"
                )
                results.append(result)
                failures += 1
        
        execution_time = time.time() - start_time
        
        # Determine overall status
        if failures > 0:
            overall_status = "fail"
        elif warnings > 0:
            overall_status = "warn"
        else:
            overall_status = "pass"
        
        return PreflightSummary(
            total_checks=len(results),
            passed=passed,
            warnings=warnings,
            failures=failures,
            results=results,
            overall_status=overall_status,
            execution_time_seconds=execution_time
        )


def run_preflight_checks(verbose: bool = False) -> PreflightSummary:
    """Run preflight checks with optional verbose output
    
    Args:
        verbose: Enable verbose output
        
    Returns:
        PreflightSummary: Check results summary
    """
    checker = PreflightChecker()
    summary = checker.run_all_checks()
    
    if verbose:
        print("=== Preflight Checks ===")
        print(f"Total checks: {summary.total_checks}")
        print(f"Passed: {summary.passed}")
        print(f"Warnings: {summary.warnings}")
        print(f"Failures: {summary.failures}")
        print(f"Execution time: {summary.execution_time_seconds:.2f}s")
        print(f"Overall status: {summary.overall_status.upper()}")
        
        for result in summary.results:
            status_emoji = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
            emoji = status_emoji.get(result.status, "❓")
            print(f"\n{emoji} {result.check_name}: {result.message}")
            
            if result.details and verbose:
                print(f"   Details: {json.dumps(result.details, indent=2)}")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WatchLockAI Sentinel Preflight Checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--fail-on-warn", action="store_true", help="Exit with error on warnings")
    
    args = parser.parse_args()
    
    summary = run_preflight_checks(verbose=args.verbose and not args.json)
    
    if args.json:
        # Convert dataclass to dict for JSON serialization
        summary_dict = asdict(summary)
        print(json.dumps(summary_dict, indent=2))
    
    # Exit with appropriate code
    if summary.overall_status == "fail":
        sys.exit(1)
    elif summary.overall_status == "warn" and args.fail_on_warn:
        sys.exit(1)
    else:
        sys.exit(0)
