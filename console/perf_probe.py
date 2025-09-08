"""Performance smoke tests and concurrency probes for WatchLockAI Sentinel (P5-005).

Implements stdlib-only performance testing with threading-based load generation.
"""

from __future__ import annotations

import concurrent.futures
import json
import statistics
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    requests = None


class PerformanceProbe:
    """Performance testing and concurrency probe for health endpoints."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        """Initialize performance probe.
        
        Args:
            base_url: Base URL for the API being tested
        """
        self.base_url = base_url.rstrip('/')
        self.session = None
        
        # Initialize requests session if available
        if requests:
            self.session = requests.Session()
            self.session.timeout = 10
    
    def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict:
        """Make a single HTTP request.
        
        Args:
            endpoint: API endpoint to test
            method: HTTP method
            **kwargs: Additional request parameters
            
        Returns:
            Dict with response data and timing
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip('/'))
        start_time = time.time()
        
        try:
            if self.session:
                response = self.session.request(method, url, **kwargs)
                status_code = response.status_code
                content_length = len(response.content)
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            else:
                # Fallback to stdlib urllib if requests not available
                import urllib.request
                import urllib.error
                
                req = urllib.request.Request(url)
                try:
                    with urllib.request.urlopen(req, timeout=10) as response:
                        status_code = response.getcode()
                        content = response.read()
                        content_length = len(content)
                        response_data = json.loads(content.decode()) if content else None
                except urllib.error.HTTPError as e:
                    status_code = e.code
                    content_length = 0
                    response_data = None
                except urllib.error.URLError:
                    status_code = 0  # Connection error
                    content_length = 0
                    response_data = None
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "status_code": status_code,
                "response_time_ms": response_time,
                "content_length": content_length,
                "response_data": response_data,
                "timestamp": datetime.now().isoformat(),
                "success": 200 <= status_code < 300
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "status_code": 0,
                "response_time_ms": response_time,
                "content_length": 0,
                "response_data": None,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def test_single_request(self, endpoint: str = "/api/metrics/health") -> Dict:
        """Test a single request to the endpoint.
        
        Args:
            endpoint: Endpoint to test
            
        Returns:
            Dict with test results
        """
        result = self._make_request(endpoint)
        
        return {
            "endpoint": endpoint,
            "single_request": result,
            "test_type": "single_request",
            "timestamp": datetime.now().isoformat()
        }
    
    def test_concurrent_requests(
        self, 
        endpoint: str = "/api/metrics/health",
        clients: int = 10,
        duration_seconds: float = 5.0
    ) -> Dict:
        """Test concurrent requests using threading.
        
        Args:
            endpoint: Endpoint to test
            clients: Number of concurrent clients
            duration_seconds: Test duration in seconds
            
        Returns:
            Dict with performance metrics
        """
        start_time = time.time()
        end_time = start_time + duration_seconds
        results = []
        
        # Thread-safe counter for requests
        request_counter = threading.Value('i', 0)
        counter_lock = threading.Lock()
        
        def worker():
            """Worker function for concurrent requests."""
            while time.time() < end_time:
                result = self._make_request(endpoint)
                results.append(result)
                
                with counter_lock:
                    request_counter.value += 1
                
                # Small delay to prevent overwhelming
                time.sleep(0.001)
        
        # Launch concurrent workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=clients) as executor:
            futures = [executor.submit(worker) for _ in range(clients)]
            
            # Wait for completion
            concurrent.futures.wait(futures, timeout=duration_seconds + 5)
        
        actual_duration = time.time() - start_time
        
        # Calculate metrics
        if results:
            response_times = [r["response_time_ms"] for r in results]
            successful_requests = [r for r in results if r["success"]]
            failed_requests = [r for r in results if not r["success"]]
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            n = len(sorted_times)
            
            def percentile(p):
                if not sorted_times:
                    return 0
                k = (n - 1) * p
                f = int(k)
                c = k - f
                if f + 1 < n:
                    return sorted_times[f] * (1 - c) + sorted_times[f + 1] * c
                else:
                    return sorted_times[f]
            
            p50 = percentile(0.50)
            p95 = percentile(0.95)
            p99 = percentile(0.99)
            
            rps = len(results) / actual_duration if actual_duration > 0 else 0
            
            metrics = {
                "total_requests": len(results),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "success_rate": len(successful_requests) / len(results) if results else 0,
                "duration_seconds": actual_duration,
                "requests_per_second": rps,
                "response_times": {
                    "min_ms": min(response_times) if response_times else 0,
                    "max_ms": max(response_times) if response_times else 0,
                    "mean_ms": statistics.mean(response_times) if response_times else 0,
                    "median_ms": statistics.median(response_times) if response_times else 0,
                    "p50_ms": p50,
                    "p95_ms": p95,
                    "p99_ms": p99,
                    "stddev_ms": statistics.stdev(response_times) if len(response_times) > 1 else 0
                }
            }
        else:
            metrics = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "success_rate": 0,
                "duration_seconds": actual_duration,
                "requests_per_second": 0,
                "response_times": {
                    "min_ms": 0, "max_ms": 0, "mean_ms": 0, "median_ms": 0,
                    "p50_ms": 0, "p95_ms": 0, "p99_ms": 0, "stddev_ms": 0
                }
            }
        
        # Error analysis
        error_analysis = {}
        if failed_requests:
            error_types = {}
            for req in failed_requests:
                error_key = f"status_{req['status_code']}"
                if "error" in req:
                    error_key += f"_{type(req['error']).__name__}"
                error_types[error_key] = error_types.get(error_key, 0) + 1
            error_analysis = error_types
        
        return {
            "endpoint": endpoint,
            "test_type": "concurrent_requests",
            "parameters": {
                "clients": clients,
                "duration_seconds": duration_seconds,
                "target_endpoint": endpoint
            },
            "metrics": metrics,
            "error_analysis": error_analysis,
            "timestamp": datetime.now().isoformat(),
            "sample_results": results[:5]  # Include first 5 results as samples
        }
    
    def test_endpoint_suite(self, endpoints: Optional[List[str]] = None) -> Dict:
        """Test a suite of endpoints with basic performance checks.
        
        Args:
            endpoints: List of endpoints to test (defaults to health endpoint)
            
        Returns:
            Dict with results for all endpoints
        """
        if endpoints is None:
            endpoints = ["/api/metrics/health"]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                # Single request test
                single_result = self.test_single_request(endpoint)
                
                # Small concurrent test
                concurrent_result = self.test_concurrent_requests(
                    endpoint=endpoint,
                    clients=3,
                    duration_seconds=2.0
                )
                
                results[endpoint] = {
                    "single_request": single_result,
                    "concurrent_test": concurrent_result,
                    "endpoint_available": single_result["single_request"]["success"]
                }
                
            except Exception as e:
                results[endpoint] = {
                    "error": str(e),
                    "endpoint_available": False
                }
        
        return {
            "test_type": "endpoint_suite",
            "endpoints_tested": endpoints,
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_endpoints": len(endpoints),
                "available_endpoints": sum(1 for r in results.values() if r.get("endpoint_available", False)),
                "failed_endpoints": sum(1 for r in results.values() if not r.get("endpoint_available", False))
            }
        }
    
    def generate_load_test_report(
        self,
        endpoint: str = "/api/metrics/health",
        clients: int = 10,
        duration_seconds: float = 10.0
    ) -> Dict:
        """Generate a comprehensive load test report.
        
        Args:
            endpoint: Endpoint to test
            clients: Number of concurrent clients
            duration_seconds: Test duration
            
        Returns:
            Comprehensive test report
        """
        test_start = datetime.now()
        
        # Run baseline single request
        baseline = self.test_single_request(endpoint)
        
        # Run concurrent load test
        load_test = self.test_concurrent_requests(endpoint, clients, duration_seconds)
        
        test_end = datetime.now()
        
        # Generate assessment
        metrics = load_test["metrics"]
        assessment = {
            "performance_grade": "unknown",
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Simple performance grading
        avg_response_time = metrics["response_times"]["mean_ms"]
        success_rate = metrics["success_rate"]
        
        if success_rate >= 0.95 and avg_response_time < 100:
            assessment["performance_grade"] = "excellent"
        elif success_rate >= 0.90 and avg_response_time < 200:
            assessment["performance_grade"] = "good"
        elif success_rate >= 0.80 and avg_response_time < 500:
            assessment["performance_grade"] = "fair"
        else:
            assessment["performance_grade"] = "poor"
        
        # Identify potential bottlenecks
        if success_rate < 0.95:
            assessment["bottlenecks"].append("high_error_rate")
        if avg_response_time > 200:
            assessment["bottlenecks"].append("slow_response_times")
        if metrics["response_times"]["p95_ms"] > metrics["response_times"]["mean_ms"] * 3:
            assessment["bottlenecks"].append("high_response_time_variance")
        
        # Generate recommendations
        if "high_error_rate" in assessment["bottlenecks"]:
            assessment["recommendations"].append("Investigate error causes and improve error handling")
        if "slow_response_times" in assessment["bottlenecks"]:
            assessment["recommendations"].append("Optimize endpoint performance or increase resources")
        if "high_response_time_variance" in assessment["bottlenecks"]:
            assessment["recommendations"].append("Investigate inconsistent performance patterns")
        
        return {
            "test_type": "load_test_report",
            "test_metadata": {
                "start_time": test_start.isoformat(),
                "end_time": test_end.isoformat(),
                "duration_seconds": (test_end - test_start).total_seconds(),
                "endpoint": endpoint,
                "parameters": {
                    "clients": clients,
                    "duration_seconds": duration_seconds
                }
            },
            "baseline_test": baseline,
            "load_test": load_test,
            "assessment": assessment,
            "system_info": {
                "timestamp": datetime.now().isoformat(),
                "test_runner": "PerformanceProbe/1.0"
            }
        }


def run_basic_performance_check(base_url: str = "http://127.0.0.1:8080") -> Dict:
    """Run a basic performance check with default parameters.
    
    Args:
        base_url: Base URL for the API
        
    Returns:
        Performance check results
    """
    probe = PerformanceProbe(base_url)
    return probe.generate_load_test_report(
        endpoint="/api/metrics/health",
        clients=5,
        duration_seconds=3.0
    )


def run_stress_test(
    base_url: str = "http://127.0.0.1:8080",
    clients: int = 20,
    duration_seconds: float = 30.0
) -> Dict:
    """Run a stress test with higher load.
    
    Args:
        base_url: Base URL for the API
        clients: Number of concurrent clients
        duration_seconds: Test duration
        
    Returns:
        Stress test results
    """
    probe = PerformanceProbe(base_url)
    return probe.generate_load_test_report(
        endpoint="/api/metrics/health",
        clients=clients,
        duration_seconds=duration_seconds
    )


# Helper function for web API integration
def get_performance_probe(base_url: str = "http://127.0.0.1:8080") -> PerformanceProbe:
    """Get a PerformanceProbe instance for web API integration.
    
    Args:
        base_url: Base URL for the API
        
    Returns:
        PerformanceProbe instance
    """
    return PerformanceProbe(base_url)
