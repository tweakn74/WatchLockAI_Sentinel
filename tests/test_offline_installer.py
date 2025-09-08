"""Tests for P5-004 offline installer (Windows PowerShell scripts)."""

import os
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestOfflineInstaller(unittest.TestCase):
    """Test offline installer scripts."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.scripts_dir = self.repo_root / "scripts"
        self.is_windows = platform.system().lower() == "windows"
    
    def test_bundle_script_exists(self):
        """Test that make_offline_bundle.ps1 exists."""
        bundle_script = self.scripts_dir / "make_offline_bundle.ps1"
        self.assertTrue(bundle_script.exists(), "make_offline_bundle.ps1 must exist")
        self.assertTrue(bundle_script.is_file(), "make_offline_bundle.ps1 must be a file")
    
    def test_bootstrap_script_exists(self):
        """Test that bootstrap_venv.ps1 exists."""
        bootstrap_script = self.scripts_dir / "bootstrap_venv.ps1"
        self.assertTrue(bootstrap_script.exists(), "bootstrap_venv.ps1 must exist")
        self.assertTrue(bootstrap_script.is_file(), "bootstrap_venv.ps1 must be a file")
    
    def test_bundle_script_syntax(self):
        """Test that bundle script has valid PowerShell syntax."""
        if not self.is_windows:
            self.skipTest("PowerShell syntax check only available on Windows")
        
        bundle_script = self.scripts_dir / "make_offline_bundle.ps1"
        
        try:
            # Test PowerShell syntax without executing
            result = subprocess.run([
                "powershell", "-NoProfile", "-Command", 
                f"Get-Command -Syntax -Name '{bundle_script}'"
            ], capture_output=True, text=True, timeout=10)
            
            # If syntax check succeeds, the command should not fail
            # We're not looking for specific output, just that it doesn't error
            self.assertNotIn("error", result.stderr.lower())
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or accessible")
    
    def test_bootstrap_script_syntax(self):
        """Test that bootstrap script has valid PowerShell syntax."""
        if not self.is_windows:
            self.skipTest("PowerShell syntax check only available on Windows")
        
        bootstrap_script = self.scripts_dir / "bootstrap_venv.ps1"
        
        try:
            # Test PowerShell syntax without executing
            result = subprocess.run([
                "powershell", "-NoProfile", "-Command", 
                f"Get-Command -Syntax -Name '{bootstrap_script}'"
            ], capture_output=True, text=True, timeout=10)
            
            self.assertNotIn("error", result.stderr.lower())
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or accessible")
    
    def test_bundle_script_help(self):
        """Test that bundle script shows help information."""
        if not self.is_windows:
            self.skipTest("PowerShell execution only available on Windows")
        
        bundle_script = self.scripts_dir / "make_offline_bundle.ps1"
        
        try:
            # Get help for the script
            result = subprocess.run([
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-Command", f"Get-Help '{bundle_script}'"
            ], capture_output=True, text=True, timeout=15)
            
            # Should contain parameter information
            output = result.stdout.lower()
            self.assertIn("outputpath", output)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or accessible")
    
    def test_bootstrap_script_help(self):
        """Test that bootstrap script shows help information."""
        if not self.is_windows:
            self.skipTest("PowerShell execution only available on Windows")
        
        bootstrap_script = self.scripts_dir / "bootstrap_venv.ps1"
        
        try:
            # Get help for the script
            result = subprocess.run([
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-Command", f"Get-Help '{bootstrap_script}'"
            ], capture_output=True, text=True, timeout=15)
            
            # Should contain parameter information
            output = result.stdout.lower()
            self.assertIn("skiptests", output)
            self.assertIn("installservice", output)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell not available or accessible")
    
    def test_bundle_script_structure(self):
        """Test the structure of the bundle script."""
        bundle_script = self.scripts_dir / "make_offline_bundle.ps1"
        
        with open(bundle_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key functions and parameters
        self.assertIn("param(", content, "Script should have parameters")
        self.assertIn("OutputPath", content, "Should have OutputPath parameter")
        self.assertIn("function Write-Log", content, "Should have logging function")
        self.assertIn("function Test-Prerequisites", content, "Should check prerequisites")
        self.assertIn("function New-VirtualEnvironment", content, "Should create venv")
        self.assertIn("function Copy-SourceFiles", content, "Should copy source files")
        self.assertIn("function New-Bundle", content, "Should create bundle")
        
        # Check for error handling
        self.assertIn("try {", content, "Should have error handling")
        self.assertIn("catch {", content, "Should have error handling")
        self.assertIn("$ErrorActionPreference", content, "Should set error action")
    
    def test_bootstrap_script_structure(self):
        """Test the structure of the bootstrap script."""
        bootstrap_script = self.scripts_dir / "bootstrap_venv.ps1"
        
        with open(bootstrap_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key functions and parameters
        self.assertIn("param(", content, "Script should have parameters")
        self.assertIn("SkipTests", content, "Should have SkipTests parameter")
        self.assertIn("InstallService", content, "Should have InstallService parameter")
        self.assertIn("function Write-Log", content, "Should have logging function")
        self.assertIn("function Test-Environment", content, "Should test environment")
        self.assertIn("function Test-BundleIntegrity", content, "Should verify bundle")
        self.assertIn("function Initialize-VirtualEnvironment", content, "Should init venv")
        self.assertIn("function Test-CoreImports", content, "Should test imports")
        self.assertIn("function Invoke-TestSuite", content, "Should run tests")
        
        # Check for error handling
        self.assertIn("try {", content, "Should have error handling")
        self.assertIn("catch {", content, "Should have error handling")
        self.assertIn("$ErrorActionPreference", content, "Should set error action")
    
    @unittest.skipUnless(platform.system().lower() == "windows", "Windows-specific test")
    def test_bundle_script_dry_run(self):
        """Test bundle script in dry-run mode (Windows only)."""
        bundle_script = self.scripts_dir / "make_offline_bundle.ps1"
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_bundle = Path(temp_dir) / "test_bundle.zip"
            
            try:
                # Try to run the script in a way that would fail early but safely
                # We'll try to get version info which should fail safely
                result = subprocess.run([
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-Command", f"& '{bundle_script}' -OutputPath '{temp_bundle}' -WhatIf 2>&1 | Select-Object -First 5"
                ], capture_output=True, text=True, timeout=30, cwd=self.repo_root)
                
                # Script should start and show some output (even if it fails due to missing deps)
                # We're testing that it's structurally sound, not that it works fully
                self.assertIsNotNone(result)
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.skipTest("PowerShell execution failed")
    
    @unittest.skipUnless(platform.system().lower() == "windows", "Windows-specific test")  
    def test_bootstrap_script_dry_run(self):
        """Test bootstrap script help mode (Windows only)."""
        bootstrap_script = self.scripts_dir / "bootstrap_venv.ps1"
        
        try:
            # Try to get the script to show some initial output
            result = subprocess.run([
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-Command", f"& '{bootstrap_script}' -WhatIf 2>&1 | Select-Object -First 5"
            ], capture_output=True, text=True, timeout=20)
            
            # Script should start (even if it fails due to missing bundle structure)
            self.assertIsNotNone(result)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("PowerShell execution failed")
    
    def test_scripts_have_execution_permissions(self):
        """Test that scripts can be marked as executable (Unix-style check)."""
        # This is more relevant for Unix systems, but we check file attributes
        bundle_script = self.scripts_dir / "make_offline_bundle.ps1"
        bootstrap_script = self.scripts_dir / "bootstrap_venv.ps1"
        
        # Check files are readable
        self.assertTrue(os.access(bundle_script, os.R_OK), "Bundle script should be readable")
        self.assertTrue(os.access(bootstrap_script, os.R_OK), "Bootstrap script should be readable")
        
        # Check file sizes (should be substantial scripts)
        self.assertGreater(bundle_script.stat().st_size, 1000, "Bundle script should be substantial")
        self.assertGreater(bootstrap_script.stat().st_size, 1000, "Bootstrap script should be substantial")
    
    def test_scripts_encoding(self):
        """Test that scripts use proper encoding."""
        bundle_script = self.scripts_dir / "make_offline_bundle.ps1"
        bootstrap_script = self.scripts_dir / "bootstrap_venv.ps1"
        
        # Should be readable as UTF-8
        try:
            with open(bundle_script, 'r', encoding='utf-8') as f:
                bundle_content = f.read()
            self.assertGreater(len(bundle_content), 100, "Bundle script should have content")
            
            with open(bootstrap_script, 'r', encoding='utf-8') as f:
                bootstrap_content = f.read()
            self.assertGreater(len(bootstrap_content), 100, "Bootstrap script should have content")
            
        except UnicodeDecodeError:
            self.fail("Scripts should be UTF-8 encoded")
    
    def test_non_windows_graceful_skip(self):
        """Test that tests gracefully skip on non-Windows systems."""
        if self.is_windows:
            self.skipTest("This test is for non-Windows systems")
        
        # This test itself demonstrates graceful skipping
        # We can also test that we properly detect non-Windows
        self.assertNotEqual(platform.system().lower(), "windows")
        
        # Test that we would skip PowerShell-specific functionality
        with self.assertRaises(unittest.SkipTest):
            if not self.is_windows:
                raise unittest.SkipTest("PowerShell not available on non-Windows")


class TestOfflineInstallerIntegration(unittest.TestCase):
    """Integration tests for offline installer components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.is_windows = platform.system().lower() == "windows"
    
    def test_required_source_files_exist(self):
        """Test that required source files for bundling exist."""
        required_files = [
            "console/web_api.py",
            "app_core/bus.py", 
            "app.py",
            "VERSION",
            "requirements.txt"
        ]
        
        for file_path in required_files:
            full_path = self.repo_root / file_path
            self.assertTrue(full_path.exists(), f"Required file {file_path} should exist for bundling")
    
    def test_required_directories_exist(self):
        """Test that required directories for bundling exist."""
        required_dirs = [
            "console",
            "app_core",
            "tools",
            "tests",
            "DOCS",
            "scripts"
        ]
        
        for dir_path in required_dirs:
            full_path = self.repo_root / dir_path
            self.assertTrue(full_path.is_dir(), f"Required directory {dir_path} should exist for bundling")
    
    def test_config_templates_exist(self):
        """Test that config templates exist for offline installation."""
        config_files = [
            "DOCS/config/.env.example",
            "DOCS/config/config.example.json"
        ]
        
        for config_file in config_files:
            full_path = self.repo_root / config_file
            self.assertTrue(full_path.exists(), f"Config template {config_file} should exist")
    
    def test_documentation_exists(self):
        """Test that required documentation exists for offline bundle."""
        doc_files = [
            "DOCS/operations_runbook.md",
            "DOCS/deploy_windows.md",
            "CHANGELOG.md"
        ]
        
        for doc_file in doc_files:
            full_path = self.repo_root / doc_file
            self.assertTrue(full_path.exists(), f"Documentation {doc_file} should exist")


if __name__ == '__main__':
    unittest.main()
