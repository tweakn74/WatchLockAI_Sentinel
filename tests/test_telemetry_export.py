# File: tests/test_telemetry_export.py
# Purpose: Unit tests for telemetry export system (P3-006)

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from console.telemetry_export import (
    TelemetryCollector, TelemetryExporter, 
    get_telemetry_exporter, export_telemetry
)


class TestTelemetryCollector(unittest.TestCase):
    """Test telemetry collector functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.collector = TelemetryCollector()
    
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.Process')
    def test_collect_system_metrics(self, mock_process, mock_disk, mock_memory, 
                                   mock_cpu_freq, mock_cpu_count, mock_cpu_percent):
        """Test system metrics collection"""
        # Mock psutil returns
        mock_cpu_percent.return_value = 25.5
        mock_cpu_count.return_value = 4
        mock_cpu_freq.return_value = MagicMock(current=2400.0)
        
        mock_memory_obj = MagicMock()
        mock_memory_obj.total = 8589934592  # 8GB
        mock_memory_obj.available = 4294967296  # 4GB
        mock_memory_obj.percent = 50.0
        mock_memory.return_value = mock_memory_obj
        
        mock_disk_obj = MagicMock()
        mock_disk_obj.total = 1073741824  # 1GB
        mock_disk_obj.free = 536870912    # 512MB
        mock_disk_obj.used = 536870912    # 512MB
        mock_disk.return_value = mock_disk_obj
        
        mock_process_obj = MagicMock()
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 52428800   # 50MB
        mock_memory_info.vms = 104857600  # 100MB
        mock_process_obj.memory_info.return_value = mock_memory_info
        mock_process.return_value = mock_process_obj
        
        # Test collection
        metrics = self.collector.collect_system_metrics()
        
        self.assertIn('cpu', metrics)
        self.assertIn('memory', metrics)
        self.assertIn('disk', metrics)
        
        self.assertEqual(metrics['cpu']['percent'], 25.5)
        self.assertEqual(metrics['cpu']['count'], 4)
        self.assertEqual(metrics['memory']['percent_used'], 50.0)
        self.assertEqual(metrics['disk']['used_bytes'], 536870912)
    
    def test_collect_application_metrics(self):
        """Test application metrics collection"""
        metrics = self.collector.collect_application_metrics()
        
        self.assertIn('uptime_seconds', metrics)
        self.assertIn('version', metrics)
        self.assertIn('environment', metrics)
        self.assertIn('configuration', metrics)
        
        # Check configuration flags
        config = metrics['configuration']
        self.assertIn('health_endpoint_enabled', config)
        self.assertIn('auth_enabled', config)
        self.assertIn('stream_enabled', config)
    
    @patch.dict(os.environ, {
        "PLUGINS_ENABLED": "1",
        "LOG_REDACT_SECRETS": "1"
    })
    def test_collect_application_metrics_with_env(self):
        """Test application metrics with environment variables"""
        metrics = self.collector.collect_application_metrics()
        
        config = metrics['configuration']
        self.assertTrue(config['plugins_enabled'])
        self.assertTrue(config['log_redaction_enabled'])
    
    def test_collect_security_metrics(self):
        """Test security metrics collection"""
        # This will mostly test that the method doesn't crash
        # since the actual stats functions may not be available
        metrics = self.collector.collect_security_metrics()
        
        # Should return a dictionary even if empty
        self.assertIsInstance(metrics, dict)
    
    @patch.dict(os.environ, {"PLUGINS_ENABLED": "0"})
    def test_collect_plugin_metrics_disabled(self):
        """Test plugin metrics when disabled"""
        metrics = self.collector.collect_plugin_metrics()
        
        self.assertFalse(metrics['enabled'])
    
    @patch.dict(os.environ, {"PLUGINS_ENABLED": "1"})
    @patch('console.telemetry_export.get_plugin_loader')
    def test_collect_plugin_metrics_enabled(self, mock_get_loader):
        """Test plugin metrics when enabled"""
        mock_loader = MagicMock()
        mock_loader.loaded_plugins = {"plugin1": None, "plugin2": None}
        mock_get_loader.return_value = mock_loader
        
        metrics = self.collector.collect_plugin_metrics()
        
        self.assertTrue(metrics['enabled'])
        self.assertEqual(metrics['loaded_count'], 2)
        self.assertIn('plugin1', metrics['loaded_plugins'])
    
    def test_collect_all_metrics(self):
        """Test collecting all metrics"""
        metrics = self.collector.collect_all_metrics()
        
        # Check top-level structure
        self.assertIn('timestamp', metrics)
        self.assertIn('collection_time_seconds', metrics)
        self.assertIn('format_version', metrics)
        self.assertIn('node', metrics)
        self.assertIn('metrics', metrics)
        
        # Check metrics sections
        metrics_data = metrics['metrics']
        self.assertIn('application', metrics_data)
        self.assertIn('security', metrics_data)
        self.assertIn('plugins', metrics_data)


class TestTelemetryExporter(unittest.TestCase):
    """Test telemetry exporter functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.exporter = TelemetryExporter()
    
    @patch.object(TelemetryCollector, 'collect_all_metrics')
    def test_export_json(self, mock_collect):
        """Test JSON export"""
        # Mock telemetry data
        mock_telemetry = {
            "timestamp": "2025-09-04T10:29:27.000000",
            "metrics": {
                "system": {"cpu": {"percent": 25.0}},
                "application": {"uptime_seconds": 1000},
                "security": {"auth_attempts": 5},
                "plugins": {"enabled": True}
            }
        }
        mock_collect.return_value = mock_telemetry
        
        result = self.exporter.export_json()
        
        # Should be valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["timestamp"], "2025-09-04T10:29:27.000000")
        self.assertIn("system", parsed["metrics"])
    
    @patch.object(TelemetryCollector, 'collect_all_metrics')
    def test_export_json_filtered(self, mock_collect):
        """Test JSON export with filtering"""
        mock_telemetry = {
            "metrics": {
                "system": {"cpu": {"percent": 25.0}},
                "application": {"uptime_seconds": 1000},
                "security": {"auth_attempts": 5}
            }
        }
        mock_collect.return_value = mock_telemetry
        
        result = self.exporter.export_json(include_system=False, include_security=False)
        
        parsed = json.loads(result)
        self.assertNotIn("system", parsed["metrics"])
        self.assertNotIn("security", parsed["metrics"])
        self.assertIn("application", parsed["metrics"])
    
    @patch.object(TelemetryCollector, 'collect_all_metrics')
    def test_export_prometheus(self, mock_collect):
        """Test Prometheus export"""
        mock_telemetry = {
            "metrics": {
                "application": {"uptime_seconds": 1000},
                "system": {
                    "cpu": {"percent": 25.0, "count": 4},
                    "memory": {"percent_used": 50.0, "process_rss_bytes": 50000000},
                    "disk": {"percent_used": 75.0}
                },
                "plugins": {"enabled": True, "loaded_count": 2}
            }
        }
        mock_collect.return_value = mock_telemetry
        
        result = self.exporter.export_prometheus()
        
        # Check Prometheus format
        self.assertIn("# HELP watchlockai_uptime_seconds", result)
        self.assertIn("# TYPE watchlockai_uptime_seconds gauge", result)
        self.assertIn("watchlockai_uptime_seconds 1000", result)
        self.assertIn("watchlockai_cpu_percent 25.0", result)
        self.assertIn("watchlockai_memory_percent 50.0", result)
    
    @patch.object(TelemetryCollector, 'collect_all_metrics')
    def test_export_csv(self, mock_collect):
        """Test CSV export"""
        mock_telemetry = {
            "timestamp": "2025-09-04T10:29:27.000000",
            "metrics": {
                "application": {"uptime_seconds": 1000},
                "system": {
                    "cpu": {"percent": 25.0},
                    "memory": {"percent_used": 50.0, "process_rss_bytes": 50000000}
                }
            }
        }
        mock_collect.return_value = mock_telemetry
        
        result = self.exporter.export_csv()
        
        lines = result.split('\n')
        self.assertEqual(lines[0], "timestamp,metric,value,unit")
        self.assertIn("uptime,1000,seconds", result)
        self.assertIn("cpu_percent,25.0,percent", result)
        self.assertIn("memory_percent,50.0,percent", result)


class TestExportFunctions(unittest.TestCase):
    """Test module-level export functions"""
    
    def test_get_telemetry_exporter(self):
        """Test getting telemetry exporter singleton"""
        exporter1 = get_telemetry_exporter()
        exporter2 = get_telemetry_exporter()
        
        # Should return the same instance
        self.assertIs(exporter1, exporter2)
    
    @patch.dict(os.environ, {"EXPORT_ENABLED": "0"})
    def test_export_telemetry_disabled(self):
        """Test telemetry export when disabled"""
        result = export_telemetry("json")
        
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertEqual(parsed["error"], "Telemetry export disabled")
    
    @patch.dict(os.environ, {"EXPORT_ENABLED": "1"})
    @patch.object(TelemetryExporter, 'export_json')
    def test_export_telemetry_json(self, mock_export_json):
        """Test JSON telemetry export"""
        mock_export_json.return_value = '{"test": "data"}'
        
        result = export_telemetry("json")
        
        self.assertEqual(result, '{"test": "data"}')
        mock_export_json.assert_called_once()
    
    @patch.dict(os.environ, {"EXPORT_ENABLED": "1"})
    @patch.object(TelemetryExporter, 'export_prometheus')
    def test_export_telemetry_prometheus(self, mock_export_prometheus):
        """Test Prometheus telemetry export"""
        mock_export_prometheus.return_value = "watchlockai_test 1"
        
        result = export_telemetry("prometheus")
        
        self.assertEqual(result, "watchlockai_test 1")
        mock_export_prometheus.assert_called_once()
    
    @patch.dict(os.environ, {"EXPORT_ENABLED": "1"})
    def test_export_telemetry_unsupported_format(self):
        """Test unsupported export format"""
        with self.assertRaises(ValueError):
            export_telemetry("xml")


if __name__ == "__main__":
    unittest.main()
