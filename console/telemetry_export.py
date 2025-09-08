# File: console/telemetry_export.py  
# Purpose: Telemetry export endpoint (P3-006)

from __future__ import annotations
import os
import json
import time
import logging
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psutil


logger = logging.getLogger(__name__)


class TelemetryCollector:
    """Collects and formats telemetry data for export"""
    
    def __init__(self):
        """Initialize telemetry collector"""
        self.start_time = time.time()
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics
        
        Returns:
            dict: System metrics
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None
                },
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "percent_used": memory.percent,
                    "process_rss_bytes": process_memory.rss,
                    "process_vms_bytes": process_memory.vms
                },
                "disk": {
                    "total_bytes": disk_usage.total,
                    "free_bytes": disk_usage.free,
                    "used_bytes": disk_usage.used,
                    "percent_used": (disk_usage.used / disk_usage.total) * 100
                }
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics
        
        Returns:
            dict: Application metrics
        """
        uptime_seconds = time.time() - self.start_time
        
        metrics = {
            "uptime_seconds": uptime_seconds,
            "version": "1.0.0",  # TODO: Get from actual version
            "environment": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform
            },
            "configuration": {
                "health_endpoint_enabled": os.getenv("HEALTH_ENDPOINT_ENABLED", "1") == "1",
                "auth_enabled": os.getenv("CONSOLE_AUTH_ENABLED", "0") == "1",
                "stream_enabled": os.getenv("STREAM_ENABLED", "0") == "1",
                "plugins_enabled": os.getenv("PLUGINS_ENABLED", "0") == "1",
                "log_redaction_enabled": os.getenv("LOG_REDACT_SECRETS", "0") == "1"
            }
        }
        
        # Try to get event bus metrics if available
        try:
            from app_core.bus import EventBus
            bus = EventBus()
            if hasattr(bus, 'get_stats'):
                bus_stats = bus.get_stats()
                metrics["event_bus"] = bus_stats
        except (ImportError, Exception) as e:
            logger.debug(f"Could not collect event bus metrics: {e}")
            
        return metrics
    
    def collect_security_metrics(self) -> Dict[str, Any]:
        """Collect security-related metrics
        
        Returns:
            dict: Security metrics  
        """
        metrics = {}
        
        # Rate limiting stats (if available)
        try:
            from console.rate_limit import get_rate_limit_stats
            metrics["rate_limiting"] = get_rate_limit_stats()
        except (ImportError, Exception):
            pass
            
        # Authentication stats (if available)
        try:
            from console.auth import get_auth_stats
            metrics["authentication"] = get_auth_stats()
        except (ImportError, Exception):
            pass
            
        # Quarantine stats (if available) 
        try:
            from console.quarantine import get_quarantine_stats
            metrics["quarantine"] = get_quarantine_stats()
        except (ImportError, Exception):
            pass
            
        return metrics
    
    def collect_plugin_metrics(self) -> Dict[str, Any]:
        """Collect plugin system metrics
        
        Returns:
            dict: Plugin metrics
        """
        if os.getenv("PLUGINS_ENABLED", "0") != "1":
            return {"enabled": False}
            
        try:
            from console.plugin_sandbox import get_plugin_loader
            loader = get_plugin_loader()
            
            return {
                "enabled": True,
                "loaded_count": len(loader.loaded_plugins),
                "loaded_plugins": list(loader.loaded_plugins.keys())
            }
        except (ImportError, Exception) as e:
            logger.error(f"Failed to collect plugin metrics: {e}")
            return {"enabled": True, "error": str(e)}
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all telemetry metrics
        
        Returns:
            dict: Complete telemetry data
        """
        timestamp = datetime.utcnow().isoformat()
        
        telemetry = {
            "timestamp": timestamp,
            "collection_time_seconds": time.time(),
            "format_version": "1.0",
            "node": {
                "hostname": os.environ.get("HOSTNAME", "unknown"),
                "process_id": os.getpid()
            },
            "metrics": {
                "system": self.collect_system_metrics(),
                "application": self.collect_application_metrics(), 
                "security": self.collect_security_metrics(),
                "plugins": self.collect_plugin_metrics()
            }
        }
        
        return telemetry


class TelemetryExporter:
    """Handles telemetry data export in various formats"""
    
    def __init__(self):
        """Initialize telemetry exporter"""
        self.collector = TelemetryCollector()
        
    def export_json(self, include_system: bool = True, include_security: bool = True) -> str:
        """Export telemetry as JSON
        
        Args:
            include_system: Include system metrics
            include_security: Include security metrics
            
        Returns:
            str: JSON telemetry data
        """
        telemetry = self.collector.collect_all_metrics()
        
        # Filter based on parameters
        if not include_system:
            telemetry["metrics"].pop("system", None)
            
        if not include_security:
            telemetry["metrics"].pop("security", None)
            
        return json.dumps(telemetry, indent=2, sort_keys=True)
    
    def export_prometheus(self) -> str:
        """Export telemetry in Prometheus format
        
        Returns:  
            str: Prometheus formatted metrics
        """
        telemetry = self.collector.collect_all_metrics()
        lines = []
        
        # Helper to add Prometheus metric
        def add_metric(name: str, value: float, help_text: str, labels: Optional[Dict[str, str]] = None):
            lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} gauge")
            label_str = ""
            if labels:
                label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
                label_str = "{" + ",".join(label_pairs) + "}"
            lines.append(f"{name}{label_str} {value}")
            lines.append("")
        
        # Application metrics
        app_metrics = telemetry["metrics"]["application"]
        add_metric("watchlockai_uptime_seconds", app_metrics["uptime_seconds"], 
                  "Application uptime in seconds")
        
        # System metrics
        if "system" in telemetry["metrics"]:
            sys_metrics = telemetry["metrics"]["system"]
            
            if "cpu" in sys_metrics:
                add_metric("watchlockai_cpu_percent", sys_metrics["cpu"]["percent"],
                          "CPU usage percentage")
                add_metric("watchlockai_cpu_count", sys_metrics["cpu"]["count"],
                          "Number of CPU cores")
                          
            if "memory" in sys_metrics:
                mem = sys_metrics["memory"]
                add_metric("watchlockai_memory_percent", mem["percent_used"],
                          "Memory usage percentage")
                add_metric("watchlockai_memory_process_rss_bytes", mem["process_rss_bytes"],
                          "Process RSS memory in bytes")
                          
            if "disk" in sys_metrics:
                disk = sys_metrics["disk"]
                add_metric("watchlockai_disk_percent", disk["percent_used"],
                          "Disk usage percentage")
        
        # Plugin metrics
        if "plugins" in telemetry["metrics"]:
            plugin_metrics = telemetry["metrics"]["plugins"]
            if plugin_metrics.get("enabled"):
                add_metric("watchlockai_plugins_loaded", plugin_metrics.get("loaded_count", 0),
                          "Number of loaded plugins")
        
        return "\n".join(lines)
    
    def export_csv(self) -> str:
        """Export key metrics as CSV
        
        Returns:
            str: CSV formatted metrics
        """
        telemetry = self.collector.collect_all_metrics()
        
        lines = ["timestamp,metric,value,unit"]
        timestamp = telemetry["timestamp"]
        
        # Extract key metrics for CSV
        metrics_to_export = []
        
        app = telemetry["metrics"]["application"]
        metrics_to_export.append(("uptime", app["uptime_seconds"], "seconds"))
        
        if "system" in telemetry["metrics"]:
            sys_metrics = telemetry["metrics"]["system"]
            
            if "cpu" in sys_metrics:
                metrics_to_export.append(("cpu_percent", sys_metrics["cpu"]["percent"], "percent"))
                
            if "memory" in sys_metrics:
                metrics_to_export.append(("memory_percent", sys_metrics["memory"]["percent_used"], "percent"))
                metrics_to_export.append(("memory_rss", sys_metrics["memory"]["process_rss_bytes"], "bytes"))
        
        for metric, value, unit in metrics_to_export:
            lines.append(f"{timestamp},{metric},{value},{unit}")
            
        return "\n".join(lines)


# Global exporter instance
_telemetry_exporter = None


def get_telemetry_exporter() -> TelemetryExporter:
    """Get global telemetry exporter instance
    
    Returns:
        TelemetryExporter: Global exporter instance
    """
    global _telemetry_exporter
    if _telemetry_exporter is None:
        _telemetry_exporter = TelemetryExporter()
    return _telemetry_exporter


def export_telemetry(format_type: str = "json", **kwargs) -> str:
    """Export telemetry data
    
    Args:
        format_type: Export format (json, prometheus, csv)
        **kwargs: Format-specific options
        
    Returns:
        str: Formatted telemetry data
    """
    if os.getenv("EXPORT_ENABLED", "0") != "1":
        return json.dumps({"error": "Telemetry export disabled"})
        
    exporter = get_telemetry_exporter()
    
    if format_type.lower() == "json":
        return exporter.export_json(**kwargs)
    elif format_type.lower() == "prometheus":
        return exporter.export_prometheus()
    elif format_type.lower() == "csv":
        return exporter.export_csv()
    else:
        raise ValueError(f"Unsupported format: {format_type}")
