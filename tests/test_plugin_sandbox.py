# File: tests/test_plugin_sandbox.py
# Purpose: Unit tests for plugin sandbox system (P3-005)

import os
import sys
import json
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from console.plugin_sandbox import (
    PluginLoader, SandboxContext, PluginSandboxError, 
    get_plugin_loader, execute_plugin_hook
)


class TestSandboxContext(unittest.TestCase):
    """Test sandbox context functionality"""
    
    def test_sandbox_context_creation(self):
        """Test creating sandbox context with permissions"""
        permissions = {
            "filesystem": True,
            "network": False,
            "system_calls": False
        }
        
        context = SandboxContext(permissions)
        
        self.assertEqual(context.permissions, permissions)
        self.assertIn('json', context.allowed_modules)
        self.assertIn('urllib', context.blocked_modules)  # Network blocked
        self.assertIn('subprocess', context.blocked_modules)  # System calls blocked
        self.assertNotIn('os', context.blocked_modules)  # Filesystem allowed
    
    def test_sandbox_context_full_permissions(self):
        """Test sandbox context with full permissions"""
        permissions = {
            "filesystem": True,
            "network": True, 
            "system_calls": True
        }
        
        context = SandboxContext(permissions)
        
        # No modules should be blocked with full permissions
        self.assertEqual(context.blocked_modules, set())
    
    def test_sandbox_context_no_permissions(self):
        """Test sandbox context with no permissions"""
        permissions = {
            "filesystem": False,
            "network": False,
            "system_calls": False
        }
        
        context = SandboxContext(permissions)
        
        # All restricted modules should be blocked
        self.assertIn('os', context.blocked_modules)
        self.assertIn('urllib', context.blocked_modules)
        self.assertIn('subprocess', context.blocked_modules)


class TestPluginLoader(unittest.TestCase):
    """Test plugin loader functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.plugins_dir = Path(self.temp_dir) / "plugins"
        self.plugins_dir.mkdir(parents=True)
        
        # Create test manifest
        self.test_manifest = {
            "plugins": {
                "test_plugin": {
                    "path": "test_plugin.py",
                    "sha256": "dummy_hash",
                    "version": "1.0.0",
                    "description": "Test plugin",
                    "author": "Test",
                    "permissions": {
                        "filesystem": False,
                        "network": False,
                        "system_calls": False
                    },
                    "api_version": "1.0",
                    "enabled": True
                }
            },
            "manifest_version": "1.0.0"
        }
        
        manifest_path = self.plugins_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.test_manifest, f)
        
        # Create test plugin file
        plugin_content = '''
def create_plugin(sandbox_context=None):
    class TestPlugin:
        def __init__(self):
            self.name = "test_plugin"
        def initialize(self):
            return True
        def execute(self, event):
            return {"status": "success", "plugin": "test_plugin"}
        def cleanup(self):
            return True
    return TestPlugin()

PLUGIN_INFO = {
    "name": "test_plugin",
    "version": "1.0.0"
}
'''
        plugin_path = self.plugins_dir / "test_plugin.py"
        with open(plugin_path, 'w') as f:
            f.write(plugin_content)
        
        # Update manifest with correct hash
        import hashlib
        plugin_hash = hashlib.sha256(plugin_content.encode()).hexdigest()
        self.test_manifest["plugins"]["test_plugin"]["sha256"] = plugin_hash
        with open(manifest_path, 'w') as f:
            json.dump(self.test_manifest, f)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_load_manifest(self):
        """Test loading plugin manifest"""
        loader = PluginLoader(str(self.plugins_dir))
        manifest = loader.load_manifest()
        
        self.assertIn("plugins", manifest)
        self.assertIn("test_plugin", manifest["plugins"])
    
    def test_load_manifest_missing(self):
        """Test loading missing manifest"""
        empty_dir = Path(self.temp_dir) / "empty"
        empty_dir.mkdir()
        
        loader = PluginLoader(str(empty_dir))
        
        with self.assertRaises(PluginSandboxError):
            loader.load_manifest()
    
    def test_verify_plugin_hash(self):
        """Test plugin hash verification"""
        loader = PluginLoader(str(self.plugins_dir))
        plugin_config = self.test_manifest["plugins"]["test_plugin"]
        
        # Should pass with correct hash
        result = loader.verify_plugin_hash("test_plugin", plugin_config)
        self.assertTrue(result)
        
        # Should fail with incorrect hash
        plugin_config["sha256"] = "wrong_hash"
        result = loader.verify_plugin_hash("test_plugin", plugin_config)
        self.assertFalse(result)
    
    def test_verify_plugin_hash_missing_file(self):
        """Test hash verification with missing file"""
        loader = PluginLoader(str(self.plugins_dir))
        plugin_config = {
            "path": "nonexistent.py",
            "sha256": "dummy_hash"
        }
        
        result = loader.verify_plugin_hash("test_plugin", plugin_config)
        self.assertFalse(result)
    
    @patch.dict(os.environ, {"PLUGINS_ENABLED": "1"})
    def test_load_plugin_success(self):
        """Test successful plugin loading"""
        loader = PluginLoader(str(self.plugins_dir))
        plugin_config = self.test_manifest["plugins"]["test_plugin"]
        
        plugin = loader.load_plugin("test_plugin", plugin_config)
        
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "test_plugin")
    
    def test_load_plugin_disabled(self):
        """Test loading disabled plugin"""
        loader = PluginLoader(str(self.plugins_dir))
        plugin_config = self.test_manifest["plugins"]["test_plugin"]
        plugin_config["enabled"] = False
        
        plugin = loader.load_plugin("test_plugin", plugin_config)
        
        self.assertIsNone(plugin)
    
    def test_execute_plugin(self):
        """Test plugin execution"""
        loader = PluginLoader(str(self.plugins_dir))
        plugin_config = self.test_manifest["plugins"]["test_plugin"]
        
        plugin = loader.load_plugin("test_plugin", plugin_config)
        loader.loaded_plugins["test_plugin"] = plugin
        
        event = {"type": "test", "data": "test_data"}
        result = loader.execute_plugin("test_plugin", event)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["plugin"], "test_plugin")
    
    def test_execute_plugin_not_loaded(self):
        """Test executing non-loaded plugin"""
        loader = PluginLoader(str(self.plugins_dir))
        
        event = {"type": "test"}
        result = loader.execute_plugin("nonexistent", event)
        
        self.assertIsNone(result)
    
    def test_unload_plugin(self):
        """Test plugin unloading"""
        loader = PluginLoader(str(self.plugins_dir))
        plugin_config = self.test_manifest["plugins"]["test_plugin"]
        
        plugin = loader.load_plugin("test_plugin", plugin_config)
        loader.loaded_plugins["test_plugin"] = plugin
        
        result = loader.unload_plugin("test_plugin")
        
        self.assertTrue(result)
        self.assertNotIn("test_plugin", loader.loaded_plugins)
    
    def test_unload_plugin_not_loaded(self):
        """Test unloading non-loaded plugin"""
        loader = PluginLoader(str(self.plugins_dir))
        
        result = loader.unload_plugin("nonexistent")
        
        self.assertTrue(result)  # Should succeed even if not loaded


class TestPluginHooks(unittest.TestCase):
    """Test plugin hook execution"""
    
    @patch.dict(os.environ, {"PLUGINS_ENABLED": "0"})
    def test_execute_plugin_hook_disabled(self):
        """Test hook execution when plugins disabled"""
        results = execute_plugin_hook("test_hook", {"data": "test"})
        
        self.assertEqual(results, [])
    
    @patch.dict(os.environ, {"PLUGINS_ENABLED": "1"})
    @patch('console.plugin_sandbox.get_plugin_loader')
    def test_execute_plugin_hook_enabled(self, mock_get_loader):
        """Test hook execution when plugins enabled"""
        # Mock plugin loader
        mock_loader = MagicMock()
        mock_loader.loaded_plugins = {"test_plugin": None}
        mock_loader.execute_plugin.return_value = {"status": "success"}
        mock_get_loader.return_value = mock_loader
        
        results = execute_plugin_hook("test_hook", {"data": "test"})
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "success")


class TestSandboxedImports(unittest.TestCase):
    """Test sandboxed import functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.plugins_dir = Path(self.temp_dir) / "plugins"
        self.plugins_dir.mkdir(parents=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_sandboxed_import_allowed_module(self):
        """Test importing allowed module in sandbox"""
        loader = PluginLoader(str(self.plugins_dir))
        context = SandboxContext({"filesystem": False, "network": False, "system_calls": False})
        
        with loader.sandboxed_import(context):
            import json  # Should work
            self.assertIsNotNone(json)
    
    def test_sandboxed_import_blocked_module(self):
        """Test importing blocked module in sandbox"""
        loader = PluginLoader(str(self.plugins_dir))
        context = SandboxContext({"filesystem": False, "network": False, "system_calls": False})
        
        with loader.sandboxed_import(context):
            with self.assertRaises(ImportError):
                import os  # Should be blocked


if __name__ == "__main__":
    unittest.main()
