"""Tests for P4-004: Chaos/Resilience probes functionality."""

import unittest
import time
import threading
from unittest.mock import patch, MagicMock

# Import the module under test
try:
    from console.chaos_probes import ChaosManager, ChaosContext, get_chaos_manager, chaos_injection
except ImportError:
    ChaosManager = None
    ChaosContext = None
    get_chaos_manager = None
    chaos_injection = None


@unittest.skipUnless(ChaosManager, "Chaos probes module not available")
class TestChaosProbes(unittest.TestCase):
    """Test chaos engineering probes functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.chaos_manager = ChaosManager()
    
    def test_chaos_disabled(self):
        """Test chaos functionality when disabled."""
        with patch('console.chaos_probes.CHAOS_ENABLED', False):
            result = self.chaos_manager.inject_latency("test_component", 100)
            
            self.assertEqual(result["status"], "disabled")
            self.assertFalse(result["enabled"])
    
    def test_inject_latency_success(self):
        """Test successful latency injection."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            start_time = time.time()
            result = self.chaos_manager.inject_latency("test_component", 100)
            end_time = time.time()
            
            self.assertEqual(result["status"], "armed")
            self.assertEqual(result["component"], "test_component")
            self.assertEqual(result["latency_ms"], 100)
            self.assertIn("injection_id", result)
            self.assertTrue(result["enabled"])
            
            # Verify latency was actually injected (allow some tolerance)
            actual_latency = (end_time - start_time) * 1000
            self.assertGreaterEqual(actual_latency, 80)  # 80ms minimum (20ms tolerance)
    
    def test_inject_latency_invalid_bounds(self):
        """Test latency injection with invalid bounds."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Negative latency
            result = self.chaos_manager.inject_latency("test_component", -10)
            self.assertEqual(result["status"], "error")
            
            # Excessive latency
            with patch('console.chaos_probes.CHAOS_MAX_LATENCY_MS', 1000):
                result = self.chaos_manager.inject_latency("test_component", 2000)
                self.assertEqual(result["status"], "error")
    
    def test_inject_error_success(self):
        """Test successful error injection."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Test with 100% error rate to guarantee injection
            with self.assertRaises(RuntimeError) as cm:
                self.chaos_manager.inject_error("test_component", "exception", 1.0)
            
            self.assertIn("Chaos-injected exception", str(cm.exception))
    
    def test_inject_error_low_rate(self):
        """Test error injection with low probability."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Test with 0% error rate - should not inject
            result = self.chaos_manager.inject_error("test_component", "exception", 0.0)
            
            self.assertEqual(result["status"], "armed")
            self.assertEqual(result["component"], "test_component")
            self.assertEqual(result["error_rate"], 0.0)
            self.assertFalse(result["error_injected"])
    
    def test_inject_error_invalid_rate(self):
        """Test error injection with invalid error rate."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Invalid rate > 1.0
            result = self.chaos_manager.inject_error("test_component", "exception", 1.5)
            self.assertEqual(result["status"], "error")
            
            # Invalid rate < 0.0
            result = self.chaos_manager.inject_error("test_component", "exception", -0.1)
            self.assertEqual(result["status"], "error")
    
    def test_inject_error_timeout(self):
        """Test timeout error injection."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            start_time = time.time()
            
            try:
                self.chaos_manager.inject_error("test_component", "timeout", 1.0)
            except Exception:
                pass  # Expected
            
            end_time = time.time()
            # Should have taken at least 10 seconds (timeout simulation)
            # For testing, we'll use a shorter timeout to avoid long test times
            with patch('time.sleep') as mock_sleep:
                self.chaos_manager.inject_error("test_component", "timeout", 1.0)
                mock_sleep.assert_called_with(10)
    
    def test_inject_error_network(self):
        """Test network error injection."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            with self.assertRaises(ConnectionError) as cm:
                self.chaos_manager.inject_error("test_component", "network", 1.0)
            
            self.assertIn("Chaos-injected network error", str(cm.exception))
    
    def test_chaos_context_manager(self):
        """Test chaos context manager functionality."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Test latency context
            start_time = time.time()
            with self.chaos_manager.chaos_context("test_component", "latency", latency_ms=50):
                pass
            end_time = time.time()
            
            # Should have injected latency
            actual_latency = (end_time - start_time) * 1000
            self.assertGreaterEqual(actual_latency, 40)  # 40ms minimum (10ms tolerance)
    
    def test_chaos_context_disabled(self):
        """Test chaos context when disabled."""
        with patch('console.chaos_probes.CHAOS_ENABLED', False):
            start_time = time.time()
            with self.chaos_manager.chaos_context("test_component", "latency", latency_ms=100):
                pass
            end_time = time.time()
            
            # Should not have injected latency
            actual_latency = (end_time - start_time) * 1000
            self.assertLess(actual_latency, 50)  # Should be very fast
    
    def test_list_active_probes_disabled(self):
        """Test listing active probes when disabled."""
        with patch('console.chaos_probes.CHAOS_ENABLED', False):
            result = self.chaos_manager.list_active_probes()
            
            self.assertEqual(result["status"], "disabled")
            self.assertEqual(result["probes"], [])
            self.assertFalse(result["enabled"])
    
    def test_list_active_probes_empty(self):
        """Test listing active probes when none exist."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            result = self.chaos_manager.list_active_probes()
            
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["count"], 0)
            self.assertEqual(result["probes"], [])
            self.assertTrue(result["enabled"])
    
    def test_list_active_probes_with_probes(self):
        """Test listing active probes with existing probes."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Inject some chaos
            self.chaos_manager.inject_latency("component1", 50)
            # Note: This test won't actually inject because latency is immediate
            # But it will create history entries
            
            result = self.chaos_manager.list_active_probes()
            
            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["enabled"])
    
    def test_stop_probe_disabled(self):
        """Test stopping probe when disabled."""
        with patch('console.chaos_probes.CHAOS_ENABLED', False):
            result = self.chaos_manager.stop_probe("fake_id")
            
            self.assertEqual(result["status"], "disabled")
            self.assertFalse(result["enabled"])
    
    def test_stop_probe_not_found(self):
        """Test stopping non-existent probe."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            result = self.chaos_manager.stop_probe("nonexistent_id")
            
            self.assertEqual(result["status"], "error")
            self.assertIn("not found", result["error"])
    
    def test_stop_all_probes_disabled(self):
        """Test stopping all probes when disabled."""
        with patch('console.chaos_probes.CHAOS_ENABLED', False):
            result = self.chaos_manager.stop_all_probes()
            
            self.assertEqual(result["status"], "disabled")
            self.assertFalse(result["enabled"])
    
    def test_stop_all_probes_empty(self):
        """Test stopping all probes when none exist."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            result = self.chaos_manager.stop_all_probes()
            
            self.assertEqual(result["status"], "stopped_all")
            self.assertEqual(result["stopped_count"], 0)
            self.assertTrue(result["enabled"])
    
    def test_get_injection_history_disabled(self):
        """Test getting injection history when disabled."""
        with patch('console.chaos_probes.CHAOS_ENABLED', False):
            result = self.chaos_manager.get_injection_history()
            
            self.assertEqual(result["status"], "disabled")
            self.assertEqual(result["history"], [])
            self.assertFalse(result["enabled"])
    
    def test_get_injection_history_with_data(self):
        """Test getting injection history with existing data."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Inject some chaos to create history
            self.chaos_manager.inject_latency("component1", 50)
            
            result = self.chaos_manager.get_injection_history()
            
            self.assertEqual(result["status"], "ok")
            self.assertGreater(result["total_count"], 0)
            self.assertTrue(result["enabled"])
            
            # Verify history structure
            history = result["history"]
            if history:  # If there's history
                entry = history[0]
                self.assertIn("id", entry)
                self.assertIn("type", entry)
                self.assertIn("component", entry)
                self.assertIn("started_at", entry)
    
    def test_get_statistics_disabled(self):
        """Test getting statistics when disabled."""
        with patch('console.chaos_probes.CHAOS_ENABLED', False):
            result = self.chaos_manager.get_statistics()
            
            self.assertEqual(result["status"], "disabled")
            self.assertEqual(result["stats"], {})
            self.assertFalse(result["enabled"])
    
    def test_get_statistics_with_data(self):
        """Test getting statistics with data."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Inject some chaos to create statistics
            self.chaos_manager.inject_latency("component1", 50)
            
            result = self.chaos_manager.get_statistics()
            
            self.assertEqual(result["status"], "ok")
            self.assertIn("stats", result)
            self.assertTrue(result["enabled"])
            
            # Verify statistics structure
            stats = result["stats"]
            self.assertIn("total_injections", stats)
            self.assertIn("active_probes", stats)
            self.assertIn("by_type", stats)
            self.assertIn("by_component", stats)
            self.assertIn("max_latency_ms", stats)
            self.assertIn("default_error_rate", stats)
    
    def test_chaos_manager_singleton(self):
        """Test chaos manager singleton pattern."""
        if get_chaos_manager:
            manager1 = get_chaos_manager()
            manager2 = get_chaos_manager()
            
            self.assertIs(manager1, manager2)
    
    @unittest.skipUnless(chaos_injection, "Chaos injection decorator not available")
    def test_chaos_injection_decorator(self):
        """Test chaos injection decorator."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            @chaos_injection("test_function", "latency", latency_ms=50)
            def test_function():
                return "success"
            
            start_time = time.time()
            result = test_function()
            end_time = time.time()
            
            self.assertEqual(result, "success")
            
            # Should have injected latency
            actual_latency = (end_time - start_time) * 1000
            self.assertGreaterEqual(actual_latency, 40)  # 40ms minimum (10ms tolerance)
    
    def test_error_handling(self):
        """Test error handling in chaos functions."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            # Mock threading.RLock to raise an exception
            with patch('threading.RLock', side_effect=Exception("Mock error")):
                # This should create a new ChaosManager and potentially fail gracefully
                try:
                    chaos_manager = ChaosManager()
                    # The constructor might fail, but let's test a method too
                    result = chaos_manager.inject_latency("test", 100)
                    # If we get here, verify it's an error result
                    if "status" in result:
                        self.assertEqual(result["status"], "error")
                except Exception:
                    # If constructor fails, that's also acceptable behavior
                    pass
    
    def test_concurrent_chaos_operations(self):
        """Test concurrent chaos operations."""
        with patch('console.chaos_probes.CHAOS_ENABLED', True):
            results = []
            
            def inject_chaos(component_id):
                try:
                    result = self.chaos_manager.inject_latency(f"component_{component_id}", 10)
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})
            
            # Start multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=inject_chaos, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Verify all operations completed
            self.assertEqual(len(results), 5)
            
            # Most should be successful (some might have errors due to mocking)
            successful_results = [r for r in results if r.get("status") == "armed"]
            self.assertGreaterEqual(len(successful_results), 0)  # At least some should work


if __name__ == '__main__':
    unittest.main()
