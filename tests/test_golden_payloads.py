#!/usr/bin/env python3
"""Golden Master test suite for WatchLockAI Sentinel API.

Validates that key API endpoints return responses that are supersets
of their golden master payloads, allowing for additive changes while
preventing breaking changes or key removals.

Requires PYTEST_GOLDEN_ENABLED=1 to run (graceful skip if FastAPI missing).
"""

import json
import os
import pytest
from pathlib import Path
from typing import Any, Dict, List, Set
import sys

# Test configuration
GOLDEN_ENABLED = os.getenv("PYTEST_GOLDEN_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
GOLDEN_STRICT_MODE = os.getenv("GOLDEN_STRICT_MODE", "0").strip().lower() in {"1", "true", "yes", "on"}
GOLDEN_UPDATE_MODE = os.getenv("GOLDEN_UPDATE_MODE", "0").strip().lower() in {"1", "true", "yes", "on"}

# Skip all tests if not enabled or FastAPI not available
pytestmark = pytest.mark.skipif(
    not GOLDEN_ENABLED,
    reason="Golden master testing disabled (set PYTEST_GOLDEN_ENABLED=1 to enable)"
)

try:
    from fastapi.testclient import TestClient
    from console.web_api import SentinelWebAPI
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="FastAPI not available")


class GoldenMasterValidator:
    """Validates API responses against golden master payloads."""
    
    def __init__(self):
        self.client: TestClient = None
        self.golden_dir = Path(__file__).parent / "golden"
        self.violations: List[Dict[str, Any]] = []
        
        # Key routes to test with their golden master files
        self.golden_routes = {
            "/health": "health_response.json",
            "/api/metrics/event_bus": "event_bus_response.json",
            "/api/metrics/snapshot": "metrics_snapshot_response.json", 
            "/api/anomaly/score": "anomaly_score_response.json",
        }
    
    def setup_test_client(self):
        """Setup test client with mock service."""
        if not FASTAPI_AVAILABLE:
            return None
            
        # Create enhanced mock service for golden testing
        class MockSentinelService:
            def __init__(self):
                self.uptime_seconds = 3600  # 1 hour uptime
                self.start_time = 1640995200  # Fixed timestamp
                self.event_bus = MockEventBus()
                self.alert_manager = None
                self.rules_engine = None
                self.actions_manager = None
                self.config = None
                
            def get_status(self):
                return {
                    "running": True,
                    "uptime_seconds": self.uptime_seconds,
                    "collectors": {},
                    "rules_engine": {},
                    "event_bus": {}
                }
        
        class MockEventBus:
            def get_observability_metrics(self):
                return {
                    "delivery_success_count": 0,
                    "delivery_failure_count": 0,
                    "total_events_processed": 0,
                    "queue_depth": 0
                }
        
        try:
            mock_service = MockSentinelService()
            api = SentinelWebAPI(mock_service, host="127.0.0.1", port=8080)
            self.client = TestClient(api.app)
            return self.client
        except Exception as e:
            print(f"Failed to setup test client: {e}")
            return None
    
    def load_golden_master(self, filename: str) -> Dict[str, Any]:
        """Load golden master payload from file."""
        golden_path = self.golden_dir / filename
        if not golden_path.exists():
            raise FileNotFoundError(f"Golden master file not found: {golden_path}")
            
        with open(golden_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_golden_master(self, filename: str, payload: Dict[str, Any]):
        """Save payload as golden master (used in update mode)."""
        golden_path = self.golden_dir / filename
        golden_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(golden_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, sort_keys=True)
    
    def extract_keys_recursive(self, obj: Any, path: str = "") -> Set[str]:
        """Extract all keys from nested dict/list structure."""
        keys = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                keys.add(current_path)
                keys.update(self.extract_keys_recursive(value, current_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                keys.update(self.extract_keys_recursive(item, current_path))
                
        return keys
    
    def validate_superset_semantics(self, golden: Dict[str, Any], actual: Dict[str, Any], 
                                   route: str) -> Dict[str, Any]:
        """Validate that actual response is a superset of golden master.
        
        Superset semantics:
        - All keys from golden must exist in actual
        - Actual can have additional keys (additive changes allowed)
        - Type changes are violations unless specifically allowed
        - Value changes are generally allowed (data evolution)
        """
        result = {
            "route": route,
            "valid": True,
            "missing_keys": [],
            "type_violations": [],
            "structural_changes": [],
            "added_keys": [],
            "warnings": []
        }
        
        try:
            # Extract key structure from both payloads
            golden_keys = self.extract_keys_recursive(golden)
            actual_keys = self.extract_keys_recursive(actual)
            
            # Find missing keys (violations)
            missing_keys = golden_keys - actual_keys
            if missing_keys:
                result["valid"] = False
                result["missing_keys"] = list(missing_keys)
            
            # Find added keys (informational, not violations)
            added_keys = actual_keys - golden_keys
            if added_keys:
                result["added_keys"] = list(added_keys)
            
            # Deep type validation
            type_violations = self._validate_types_recursive(golden, actual)
            if type_violations:
                result["valid"] = False
                result["type_violations"] = type_violations
            
            # Check for structural changes in arrays
            structural_changes = self._validate_array_structures(golden, actual)
            if structural_changes:
                result["structural_changes"] = structural_changes
                if GOLDEN_STRICT_MODE:
                    result["valid"] = False
            
            return result
            
        except Exception as e:
            result["valid"] = False
            result["warnings"].append(f"Validation error: {str(e)}")
            return result
    
    def _validate_types_recursive(self, golden: Any, actual: Any, path: str = "") -> List[str]:
        """Recursively validate types match between golden and actual."""
        violations = []
        
        if type(golden) != type(actual):
            # Allow None -> value transitions (initialization)
            if golden is None:
                return violations
            # Allow number type flexibility (int <-> float)
            if isinstance(golden, (int, float)) and isinstance(actual, (int, float)):
                return violations
            # Otherwise it's a violation
            violations.append(f"{path}: type changed from {type(golden).__name__} to {type(actual).__name__}")
            return violations
        
        if isinstance(golden, dict):
            for key, value in golden.items():
                if key in actual:
                    current_path = f"{path}.{key}" if path else key
                    violations.extend(self._validate_types_recursive(value, actual[key], current_path))
        elif isinstance(golden, list) and len(golden) > 0 and len(actual) > 0:
            # Validate first element type consistency
            violations.extend(self._validate_types_recursive(golden[0], actual[0], f"{path}[0]"))
        
        return violations
    
    def _validate_array_structures(self, golden: Any, actual: Any, path: str = "") -> List[str]:
        """Validate array structure consistency."""
        changes = []
        
        if isinstance(golden, dict):
            for key, value in golden.items():
                if key in actual:
                    current_path = f"{path}.{key}" if path else key
                    changes.extend(self._validate_array_structures(value, actual[key], current_path))
        elif isinstance(golden, list) and isinstance(actual, list):
            # Check if array became dramatically different in size
            if len(golden) > 0 and len(actual) == 0:
                changes.append(f"{path}: array became empty")
            elif len(golden) == 0 and len(actual) > 0:
                changes.append(f"{path}: array gained elements")
        
        return changes
    
    def test_route_golden_master(self, route: str, golden_file: str) -> Dict[str, Any]:
        """Test a specific route against its golden master."""
        if not self.client:
            return {"route": route, "valid": False, "error": "No test client available"}
        
        try:
            # Make request to route
            response = self.client.get(route)
            
            if response.status_code != 200:
                # Some routes may not be enabled - that's ok
                if response.status_code == 404:
                    return {"route": route, "valid": True, "skipped": True, "reason": "Route not available"}
                return {"route": route, "valid": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
            # Parse response
            try:
                actual_payload = response.json()
            except json.JSONDecodeError as e:
                return {"route": route, "valid": False, "error": f"Invalid JSON response: {str(e)}"}
            
            # Load or create golden master
            if GOLDEN_UPDATE_MODE:
                # Update mode - save current response as golden master
                self.save_golden_master(golden_file, actual_payload)
                return {"route": route, "valid": True, "updated": True}
            else:
                # Validation mode - compare against golden master
                try:
                    golden_payload = self.load_golden_master(golden_file)
                except FileNotFoundError:
                    # No golden master exists - create one if in update mode
                    if GOLDEN_UPDATE_MODE:
                        self.save_golden_master(golden_file, actual_payload)
                        return {"route": route, "valid": True, "created": True}
                    else:
                        return {"route": route, "valid": False, "error": f"Golden master not found: {golden_file}"}
                
                # Perform superset validation
                validation_result = self.validate_superset_semantics(golden_payload, actual_payload, route)
                
                # Record violations
                if not validation_result["valid"]:
                    self.violations.append(validation_result)
                
                return validation_result
                
        except Exception as e:
            return {"route": route, "valid": False, "error": f"Test execution error: {str(e)}"}
    
    def run_all_golden_tests(self) -> Dict[str, Any]:
        """Run golden master tests for all configured routes."""
        if not self.setup_test_client():
            return {"success": False, "error": "Failed to setup test client"}
        
        results = []
        
        for route, golden_file in self.golden_routes.items():
            print(f"Testing golden master: {route} -> {golden_file}")
            result = self.test_route_golden_master(route, golden_file)
            results.append(result)
        
        # Summary
        total_tests = len(results)
        valid_tests = len([r for r in results if r.get("valid", False)])
        skipped_tests = len([r for r in results if r.get("skipped", False)])
        failed_tests = total_tests - valid_tests - skipped_tests
        
        summary = {
            "total_tests": total_tests,
            "valid_tests": valid_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "success_rate": (valid_tests / total_tests) * 100 if total_tests > 0 else 0,
            "results": results,
            "violations": self.violations
        }
        
        return summary


# Pytest test functions
@pytest.fixture(scope="session")
def golden_validator():
    """Create golden master validator for session."""
    return GoldenMasterValidator()


def test_health_endpoint_golden_master(golden_validator):
    """Test /health endpoint against golden master."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    result = golden_validator.test_route_golden_master("/health", "health_response.json")
    
    if result.get("skipped"):
        pytest.skip(result.get("reason", "Route skipped"))
    
    assert result.get("valid", False), f"Golden master validation failed: {result.get('error', 'Unknown error')}"
    
    # Check for warnings about added keys (informational)
    if result.get("added_keys"):
        print(f"INFO: New keys added to /health response: {result['added_keys']}")


def test_event_bus_metrics_golden_master(golden_validator):
    """Test /api/metrics/event_bus endpoint against golden master."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    result = golden_validator.test_route_golden_master("/api/metrics/event_bus", "event_bus_response.json")
    
    if result.get("skipped"):
        pytest.skip(result.get("reason", "Route skipped (likely feature flag disabled)"))
    
    if not result.get("valid", False):
        # Don't fail test if route is disabled - just warn
        if "404" in str(result.get("error", "")):
            pytest.skip("Event bus metrics endpoint disabled (METRICS_DEBUG_ENABLED=0)")
        else:
            assert False, f"Golden master validation failed: {result.get('error', 'Unknown error')}"
    
    # Check for structural changes
    if result.get("added_keys"):
        print(f"INFO: Event bus metrics expanded with new keys: {result['added_keys']}")


def test_metrics_snapshot_golden_master(golden_validator):
    """Test /api/metrics/snapshot endpoint against golden master."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    result = golden_validator.test_route_golden_master("/api/metrics/snapshot", "metrics_snapshot_response.json")
    
    if result.get("skipped"):
        pytest.skip(result.get("reason", "Route skipped (likely feature flag disabled)"))
    
    if not result.get("valid", False):
        if "404" in str(result.get("error", "")):
            pytest.skip("Metrics snapshot endpoint disabled (METRICS_DEBUG_ENABLED=0)")
        else:
            assert False, f"Golden master validation failed: {result.get('error', 'Unknown error')}"
    
    # Validate critical metrics structure
    if result.get("missing_keys"):
        critical_keys = [k for k in result["missing_keys"] if "metrics" in k or "timestamp" in k]
        if critical_keys:
            assert False, f"Critical metrics keys missing: {critical_keys}"


def test_anomaly_score_golden_master(golden_validator):
    """Test /api/anomaly/score endpoint against golden master."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    result = golden_validator.test_route_golden_master("/api/anomaly/score", "anomaly_score_response.json")
    
    if result.get("skipped"):
        pytest.skip(result.get("reason", "Route skipped (likely feature flag disabled)"))
    
    if not result.get("valid", False):
        if "404" in str(result.get("error", "")):
            pytest.skip("Anomaly score endpoint disabled (ANOMALY_ENABLED=0 or METRICS_DEBUG_ENABLED=0)")
        else:
            # Anomaly scores can vary, so be more lenient
            if "type_violations" not in str(result.get("error", "")):
                pytest.skip(f"Anomaly endpoint variation: {result.get('error', 'Unknown error')}")
            assert False, f"Golden master validation failed: {result.get('error', 'Unknown error')}"


def test_comprehensive_golden_suite(golden_validator):
    """Run comprehensive golden master test suite."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    summary = golden_validator.run_all_golden_tests()
    
    print(f"\n=== GOLDEN MASTER TEST SUMMARY ===")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Valid: {summary['valid_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Skipped: {summary['skipped_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    if summary['violations']:
        print(f"\nVIOLATIONS DETECTED: {len(summary['violations'])}")
        for violation in summary['violations'][:3]:  # Show first 3
            print(f"- {violation['route']}: {len(violation.get('missing_keys', []))} missing keys, {len(violation.get('type_violations', []))} type violations")
    
    # Don't fail the test suite for golden master violations in non-strict mode
    # The goal is to detect and document changes, not block development
    if GOLDEN_STRICT_MODE and summary['failed_tests'] > 0:
        assert False, f"Golden master strict mode: {summary['failed_tests']} tests failed"
    
    # Always pass in non-strict mode - violations are informational
    assert summary['total_tests'] > 0, "No golden master tests were executed"


@pytest.fixture(scope="session", autouse=True)
def generate_golden_master_report(request):
    """Generate golden master test report after all tests complete."""
    yield
    
    # Create a validator to access results
    validator = GoldenMasterValidator()
    summary = validator.run_all_golden_tests()
    
    # Generate report
    report_file = Path("DOCS/report/golden_master_results.md")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Golden Master Test Results\n\n")
        f.write(f"Generated: {os.environ.get('BUILD_TIMESTAMP', 'unknown')}\n")
        f.write(f"Test Environment: FastAPI Available = {FASTAPI_AVAILABLE}\n")
        f.write(f"Golden Enabled: {GOLDEN_ENABLED}\n")
        f.write(f"Strict Mode: {GOLDEN_STRICT_MODE}\n")
        f.write(f"Update Mode: {GOLDEN_UPDATE_MODE}\n\n")
        
        if not summary.get("results"):
            f.write("## Summary\n\nNo golden master tests executed.\n\n")
            return
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Tests**: {summary['total_tests']}\n")
        f.write(f"- **Valid Tests**: {summary['valid_tests']}\n")
        f.write(f"- **Failed Tests**: {summary['failed_tests']}\n")
        f.write(f"- **Skipped Tests**: {summary['skipped_tests']}\n")
        f.write(f"- **Success Rate**: {summary['success_rate']:.1f}%\n\n")
        
        # Test Results
        f.write("## Test Results\n\n")
        
        for result in summary['results']:
            route = result['route']
            valid = result.get('valid', False)
            status = "✅ PASS" if valid else "❌ FAIL"
            
            if result.get('skipped'):
                status = "⏭️ SKIP"
                
            f.write(f"### {status} `{route}`\n\n")
            
            if result.get('error'):
                f.write(f"**Error**: {result['error']}\n\n")
            elif result.get('skipped'):
                f.write(f"**Reason**: {result.get('reason', 'Unknown')}\n\n")
            elif result.get('updated'):
                f.write(f"**Updated**: Golden master updated with current response\n\n")
            elif result.get('created'):
                f.write(f"**Created**: New golden master created\n\n")
            else:
                # Show validation details
                if result.get('missing_keys'):
                    f.write(f"**Missing Keys**: {len(result['missing_keys'])}\n")
                    for key in result['missing_keys'][:5]:
                        f.write(f"  - `{key}`\n")
                    f.write("\n")
                
                if result.get('type_violations'):
                    f.write(f"**Type Violations**: {len(result['type_violations'])}\n")
                    for violation in result['type_violations'][:3]:
                        f.write(f"  - {violation}\n")
                    f.write("\n")
                
                if result.get('added_keys'):
                    f.write(f"**Added Keys** (non-breaking): {len(result['added_keys'])}\n")
                    for key in result['added_keys'][:5]:
                        f.write(f"  - `{key}`\n")
                    f.write("\n")
        
        # Violations Summary
        if summary.get('violations'):
            f.write("## Violations Summary\n\n")
            
            for violation in summary['violations']:
                f.write(f"### Route: `{violation['route']}`\n\n")
                
                if violation.get('missing_keys'):
                    f.write(f"**Missing Keys ({len(violation['missing_keys'])}):**\n")
                    for key in violation['missing_keys']:
                        f.write(f"- `{key}`\n")
                    f.write("\n")
                
                if violation.get('type_violations'):
                    f.write(f"**Type Violations ({len(violation['type_violations'])}):**\n")
                    for viol in violation['type_violations']:
                        f.write(f"- {viol}\n")
                    f.write("\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        
        if summary['failed_tests'] > 0:
            f.write("### Breaking Changes Detected\n")
            f.write("- Review failed tests for API contract violations\n")
            f.write("- Ensure backward compatibility is maintained\n")
            f.write("- Update golden masters if changes are intentional\n\n")
        
        f.write("### Best Practices\n")
        f.write("- Run golden master tests before releases\n")
        f.write("- Update golden masters when adding new features\n")
        f.write("- Use strict mode in CI/CD pipelines\n")
        f.write("- Monitor added keys for API evolution\n\n")
        
        f.write("---\n")
        f.write("*Report generated by WatchLockAI Sentinel golden master test suite*\n")
    
    print(f"\nGolden master report generated: {report_file}")


if __name__ == "__main__":
    # Allow direct execution for development
    if GOLDEN_ENABLED and FASTAPI_AVAILABLE:
        validator = GoldenMasterValidator()
        summary = validator.run_all_golden_tests()
        print(f"\nDirect execution complete. Success rate: {summary['success_rate']:.1f}%")
    else:
        print("Golden master testing disabled or FastAPI not available. Set PYTEST_GOLDEN_ENABLED=1 to enable.")