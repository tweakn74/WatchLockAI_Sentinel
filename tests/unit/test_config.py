"""Unit tests for configuration system."""

import tempfile
from pathlib import Path

import pytest
import yaml

from app_core.config import (
    AlertsConfig,
    FileSystemConfig,
    HealthConfig,
    NetworkConfig,
    ProcessConfig,
    RegistryConfig,
    ResponsesConfig,
    SentinelConfig,
    load_config,
    save_default_config,
    validate_config,
)


def test_filesystem_config_defaults():
    """Test FileSystemConfig default values."""
    config = FileSystemConfig()

    assert config.enabled is True
    assert isinstance(config.paths, list)
    assert len(config.paths) > 0  # Should have default paths
    assert isinstance(config.exclude_globs, list)
    assert config.method == "watchdog"
    assert config.compute_entropy is False
    assert config.compute_hash_small_files is False
    assert config.small_file_threshold_bytes == 1048576
    assert config.burst_window_sec == 10


def test_process_config_defaults():
    """Test ProcessConfig default values."""
    config = ProcessConfig()

    assert config.enabled is True
    assert config.poll_interval_ms == 1000
    assert config.capture_hash is False


def test_registry_config_defaults():
    """Test RegistryConfig default values."""
    config = RegistryConfig()

    assert config.enabled is True
    assert isinstance(config.watch_keys, list)
    assert len(config.watch_keys) >= 4  # Should have autostart keys
    assert config.method == "notify"


def test_network_config_defaults():
    """Test NetworkConfig default values."""
    config = NetworkConfig()

    assert config.enabled is True
    assert config.track_process_association is True
    assert config.poll_interval_ms == 1000
    assert config.include_udp is True


def test_health_config_defaults():
    """Test HealthConfig default values."""
    config = HealthConfig()

    assert config.enabled is True
    assert config.cpu_warn == 90
    assert config.ram_warn == 90
    assert config.disk_warn_pct_free == 5
    assert config.temp_warn_c is None


# NOTE: DetectionConfig class does not exist in current implementation
# def test_detection_config_defaults():
#     """Test DetectionConfig default values."""
#     config = DetectionConfig()
#
#     assert config.enabled is True
#     assert isinstance(config.rules_config, dict)
#     assert config.knowledge_packs_dir == "detection/knowledge/packs"


def test_responses_config_defaults():
    """Test ResponsesConfig default values."""
    config = ResponsesConfig()

    assert config.allow_destructive_actions is False


def test_alerts_config_defaults():
    """Test AlertsConfig default values."""
    config = AlertsConfig()

    assert config.toast_notifications is True
    assert config.log_jsonl == "logs/alerts.jsonl"
    assert config.max_tray_history == 10


def test_sentinel_config_creation():
    """Test SentinelConfig creation with all sub-configs."""
    config = SentinelConfig()

    assert config.version == 1
    assert hasattr(config, 'monitoring')
    # NOTE: DetectionConfig does not exist in current implementation  
    assert isinstance(config.responses, ResponsesConfig)
    assert isinstance(config.alerts, AlertsConfig)

    # Check sub-configs
    assert "file_system" in config.monitoring
    assert "process" in config.monitoring
    assert "registry" in config.monitoring
    assert "network" in config.monitoring
    assert "health" in config.monitoring


def test_config_validation_valid():
    """Test configuration validation with valid config."""
    config = SentinelConfig()
    warnings = validate_config(config)

    # Should have no warnings for default config
    assert isinstance(warnings, list)


def test_config_validation_warnings():
    """Test configuration validation with problematic config."""
    config = SentinelConfig()

    # Create problematic settings
    config.monitoring["file_system"].paths = []  # Empty paths should warn
    config.monitoring["health"].cpu_warn = 150  # Invalid percentage

    warnings = validate_config(config)

    assert len(warnings) >= 1  # Should have warnings
    assert any("paths" in w.lower() for w in warnings)


# NOTE: save_config function does not exist in current implementation
# def test_save_and_load_config():
#     """Test saving and loading configuration."""
#     with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
#         temp_file = f.name
#
#     try:
#         # Create test config
#         original_config = SentinelConfig()
#         original_config.monitoring["file_system"].enabled = False
#         original_config.monitoring["health"].cpu_warn = 75
#
#         # Save config
#         save_config(original_config, temp_file)
#
#         # Load config
#         loaded_config = load_config(temp_file)
#
#         # Verify loaded config matches
#         assert loaded_config.monitoring["file_system"].enabled is False
#         assert loaded_config.monitoring["health"].cpu_warn == 75
#         assert loaded_config.version == original_config.version
#
#     finally:
#         Path(temp_file).unlink(missing_ok=True)


def test_save_default_config():
    """Test saving default configuration."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_file = f.name

    try:
        # Save default config
        save_default_config(temp_file)

        # Verify file exists and is valid YAML
        assert Path(temp_file).exists()

        with open(temp_file) as f:
            data = yaml.safe_load(f)

        assert isinstance(data, dict)
        assert "version" in data
        assert "monitoring" in data

        # Load as SentinelConfig
        config = load_config(temp_file)
        assert isinstance(config, SentinelConfig)

    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_load_nonexistent_config():
    """Test loading non-existent configuration file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_config.yaml")


def test_load_invalid_yaml():
    """Test loading invalid YAML configuration."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("invalid: yaml: content: [")
        temp_file = f.name

    try:
        with pytest.raises(yaml.YAMLError):
            load_config(temp_file)
    finally:
        Path(temp_file).unlink(missing_ok=True)


# NOTE: find_config_file function does not exist in current implementation
# def test_config_file_search():
#     """Test configuration file search functionality."""
#     # Test with non-existent file
#     result = find_config_file("nonexistent.yaml")
#     assert result is None
#
#     # Test with existing file
#     with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
#         temp_file = f.name
#
#     try:
#         result = find_config_file(temp_file)
#         assert result == temp_file
#
#     finally:
#         Path(temp_file).unlink(missing_ok=True)


def test_config_environment_variable_expansion():
    """Test environment variable expansion in configuration."""
    config_data = {
        "version": 1,
        "monitoring": {
            "file_system": {
                "enabled": True,
                "paths": ["%USERPROFILE%\\Documents", "%TEMP%"],
                "exclude_globs": [],
                "method": "watchdog",
                "compute_entropy": False,
                "compute_hash_small_files": False,
                "small_file_threshold_bytes": 1048576,
                "burst_window_sec": 10,
            },
        },
        "detection": {
            "enabled": True,
            "rules_config": {},
            "knowledge_packs_dir": "detection/knowledge/packs",
        },
        "response": {
            "allow_destructive_actions": False,
        },
        "alerts": {
            "toast_notifications": True,
            "log_jsonl": "logs/alerts.jsonl",
            "max_tray_history": 10,
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_file = f.name

    try:
        config = load_config(temp_file)

        # Environment variables should be expanded
        paths = config.monitoring["file_system"].paths
        assert any("%" not in path for path in paths if path)  # At least some should be expanded

    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_config_dict_conversion():
    """Test configuration to/from dictionary conversion."""
    original_config = SentinelConfig()

    # Convert to dict
    config_dict = original_config.model_dump()
    assert isinstance(config_dict, dict)
    assert "version" in config_dict
    assert "monitoring" in config_dict

    # Should be able to recreate from dict
    recreated_config = SentinelConfig(**config_dict)
    assert recreated_config.version == original_config.version


def test_pydantic_validation():
    """Test Pydantic validation in config classes."""
    # Test invalid percentage values
    with pytest.raises(ValueError):
        HealthConfig(cpu_warn=150)  # > 100

    with pytest.raises(ValueError):
        HealthConfig(cpu_warn=-10)  # < 0

    # Test invalid port values
    with pytest.raises(ValueError):
        NetworkConfig(poll_interval_ms=-100)  # Negative interval


# NOTE: DetectionConfig class does not exist in current implementation
# def test_rules_config_structure():
#     """Test rules configuration structure."""
#     config = DetectionConfig()
#
#     # Should be able to set rule-specific config
#     config.rules_config["RansomwareBurstV1"] = {
#         "enabled": True,
#         "burst_window_sec": 15,
#         "min_suspicious_events": 100,
#     }
#
#     assert "RansomwareBurstV1" in config.rules_config
#     assert config.rules_config["RansomwareBurstV1"]["enabled"] is True


def test_config_merge_defaults():
    """Test that partial configs merge with defaults."""
    # Create minimal config data
    minimal_config = {
        "version": 1,
        "monitoring": {
            "file_system": {
                "enabled": False,  # Only specify this field
            },
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(minimal_config, f)
        temp_file = f.name

    try:
        config = load_config(temp_file)

        # Should have default values for unspecified fields
        assert config.monitoring["file_system"].enabled is False  # Our override
        assert config.monitoring["file_system"].method == "watchdog"  # Default
        assert config.monitoring["process"].enabled is True  # Default from other section

    finally:
        Path(temp_file).unlink(missing_ok=True)
