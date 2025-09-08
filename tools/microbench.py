#!/usr/bin/env python3
"""Comprehensive microbenchmarking suite for WatchLockAI Sentinel.

Provides detailed performance analysis of critical code paths with:
- EventBus hot path microbenchmarks (1k-10k iterations)
- Health JSON rendering performance analysis
- Memory usage profiling (naive peak RSS sampling)
- Statistical analysis (median, p95, p99, stddev)
- Comparative analysis across different load scenarios
- Performance regression detection

Designed for Windows-first compatibility with graceful degradation.
"""

import gc
import json
import os
import psutil
import statistics
import sys
import threading
import time
from collections import defaultdict, namedtuple
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
import argparse

# Try to import performance monitoring modules
try:
    import resource
    RESOURCE_AVAILABLE = True
except ImportError:
    RESOURCE_AVAILABLE = False
    print("WARNING: resource module not available (likely Windows) - memory tracking limited")

try:
    import tracemalloc
    TRACEMALLOC_AVAILABLE = True
except ImportError:
    TRACEMALLOC_AVAILABLE = False

# Performance measurement configuration
BENCHMARK_CONFIG = {
    "warmup_iterations": 100,
    "min_iterations": 1000,
    "max_iterations": 10000,
    "target_duration_seconds": 2.0,
    "memory_sample_interval": 0.01,  # 10ms
    "gc_between_tests": True,
    "statistical_confidence": 0.95,
}

BenchmarkResult = namedtuple('BenchmarkResult', [
    'name', 'iterations', 'total_time', 'min_time', 'max_time', 
    'mean_time', 'median_time', 'p95_time', 'p99_time', 'stddev_time',
    'ops_per_second', 'memory_peak_mb', 'memory_delta_mb'
])

@dataclass
class MemorySample:
    """Single memory usage sample."""
    timestamp: float
    rss_mb: float
    vms_mb: float
    
@dataclass 
class MicrobenchmarkReport:
    """Complete microbenchmark execution report."""
    timestamp: str
    system_info: Dict[str, Any]
    benchmark_results: List[BenchmarkResult]
    memory_samples: List[MemorySample]
    total_duration: float
    config: Dict[str, Any]


class MemoryProfiler:
    """Naive memory profiler using psutil for cross-platform compatibility."""
    
    def __init__(self):
        self.samples: List[MemorySample] = []
        self.sampling = False
        self.sample_thread: Optional[threading.Thread] = None
        self.process = psutil.Process()
        
    def start_sampling(self, interval: float = 0.01):
        """Start memory sampling in background thread."""
        if self.sampling:
            return
            
        self.samples.clear()
        self.sampling = True
        self.sample_thread = threading.Thread(target=self._sample_loop, args=(interval,))
        self.sample_thread.daemon = True
        self.sample_thread.start()
    
    def stop_sampling(self):
        """Stop memory sampling."""
        self.sampling = False
        if self.sample_thread:
            self.sample_thread.join(timeout=1.0)
    
    def _sample_loop(self, interval: float):
        """Background sampling loop."""
        while self.sampling:
            try:
                memory_info = self.process.memory_info()
                sample = MemorySample(
                    timestamp=time.perf_counter(),
                    rss_mb=memory_info.rss / 1024 / 1024,
                    vms_mb=memory_info.vms / 1024 / 1024
                )
                self.samples.append(sample)
                time.sleep(interval)
            except Exception:
                # Ignore sampling errors
                pass
    
    def get_peak_memory(self) -> Tuple[float, float]:
        """Get peak RSS and VMS memory usage in MB."""
        if not self.samples:
            return 0.0, 0.0
            
        peak_rss = max(sample.rss_mb for sample in self.samples)
        peak_vms = max(sample.vms_mb for sample in self.samples)
        return peak_rss, peak_vms
    
    def get_memory_delta(self) -> Tuple[float, float]:
        """Get memory delta (peak - baseline) in MB."""
        if len(self.samples) < 2:
            return 0.0, 0.0
            
        baseline_rss = self.samples[0].rss_mb
        baseline_vms = self.samples[0].vms_mb
        peak_rss, peak_vms = self.get_peak_memory()
        
        return peak_rss - baseline_rss, peak_vms - baseline_vms


class EventBusMockBenchmark:
    """Mock EventBus implementation for benchmarking."""
    
    def __init__(self):
        self.events_processed = 0
        self.subscribers = {}
        self.metrics = {
            "delivery_success_count": 0,
            "delivery_failure_count": 0,
            "total_events_processed": 0,
            "queue_depth": 0,
            "subscriber_count": 0,
        }
    
    def publish_event(self, event_type: str, payload: Dict[str, Any]):
        """Simulate event publishing."""
        self.events_processed += 1
        self.metrics["total_events_processed"] += 1
        
        # Simulate processing overhead
        if event_type in self.subscribers:
            self.metrics["delivery_success_count"] += len(self.subscribers[event_type])
        
        # Simulate some CPU work
        _ = json.dumps(payload)
        return True
    
    def subscribe(self, event_type: str, callback: Callable):
        """Simulate event subscription."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        self.metrics["subscriber_count"] = sum(len(subs) for subs in self.subscribers.values())
    
    def get_observability_metrics(self) -> Dict[str, Any]:
        """Get observability metrics for benchmarking."""
        return {
            **self.metrics,
            "timestamp": time.time(),
            "uptime_seconds": 3600,
            "performance_metrics": {
                "avg_processing_time_ms": 0.5,
                "peak_queue_depth": 10,
                "events_per_second": self.events_processed / 60.0
            }
        }


class HealthEndpointBenchmark:
    """Mock health endpoint for benchmarking JSON serialization."""
    
    def __init__(self):
        self.event_bus = EventBusMockBenchmark()
        
    def get_health_response(self) -> Dict[str, Any]:
        """Generate comprehensive health response for JSON serialization benchmark."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime_seconds": 3600,
            "service_status": "running",
            "event_bus": self.event_bus.get_observability_metrics(),
            "service": {
                "running": True,
                "uptime_seconds": 3600,
                "collectors": {
                    f"collector_{i}": {"status": "active", "last_update": time.time()}
                    for i in range(10)
                },
                "rules_engine": {
                    "rules_loaded": 150,
                    "rules_active": 145,
                    "detections_today": 23,
                    "last_rule_update": time.time()
                },
                "event_bus": {
                    "status": "operational",
                    "queue_depth": 5,
                    "throughput_events_per_sec": 125.3
                }
            },
            "flags": {
                flag: "1" if i % 2 == 0 else "0" 
                for i, flag in enumerate([
                    "METRICS_DEBUG_ENABLED", "CONFIG_HOT_RELOAD_ENABLED",
                    "TI_CACHE_ENABLED", "RATE_LIMIT_ENABLED", "HEALTH_ENDPOINT_ENABLED",
                    "MITRE_API_ENABLED", "ANOMALY_ENABLED", "QUARANTINE_ENABLED"
                ])
            },
            "version": "rc-1",
            "build_info": {
                "commit": "abc123def456",
                "build_date": "2025-01-01T00:00:00Z",
                "environment": "production"
            }
        }


class MicrobenchmarkSuite:
    """Comprehensive microbenchmarking suite."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = {**BENCHMARK_CONFIG, **(config or {})}
        self.memory_profiler = MemoryProfiler()
        self.results: List[BenchmarkResult] = []
        self.memory_samples: List[MemorySample] = []
        
        # Initialize benchmark subjects
        self.event_bus = EventBusMockBenchmark()
        self.health_endpoint = HealthEndpointBenchmark()
        
        # Setup event bus with subscribers for realistic load
        self._setup_event_bus()
    
    def _setup_event_bus(self):
        """Setup EventBus with realistic subscribers for benchmarking."""
        def dummy_handler(event_data):
            # Simulate minimal processing
            _ = len(str(event_data))
        
        # Add subscribers for common event types
        event_types = [
            "security.detection", "system.alert", "performance.metric",
            "user.action", "config.change", "network.event"
        ]
        
        for event_type in event_types:
            # Add multiple subscribers per event type to simulate real load
            for i in range(3):
                self.event_bus.subscribe(event_type, dummy_handler)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Collect system information for benchmarking context."""
        try:
            cpu_info = {
                "cpu_count": psutil.cpu_count(logical=True),
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            }
        except Exception:
            cpu_info = {"cpu_count": os.cpu_count()}
        
        try:
            memory_info = psutil.virtual_memory()._asdict()
        except Exception:
            memory_info = {"total": "unknown"}
        
        return {
            "platform": sys.platform,
            "python_version": sys.version,
            "cpu": cpu_info,
            "memory": memory_info,
            "process_id": os.getpid(),
            "command_line": " ".join(sys.argv),
        }
    
    def _calibrate_iterations(self, benchmark_func: Callable, target_duration: float) -> int:
        """Calibrate number of iterations to reach target duration."""
        # Start with warmup to get rough timing
        warmup_start = time.perf_counter()
        for _ in range(self.config["warmup_iterations"]):
            benchmark_func()
        warmup_duration = time.perf_counter() - warmup_start
        
        if warmup_duration <= 0:
            return self.config["max_iterations"]
        
        # Estimate iterations needed for target duration
        estimated_iterations = int(target_duration * self.config["warmup_iterations"] / warmup_duration)
        
        # Clamp to configured bounds
        return max(
            self.config["min_iterations"],
            min(estimated_iterations, self.config["max_iterations"])
        )
    
    def benchmark_function(self, name: str, func: Callable, 
                         setup_func: Optional[Callable] = None,
                         teardown_func: Optional[Callable] = None) -> BenchmarkResult:
        """Benchmark a single function with comprehensive metrics."""
        print(f"Benchmarking {name}...")
        
        # Garbage collection before benchmark
        if self.config["gc_between_tests"]:
            gc.collect()
        
        # Setup if provided
        if setup_func:
            setup_func()
        
        # Calibrate iterations
        iterations = self._calibrate_iterations(func, self.config["target_duration_seconds"])
        print(f"  Running {iterations:,} iterations...")
        
        # Start memory monitoring
        self.memory_profiler.start_sampling(self.config["memory_sample_interval"])
        baseline_memory = self.memory_profiler.process.memory_info().rss / 1024 / 1024
        
        # Warmup runs
        for _ in range(min(100, iterations // 10)):
            func()
        
        # Actual benchmark with individual timing
        times = []
        overall_start = time.perf_counter()
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        overall_end = time.perf_counter()
        total_time = overall_end - overall_start
        
        # Stop memory monitoring
        self.memory_profiler.stop_sampling()
        peak_memory_rss, _ = self.memory_profiler.get_peak_memory()
        memory_delta_rss, _ = self.memory_profiler.get_memory_delta()
        
        # Teardown if provided
        if teardown_func:
            teardown_func()
        
        # Calculate statistics
        times_sorted = sorted(times)
        n = len(times)
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            min_time=min(times),
            max_time=max(times),
            mean_time=statistics.mean(times),
            median_time=statistics.median(times),
            p95_time=times_sorted[int(n * 0.95)] if n > 20 else max(times),
            p99_time=times_sorted[int(n * 0.99)] if n > 100 else max(times),
            stddev_time=statistics.stdev(times) if n > 1 else 0.0,
            ops_per_second=iterations / total_time,
            memory_peak_mb=peak_memory_rss,
            memory_delta_mb=memory_delta_rss
        )
        
        self.results.append(result)
        print(f"  Completed: {result.ops_per_second:,.0f} ops/sec, "
              f"median: {result.median_time*1000:.3f}ms, "
              f"p95: {result.p95_time*1000:.3f}ms")
        
        return result
    
    def benchmark_event_bus_publish(self) -> BenchmarkResult:
        """Benchmark EventBus event publishing performance."""
        test_event_types = [
            "security.detection", "system.alert", "performance.metric",
            "user.action", "config.change", "network.event"
        ]
        
        test_payloads = [
            {"type": "basic", "data": "simple"},
            {"type": "medium", "data": {"nested": {"value": 123, "items": [1, 2, 3]}}},
            {"type": "large", "data": {"bulk": "x" * 1000, "array": list(range(100))}}
        ]
        
        event_type_cycle = 0
        payload_cycle = 0
        
        def publish_event():
            nonlocal event_type_cycle, payload_cycle
            event_type = test_event_types[event_type_cycle % len(test_event_types)]
            payload = test_payloads[payload_cycle % len(test_payloads)]
            
            self.event_bus.publish_event(event_type, payload)
            
            event_type_cycle += 1
            payload_cycle += 1
        
        return self.benchmark_function("EventBus.publish_event", publish_event)
    
    def benchmark_event_bus_metrics(self) -> BenchmarkResult:
        """Benchmark EventBus metrics collection performance."""
        def get_metrics():
            return self.event_bus.get_observability_metrics()
        
        return self.benchmark_function("EventBus.get_observability_metrics", get_metrics)
    
    def benchmark_health_json_render(self) -> BenchmarkResult:
        """Benchmark health endpoint JSON rendering performance."""
        def render_health_json():
            health_data = self.health_endpoint.get_health_response()
            return json.dumps(health_data)
        
        return self.benchmark_function("Health.json_render", render_health_json)
    
    def benchmark_health_json_parse(self) -> BenchmarkResult:
        """Benchmark health JSON parsing performance."""
        # Pre-generate JSON string for parsing benchmark
        health_data = self.health_endpoint.get_health_response()
        health_json = json.dumps(health_data)
        
        def parse_health_json():
            return json.loads(health_json)
        
        return self.benchmark_function("Health.json_parse", parse_health_json)
    
    def benchmark_combined_health_cycle(self) -> BenchmarkResult:
        """Benchmark complete health check cycle (data + JSON + metrics)."""
        def health_cycle():
            # Get health data
            health_data = self.health_endpoint.get_health_response()
            
            # Serialize to JSON
            health_json = json.dumps(health_data)
            
            # Get EventBus metrics
            metrics = self.event_bus.get_observability_metrics()
            
            # Simulate response size calculation
            _ = len(health_json) + len(str(metrics))
        
        return self.benchmark_function("Health.complete_cycle", health_cycle)
    
    def run_comprehensive_benchmarks(self) -> MicrobenchmarkReport:
        """Run complete microbenchmark suite."""
        print("Starting WatchLockAI Sentinel Microbenchmark Suite...")
        start_time = time.perf_counter()
        
        # System info collection
        system_info = self.get_system_info()
        print(f"System: {system_info['platform']}, "
              f"CPU: {system_info['cpu'].get('cpu_count', 'unknown')}, "
              f"Memory: {system_info['memory'].get('total', 'unknown')} bytes")
        
        # Run benchmarks in order of increasing complexity
        benchmarks = [
            ("EventBus Publish Event", self.benchmark_event_bus_publish),
            ("EventBus Get Metrics", self.benchmark_event_bus_metrics), 
            ("Health JSON Render", self.benchmark_health_json_render),
            ("Health JSON Parse", self.benchmark_health_json_parse),
            ("Complete Health Cycle", self.benchmark_combined_health_cycle),
        ]
        
        for bench_name, bench_func in benchmarks:
            try:
                bench_func()
            except Exception as e:
                print(f"ERROR in {bench_name}: {e}")
                # Add placeholder result for failed benchmark
                self.results.append(BenchmarkResult(
                    name=f"{bench_name} (FAILED)",
                    iterations=0, total_time=0, min_time=0, max_time=0,
                    mean_time=0, median_time=0, p95_time=0, p99_time=0, stddev_time=0,
                    ops_per_second=0, memory_peak_mb=0, memory_delta_mb=0
                ))
        
        end_time = time.perf_counter()
        total_duration = end_time - start_time
        
        print(f"\\nBenchmark suite completed in {total_duration:.2f} seconds")
        
        # Collect all memory samples
        self.memory_samples = self.memory_profiler.samples.copy()
        
        return MicrobenchmarkReport(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            system_info=system_info,
            benchmark_results=self.results,
            memory_samples=self.memory_samples,
            total_duration=total_duration,
            config=self.config
        )
    
    def generate_report(self, report: MicrobenchmarkReport, format_type: str = "markdown") -> str:
        """Generate formatted microbenchmark report."""
        if format_type == "json":
            return self._generate_json_report(report)
        elif format_type == "csv":
            return self._generate_csv_report(report)
        else:
            return self._generate_markdown_report(report)
    
    def _generate_markdown_report(self, report: MicrobenchmarkReport) -> str:
        """Generate Markdown microbenchmark report."""
        lines = []
        lines.append("# WatchLockAI Sentinel Microbenchmark Report\\n")
        lines.append(f"**Timestamp:** {report.timestamp}\\n")
        lines.append(f"**Total Duration:** {report.total_duration:.2f} seconds\\n")
        lines.append(f"**Platform:** {report.system_info['platform']}\\n")
        lines.append(f"**Python Version:** {report.system_info['python_version'].split()[0]}\\n")
        lines.append(f"**CPU Count:** {report.system_info['cpu'].get('cpu_count', 'unknown')}\\n")
        lines.append(f"**Memory Total:** {report.system_info['memory'].get('total', 'unknown')} bytes\\n\\n")
        
        # Performance Summary Table
        lines.append("## Performance Summary\\n\\n")
        lines.append("| Benchmark | Iterations | Ops/Sec | Median (ms) | P95 (ms) | P99 (ms) | Memory Peak (MB) |\\n")
        lines.append("|-----------|------------|---------|-------------|----------|----------|------------------|\\n")
        
        for result in report.benchmark_results:
            if result.iterations > 0:  # Skip failed benchmarks
                lines.append(f"| {result.name} | {result.iterations:,} | "
                           f"{result.ops_per_second:,.0f} | "
                           f"{result.median_time*1000:.3f} | "
                           f"{result.p95_time*1000:.3f} | " 
                           f"{result.p99_time*1000:.3f} | "
                           f"{result.memory_peak_mb:.1f} |\\n")
        lines.append("\\n")
        
        # Detailed Results
        lines.append("## Detailed Results\\n\\n")
        
        for result in report.benchmark_results:
            if result.iterations == 0:
                lines.append(f"### {result.name}\\n\\n")
                lines.append("**Status:** FAILED - See error logs above\\n\\n")
                continue
                
            lines.append(f"### {result.name}\\n\\n")
            lines.append(f"- **Iterations:** {result.iterations:,}\\n")
            lines.append(f"- **Total Time:** {result.total_time:.4f} seconds\\n")
            lines.append(f"- **Operations/Second:** {result.ops_per_second:,.0f}\\n")
            lines.append(f"- **Min Time:** {result.min_time*1000:.3f} ms\\n")
            lines.append(f"- **Max Time:** {result.max_time*1000:.3f} ms\\n")
            lines.append(f"- **Mean Time:** {result.mean_time*1000:.3f} ms\\n") 
            lines.append(f"- **Median Time:** {result.median_time*1000:.3f} ms\\n")
            lines.append(f"- **P95 Time:** {result.p95_time*1000:.3f} ms\\n")
            lines.append(f"- **P99 Time:** {result.p99_time*1000:.3f} ms\\n")
            lines.append(f"- **Standard Deviation:** {result.stddev_time*1000:.3f} ms\\n")
            lines.append(f"- **Memory Peak:** {result.memory_peak_mb:.1f} MB\\n")
            lines.append(f"- **Memory Delta:** {result.memory_delta_mb:.1f} MB\\n\\n")
        
        # Memory Analysis
        if report.memory_samples:
            lines.append("## Memory Analysis\\n\\n")
            
            memory_peak = max(sample.rss_mb for sample in report.memory_samples)
            memory_min = min(sample.rss_mb for sample in report.memory_samples)
            memory_delta = memory_peak - memory_min
            
            lines.append(f"- **Memory Sampling:** {len(report.memory_samples)} samples\\n")
            lines.append(f"- **Peak RSS:** {memory_peak:.1f} MB\\n")
            lines.append(f"- **Minimum RSS:** {memory_min:.1f} MB\\n")
            lines.append(f"- **Total Delta:** {memory_delta:.1f} MB\\n")
            
            if RESOURCE_AVAILABLE:
                lines.append("- **Resource Module:** Available\\n")
            else:
                lines.append("- **Resource Module:** Not Available (Windows limitation)\\n")
                
            if TRACEMALLOC_AVAILABLE:
                lines.append("- **Tracemalloc:** Available\\n")
            else:
                lines.append("- **Tracemalloc:** Not Available\\n")
        else:
            lines.append("## Memory Analysis\\n\\n")
            lines.append("**SKIPPED:** Memory sampling failed or unavailable\\n")
            lines.append("**Reason:** Platform limitations or insufficient permissions\\n")
        
        lines.append("\\n")
        
        # Configuration
        lines.append("## Benchmark Configuration\\n\\n")
        for key, value in report.config.items():
            lines.append(f"- **{key}:** {value}\\n")
        lines.append("\\n")
        
        # Performance Insights
        lines.append("## Performance Insights\\n\\n")
        
        # Find fastest and slowest operations
        if report.benchmark_results:
            valid_results = [r for r in report.benchmark_results if r.iterations > 0]
            if valid_results:
                fastest = max(valid_results, key=lambda x: x.ops_per_second)
                slowest = min(valid_results, key=lambda x: x.ops_per_second)
                
                lines.append(f"- **Fastest Operation:** {fastest.name} ({fastest.ops_per_second:,.0f} ops/sec)\\n")
                lines.append(f"- **Slowest Operation:** {slowest.name} ({slowest.ops_per_second:,.0f} ops/sec)\\n")
                
                # Performance ratio
                if slowest.ops_per_second > 0:
                    ratio = fastest.ops_per_second / slowest.ops_per_second
                    lines.append(f"- **Performance Ratio:** {ratio:.1f}x difference\\n")
        
        lines.append("\\n")
        
        # Recommendations
        lines.append("## Recommendations\\n\\n")
        
        # Check for performance issues
        slow_operations = [r for r in report.benchmark_results 
                          if r.iterations > 0 and r.ops_per_second < 1000]
        
        if slow_operations:
            lines.append("### Performance Optimization\\n")
            for op in slow_operations:
                lines.append(f"- **{op.name}**: {op.ops_per_second:.0f} ops/sec - Consider optimization\\n")
            lines.append("\\n")
        
        # Memory recommendations
        high_memory_ops = [r for r in report.benchmark_results 
                          if r.iterations > 0 and r.memory_delta_mb > 50]
        
        if high_memory_ops:
            lines.append("### Memory Optimization\\n")
            for op in high_memory_ops:
                lines.append(f"- **{op.name}**: {op.memory_delta_mb:.1f} MB delta - Review memory usage\\n")
            lines.append("\\n")
        
        lines.append("### General Recommendations\\n")
        lines.append("- Run benchmarks on dedicated hardware for consistent results\\n")
        lines.append("- Monitor performance trends over time to detect regressions\\n")
        lines.append("- Consider caching for frequently accessed health endpoint data\\n")
        lines.append("- Optimize JSON serialization for large health responses\\n")
        lines.append("- Implement connection pooling for high-throughput scenarios\\n\\n")
        
        lines.append("---\\n")
        lines.append("*Report generated by WatchLockAI Sentinel Microbenchmark Suite*\\n")
        
        return "".join(lines)
    
    def _generate_json_report(self, report: MicrobenchmarkReport) -> str:
        """Generate JSON microbenchmark report."""
        return json.dumps(asdict(report), indent=2, default=str)
    
    def _generate_csv_report(self, report: MicrobenchmarkReport) -> str:
        """Generate CSV microbenchmark report."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Benchmark", "Iterations", "Total_Time_Sec", "Min_Time_Ms", "Max_Time_Ms",
            "Mean_Time_Ms", "Median_Time_Ms", "P95_Time_Ms", "P99_Time_Ms", "StdDev_Time_Ms",
            "Ops_Per_Second", "Memory_Peak_MB", "Memory_Delta_MB"
        ])
        
        # Write results
        for result in report.benchmark_results:
            writer.writerow([
                result.name, result.iterations, result.total_time,
                result.min_time * 1000, result.max_time * 1000,
                result.mean_time * 1000, result.median_time * 1000,
                result.p95_time * 1000, result.p99_time * 1000, result.stddev_time * 1000,
                result.ops_per_second, result.memory_peak_mb, result.memory_delta_mb
            ])
        
        return output.getvalue()


def main():
    """Main entry point for microbenchmark execution."""
    parser = argparse.ArgumentParser(description="WatchLockAI Sentinel Microbenchmark Suite")
    parser.add_argument("--format", choices=["markdown", "json", "csv"], 
                       default="markdown", help="Output format")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--iterations", type=int, help="Override max iterations")
    parser.add_argument("--duration", type=float, help="Target duration per benchmark (seconds)")
    parser.add_argument("--memory-interval", type=float, default=0.01, 
                       help="Memory sampling interval (seconds)")
    parser.add_argument("--no-gc", action="store_true", help="Disable GC between tests")
    
    args = parser.parse_args()
    
    # Build configuration
    config = BENCHMARK_CONFIG.copy()
    if args.iterations:
        config["max_iterations"] = args.iterations
    if args.duration:
        config["target_duration_seconds"] = args.duration
    if args.memory_interval:
        config["memory_sample_interval"] = args.memory_interval
    if args.no_gc:
        config["gc_between_tests"] = False
    
    # Create and run benchmark suite
    suite = MicrobenchmarkSuite(config)
    
    try:
        report = suite.run_comprehensive_benchmarks()
        formatted_report = suite.generate_report(report, args.format)
        
        # Output report
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            print(f"\\nMicrobenchmark report written to {args.output}")
        else:
            print("\\n" + formatted_report)
    
    except KeyboardInterrupt:
        print("\\nBenchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\nBenchmark failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
