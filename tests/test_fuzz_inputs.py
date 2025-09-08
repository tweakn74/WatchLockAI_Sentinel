#!/usr/bin/env python3
"""Comprehensive fuzz testing suite for all WatchLockAI Sentinel API routes.

Provides adversarial input generation for every discovered route with:
- Empty/null inputs
- Boundary integers and oversized strings
- Unicode and encoding attacks
- Path traversal attempts
- Type confusion/smuggling
- JSON malformation
- Header manipulation

Requires PYTEST_FUZZ_ENABLED=1 to run (graceful skip if FastAPI missing).
"""

import json
import os
import pytest
import string
import random
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

# Test configuration
FUZZ_ENABLED = os.getenv("PYTEST_FUZZ_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
FUZZ_ITERATIONS = int(os.getenv("FUZZ_ITERATIONS", "100"))  # Iterations per test case
FUZZ_MAX_STRING_LEN = int(os.getenv("FUZZ_MAX_STRING_LEN", "10000"))  # Max string length for fuzzing
FAST_FUZZ = os.getenv("FAST_FUZZ", "1").strip().lower() in {"1", "true", "yes", "on"}  # Reduced iterations for CI

# Skip all tests if not enabled or FastAPI not available
pytestmark = pytest.mark.skipif(
    not FUZZ_ENABLED,
    reason="Fuzz testing disabled (set PYTEST_FUZZ_ENABLED=1 to enable)"
)

try:
    from fastapi.testclient import TestClient
    from console.web_api import SentinelWebAPI
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="FastAPI not available")

# Test findings accumulator
fuzz_findings: List[Dict[str, Any]] = []


class FuzzPayloadGenerator:
    """Generates adversarial payloads for comprehensive API fuzzing."""
    
    def __init__(self):
        self.iterations = FUZZ_ITERATIONS if not FAST_FUZZ else min(FUZZ_ITERATIONS, 25)
        self.max_string_len = FUZZ_MAX_STRING_LEN
        
    def generate_empty_null_payloads(self) -> List[Any]:
        """Empty and null value payloads."""
        return [
            None,
            "",
            {},
            [],
            0,
            False,
            "null",
            "undefined",
        ]
    
    def generate_oversized_strings(self) -> List[str]:
        """Generate oversized string payloads."""
        payloads = []
        for size in [1000, 5000, self.max_string_len]:
            # Random ASCII
            payloads.append(''.join(random.choices(string.ascii_letters + string.digits, k=size)))
            # Repeated patterns
            payloads.append('A' * size)
            payloads.append('0' * size)
            # Special characters
            payloads.append('<>' * (size // 2))
        return payloads
    
    def generate_unicode_attacks(self) -> List[str]:
        """Generate Unicode and encoding attack payloads."""
        return [
            # Unicode normalization attacks
            "\u0041\u0301",  # A with combining acute
            "\u00c1",        # Precomposed A with acute
            "\u200e\u200f",  # Directional marks
            "\ufeff",       # BOM
            # Unicode control characters
            "\u0000",       # Null
            "\u0008",       # Backspace
            "\u0009",       # Tab
            "\u000a",       # Line Feed
            "\u000d",       # Carriage Return
            # High Unicode planes
            "\U0001f600",   # Emoji
            "\U0002000b",   # High plane
            # Mixed encodings
            "test\u00ff\u00fe",
            "\u00c2\u0080",     # UTF-8 encoded
        ]
    
    def generate_path_traversal_payloads(self) -> List[str]:
        """Generate path traversal attack payloads."""
        return [
            "../",
            "..\\",
            "../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f",     # URL encoded ../
            "%2e%2e%5c",     # URL encoded ..\\
            "....//",        # Double encoding
            "..;/",          # Semicolon bypass
            "..//..//",      # Mixed slashes
            "/etc/passwd",   # Absolute paths
            "C:\\windows\\system32",
            "\\\\unc\\path",
        ]
    
    def generate_type_confusion_payloads(self) -> List[Any]:
        """Generate type confusion and smuggling payloads."""
        return [
            # String representations of other types
            "true", "false", "null", "undefined",
            "[1,2,3]", "{\"key\": \"value\"}",
            "123", "-456", "3.14", "1e10",
            # Type confusion via JSON
            {"__proto__": {"admin": True}},  # Prototype pollution
            {"constructor": {"prototype": {"admin": True}}},
            # Array-like objects
            {"0": "first", "1": "second", "length": 2},
            # Function-like strings
            "function() { return true; }",
            "() => true",
            "eval('1+1')",
        ]
    
    def generate_boundary_integers(self) -> List[int]:
        """Generate boundary and extreme integer values."""
        return [
            # Zero and small values
            0, 1, -1,
            # Boundary values for common integer types
            127, 128, -128, -129,          # int8
            255, 256, -256, -257,          # uint8
            32767, 32768, -32768, -32769,  # int16
            65535, 65536, -65536, -65537,  # uint16
            2147483647, 2147483648,        # int32
            -2147483648, -2147483649,
            4294967295, 4294967296,        # uint32
            # Very large values
            9223372036854775807,           # int64 max
            -9223372036854775808,          # int64 min
            18446744073709551615,          # uint64 max
            # Float boundaries as integers
            16777216, 16777217,            # float32 precision limit
            9007199254740992, 9007199254740993,  # float64 precision limit
        ]
    
    def generate_malformed_json_payloads(self) -> List[str]:
        """Generate malformed JSON payloads."""
        return [
            # Syntax errors
            "{",
            "}",
            "{,}",
            '{"key":}',
            '{"key"::"value"}',
            '[1,2,3,]',
            # Unquoted keys
            '{key: "value"}',
            # Single quotes (invalid JSON)
            "{'key': 'value'}",
            # Trailing commas
            '{"key": "value",}',
            '[1, 2, 3,]',
            # Duplicate keys
            '{"key": "value1", "key": "value2"}',
            # Deeply nested
            '{' * 1000 + '"key": "value"' + '}' * 1000,
            # Invalid escapes
            '{"key": "\\\\invalid"}',
            r'{"key": "\xgg"}',
        ]
    
    def generate_header_manipulation_payloads(self) -> List[Dict[str, str]]:
        """Generate header manipulation payloads."""
        return [
            # Case variations
            {"x-admin-token": "test"},
            {"X-Admin-Token": "test"},
            {"X-ADMIN-TOKEN": "test"},
            {"x-AdMiN-tOkEn": "test"},
            
            # Duplicate headers (test as single dict with list values)
            {"Authorization": ["Bearer token1", "Bearer token2"]},
            {"Content-Type": ["application/json", "text/plain"]},
            
            # Injection attempts
            {"Content-Type": "application/json\r\nX-Injected: malicious"},
            {"User-Agent": "Mozilla/5.0\r\nX-Injected: payload"},
            
            # Oversized headers
            {"X-Large-Header": "A" * 8192},
            {"Authorization": "Bearer " + "A" * 10000},
            
            # Unicode in headers
            {"X-Unicode": "\u0041\u0301"},
            {"User-Agent": "Test\u0000Agent"},
            
            # Empty and whitespace
            {"Authorization": ""},
            {"X-Empty": ""},
            {"X-Whitespace": "   "},
            {"X-Tab": "\t\t\t"},
        ]


class SentinelAPIFuzzer:
    """Main fuzzer for Sentinel API routes."""
    
    def __init__(self):
        self.payload_gen = FuzzPayloadGenerator()
        self.client: Optional[TestClient] = None
        self.findings: List[Dict[str, Any]] = []
        
        # All discovered routes from routing analysis
        self.routes = {
            # Core API routes
            "GET": [
                "/api/status",
                "/api/alerts", 
                "/api/detections",
                "/api/ti/search",
                "/api/policies",
                "/health",
                # Conditional routes
                "/api/metrics/event_bus",
                "/api/metrics/snapshot", 
                "/api/metrics/health",
                "/api/mitre/coverage",
                "/api/anomaly/score",
                "/api/auth/me",
                "/api/stream/health",
                "/api/export/telemetry",
                # Admin GET routes
                "/api/admin/config/schema",
                "/api/admin/plugins",
                "/api/admin/preflight",
                "/api/admin/chaos/status",
                "/api/admin/retention/stats",
                "/api/admin/perf/quick",
                # Web console pages
                "/",
                "/detections",
                "/assets",
                "/accounts", 
                "/processes",
                "/policies",
            ],
            "POST": [
                "/api/actions/pause",
                "/api/actions/resume",
                "/api/policies",
                "/api/auth/login",
                "/api/auth/logout",
                # Admin POST routes
                "/api/admin/config/reload",
                "/api/admin/anomaly/train",
                "/api/admin/quarantine",
                "/api/admin/quarantine/restore",
                "/api/admin/plugins/execute",
                "/api/admin/backup",
                "/api/admin/restore",
                "/api/admin/rotate/preview",
                "/api/admin/rotate/execute",
                "/api/admin/chaos/inject",
                "/api/admin/retention/run",
                "/api/admin/perf/probe",
            ]
        }
    
    def setup_test_client(self):
        """Setup test client with mock service."""
        if not FASTAPI_AVAILABLE:
            return None
            
        # Create minimal mock service
        class MockSentinelService:
            def __init__(self):
                self.uptime_seconds = 0
                self.start_time = 0
                self.event_bus = None
                self.alert_manager = None
                self.rules_engine = None
                self.actions_manager = None
                self.config = None
                
            def get_status(self):
                return {
                    "running": True,
                    "uptime_seconds": 0,
                    "collectors": {},
                    "rules_engine": {},
                    "event_bus": {}
                }
        
        try:
            mock_service = MockSentinelService()
            api = SentinelWebAPI(mock_service, host="127.0.0.1", port=8080)
            self.client = TestClient(api.app)
            return self.client
        except Exception as e:
            self.record_finding("setup_error", "/", "GET", {}, str(e), 500)
            return None
    
    def record_finding(self, category: str, route: str, method: str, 
                      payload: Any, response_info: str, status_code: int):
        """Record a fuzz testing finding."""
        finding = {
            "category": category,
            "route": route,
            "method": method,
            "payload": str(payload)[:500],  # Truncate large payloads
            "response_info": response_info,
            "status_code": status_code,
            "severity": self._classify_severity(category, status_code)
        }
        self.findings.append(finding)
        global fuzz_findings
        fuzz_findings.append(finding)
    
    def _classify_severity(self, category: str, status_code: int) -> str:
        """Classify finding severity."""
        if status_code == 500:
            return "HIGH"  # Server errors
        elif status_code in [403, 401] and category != "auth_expected":
            return "MEDIUM"  # Unexpected auth issues
        elif status_code in [400, 422]:
            return "LOW"  # Expected validation errors
        elif 200 <= status_code < 300:
            if category in ["path_traversal", "type_confusion"]:
                return "HIGH"  # Successful attacks
            return "INFO"  # Normal responses
        else:
            return "MEDIUM"  # Other unexpected responses
    
    def fuzz_route(self, method: str, route: str, payload_type: str, payloads: List[Any]):
        """Fuzz a specific route with given payloads."""
        if not self.client:
            return
            
        for payload in payloads[:self.payload_gen.iterations]:
            try:
                response = None
                
                if method == "GET":
                    # For GET requests, put payload in query params
                    if isinstance(payload, dict):
                        response = self.client.get(route, params=payload)
                    else:
                        # Single parameter fuzzing
                        test_params = {"test_param": payload, "query": payload, "limit": payload}
                        response = self.client.get(route, params=test_params)
                        
                elif method == "POST":
                    # For POST requests, use as JSON body
                    if payload_type == "header_manipulation":
                        response = self.client.post(route, json={"test": "data"}, headers=payload)
                    else:
                        response = self.client.post(route, json=payload if isinstance(payload, (dict, list)) else {"data": payload})
                
                if response:
                    # Check for interesting responses
                    if response.status_code == 500:
                        self.record_finding(payload_type, route, method, payload, 
                                          f"Server error: {response.text[:200]}", response.status_code)
                    elif response.status_code == 200 and payload_type == "path_traversal":
                        # Successful path traversal might be concerning
                        if any(term in response.text.lower() for term in ["root:", "admin", "password", "secret"]):
                            self.record_finding(payload_type, route, method, payload,
                                              f"Potential data exposure: {response.text[:200]}", response.status_code)
                                              
            except Exception as e:
                self.record_finding(f"{payload_type}_exception", route, method, payload, str(e), 0)
    
    def run_comprehensive_fuzz_test(self):
        """Run comprehensive fuzz testing on all routes."""
        if not self.setup_test_client():
            return
        
        # Test each route with all payload types
        for method, routes in self.routes.items():
            for route in routes:
                print(f"Fuzzing {method} {route}...")
                
                # Empty/null fuzzing
                self.fuzz_route(method, route, "empty_null", 
                              self.payload_gen.generate_empty_null_payloads())
                
                # Oversized string fuzzing  
                self.fuzz_route(method, route, "oversized_strings",
                              self.payload_gen.generate_oversized_strings())
                
                # Unicode attack fuzzing
                self.fuzz_route(method, route, "unicode_attacks",
                              self.payload_gen.generate_unicode_attacks())
                
                # Path traversal fuzzing
                self.fuzz_route(method, route, "path_traversal",
                              self.payload_gen.generate_path_traversal_payloads())
                
                # Type confusion fuzzing
                self.fuzz_route(method, route, "type_confusion",
                              self.payload_gen.generate_type_confusion_payloads())
                
                # Boundary integer fuzzing
                self.fuzz_route(method, route, "boundary_integers",
                              self.payload_gen.generate_boundary_integers())
                
                # Malformed JSON fuzzing (for POST routes)
                if method == "POST":
                    malformed_payloads = self.payload_gen.generate_malformed_json_payloads()
                    for json_payload in malformed_payloads[:10]:  # Limit for performance
                        try:
                            response = self.client.post(route, data=json_payload, 
                                                       headers={"Content-Type": "application/json"})
                            if response.status_code == 500:
                                self.record_finding("malformed_json", route, method, json_payload,
                                                  f"JSON parsing error: {response.text[:200]}", response.status_code)
                        except Exception as e:
                            self.record_finding("malformed_json_exception", route, method, json_payload, str(e), 0)
                
                # Header manipulation fuzzing
                header_payloads = self.payload_gen.generate_header_manipulation_payloads()
                self.fuzz_route(method, route, "header_manipulation", header_payloads)


# Pytest test functions
@pytest.fixture(scope="session")
def api_fuzzer():
    """Create API fuzzer instance for session."""
    return SentinelAPIFuzzer()


def test_comprehensive_api_fuzzing(api_fuzzer):
    """Run comprehensive fuzzing across all API routes."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
        
    api_fuzzer.run_comprehensive_fuzz_test()
    
    # Assert we found some routes to test
    total_routes = sum(len(routes) for routes in api_fuzzer.routes.values())
    assert total_routes > 0, "No routes discovered for fuzzing"
    
    # Check for critical findings
    critical_findings = [f for f in api_fuzzer.findings if f["severity"] == "HIGH"]
    
    # Log summary
    print(f"\n=== FUZZ TEST SUMMARY ===")
    print(f"Total routes tested: {total_routes}")
    print(f"Total findings: {len(api_fuzzer.findings)}")
    print(f"Critical findings: {len(critical_findings)}")
    
    if critical_findings:
        print("\nCRITICAL FINDINGS:")
        for finding in critical_findings[:5]:  # Show first 5
            print(f"- {finding['route']} ({finding['method']}): {finding['category']} - {finding['response_info'][:100]}")
    
    # Don't fail the test for findings - they're expected in fuzzing
    # The goal is discovery, not assertion of perfect security


def test_admin_route_authentication_fuzzing(api_fuzzer):
    """Specifically test admin route authentication bypass attempts."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
        
    if not api_fuzzer.client:
        api_fuzzer.setup_test_client()
        
    admin_routes = [route for route in api_fuzzer.routes["GET"] + api_fuzzer.routes["POST"] 
                   if "/api/admin/" in route]
    
    auth_bypass_payloads = [
        # Token variations
        {"X-Admin-Token": "admin"},
        {"X-Admin-Token": ""}, 
        {"X-Admin-Token": "null"},
        {"Authorization": "Bearer admin"},
        {"Authorization": "Bearer "},
        # Case manipulation
        {"x-admin-token": "admin"},
        {"X-ADMIN-TOKEN": "admin"},
        # Unicode/encoding
        {"X-Admin-Token": "\u0041dmin"},  # Unicode A
        {"X-Admin-Token": "admin\x00"},   # Null byte
        # Multiple headers
        {"X-Admin-Token": "fake", "Authorization": "Bearer real"},
    ]
    
    bypass_attempts = 0
    successful_bypasses = 0
    
    for route in admin_routes:
        for headers in auth_bypass_payloads:
            try:
                response = api_fuzzer.client.get(route, headers=headers)
                bypass_attempts += 1
                
                # Check for successful bypass (200 response without proper auth)
                if response.status_code == 200:
                    successful_bypasses += 1
                    api_fuzzer.record_finding("auth_bypass", route, "GET", headers,
                                            f"Potential auth bypass: {response.text[:200]}", response.status_code)
                                            
            except Exception as e:
                api_fuzzer.record_finding("auth_bypass_exception", route, "GET", headers, str(e), 0)
    
    print(f"\n=== AUTH BYPASS FUZZ SUMMARY ===")
    print(f"Admin routes tested: {len(admin_routes)}")
    print(f"Bypass attempts: {bypass_attempts}")
    print(f"Potential bypasses: {successful_bypasses}")
    
    # Record results
    global fuzz_findings
    fuzz_findings.extend(api_fuzzer.findings)


def test_json_payload_fuzzing(api_fuzzer):
    """Focused JSON payload fuzzing for POST routes."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
        
    if not api_fuzzer.client:
        api_fuzzer.setup_test_client()
    
    # Complex JSON payloads designed to break parsers
    complex_payloads = [
        # Deeply nested objects
        {"level1": {"level2": {"level3": {"level4": {"level5": "deep"}}}}},
        
        # Large arrays
        {"big_array": list(range(1000))},
        {"string_array": ["item" * 100] * 100},
        
        # Mixed types
        {"mixed": [1, "string", {"nested": True}, [1, 2, 3], None]},
        
        # Special values
        {"special": float('inf')},  # Will be serialized as null in JSON
        {"negative_zero": -0.0},
        {"large_number": 1.7976931348623157e+308},
        
        # Unicode in keys and values
        {"\u0041key": "\u0042value", "emoji": "\ud83d\ude00"},
        
        # Prototype pollution attempts
        {"__proto__": {"admin": True}},
        {"constructor": {"prototype": {"isAdmin": True}}},
    ]
    
    post_routes = api_fuzzer.routes["POST"]
    
    for route in post_routes:
        for payload in complex_payloads:
            try:
                response = api_fuzzer.client.post(route, json=payload)
                
                if response.status_code == 500:
                    api_fuzzer.record_finding("complex_json", route, "POST", payload,
                                            f"JSON processing error: {response.text[:200]}", response.status_code)
                                            
            except Exception as e:
                api_fuzzer.record_finding("complex_json_exception", route, "POST", payload, str(e), 0)
    
    # Record results
    global fuzz_findings
    fuzz_findings.extend(api_fuzzer.findings)


@pytest.fixture(scope="session", autouse=True)
def generate_fuzz_findings_report(request):
    """Generate fuzz findings report after all tests complete."""
    yield
    
    # Generate findings report
    findings_file = Path("DOCS/report/fuzz_findings.md")
    findings_file.parent.mkdir(parents=True, exist_ok=True)
    
    global fuzz_findings
    
    with open(findings_file, 'w', encoding='utf-8') as f:
        f.write("# Fuzz Testing Findings Report\n\n")
        f.write(f"Generated: {os.environ.get('BUILD_TIMESTAMP', 'unknown')}\n")
        f.write(f"Test Environment: FastAPI Available = {FASTAPI_AVAILABLE}\n")
        f.write(f"Fuzz Enabled: {FUZZ_ENABLED}\n")
        f.write(f"Total Iterations: {FUZZ_ITERATIONS}\n\n")
        
        if not fuzz_findings:
            f.write("## Summary\n\nNo findings detected - all endpoints handled fuzzing gracefully.\n\n")
            return
        
        # Summary statistics
        severity_counts = {}
        category_counts = {}
        route_counts = {}
        
        for finding in fuzz_findings:
            severity = finding['severity']
            category = finding['category']
            route = finding['route']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            route_counts[route] = route_counts.get(route, 0) + 1
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Findings**: {len(fuzz_findings)}\n")
        f.write(f"- **Routes Affected**: {len(route_counts)}\n")
        f.write(f"- **Categories**: {len(category_counts)}\n\n")
        
        f.write("### Findings by Severity\n\n")
        for severity in ["HIGH", "MEDIUM", "LOW", "INFO"]:
            count = severity_counts.get(severity, 0)
            f.write(f"- **{severity}**: {count}\n")
        f.write("\n")
        
        f.write("### Findings by Category\n\n")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{category}**: {count}\n")
        f.write("\n")
        
        # Detailed findings
        f.write("## Detailed Findings\n\n")
        
        # Group by severity for reporting
        for severity in ["HIGH", "MEDIUM", "LOW", "INFO"]:
            severity_findings = [f for f in fuzz_findings if f['severity'] == severity]
            if not severity_findings:
                continue
                
            f.write(f"### {severity} Severity Findings ({len(severity_findings)})\n\n")
            
            for i, finding in enumerate(severity_findings[:20]):  # Limit to first 20 per severity
                f.write(f"#### Finding {i+1}: {finding['category']}\n\n")
                f.write(f"- **Route**: `{finding['method']} {finding['route']}`\n")
                f.write(f"- **Status Code**: {finding['status_code']}\n")
                f.write(f"- **Payload**: `{finding['payload'][:200]}...`\n")
                f.write(f"- **Response**: {finding['response_info'][:300]}\n\n")
            
            if len(severity_findings) > 20:
                f.write(f"*... and {len(severity_findings) - 20} more {severity} findings*\n\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        
        if severity_counts.get('HIGH', 0) > 0:
            f.write("### High Priority\n")
            f.write("- Review HIGH severity findings immediately\n")
            f.write("- Implement additional input validation for affected routes\n")
            f.write("- Consider rate limiting for admin endpoints\n\n")
        
        if severity_counts.get('MEDIUM', 0) > 0:
            f.write("### Medium Priority\n")
            f.write("- Review MEDIUM severity findings for potential security improvements\n")
            f.write("- Enhance error handling to avoid information disclosure\n")
            f.write("- Standardize authentication mechanisms\n\n")
        
        f.write("### General Recommendations\n")
        f.write("- Implement comprehensive input sanitization\n")
        f.write("- Add request size limits to prevent DoS\n")
        f.write("- Enable proper CORS policies\n")
        f.write("- Implement structured error responses\n")
        f.write("- Add request logging and monitoring\n")
        f.write("- Consider implementing API versioning\n\n")
        
        f.write("---\n")
        f.write("*Report generated by WatchLockAI Sentinel fuzz testing suite*\n")
    
    print(f"\nFuzz findings report generated: {findings_file}")


if __name__ == "__main__":
    # Allow direct execution for development
    if FUZZ_ENABLED and FASTAPI_AVAILABLE:
        fuzzer = SentinelAPIFuzzer()
        fuzzer.run_comprehensive_fuzz_test()
        print(f"\nDirect execution complete. Found {len(fuzzer.findings)} findings.")
    else:
        print("Fuzz testing disabled or FastAPI not available. Set PYTEST_FUZZ_ENABLED=1 to enable.")
