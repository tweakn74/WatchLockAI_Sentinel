# File: tests/test_config_schema.py
# Purpose: Unit tests for configuration schema system (P3-001)

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from console.config_schema import ConfigSchema, ConfigValidationError


class TestConfigSchema(unittest.TestCase):
    """Test configuration schema functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.schema = ConfigSchema()
    
    def test_schema_creation(self):
        """Test schema creation and structure"""
        schema_dict = self.schema.schema
        
        self.assertEqual(schema_dict["type"], "object")
        self.assertEqual(schema_dict["version"], "1.0.0")
        self.assertIn("properties", schema_dict)
        
        # Check some expected properties
        properties = schema_dict["properties"]
        self.assertIn("HEALTH_ENDPOINT_ENABLED", properties)
        self.assertIn("CONSOLE_AUTH_ENABLED", properties)
        self.assertIn("PLUGINS_ENABLED", properties)
    
    def test_schema_property_structure(self):
        """Test individual property structure"""
        properties = self.schema.schema["properties"]
        
        # Test a boolean property
        health_prop = properties["HEALTH_ENDPOINT_ENABLED"]
        self.assertEqual(health_prop["type"], "boolean")
        self.assertEqual(health_prop["default"], "1")
        self.assertIn("description", health_prop)
        
        # Test an integer property
        debounce_prop = properties["CONFIG_HOT_RELOAD_DEBOUNCE_MS"]
        self.assertEqual(debounce_prop["type"], "integer")
        self.assertEqual(debounce_prop["minimum"], 100)
        self.assertEqual(debounce_prop["maximum"], 5000)
    
    def test_schema_completeness(self):
        """Test that schema covers all major configuration areas"""
        properties = self.schema.schema["properties"]
        
        # Check major feature areas are covered
        feature_areas = [
            "HEALTH_ENDPOINT_ENABLED",  # Health endpoints
            "CONSOLE_AUTH_ENABLED",     # Authentication
            "STREAM_ENABLED",           # Streaming
            "RATE_LIMIT_ENABLED",       # Rate limiting
            "ANOMALY_ENABLED",          # Anomaly detection
            "QUARANTINE_ENABLED",       # Quarantine
            "PLUGINS_ENABLED",          # Plugins
            "EXPORT_ENABLED",           # Telemetry export
            "LOG_REDACT_SECRETS"        # Log redaction
        ]
        
        for feature in feature_areas:
            self.assertIn(feature, properties, f"Missing feature: {feature}")


if __name__ == "__main__":
    unittest.main()
