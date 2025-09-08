# File: console/plugin_sandbox.py
# Purpose: Plugin/extension sandbox system (P3-005)

from __future__ import annotations
import os
import sys
import json
import hashlib
import importlib
import importlib.util
import logging
import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import traceback
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class PluginSandboxError(Exception):
    """Plugin sandbox error"""
    pass


class SandboxContext:
    """Restricted context for plugin execution"""
    
    def __init__(self, permissions: Dict[str, bool]):
        """Initialize sandbox context
        
        Args:
            permissions: Permission flags for the plugin
        """
        self.permissions = permissions
        self.allowed_modules = {
            # Safe standard library modules
            'json', 'datetime', 'typing', 'collections', 
            'itertools', 'functools', 're', 'math', 'random',
            'hashlib', 'base64', 'uuid', 'time'
        }
        
        if not permissions.get('filesystem', False):
            # Block filesystem access
            self.blocked_modules = {'os', 'shutil', 'pathlib', 'glob', 'tempfile'}
        else:
            self.blocked_modules = set()
            
        if not permissions.get('network', False):
            # Block network access  
            self.blocked_modules.update({
                'urllib', 'requests', 'http', 'socket', 'ssl', 'ftplib', 
                'smtplib', 'poplib', 'imaplib'
            })
            
        if not permissions.get('system_calls', False):
            # Block system calls
            self.blocked_modules.update({
                'subprocess', 'multiprocessing', 'threading', 'signal',
                'ctypes', 'mmap', 'resource'
            })


class PluginLoader:
    """Safe plugin loader with sandboxing"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        """Initialize plugin loader
        
        Args:
            plugins_dir: Directory containing plugins
        """
        self.plugins_dir = Path(plugins_dir)
        self.manifest_path = self.plugins_dir / "manifest.json"
        self.loaded_plugins = {}
        self._original_import = __builtins__.__import__
        
    def load_manifest(self) -> Dict[str, Any]:
        """Load plugin manifest
        
        Returns:
            dict: Plugin manifest data
            
        Raises:
            PluginSandboxError: If manifest invalid or missing
        """
        if not self.manifest_path.exists():
            raise PluginSandboxError(f"Plugin manifest not found: {self.manifest_path}")
            
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                
            # Validate manifest structure
            if 'plugins' not in manifest:
                raise PluginSandboxError("Invalid manifest: missing 'plugins' section")
                
            return manifest
            
        except (json.JSONDecodeError, IOError) as e:
            raise PluginSandboxError(f"Failed to load manifest: {e}")
    
    def verify_plugin_hash(self, plugin_name: str, plugin_config: Dict[str, Any]) -> bool:
        """Verify plugin file matches expected hash
        
        Args:
            plugin_name: Name of the plugin
            plugin_config: Plugin configuration from manifest
            
        Returns:
            bool: True if hash matches
        """
        plugin_path = self.plugins_dir / plugin_config["path"]
        expected_hash = plugin_config.get("sha256", "")
        
        if not plugin_path.exists():
            logger.error(f"Plugin file not found: {plugin_path}")
            return False
            
        try:
            with open(plugin_path, 'rb') as f:
                file_data = f.read()
                actual_hash = hashlib.sha256(file_data).hexdigest()
                
            if actual_hash.lower() != expected_hash.lower():
                logger.error(f"Plugin {plugin_name} hash mismatch: expected {expected_hash}, got {actual_hash}")
                return False
                
            return True
            
        except IOError as e:
            logger.error(f"Failed to verify plugin hash: {e}")
            return False
    
    @contextmanager
    def sandboxed_import(self, context: SandboxContext):
        """Context manager for sandboxed imports
        
        Args:
            context: Sandbox context with permissions
        """
        def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
            """Restricted import function"""
            # Check if module is blocked
            root_module = name.split('.')[0]
            if root_module in context.blocked_modules:
                raise ImportError(f"Module '{name}' is blocked by sandbox")
                
            # Allow only whitelisted modules if not explicitly permitted
            if root_module not in context.allowed_modules and root_module not in {'__main__'}:
                if not any(context.permissions.values()):  # No special permissions granted
                    raise ImportError(f"Module '{name}' not allowed in sandbox")
                    
            return self._original_import(name, globals, locals, fromlist, level)
        
        # Temporarily replace import
        __builtins__.__import__ = restricted_import
        try:
            yield
        finally:
            __builtins__.__import__ = self._original_import
    
    def load_plugin(self, plugin_name: str, plugin_config: Dict[str, Any]) -> Optional[Any]:
        """Load a single plugin with sandboxing
        
        Args:
            plugin_name: Name of the plugin
            plugin_config: Plugin configuration from manifest
            
        Returns:
            Plugin instance or None if failed
        """
        if not plugin_config.get("enabled", False):
            logger.info(f"Plugin {plugin_name} is disabled")
            return None
            
        # Verify plugin hash
        if not self.verify_plugin_hash(plugin_name, plugin_config):
            logger.error(f"Plugin {plugin_name} failed hash verification")
            return None
            
        # Set up sandbox context
        permissions = plugin_config.get("permissions", {})
        context = SandboxContext(permissions)
        
        plugin_path = self.plugins_dir / plugin_config["path"]
        
        try:
            with self.sandboxed_import(context):
                # Load plugin module
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                if spec is None:
                    raise PluginSandboxError(f"Could not load plugin spec: {plugin_path}")
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)
                
                # Get plugin factory function
                if hasattr(module, 'create_plugin'):
                    plugin_instance = module.create_plugin(context.permissions)
                else:
                    raise PluginSandboxError(f"Plugin {plugin_name} missing create_plugin function")
                
                # Initialize plugin
                if hasattr(plugin_instance, 'initialize'):
                    if not plugin_instance.initialize():
                        raise PluginSandboxError(f"Plugin {plugin_name} initialization failed")
                
                logger.info(f"Successfully loaded plugin: {plugin_name}")
                return plugin_instance
                
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            logger.debug(traceback.format_exc())
            return None
    
    def load_all_plugins(self) -> Dict[str, Any]:
        """Load all enabled plugins from manifest
        
        Returns:
            dict: Loaded plugin instances by name
        """
        try:
            manifest = self.load_manifest()
        except PluginSandboxError as e:
            logger.error(f"Cannot load plugins: {e}")
            return {}
            
        loaded = {}
        
        for plugin_name, plugin_config in manifest["plugins"].items():
            plugin_instance = self.load_plugin(plugin_name, plugin_config)
            if plugin_instance:
                loaded[plugin_name] = plugin_instance
                
        logger.info(f"Loaded {len(loaded)} plugins successfully")
        return loaded
    
    def execute_plugin(self, plugin_name: str, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a plugin with given event data
        
        Args:
            plugin_name: Name of plugin to execute
            event: Event data to pass to plugin
            
        Returns:
            Plugin execution result or None if failed
        """
        if plugin_name not in self.loaded_plugins:
            logger.error(f"Plugin not loaded: {plugin_name}")
            return None
            
        plugin = self.loaded_plugins[plugin_name]
        
        try:
            if hasattr(plugin, 'execute'):
                return plugin.execute(event)
            else:
                logger.error(f"Plugin {plugin_name} missing execute method")
                return None
                
        except Exception as e:
            logger.error(f"Plugin {plugin_name} execution failed: {e}")
            logger.debug(traceback.format_exc())
            return None
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            bool: True if successful
        """
        if plugin_name not in self.loaded_plugins:
            return True
            
        plugin = self.loaded_plugins[plugin_name]
        
        try:
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()
                
            del self.loaded_plugins[plugin_name]
            
            # Remove from sys.modules if present
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
                
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False


# Global plugin loader instance
_plugin_loader = None


def get_plugin_loader() -> PluginLoader:
    """Get global plugin loader instance
    
    Returns:
        PluginLoader: Global plugin loader
    """
    global _plugin_loader
    if _plugin_loader is None:
        plugins_enabled = os.getenv("PLUGINS_ENABLED", "0") == "1"
        plugins_dir = os.getenv("PLUGINS_DIR", "plugins")
        
        if plugins_enabled:
            _plugin_loader = PluginLoader(plugins_dir)
            _plugin_loader.loaded_plugins = _plugin_loader.load_all_plugins()
        else:
            logger.info("Plugin system disabled")
            _plugin_loader = PluginLoader()
            
    return _plugin_loader


def execute_plugin_hook(hook_name: str, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute all plugins for a given hook
    
    Args:
        hook_name: Name of the hook/event
        event_data: Event data to pass to plugins
        
    Returns:
        list: Results from all plugin executions
    """
    if os.getenv("PLUGINS_ENABLED", "0") != "1":
        return []
        
    loader = get_plugin_loader()
    results = []
    
    event = {
        "hook": hook_name,
        "data": event_data,
        "timestamp": str(datetime.datetime.utcnow().isoformat())
    }
    
    for plugin_name in loader.loaded_plugins:
        result = loader.execute_plugin(plugin_name, event)
        if result:
            results.append(result)
            
    return results
