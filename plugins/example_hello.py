# File: plugins/example_hello.py
# Purpose: Example plugin for P3-005 sandbox demonstration
# API Version: 1.0
# Author: WatchLockAI

"""
Example Hello World Plugin

This plugin demonstrates the basic structure and capabilities
of the WatchLockAI Sentinel plugin system.
"""

from typing import Dict, Any, Optional


class HelloPlugin:
    """Example plugin class"""
    
    def __init__(self, sandbox_context: Optional[Dict[str, Any]] = None):
        """Initialize the plugin with sandbox context
        
        Args:
            sandbox_context: Sandbox environment and permissions
        """
        self.name = "example_hello"
        self.version = "1.0.0"
        self.description = "Example hello world plugin for demonstration"
        self.context = sandbox_context or {}
        
    def initialize(self) -> bool:
        """Initialize plugin resources
        
        Returns:
            bool: True if initialization successful
        """
        print(f"Initializing {self.name} v{self.version}")
        return True
        
    def execute(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic
        
        Args:
            event: Event data from the main application
            
        Returns:
            dict: Plugin execution result
        """
        result = {
            "plugin": self.name,
            "status": "success",
            "message": f"Hello from {self.name}! Event type: {event.get('type', 'unknown')}",
            "event_id": event.get("id"),
            "timestamp": event.get("timestamp")
        }
        
        return result
        
    def cleanup(self) -> bool:
        """Clean up plugin resources
        
        Returns:
            bool: True if cleanup successful
        """
        print(f"Cleaning up {self.name}")
        return True
        
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information
        
        Returns:
            dict: Plugin metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "api_version": "1.0",
            "permissions_required": {
                "filesystem": False,
                "network": False,
                "system_calls": False
            }
        }


# Plugin factory function (required entry point)
def create_plugin(sandbox_context: Optional[Dict[str, Any]] = None):
    """Create and return plugin instance
    
    Args:
        sandbox_context: Sandbox environment
        
    Returns:
        HelloPlugin: Plugin instance
    """
    return HelloPlugin(sandbox_context)


# Plugin metadata (required)
PLUGIN_INFO = {
    "name": "example_hello",
    "version": "1.0.0",
    "api_version": "1.0",
    "description": "Example hello world plugin for demonstration",
    "author": "WatchLockAI",
    "entry_point": "create_plugin"
}
