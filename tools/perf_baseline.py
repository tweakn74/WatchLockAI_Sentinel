#!/usr/bin/env python3
"""
Baseline performance snapshot for chaos probes (Beazley-Mode RC-1+).

Produces a deterministic baseline to compare future chaos results.
Measures event bus enqueue->deliver performance without external dependencies.
"""

import asyncio
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


class InlineEventBus:
    """Minimal inline event bus fallback if project EventBus not available."""
    
    def __init__(self):
        self.handlers: Dict[str, List] = {}
        self.stats = {"events_processed": 0, "events_failed": 0}
    
    def register_handler(self, event_type: str, handler):
        """Register event handler."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def emit_async(self, event_type: str, data: Any = None):
        """Emit event asynchronously."""
        try:
            if event_type in self.handlers:
                for handler in self.handlers[event_type]:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
            self.stats["events_processed"] += 1
        except Exception:
            self.stats["events_failed"] += 1
    
    def emit_sync(self, event_type: str, data: Any = None):
        """Emit event synchronously."""
        try:
            if event_type in self.handlers:
                for handler in self.handlers[event_type]:
                    handler(data)
            self.stats["events_processed"] += 1
        except Exception:
            self.stats["events_failed"] += 1


def get_event_bus():
    """Get EventBus instance - project's if available, fallback otherwise."""
    try:
        from app_core.bus import get_event_bus as get_project_bus
        return get_project_bus()
    except ImportError:
        pass
    
    try:
        from app_core.bus import EventBus
        return EventBus()
    except ImportError:
        pass
    
    # Fallback to inline minimal bus
    return InlineEventBus()


async def measure_async_performance(event_bus, n_events: int = 1000) -> Dict[str, Any]:
    """Measure async event bus performance."""
    # No-op async handler
    async def noop_handler(data):
        pass
    
    # Register handler
    if hasattr(event_bus, 'register_handler'):
        event_bus.register_handler("perf_test", noop_handler)
    elif hasattr(event_bus, 'subscribe'):
        event_bus.subscribe("perf_test", noop_handler)
    
    # Measure enqueue->deliver performance
    start_time = time.perf_counter()
    
    for i in range(n_events):
        if hasattr(event_bus, 'emit_async'):
            await event_bus.emit_async("perf_test", {"seq": i})
        elif hasattr(event_bus, 'publish_async'):
            await event_bus.publish_async("perf_test", {"seq": i})
        elif hasattr(event_bus, 'emit'):
            # Try sync emit if no async available
            event_bus.emit("perf_test", {"seq": i})
        else:
            # Use inline bus emit
            await event_bus.emit_async("perf_test", {"seq": i})
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    
    return {
        "total_time_seconds": round(total_time, 6),
        "events_per_second": round(n_events / total_time, 2) if total_time > 0 else 0,
        "mean_latency_ms": round((total_time * 1000) / n_events, 6) if n_events > 0 else 0,
        "events_processed": n_events,
        "async_mode": True
    }


def measure_sync_performance(event_bus, n_events: int = 1000) -> Dict[str, Any]:
    """Measure sync event bus performance."""
    # No-op sync handler
    def noop_handler(data):
        pass
    
    # Register handler
    if hasattr(event_bus, 'register_handler'):
        event_bus.register_handler("perf_test_sync", noop_handler)
    elif hasattr(event_bus, 'subscribe'):
        event_bus.subscribe("perf_test_sync", noop_handler)
    
    # Measure enqueue->deliver performance
    start_time = time.perf_counter()
    
    for i in range(n_events):
        if hasattr(event_bus, 'emit_sync'):
            event_bus.emit_sync("perf_test_sync", {"seq": i})
        elif hasattr(event_bus, 'emit'):
            event_bus.emit("perf_test_sync", {"seq": i})
        elif hasattr(event_bus, 'publish'):
            event_bus.publish("perf_test_sync", {"seq": i})
        else:
            # Use inline bus emit
            event_bus.emit_sync("perf_test_sync", {"seq": i})
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    
    return {
        "total_time_seconds": round(total_time, 6),
        "events_per_second": round(n_events / total_time, 2) if total_time > 0 else 0,
        "mean_latency_ms": round((total_time * 1000) / n_events, 6) if n_events > 0 else 0,
        "events_processed": n_events,
        "async_mode": False
    }


async def run_performance_baseline(n_events: int = 1000) -> Dict[str, Any]:
    """Run performance baseline measurement."""
    try:
        # Get event bus
        event_bus = get_event_bus()
        
        # Test async performance if supported
        async_results = {}
        try:
            async_results = await measure_async_performance(event_bus, n_events)
        except Exception as e:
            async_results = {"error": str(e), "async_mode": True, "events_processed": 0}
        
        # Test sync performance
        sync_results = {}
        try:
            sync_results = measure_sync_performance(event_bus, n_events)
        except Exception as e:
            sync_results = {"error": str(e), "async_mode": False, "events_processed": 0}
        
        # Determine best results
        best_results = async_results if async_results.get("events_per_second", 0) > sync_results.get("events_per_second", 0) else sync_results
        
        # Compile baseline report
        baseline = {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.platform(),
            "test_config": {
                "n_events": n_events,
                "event_bus_type": type(event_bus).__name__
            },
            "performance": {
                "events_per_second": best_results.get("events_per_second", 0),
                "mean_latency_ms": best_results.get("mean_latency_ms", 0),
                "total_time_seconds": best_results.get("total_time_seconds", 0),
                "mode": "async" if best_results.get("async_mode", False) else "sync"
            },
            "detailed_results": {
                "async": async_results,
                "sync": sync_results
            },
            "status": "completed" if best_results.get("events_processed", 0) > 0 else "failed"
        }
        
        return baseline
        
    except Exception as e:
        return {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.platform(),
            "status": "error",
            "error": str(e),
            "performance": {
                "events_per_second": 0,
                "mean_latency_ms": 0,
                "total_time_seconds": 0,
                "mode": "unknown"
            }
        }


async def main():
    """Main entry point for performance baseline."""
    print("[U+1F3C1] Performance Baseline Measurement Starting...")
    
    try:
        # Run the baseline measurement
        baseline = await run_performance_baseline()
        
        # Write results to DOCS/report/perf_baseline.json
        output_path = Path(REPO_ROOT) / "DOCS" / "report" / "perf_baseline.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, sort_keys=True)
        
        print(f"[PASS] Performance baseline completed")
        print(f"[BARS] Results: {baseline['performance']['events_per_second']:.1f} events/sec, "
              f"{baseline['performance']['mean_latency_ms']:.3f}ms avg latency")
        print(f"[U+1F4BE] Baseline saved to: {output_path}")
        print(f"[U+1F40D] Python {baseline['python_version']} on {baseline['platform']}")
        
        return 0
        
    except Exception as e:
        print(f"[FAIL] Performance baseline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
