# File: console/config_schema.py
# Purpose: JSON-schema-like configuration validator (P3-001)

from __future__ import annotations
import os
import json
import re
from typing import Dict, Any, List, Optional, Union
from pathlib import Path


class ConfigValidationError(Exception):
    """Configuration validation error"""
    pass


class ConfigSchema:
    """JSON-schema-like configuration validator using stdlib only"""
    
    def __init__(self):
        self.schema = self._build_schema()
    
    def _build_schema(self) -> Dict[str, Any]:
        """Build the complete configuration schema"""
        return {
            "type": "object",
            "title": "WatchLockAI Sentinel Configuration Schema",
            "version": "1.0.0",
            "properties": {
                # Core service flags
                "HEALTH_ENDPOINT_ENABLED": {
                    "type": "boolean",
                    "default": "1",
                    "description": "Enable /api/metrics/health endpoint"
                },
                "METRICS_DEBUG_ENABLED": {
                    "type": "boolean", 
                    "default": "0",
                    "description": "Enable debug metrics endpoints"
                },
                "CONFIG_HOT_RELOAD_ENABLED": {
                    "type": "boolean",
                    "default": "0", 
                    "description": "Enable configuration hot reload"
                },
                "CONFIG_HOT_RELOAD_DEBOUNCE_MS": {
                    "type": "integer",
                    "default": "750",
                    "minimum": 100,
                    "maximum": 5000,
                    "description": "Hot reload debounce time in milliseconds"
                },
                
                # RBAC and authentication
                "ADMIN_AUTH_ENABLED": {
                    "type": "boolean",
                    "default": "0",
                    "description": "Enable admin authentication for /api/admin/* routes"
                },
                "ADMIN_TOKEN": {
                    "type": "string",
                    "description": "Admin authentication token (required when ADMIN_AUTH_ENABLED=1)",
                    "required_when": ["ADMIN_AUTH_ENABLED=1"]
                },
                "RATE_LIMIT_ENABLED": {
                    "type": "boolean",
                    "default": "0", 
                    "description": "Enable API rate limiting"
                },
                
                # P2-001: Anomaly detection
                "ANOMALY_ENABLED": {
                    "type": "boolean",
                    "default": "0",
                    "description": "Enable anomaly detection system"
                },
                "ANOMALY_SKLEARN_ENABLED": {
                    "type": "boolean", 
                    "default": "0",
                    "description": "Enable sklearn-based anomaly detection (requires sklearn)"
                },
                
                # P2-002: Quarantine system
                "QUARANTINE_ENABLED": {
                    "type": "boolean",
                    "default": "0",
                    "description": "Enable file quarantine system"
                },
                "QUARANTINE_DIR": {
                    "type": "string",
                    "default": "data/quarantine",
                    "description": "Directory for quarantined files"
                },
                
                # P2-003: Console authentication  
                "CONSOLE_AUTH_ENABLED": {
                    "type": "boolean",
                    "default": "0",
                    "description": "Enable console web authentication"
                },
                "CONSOLE_AUTH_SESSION_KEY": {
                    "type": "string",
                    "description": "Session signing key (32+ bytes hex, required when CONSOLE_AUTH_ENABLED=1)",
                    "required_when": ["CONSOLE_AUTH_ENABLED=1"],
                    "min_length": 64
                },
                "CONSOLE_AUTH_USER_DB": {
                    "type": "string", 
                    "default": "data/auth/users.json",
                    "description": "User database file path"
                },
                
                # P2-004: Streaming/SSE
                "STREAM_ENABLED": {
                    "type": "boolean",
                    "default": "0", 
                    "description": "Enable Server-Sent Events streaming"
                },
                "STREAM_TYPE": {
                    "type": "string",
                    "default": "sse",
                    "enum": ["sse"],
                    "description": "Streaming protocol type"
                },
                "STREAM_HEALTH_INTERVAL_MS": {
                    "type": "integer",
                    "default": "1000",
                    "minimum": 100,
                    "maximum": 30000,
                    "description": "Health metrics streaming interval"
                },
                "STREAM_REQUIRE_AUTH": {
                    "type": "boolean",
                    "default": "0",
                    "description": "Require authentication for streaming endpoints"
                },
                
                # P3-002: Log rotation
                "LOG_MAX_BYTES": {
                    "type": "integer", 
                    "default": "1048576",
                    "minimum": 1024,
                    "maximum": 104857600,
                    "description": "Maximum log file size in bytes"
                },
                "LOG_BACKUPS": {
                    "type": "integer",
                    "default": "5",
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Number of backup log files to keep"
                },
                "LOG_REDACT_SECRETS": {
                    "type": "boolean",
                    "default": "1",
                    "description": "Enable secret redaction in logs"
                },
                
                # P3-003: Service packaging
                "SERVICE_ENABLED": {
                    "type": "boolean",
                    "default": "0",
                    "description": "Enable Windows service mode"
                },
                
                # P3-005: Plugin system
                "PLUGINS_ENABLED": {
                    "type": "boolean",
                    "default": "0", 
                    "description": "Enable plugin/extension system"
                },
                "PLUGINS_DIR": {
                    "type": "string",
                    "default": "plugins",
                    "description": "Directory containing plugin modules"
                },
                
                # P3-006: Telemetry export
                "EXPORT_ENABLED": {
                    "type": "boolean",
                    "default": "0",
                    "description": "Enable telemetry export functionality"
                },
                "EXPORT_FORMAT": {
                    "type": "string",
                    "default": "ndjson",
                    "enum": ["ndjson", "csv"],
                    "description": "Export file format"
                },
                "EXPORT_INCLUDE": {
                    "type": "string",
                    "default": "metrics,events",
                    "description": "Comma-separated list of data types to export"
                }
            }
        }
    
    def validate_env_config(self) -> Dict[str, Any]:
        """Validate current environment configuration"""
        errors = []
        warnings = []
        config = {}
        
        for key, schema_def in self.schema["properties"].items():
            env_value = os.environ.get(key)
            default_value = schema_def.get("default")
            
            # Use environment value or default
            value = env_value if env_value is not None else default_value
            config[key] = value
            
            try:
                # Type validation
                validated_value = self._validate_value(key, value, schema_def)
                config[key + "_validated"] = validated_value
                
                # Required dependencies
                if "required_when" in schema_def:
                    self._check_required_dependencies(key, value, schema_def, config, errors)
                    
            except ConfigValidationError as e:
                errors.append(f"{key}: {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "config": config,
            "schema_version": self.schema["version"]
        }
    
    def _validate_value(self, key: str, value: Any, schema_def: Dict[str, Any]) -> Any:
        """Validate a single configuration value"""
        if value is None:
            return None
            
        value_str = str(value)
        expected_type = schema_def.get("type")
        
        if expected_type == "boolean":
            if value_str.lower() in {"1", "true", "yes", "on"}:
                return True
            elif value_str.lower() in {"0", "false", "no", "off"}:
                return False
            else:
                raise ConfigValidationError(f"invalid boolean value '{value}', expected 0/1/true/false")
        
        elif expected_type == "integer":
            try:
                int_val = int(value_str)
                min_val = schema_def.get("minimum")
                max_val = schema_def.get("maximum")
                
                if min_val is not None and int_val < min_val:
                    raise ConfigValidationError(f"value {int_val} below minimum {min_val}")
                if max_val is not None and int_val > max_val:
                    raise ConfigValidationError(f"value {int_val} above maximum {max_val}")
                    
                return int_val
            except ValueError:
                raise ConfigValidationError(f"invalid integer value '{value}'")
        
        elif expected_type == "string":
            min_len = schema_def.get("min_length")
            max_len = schema_def.get("max_length")
            enum_values = schema_def.get("enum")
            
            if min_len is not None and len(value_str) < min_len:
                raise ConfigValidationError(f"string too short, minimum length {min_len}")
            if max_len is not None and len(value_str) > max_len:
                raise ConfigValidationError(f"string too long, maximum length {max_len}")
            if enum_values and value_str not in enum_values:
                raise ConfigValidationError(f"value '{value_str}' not in allowed values: {enum_values}")
                
            return value_str
        
        return value
    
    def _check_required_dependencies(self, key: str, value: Any, schema_def: Dict[str, Any], 
                                   config: Dict[str, Any], errors: List[str]):
        """Check required dependency conditions"""
        required_when = schema_def.get("required_when", [])
        
        for condition in required_when:
            dep_key, dep_value = condition.split("=", 1)
            dep_current = config.get(dep_key)
            
            # If dependency condition is met, this value must be present and valid
            if dep_current == dep_value:
                if not value:
                    errors.append(f"{key}: required when {condition}")
    
    def get_schema_dict(self) -> Dict[str, Any]:
        """Get the complete schema as dictionary"""
        return self.schema
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        validation_result = self.validate_env_config()
        
        # Count enabled features
        enabled_features = []
        config = validation_result["config"]
        
        for key, value in config.items():
            if key.endswith("_validated"):
                continue
            validated_key = key + "_validated"
            if validated_key in config and config[validated_key] is True:
                enabled_features.append(key)
        
        return {
            "validation": validation_result,
            "enabled_features": enabled_features,
            "total_settings": len(self.schema["properties"]),
            "schema_version": self.schema["version"]
        }


# Global schema instance
_global_schema = None

def get_config_schema() -> ConfigSchema:
    """Get global configuration schema instance"""
    global _global_schema
    if _global_schema is None:
        _global_schema = ConfigSchema()
    return _global_schema


def validate_current_config() -> Dict[str, Any]:
    """Validate current environment configuration"""
    return get_config_schema().validate_env_config()


def get_schema_for_api() -> Dict[str, Any]:
    """Get schema suitable for API responses"""
    schema = get_config_schema()
    return {
        "schema": schema.get_schema_dict(),
        "summary": schema.get_config_summary()
    }
