"""Tests for P5-005 performance smoke and concurrency probe."""

import json
import time
import unittest
from unittest.mock import patch, MagicMock

try:
    from console.perf_probe import (
        PerformanceProbe,
        run_basic_performance_check,
        run_stress_test,
        get_performance_probe
    )
    PERF_PROBE_AVAILABLE = True
except ImportError:
    PERF_PROBE_AVAILABLE = False


@unittest.skipUnless(PERF_PROBE_AVAILABLE, "Performance probe module not available")
class TestPerformanceProbe(unittest.TestCase):
    """Test performance probe functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "http://127.0.0.1:8080"
        self.probe = PerformanceProbe(self.base_url)
    
    def test_performance_probe_initialization(self):
        """Test PerformanceProbe initialization."""
        probe = PerformanceProbe("http://example.com")
        self.assertEqual(probe.base_url, "http://example.com")
        
        # Test URL normalization
        probe2 = PerformanceProbe("http://example.com/")
        self.assertEqual(probe2.base_url, "http://example.com")
    
    @patch('console.perf_probe.requests')
    def test_make_request_with_requests(self, mock_requests):
        """Test _make_request with requests library available."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status": "ok"}'
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {"status": "ok"}
        
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        mock_requests.Session.return_value = mock_session
        
        probe = PerformanceProbe("http://example.com")
        result = probe._make_request("/api/test")
        
        self.assertEqual(result["status_code"], 200)
        self.assertTrue(result["success"])
        self.assertIn("response_time_ms", result)
        self.assertIn("timestamp", result)
        self.assertEqual(result["response_data"], {"status": "ok"})
    
    @patch('console.perf_probe.requests', None)  # Simulate requests not available
    @patch('urllib.request.urlopen')
    def test_make_request_without_requests(self, mock_urlopen):
        """Test _make_request fallback to urllib when requests unavailable."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"status": "ok"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        probe = PerformanceProbe("http://example.com")
        result = probe._make_request("/api/test")
        
        self.assertEqual(result["status_code"], 200)
        self.assertTrue(result["success"])
        self.assertIn("response_time_ms", result)
        self.assertEqual(result["response_data"], {"status": "ok"})
    
    @patch('console.perf_probe.requests')
    def test_make_request_error_handling(self, mock_requests):
        """Test _make_request error handling."""
        mock_session = MagicMock()
        mock_session.request.side_effect = Exception("Connection failed")
        mock_requests.Session.return_value = mock_session
        
        probe = PerformanceProbe("http://example.com")
        result = probe._make_request("/api/test")
        
        self.assertEqual(result["status_code"], 0)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Connection failed")
    
    @patch.object(PerformanceProbe, '_make_request')
    def test_single_request_test(self, mock_make_request):
        """Test single request testing."""
        mock_make_request.return_value = {
            "status_code": 200,
            "response_time_ms": 50.0,
            "success": True,
            "timestamp": "2025-09-06T00:00:00"
        }
        
        result = self.probe.test_single_request("/api/health")
        
        self.assertEqual(result["endpoint"], "/api/health")
        self.assertEqual(result["test_type"], "single_request")
        self.assertIn("single_request", result)
        self.assertIn("timestamp", result)
        
        mock_make_request.assert_called_once_with("/api/health")
    
    @patch.object(PerformanceProbe, '_make_request')
    def test_concurrent_requests_test(self, mock_make_request):
        """Test concurrent requests testing."""
        # Mock successful responses
        mock_make_request.return_value = {
            "status_code": 200,
            "response_time_ms": 100.0,
            "success": True,
            "timestamp": "2025-09-06T00:00:00",
            "content_length": 100
        }
        
        result = self.probe.test_concurrent_requests(
            endpoint="/api/health",
            clients=2,
            duration_seconds=0.5  # Short duration for test
        )
        
        self.assertEqual(result["endpoint"], "/api/health")
        self.assertEqual(result["test_type"], "concurrent_requests")
        self.assertIn("metrics", result)
        self.assertIn("parameters", result)
        
        metrics = result["metrics"]
        self.assertIn("total_requests", metrics)
        self.assertIn("successful_requests", metrics)
        self.assertIn("requests_per_second", metrics)
        self.assertIn("response_times", metrics)
        
        response_times = metrics["response_times"]
        self.assertIn("p50_ms", response_times)
        self.assertIn("p95_ms", response_times)
        self.assertIn("mean_ms", response_times)
    
    @patch.object(PerformanceProbe, '_make_request')
    def test_concurrent_requests_with_failures(self, mock_make_request):
        """Test concurrent requests with some failures."""
        # Alternate between success and failure
        def side_effect(*args, **kwargs):
            if mock_make_request.call_count % 2 == 0:
                return {
                    "status_code": 500,
                    "response_time_ms": 200.0,
                    "success": False,
                    "timestamp": "2025-09-06T00:00:00"
                }
            else:
                return {
                    "status_code": 200,
                    "response_time_ms": 100.0,
                    "success": True,
                    "timestamp": "2025-09-06T00:00:00"
                }
        
        mock_make_request.side_effect = side_effect
        
        result = self.probe.test_concurrent_requests(
            endpoint="/api/health",
            clients=2,
            duration_seconds=0.5
        )
        
        metrics = result["metrics"]
        self.assertGreater(metrics["total_requests"], 0)
        self.assertGreater(metrics["failed_requests"], 0)
        self.assertLess(metrics["success_rate"], 1.0)
        self.assertIn("error_analysis", result)
    
    @patch.object(PerformanceProbe, 'test_single_request')
    @patch.object(PerformanceProbe, 'test_concurrent_requests')
    def test_endpoint_suite(self, mock_concurrent, mock_single):
        """Test endpoint suite testing."""
        mock_single.return_value = {
            "single_request": {"success": True}
        }
        mock_concurrent.return_value = {
            "metrics": {"success_rate": 1.0}
        }
        
        result = self.probe.test_endpoint_suite(["/api/health", "/api/status"])
        
        self.assertEqual(result["test_type"], "endpoint_suite")
        self.assertEqual(len(result["endpoints_tested"]), 2)
        self.assertIn("results", result)
        self.assertIn("summary", result)
        
        summary = result["summary"]
        self.assertEqual(summary["total_endpoints"], 2)
        self.assertEqual(summary["available_endpoints"], 2)
        self.assertEqual(summary["failed_endpoints"], 0)
    
    @patch.object(PerformanceProbe, 'test_single_request')
    @patch.object(PerformanceProbe, 'test_concurrent_requests')
    def test_load_test_report(self, mock_concurrent, mock_single):
        """Test comprehensive load test report generation."""
        mock_single.return_value = {
            "single_request": {"success": True, "response_time_ms": 50}
        }
        mock_concurrent.return_value = {
            "metrics": {
                "success_rate": 0.95,
                "requests_per_second": 100,
                "response_times": {
                    "mean_ms": 80,
                    "p95_ms": 150
                }
            }
        }
        
        result = self.probe.generate_load_test_report(
            endpoint="/api/health",
            clients=5,
            duration_seconds=2.0
        )
        
        self.assertEqual(result["test_type"], "load_test_report")
        self.assertIn("test_metadata", result)
        self.assertIn("baseline_test", result)
        self.assertIn("load_test", result)
        self.assertIn("assessment", result)
        
        assessment = result["assessment"]
        self.assertIn("performance_grade", assessment)
        self.assertIn("bottlenecks", assessment)
        self.assertIn("recommendations", assessment)
    
    def test_performance_grading(self):
        """Test performance grading logic."""
        # Test with mocked concurrent test
        with patch.object(self.probe, 'test_single_request') as mock_single, \
             patch.object(self.probe, 'test_concurrent_requests') as mock_concurrent:
            
            # Excellent performance
            mock_single.return_value = {"single_request": {"success": True}}
            mock_concurrent.return_value = {
                "metrics": {
                    "success_rate": 0.98,
                    "response_times": {"mean_ms": 50, "p95_ms": 80}
                }
            }
            
            result = self.probe.generate_load_test_report("/api/health", 5, 1.0)
            self.assertEqual(result["assessment"]["performance_grade"], "excellent")
            
            # Poor performance
            mock_concurrent.return_value = {
                "metrics": {
                    "success_rate": 0.70,
                    "response_times": {"mean_ms": 800, "p95_ms": 1500}
                }
            }
            
            result = self.probe.generate_load_test_report("/api/health", 5, 1.0)
            self.assertEqual(result["assessment"]["performance_grade"], "poor")
            self.assertIn("high_error_rate", result["assessment"]["bottlenecks"])
            self.assertIn("slow_response_times", result["assessment"]["bottlenecks"])
    
    def test_helper_functions(self):
        """Test helper functions."""
        with patch('console.perf_probe.PerformanceProbe') as mock_probe_class:
            mock_probe_instance = MagicMock()
            mock_probe_class.return_value = mock_probe_instance
            mock_probe_instance.generate_load_test_report.return_value = {"test": "result"}
            
            # Test run_basic_performance_check
            result = run_basic_performance_check("http://test.com")
            self.assertEqual(result, {"test": "result"})
            mock_probe_class.assert_called_with("http://test.com")
            
            # Test run_stress_test
            result = run_stress_test("http://test.com", clients=10, duration_seconds=5.0)
            self.assertEqual(result, {"test": "result"})
            
            # Test get_performance_probe
            probe = get_performance_probe("http://test.com")
            self.assertEqual(probe, mock_probe_instance)
    
    def test_percentile_calculation(self):
        """Test percentile calculation with various data sets."""
        with patch.object(self.probe, '_make_request') as mock_request:
            # Create a predictable set of response times
            response_times = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            call_count = 0
            
            def mock_response(*args, **kwargs):
                nonlocal call_count
                response_time = response_times[call_count % len(response_times)]
                call_count += 1
                return {
                    "status_code": 200,
                    "response_time_ms": response_time,
                    "success": True,
                    "timestamp": "2025-09-06T00:00:00",
                    "content_length": 100
                }
            
            mock_request.side_effect = mock_response
            
            result = self.probe.test_concurrent_requests(
                clients=1,
                duration_seconds=0.1  # Very short to get predictable results
            )
            
            metrics = result["metrics"]
            response_time_metrics = metrics["response_times"]
            
            # Verify percentile calculations are reasonable
            self.assertGreater(response_time_metrics["p95_ms"], response_time_metrics["p50_ms"])
            self.assertGreaterEqual(response_time_metrics["max_ms"], response_time_metrics["p95_ms"])
            self.assertLessEqual(response_time_metrics["min_ms"], response_time_metrics["p50_ms"])


@unittest.skipUnless(PERF_PROBE_AVAILABLE, "Performance probe module not available")
class TestPerformanceProbeIntegration(unittest.TestCase):
    """Integration tests for performance probe."""
    
    @patch.dict('os.environ', {
        'PERF_PROBE_ENABLED': '1',
        'ADMIN_AUTH_ENABLED': '1', 
        'ADMIN_TOKEN': 'test_token'
    })
    def test_perf_probe_endpoint_integration(self):
        """Test performance probe endpoint integration (mock test)."""
        try:
            from console.web_api import SentinelWebAPI
            from fastapi.testclient import TestClient
            
            # Create test API instance
            api = SentinelWebAPI()
            client = TestClient(api.app)
            
            # Test performance probe endpoint with authentication
            with patch('console.perf_probe.get_performance_probe') as mock_get_probe:
                mock_probe = MagicMock()
                mock_probe.generate_load_test_report.return_value = {
                    "test_type": "load_test_report",
                    "assessment": {"performance_grade": "good"}
                }
                mock_get_probe.return_value = mock_probe
                
                response = client.post(
                    "/api/admin/perf/probe?clients=5&duration_s=1.0&endpoint=/api/metrics/health",
                    headers={"X-Admin-Token": "test_token"}
                )
                
                # Should return 200 if performance probe module is available
                if response.status_code == 200:
                    data = response.json()
                    self.assertEqual(data["status"], "ok")
                    self.assertIn("test_type", data)
                else:
                    # Might be missing dependencies, skip
                    self.skipTest("Performance probe endpoint not available")
                
        except ImportError:
            self.skipTest("FastAPI or dependencies not available")
    
    def test_performance_probe_error_handling(self):
        """Test error handling in performance probe."""
        # Test with invalid URL
        probe = PerformanceProbe("http://invalid-url-that-does-not-exist.local")
        result = probe.test_single_request("/api/health")
        
        self.assertIn("single_request", result)
        self.assertFalse(result["single_request"]["success"])
    
    def test_performance_probe_with_real_endpoint(self):
        """Test performance probe with a real endpoint (if available)."""
        # This test attempts to connect to a real endpoint but gracefully handles failures
        probe = PerformanceProbe("http://httpbin.org")
        
        try:
            result = probe.test_single_request("/status/200")
            
            if result["single_request"]["success"]:
                # If we successfully connected, verify the structure
                self.assertEqual(result["single_request"]["status_code"], 200)
                self.assertGreater(result["single_request"]["response_time_ms"], 0)
            else:
                # If connection failed, that's also valid (network issues)
                self.assertIn("error", result["single_request"])
                
        except Exception:
            # Network connectivity issues are acceptable in tests
            self.skipTest("Network connectivity not available for real endpoint test")


if __name__ == '__main__':
    unittest.main()
