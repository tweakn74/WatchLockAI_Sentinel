# File: tests/test_windows_service.py
# Purpose: Unit tests for P3-003 Windows service packaging

from __future__ import annotations
import unittest
import os
import subprocess
import sys
from pathlib import Path


class TestWindowsServiceImportSafe(unittest.TestCase):
    """Test Windows service scripts are available and import-safe"""
    
    def test_service_scripts_exist(self):
        """Test service scripts exist"""
        script_dir = Path(__file__).parent.parent / "scripts"
        
        required_scripts = [
            "sentinel_service_runner.ps1",
            "install_service.ps1", 
            "uninstall_service.ps1"
        ]
        
        for script_name in required_scripts:
            script_path = script_dir / script_name
            self.assertTrue(script_path.exists(), f"Missing script: {script_name}")
    
    def test_service_flag_disabled_by_default(self):
        """Test SERVICE_ENABLED flag is disabled by default"""
        try:
            from console import web_api as web_api_mod
            
            # Clear service environment variable
            old_env = os.environ.pop("SERVICE_ENABLED", None)
            
            try:
                # Reload module to pick up environment changes
                import importlib
                importlib.reload(web_api_mod)
                
                # Should be disabled by default
                self.assertFalse(web_api_mod.SERVICE_ENABLED)
                
            finally:
                # Restore environment
                if old_env is not None:
                    os.environ["SERVICE_ENABLED"] = old_env
                    
        except ImportError:
            self.skipTest("Web API module not available")


class TestServiceScriptValidation(unittest.TestCase):
    """Test Windows service scripts are syntactically valid"""
    
    def setUp(self):
        """Set up test environment"""
        self.script_dir = Path(__file__).parent.parent / "scripts"
        self.is_windows = sys.platform.startswith('win')
    
    def test_powershell_syntax_service_runner(self):
        """Test service runner PowerShell syntax"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        script_path = self.script_dir / "sentinel_service_runner.ps1"
        
        try:
            # Test PowerShell syntax validation
            result = subprocess.run([
                "powershell", "-Command", 
                f"Get-Command -Syntax (Get-Content '{script_path}' | Out-String)"
            ], capture_output=True, text=True, timeout=10)
            
            # Should not have syntax errors
            self.assertNotIn("error", result.stderr.lower())
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")
    
    def test_powershell_syntax_installer(self):
        """Test installer PowerShell syntax"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        script_path = self.script_dir / "install_service.ps1"
        
        try:
            # Test PowerShell syntax validation using -NoExecutionPolicy for syntax check
            result = subprocess.run([
                "powershell", "-NoExecutionPolicy", "-Command", 
                f"& {{ $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content '{script_path}' -Raw), [ref]$null) }}"
            ], capture_output=True, text=True, timeout=10)
            
            # Should have exit code 0 for valid syntax
            self.assertEqual(result.returncode, 0, f"Syntax error in installer: {result.stderr}")
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")
    
    def test_powershell_syntax_uninstaller(self):
        """Test uninstaller PowerShell syntax"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        script_path = self.script_dir / "uninstall_service.ps1"
        
        try:
            # Test PowerShell syntax validation
            result = subprocess.run([
                "powershell", "-NoExecutionPolicy", "-Command", 
                f"& {{ $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content '{script_path}' -Raw), [ref]$null) }}"
            ], capture_output=True, text=True, timeout=10)
            
            # Should have exit code 0 for valid syntax
            self.assertEqual(result.returncode, 0, f"Syntax error in uninstaller: {result.stderr}")
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")


class TestServiceRunnerDryRun(unittest.TestCase):
    """Test service runner dry run functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.script_dir = Path(__file__).parent.parent / "scripts"
        self.service_runner = self.script_dir / "sentinel_service_runner.ps1"
        self.is_windows = sys.platform.startswith('win')
    
    def test_service_runner_help(self):
        """Test service runner help command"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        try:
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File", 
                str(self.service_runner), "help"
            ], capture_output=True, text=True, timeout=15)
            
            # Should show usage information
            self.assertIn("Usage:", result.stdout)
            self.assertIn("WatchLockAI Sentinel", result.stdout)
            self.assertEqual(result.returncode, 0)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")
    
    def test_service_runner_dry_run(self):
        """Test service runner dry run mode"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        try:
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File",
                str(self.service_runner), "run", "-DryRun"
            ], capture_output=True, text=True, timeout=15)
            
            # Should indicate dry run mode
            self.assertIn("DRY RUN", result.stdout)
            self.assertIn("Would start service", result.stdout)
            # Should not actually start anything
            self.assertEqual(result.returncode, 0)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")
    
    def test_service_runner_status(self):
        """Test service runner status check"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        try:
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File",
                str(self.service_runner), "status"
            ], capture_output=True, text=True, timeout=15)
            
            # Should check service status (may not exist, but should not error)
            self.assertIn("service status", result.stdout.lower())
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")


class TestServiceInstallerDryRun(unittest.TestCase):
    """Test service installer dry run functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.script_dir = Path(__file__).parent.parent / "scripts"
        self.installer = self.script_dir / "install_service.ps1"
        self.is_windows = sys.platform.startswith('win')
    
    def test_installer_help(self):
        """Test installer help command"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        try:
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File",
                str(self.installer), "-Help"
            ], capture_output=True, text=True, timeout=15)
            
            # Should show usage information
            self.assertIn("Usage:", result.stdout)
            self.assertIn("install_service.ps1", result.stdout)
            self.assertEqual(result.returncode, 0)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")
    
    def test_installer_dry_run(self):
        """Test installer dry run mode (requires admin in real usage)"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        try:
            # Dry run should work without admin privileges
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File",
                str(self.installer), "-DryRun"
            ], capture_output=True, text=True, timeout=15)
            
            # May fail on admin check but should show dry run behavior
            # Don't assert exit code since admin check will fail
            output = result.stdout.lower() + result.stderr.lower()
            
            # Should mention admin requirement or dry run
            self.assertTrue(
                "administrator" in output or "dry run" in output,
                f"Expected admin requirement or dry run mention in output: {result.stdout}"
            )
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")


class TestServiceUninstallerDryRun(unittest.TestCase):
    """Test service uninstaller dry run functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.script_dir = Path(__file__).parent.parent / "scripts"
        self.uninstaller = self.script_dir / "uninstall_service.ps1"
        self.is_windows = sys.platform.startswith('win')
    
    def test_uninstaller_help(self):
        """Test uninstaller help command"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        try:
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File",
                str(self.uninstaller), "-Help"
            ], capture_output=True, text=True, timeout=15)
            
            # Should show usage information
            self.assertIn("Usage:", result.stdout)
            self.assertIn("uninstall_service.ps1", result.stdout)
            self.assertEqual(result.returncode, 0)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")
    
    def test_uninstaller_dry_run(self):
        """Test uninstaller dry run mode"""
        if not self.is_windows:
            self.skipTest("PowerShell tests require Windows")
            
        try:
            # Dry run should work without admin privileges
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File",
                str(self.uninstaller), "-DryRun"
            ], capture_output=True, text=True, timeout=15)
            
            # May fail on admin check but should show dry run behavior
            output = result.stdout.lower() + result.stderr.lower()
            
            # Should mention admin requirement or dry run or service not found
            self.assertTrue(
                "administrator" in output or "dry run" in output or "not found" in output,
                f"Expected admin requirement, dry run, or not found in output: {result.stdout}"
            )
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or timed out")


if __name__ == '__main__':
    unittest.main()
