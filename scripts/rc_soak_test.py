#!/usr/bin/env python3
"""P6-001: RC Soak & Performance Baseline Test

Executes 10-15 minute performance soak test using existing perf probe.
Generates comprehensive baseline report for GA readiness assessment.
"""

from __future__ import annotations

import json
import os
import sys
import time
import psutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
REPO_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(REPO_ROOT))

try:
    from console.perf_probe import PerformanceProbe
except ImportError:
    print("ERROR: Unable to import PerformanceProbe from console.perf_probe")
    sys.exit(1)


class RCSoakTest:
    """RC release candidate soak testing with comprehensive monitoring."""
    
    def __init__(self, 
                 duration_s: int = 600,  # 10 minutes default
                 clients: int = 16,
                 base_url: str = "http://127.0.0.1:8080"):
        """Initialize soak test parameters.
        
        Args:
            duration_s: Test duration in seconds (default 600 = 10 min)
            clients: Concurrent client count for load generation
            base_url: Base URL for API testing
        """
        self.duration_s = duration_s
        self.clients = clients
        self.base_url = base_url
        self.probe = PerformanceProbe(base_url)
        
        # Monitoring data
        self.cpu_samples: List[float] = []
        self.memory_samples: List[float] = []
        self.response_times: List[float] = []
        self.error_count = 0
        self.total_requests = 0
        
        # Control flags
        self.monitoring_active = False
        self.test_start_time: Optional[float] = None
    
    def _monitor_system_resources(self) -> None:
        """Background thread to monitor CPU and memory usage."""
        while self.monitoring_active:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                
                self.cpu_samples.append(cpu_percent)
                self.memory_samples.append(memory_info.percent)
            except Exception:
                # Skip failed samples
                pass
    
    def _run_load_test(self) -> Dict:
        """Execute the load test using performance probe.
        
        Returns:
            Dict containing test results and metrics
        """
        print(f"Starting RC soak test: {self.clients} clients, {self.duration_s}s duration")
        print(f"Target: {self.base_url}")
        
        # Start system monitoring
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._monitor_system_resources, daemon=True)
        monitor_thread.start()
        
        self.test_start_time = time.time()
        
        try:
            # Use the existing performance probe to run the concurrent requests test
            results = self.probe.test_concurrent_requests(
                endpoint="/api/metrics/health",
                clients=self.clients,
                duration_seconds=self.duration_s
            )
            
            # Extract metrics from probe results
            if results and "metrics" in results:
                metrics = results["metrics"]
                self.total_requests = metrics.get("total_requests", 0)
                self.error_count = metrics.get("failed_requests", 0)
                
                # Response time data - extract from response_times dict
                if "response_times" in metrics:
                    rt_data = metrics["response_times"]
                    # Create list of response times for percentile calculation
                    # Use the existing percentiles from the probe
                    self.response_times = [
                        rt_data.get("p50_ms", 0),
                        rt_data.get("p95_ms", 0),
                        rt_data.get("p99_ms", 0),
                        rt_data.get("median_ms", 0),
                        rt_data.get("mean_ms", 0)
                    ]
        
        except Exception as e:
            print(f"Load test execution error: {e}")
            results = {"error": str(e)}
        finally:
            # Stop monitoring
            self.monitoring_active = False
            if monitor_thread.is_alive():
                monitor_thread.join(timeout=2)
        
        # Store results for later use
        self._probe_results = results
        
        return results
    
    def _calculate_percentiles(self, data: List[float]) -> Dict[str, float]:
        """Calculate P50, P95, P99 percentiles from data.
        
        Args:
            data: List of numeric values
            
        Returns:
            Dict with percentile values
        """
        if not data:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        return {
            "p50": sorted_data[int(n * 0.5)] if n > 0 else 0.0,
            "p95": sorted_data[int(n * 0.95)] if n > 0 else 0.0,
            "p99": sorted_data[int(n * 0.99)] if n > 0 else 0.0,
        }
    
    def generate_baseline_report(self, output_path: str) -> bool:
        """Generate comprehensive performance baseline report.
        
        Args:
            output_path: Path to write the baseline report
            
        Returns:
            True if report generated successfully
        """
        print("Generating performance baseline report...")
        
        # Run the soak test
        load_results = self._run_load_test()
        
        # Calculate metrics
        test_duration = time.time() - (self.test_start_time or time.time())
        
        # Response time percentiles (use probe data if available)
        if hasattr(self, '_probe_results') and 'metrics' in self._probe_results:
            rt_metrics = self._probe_results['metrics']['response_times']
            response_percentiles = {
                'p50': rt_metrics.get('p50_ms', 0),
                'p95': rt_metrics.get('p95_ms', 0), 
                'p99': rt_metrics.get('p99_ms', 0)
            }
        else:
            response_percentiles = self._calculate_percentiles(self.response_times)
        
        # System resource percentiles
        cpu_percentiles = self._calculate_percentiles(self.cpu_samples)
        memory_percentiles = self._calculate_percentiles(self.memory_samples)
        
        # RPS calculation
        rps = self.total_requests / test_duration if test_duration > 0 else 0.0
        
        # Generate report content
        report_content = f"""# WatchLockAI Sentinel RC Performance Baseline

**Test Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Version:** 0.9.0-rc1  
**Test Duration:** {test_duration:.1f}s ({test_duration/60:.1f} minutes)  
**Load Configuration:** {self.clients} concurrent clients  
**Target Endpoint:** /api/metrics/health  

## Load Test Results

### Request Metrics
- **Total Requests:** {self.total_requests:,}
- **Error Count:** {self.error_count}
- **Success Rate:** {((self.total_requests - self.error_count) / max(self.total_requests, 1) * 100):.2f}%
- **Requests Per Second (RPS):** {rps:.2f}

### Response Time Performance
- **P50 (Median):** {response_percentiles['p50']:.2f}ms
- **P95:** {response_percentiles['p95']:.2f}ms  
- **P99:** {response_percentiles['p99']:.2f}ms

## System Resource Utilization

### CPU Usage
- **P50:** {cpu_percentiles['p50']:.1f}%
- **P95:** {cpu_percentiles['p95']:.1f}%
- **P99:** {cpu_percentiles['p99']:.1f}%
- **Average:** {sum(self.cpu_samples) / len(self.cpu_samples):.1f}% (over {len(self.cpu_samples)} samples)

### Memory Usage
- **P50:** {memory_percentiles['p50']:.1f}%
- **P95:** {memory_percentiles['p95']:.1f}%
- **P99:** {memory_percentiles['p99']:.1f}%
- **Average:** {sum(self.memory_samples) / len(self.memory_samples):.1f}% (over {len(self.memory_samples)} samples)

## Performance Assessment

### Capacity Baseline
- **Sustained RPS:** {rps:.2f} req/sec under {self.clients} concurrent clients
- **Response Latency:** P95 = {response_percentiles['p95']:.2f}ms (target: <500ms)
- **Resource Efficiency:** CPU P95 = {cpu_percentiles['p95']:.1f}%, Memory P95 = {memory_percentiles['p95']:.1f}%

### Stability Indicators
- **Error Rate:** {(self.error_count / max(self.total_requests, 1) * 100):.3f}% (target: <1%)
- **Performance Consistency:** P99/P50 ratio = {(response_percentiles['p99'] / max(response_percentiles['p50'], 0.1)):.2f} (target: <5.0)

### GA Readiness Assessment
{self._assess_ga_readiness(rps, response_percentiles, cpu_percentiles, memory_percentiles)}

## Test Configuration

```json
{{
    "test_parameters": {{
        "duration_seconds": {self.duration_s},
        "concurrent_clients": {self.clients},
        "target_url": "{self.base_url}",
        "endpoint": "/api/metrics/health"
    }},
    "environment": {{
        "timestamp": "{datetime.now(timezone.utc).isoformat()}",
        "version": "0.9.0-rc1",
        "test_type": "rc_soak_baseline"
    }}
}}
```

## Notes

- This baseline establishes performance characteristics for the RC build
- Results provide capacity planning data for production deployment  
- Any performance regressions in future builds should be measured against this baseline
- Test conducted with health endpoint only; full API load testing recommended for production

---
*Generated by WatchLockAI Sentinel RC Soak Test (P6-001)*
"""
        
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write report
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"[PASS] Performance baseline report generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"[FAIL] Failed to generate baseline report: {e}")
            return False
    
    def _assess_ga_readiness(self, rps: float, response_perf: Dict, cpu_perf: Dict, memory_perf: Dict) -> str:
        """Assess GA readiness based on performance metrics.
        
        Args:
            rps: Requests per second achieved
            response_perf: Response time percentiles
            cpu_perf: CPU usage percentiles  
            memory_perf: Memory usage percentiles
            
        Returns:
            GA readiness assessment text
        """
        issues = []
        
        # Performance thresholds for GA readiness
        if rps < 10:
            issues.append("Low sustained RPS may indicate capacity constraints")
        
        if response_perf['p95'] > 500:
            issues.append("P95 response time exceeds 500ms target")
            
        if cpu_perf['p95'] > 80:
            issues.append("High CPU utilization (P95 > 80%) indicates resource pressure")
            
        if memory_perf['p95'] > 85:
            issues.append("High memory utilization (P95 > 85%) indicates resource pressure")
            
        if self.error_count / max(self.total_requests, 1) > 0.01:
            issues.append("Error rate exceeds 1% threshold")
        
        if not issues:
            return "**[PASS] GA READY**: All performance metrics meet production readiness criteria."
        else:
            return f"**[WARN]  REVIEW NEEDED**: {len(issues)} performance concerns identified:\n" + "\n".join(f"- {issue}" for issue in issues)


def main():
    """Main entry point for RC soak testing."""
    # Get parameters from environment or use defaults
    duration_s = int(os.getenv("PERF_SOAK_DURATION_S", "600"))  # 10 minutes
    clients = int(os.getenv("PERF_SOAK_CLIENTS", "16"))
    base_url = os.getenv("PERF_SOAK_BASE_URL", "http://127.0.0.1:8080")
    
    # Output path
    output_path = os.path.join(REPO_ROOT, "DOCS", "report", "perf_baseline_rc1.md")
    
    print(f"RC Soak Test Configuration:")
    print(f"  Duration: {duration_s}s ({duration_s//60}m {duration_s%60}s)")
    print(f"  Clients: {clients}")
    print(f"  Target: {base_url}")
    print(f"  Report: {output_path}")
    print()
    
    # Create and run soak test
    soak_test = RCSoakTest(duration_s=duration_s, clients=clients, base_url=base_url)
    
    success = soak_test.generate_baseline_report(output_path)
    
    if success:
        print(f"\n[PASS] RC soak test completed successfully")
        print(f"[BARS] Baseline report: {output_path}")
        return 0
    else:
        print(f"\n[FAIL] RC soak test failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
