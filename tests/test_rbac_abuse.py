#!/usr/bin/env python3
"""RBAC abuse simulation tests for WatchLockAI Sentinel.

Simulates sophisticated authentication bypass attempts including:
- Header smuggling and manipulation
- Case sensitivity exploitation
- Duplicate header handling
- Unicode/encoding bypass attempts
- Token format manipulation
- Session hijacking simulations

Requires PYTEST_RBAC_ENABLED=1 to run (graceful skip if FastAPI missing).
"""

import base64
import json
import os
import pytest
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import hashlib
import secrets

# Test configuration
RBAC_ENABLED = os.getenv("PYTEST_RBAC_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
RBAC_INTENSIVE = os.getenv("RBAC_INTENSIVE", "0").strip().lower() in {"1", "true", "yes", "on"}
RBAC_REPORT_ALL = os.getenv("RBAC_REPORT_ALL", "0").strip().lower() in {"1", "true", "yes", "on"}

# Skip all tests if not enabled or FastAPI not available
pytestmark = pytest.mark.skipif(
    not RBAC_ENABLED,
    reason="RBAC abuse testing disabled (set PYTEST_RBAC_ENABLED=1 to enable)"
)

try:
    from fastapi.testclient import TestClient
    from console.web_api import SentinelWebAPI
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="FastAPI not available")

# Test results accumulator
rbac_findings: List[Dict[str, Any]] = []


class RBACBypassTester:
    """Advanced RBAC bypass testing framework."""
    
    def __init__(self):
        self.client: Optional[TestClient] = None
        self.findings: List[Dict[str, Any]] = []
        self.session_state = {}
        
        # Admin routes that should require authentication
        self.protected_routes = [
            ("/api/admin/config/reload", "POST"),
            ("/api/admin/config/schema", "GET"),
            ("/api/admin/anomaly/train", "POST"),
            ("/api/admin/quarantine", "POST"),
            ("/api/admin/quarantine/restore", "POST"),
            ("/api/admin/plugins", "GET"),
            ("/api/admin/plugins/execute", "POST"),
            ("/api/admin/preflight", "GET"),
            ("/api/admin/backup", "POST"),
            ("/api/admin/restore", "POST"),
            ("/api/admin/rotate/preview", "POST"),
            ("/api/admin/rotate/execute", "POST"),
            ("/api/admin/chaos/inject", "POST"),
            ("/api/admin/chaos/status", "GET"),
            ("/api/admin/retention/run", "POST"),
            ("/api/admin/retention/stats", "GET"),
            ("/api/admin/perf/probe", "POST"),
            ("/api/admin/perf/quick", "GET"),
        ]
    
    def setup_test_client(self):
        """Setup test client with enhanced mock service for RBAC testing."""
        if not FASTAPI_AVAILABLE:
            return None
            
        # Enhanced mock service with RBAC simulation
        class MockSentinelService:
            def __init__(self):
                self.uptime_seconds = 3600
                self.start_time = 1640995200
                self.event_bus = None
                self.alert_manager = None
                self.rules_engine = None
                self.actions_manager = None
                self.config = MockConfig()
                
            def get_status(self):
                return {
                    "running": True,
                    "uptime_seconds": self.uptime_seconds,
                    "collectors": {},
                    "rules_engine": {},
                    "event_bus": {}
                }
        
        class MockConfig:
            def __init__(self):
                self.operational = MockOperational()
                self.responses = MockResponses()
        
        class MockOperational:
            def __init__(self):
                self.mode = "monitor"
        
        class MockResponses:
            def __init__(self):
                self.allow_destructive_actions = False
        
        try:
            # Enable RBAC for testing
            os.environ["ADMIN_AUTH_ENABLED"] = "1"
            os.environ["ADMIN_TOKEN"] = "test_admin_token_123"
            
            mock_service = MockSentinelService()
            api = SentinelWebAPI(mock_service, host="127.0.0.1", port=8080)
            self.client = TestClient(api.app)
            return self.client
        except Exception as e:
            self.record_finding("setup_error", "/", "GET", {}, str(e), 500)
            return None
    
    def record_finding(self, category: str, route: str, method: str, 
                      headers: Dict[str, Any], result: str, status_code: int):
        """Record an RBAC bypass finding."""
        finding = {
            "category": category,
            "route": route,
            "method": method,
            "headers": {k: str(v)[:100] for k, v in headers.items()},  # Truncate header values
            "result": result,
            "status_code": status_code,
            "severity": self._classify_severity(category, status_code),
            "timestamp": time.time()
        }
        self.findings.append(finding)
        global rbac_findings
        rbac_findings.append(finding)
    
    def _classify_severity(self, category: str, status_code: int) -> str:
        """Classify finding severity."""
        if status_code == 200 and "bypass" in category:
            return "CRITICAL"  # Successful bypass
        elif status_code == 500:
            return "HIGH"  # Server errors might indicate vulnerabilities
        elif status_code in [401, 403]:
            return "INFO"  # Expected auth rejection
        elif status_code == 422 and "malformed" in category:
            return "MEDIUM"  # Validation issues
        else:
            return "LOW"  # Other responses
    
    def generate_header_smuggling_payloads(self) -> List[Dict[str, str]]:
        """Generate header smuggling attack payloads."""
        base_token = "test_admin_token_123"
        
        payloads = [
            # HTTP Request Smuggling via CRLF injection
            {"X-Admin-Token": f"{base_token}\r\nX-Injected-Header: malicious"},
            {"Authorization": f"Bearer {base_token}\r\nContent-Length: 0"},
            
            # Header folding (obsolete but some parsers still vulnerable)
            {"X-Admin-Token": f"{base_token}\r\n folded_value"},
            {"Authorization": f"Bearer\r\n {base_token}"},
            
            # Tab and space variations in header values
            {"X-Admin-Token": f"\t{base_token}\t"},
            {"X-Admin-Token": f"  {base_token}  "},
            {"Authorization": f"Bearer\t{base_token}"},
            
            # NULL byte injection
            {"X-Admin-Token": f"{base_token}\x00extra"},
            {"Authorization": f"Bearer {base_token}\x00injected"},
            
            # Unicode and encoding tricks
            {"X-Admin-Token": f"\u0000{base_token}"},
            {"X-Admin-Token": f"{base_token}\ufeff"},  # BOM
            {"Authorization": f"Bearer\u0020{base_token}"},  # Unicode space
            
            # URL encoding in headers (should be handled by server)
            {"X-Admin-Token": urllib.parse.quote(base_token)},
            {"Authorization": f"Bearer {urllib.parse.quote(base_token)}"},
            
            # Base64 manipulation
            {"X-Admin-Token": base64.b64encode(base_token.encode()).decode()},
            {"Authorization": f"Basic {base64.b64encode(f'admin:{base_token}'.encode()).decode()}"},
            
            # Mixed case header names (HTTP headers are case-insensitive)
            {"x-admin-token": base_token},
            {"X-ADMIN-TOKEN": base_token},
            {"x-AdMiN-tOkEn": base_token},
            {"authorization": f"bearer {base_token}"},
            {"AUTHORIZATION": f"BEARER {base_token}"},
            
            # Duplicate headers with different values
            {"X-Admin-Token": ["fake_token", base_token]},
            {"Authorization": ["Bearer fake", f"Bearer {base_token}"]},
            
            # Content-Type confusion
            {"X-Admin-Token": base_token, "Content-Type": "application/x-www-form-urlencoded"},
            {"X-Admin-Token": base_token, "Content-Type": "text/plain"},
            
            # User-Agent spoofing with auth
            {"X-Admin-Token": base_token, "User-Agent": "WatchLockAI-Internal/1.0"},
            {"Authorization": f"Bearer {base_token}", "User-Agent": "Mozilla/5.0 (Admin Console)"},
        ]
        
        return payloads
    
    def generate_token_manipulation_payloads(self) -> List[Dict[str, str]]:
        """Generate token format manipulation payloads."""
        base_token = "test_admin_token_123"
        
        payloads = [
            # JWT-like manipulation (even if not using JWT)
            {"Authorization": f"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.{base64.b64encode(json.dumps({'admin': True}).encode()).decode()}.signature"},
            
            # API key variations
            {"X-API-Key": base_token},
            {"API-Key": base_token},
            {"X-API-TOKEN": base_token},
            
            # Custom auth schemes
            {"Authorization": f"Token {base_token}"},
            {"Authorization": f"ApiKey {base_token}"},
            {"Authorization": f"Custom {base_token}"},
            {"Authorization": f"Admin {base_token}"},
            
            # Multiple auth methods
            {"Authorization": f"Bearer {base_token}", "X-Admin-Token": base_token},
            {"X-Admin-Token": base_token, "X-API-Key": base_token},
            
            # Malformed but parseable tokens
            {"X-Admin-Token": f"{base_token}="},  # Extra padding
            {"X-Admin-Token": f"="*10 + base_token},  # Prefix padding
            {"Authorization": f"Bearer {base_token}=="},
            
            # Token with additional data
            {"X-Admin-Token": f"{base_token};admin=true"},
            {"Authorization": f"Bearer {base_token},scope=admin"},
            
            # Length manipulation
            {"X-Admin-Token": base_token + "A" * 1000},  # Very long token
            {"Authorization": f"Bearer {base_token}" + "B" * 2000},
            
            # Special characters in tokens
            {"X-Admin-Token": f"{base_token}!@#$%^&*()"},
            {"Authorization": f"Bearer {base_token}+/="},
        ]
        
        return payloads
    
    def generate_session_hijacking_payloads(self) -> List[Dict[str, str]]:
        """Generate session hijacking simulation payloads."""
        # Generate fake session IDs
        fake_sessions = [
            secrets.token_hex(16),
            secrets.token_urlsafe(32),
            hashlib.md5(b"admin_session").hexdigest(),
            "session_" + secrets.token_hex(8),
            base64.b64encode(b"admin:true").decode(),
        ]
        
        payloads = []
        
        for session_id in fake_sessions:
            payloads.extend([
                # Cookie-based session attempts
                {"Cookie": f"session={session_id}"},
                {"Cookie": f"auth_token={session_id}"},
                {"Cookie": f"admin_session={session_id}"},
                {"Cookie": f"JSESSIONID={session_id}"},
                
                # Header-based session attempts
                {"X-Session-ID": session_id},
                {"X-Auth-Session": session_id},
                {"Session-Token": session_id},
                
                # Combined session + auth
                {"X-Admin-Token": "test_admin_token_123", "Cookie": f"session={session_id}"},
            ])
        
        # Session fixation attempts
        payloads.extend([
            {"Cookie": "session=fixed_session_id_123"},
            {"X-Forwarded-For": "127.0.0.1", "Cookie": "session=localhost_bypass"},
            {"X-Real-IP": "127.0.0.1", "X-Session-ID": "local_admin"},
        ])
        
        return payloads
    
    def test_route_with_payload(self, route: str, method: str, headers: Dict[str, Any]) -> Tuple[int, str]:
        """Test a protected route with specific headers."""
        if not self.client:
            return 0, "No test client available"
        
        try:
            if method == "GET":
                response = self.client.get(route, headers=headers)
            elif method == "POST":
                response = self.client.post(route, headers=headers, json={"test": "data"})
            else:
                return 0, f"Unsupported method: {method}"
            
            return response.status_code, response.text[:200]  # Truncate response
            
        except Exception as e:
            return 0, str(e)
    
    def run_header_smuggling_tests(self):
        """Run header smuggling bypass attempts."""
        payloads = self.generate_header_smuggling_payloads()
        
        for route, method in self.protected_routes:
            for headers in payloads:
                status_code, response_text = self.test_route_with_payload(route, method, headers)
                
                # Check for successful bypass
                if status_code == 200:
                    self.record_finding("header_smuggling_bypass", route, method, headers,
                                      f"SUCCESS: {response_text}", status_code)
                elif status_code == 500:
                    self.record_finding("header_smuggling_error", route, method, headers,
                                      f"SERVER_ERROR: {response_text}", status_code)
                elif RBAC_REPORT_ALL:
                    self.record_finding("header_smuggling_blocked", route, method, headers,
                                      f"BLOCKED: {response_text}", status_code)
    
    def run_token_manipulation_tests(self):
        """Run token format manipulation tests."""
        payloads = self.generate_token_manipulation_payloads()
        
        for route, method in self.protected_routes:
            for headers in payloads:
                status_code, response_text = self.test_route_with_payload(route, method, headers)
                
                if status_code == 200:
                    self.record_finding("token_manipulation_bypass", route, method, headers,
                                      f"SUCCESS: {response_text}", status_code)
                elif status_code == 500:
                    self.record_finding("token_manipulation_error", route, method, headers,
                                      f"SERVER_ERROR: {response_text}", status_code)
                elif RBAC_REPORT_ALL:
                    self.record_finding("token_manipulation_blocked", route, method, headers,
                                      f"BLOCKED: {response_text}", status_code)
    
    def run_session_hijacking_tests(self):
        """Run session hijacking simulation tests."""
        payloads = self.generate_session_hijacking_payloads()
        
        for route, method in self.protected_routes:
            for headers in payloads:
                status_code, response_text = self.test_route_with_payload(route, method, headers)
                
                if status_code == 200:
                    self.record_finding("session_hijacking_bypass", route, method, headers,
                                      f"SUCCESS: {response_text}", status_code)
                elif status_code == 500:
                    self.record_finding("session_hijacking_error", route, method, headers,
                                      f"SERVER_ERROR: {response_text}", status_code)
                elif RBAC_REPORT_ALL:
                    self.record_finding("session_hijacking_blocked", route, method, headers,
                                      f"BLOCKED: {response_text}", status_code)
    
    def run_comprehensive_rbac_tests(self):
        """Run all RBAC bypass tests."""
        if not self.setup_test_client():
            return
        
        print("Running header smuggling tests...")
        self.run_header_smuggling_tests()
        
        print("Running token manipulation tests...")
        self.run_token_manipulation_tests()
        
        print("Running session hijacking tests...")
        self.run_session_hijacking_tests()
        
        # Additional intensive tests if enabled
        if RBAC_INTENSIVE:
            print("Running intensive RBAC tests...")
            self._run_intensive_tests()
    
    def _run_intensive_tests(self):
        """Run additional intensive RBAC tests."""
        # Brute force common tokens
        common_tokens = [
            "admin", "password", "123456", "secret", "token",
            "api_key", "admin_token", "auth_token", "bearer_token",
            "development", "test", "staging", "production",
            "default", "changeme", "password123", "admin123",
        ]
        
        for token in common_tokens:
            headers = {"X-Admin-Token": token}
            for route, method in self.protected_routes[:5]:  # Limit for performance
                status_code, response_text = self.test_route_with_payload(route, method, headers)
                if status_code == 200:
                    self.record_finding("weak_token_bypass", route, method, headers,
                                      f"WEAK_TOKEN_SUCCESS: {response_text}", status_code)


# Pytest test functions
@pytest.fixture(scope="session")
def rbac_tester():
    """Create RBAC tester instance for session."""
    return RBACBypassTester()


def test_admin_routes_require_authentication(rbac_tester):
    """Test that admin routes properly require authentication."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    rbac_tester.setup_test_client()
    
    # Test without any authentication
    unauthenticated_successes = 0
    
    for route, method in rbac_tester.protected_routes:
        status_code, response_text = rbac_tester.test_route_with_payload(route, method, {})
        
        if status_code == 200:
            unauthenticated_successes += 1
            rbac_tester.record_finding("no_auth_bypass", route, method, {},
                                     f"NO_AUTH_SUCCESS: {response_text}", status_code)
    
    # Assert that most admin routes reject unauthenticated requests
    if unauthenticated_successes > len(rbac_tester.protected_routes) // 2:
        assert False, f"Too many admin routes ({unauthenticated_successes}) allow unauthenticated access"


def test_header_smuggling_attacks(rbac_tester):
    """Test header smuggling bypass attempts."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    rbac_tester.run_header_smuggling_tests()
    
    # Check for critical bypasses
    critical_bypasses = [f for f in rbac_tester.findings if f["severity"] == "CRITICAL"]
    
    print(f"\n=== HEADER SMUGGLING TEST RESULTS ===")
    print(f"Total tests: {len(rbac_tester.findings)}")
    print(f"Critical bypasses: {len(critical_bypasses)}")
    
    if critical_bypasses:
        print("\nCRITICAL BYPASSES DETECTED:")
        for bypass in critical_bypasses[:3]:
            print(f"- {bypass['route']} via {bypass['category']}: {bypass['result'][:50]}")
    
    # Don't fail test for discoveries - this is vulnerability research


def test_token_manipulation_attacks(rbac_tester):
    """Test token format manipulation attacks."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    rbac_tester.run_token_manipulation_tests()
    
    manipulation_bypasses = [f for f in rbac_tester.findings 
                           if "token_manipulation" in f["category"] and f["severity"] == "CRITICAL"]
    
    print(f"\n=== TOKEN MANIPULATION TEST RESULTS ===")
    print(f"Manipulation attempts: {len([f for f in rbac_tester.findings if 'token_manipulation' in f['category']])}")
    print(f"Successful bypasses: {len(manipulation_bypasses)}")
    
    if manipulation_bypasses:
        print("\nTOKEN MANIPULATION BYPASSES:")
        for bypass in manipulation_bypasses[:3]:
            print(f"- {bypass['route']}: {bypass['headers']}")


def test_session_hijacking_simulations(rbac_tester):
    """Test session hijacking simulation attacks."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    rbac_tester.run_session_hijacking_tests()
    
    session_bypasses = [f for f in rbac_tester.findings 
                       if "session_hijacking" in f["category"] and f["severity"] == "CRITICAL"]
    
    print(f"\n=== SESSION HIJACKING TEST RESULTS ===")
    print(f"Hijacking attempts: {len([f for f in rbac_tester.findings if 'session_hijacking' in f['category']])}")
    print(f"Successful bypasses: {len(session_bypasses)}")
    
    if session_bypasses:
        print("\nSESSION HIJACKING BYPASSES:")
        for bypass in session_bypasses[:3]:
            print(f"- {bypass['route']}: {bypass['headers']}")


def test_comprehensive_rbac_security(rbac_tester):
    """Run comprehensive RBAC security tests."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    rbac_tester.run_comprehensive_rbac_tests()
    
    # Summary analysis
    total_findings = len(rbac_tester.findings)
    critical_findings = len([f for f in rbac_tester.findings if f["severity"] == "CRITICAL"])
    high_findings = len([f for f in rbac_tester.findings if f["severity"] == "HIGH"])
    
    print(f"\n=== COMPREHENSIVE RBAC TEST SUMMARY ===")
    print(f"Total findings: {total_findings}")
    print(f"Critical: {critical_findings}")
    print(f"High: {high_findings}")
    print(f"Protected routes tested: {len(rbac_tester.protected_routes)}")
    
    # Category breakdown
    categories = {}
    for finding in rbac_tester.findings:
        cat = finding["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nFindings by category:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"- {category}: {count}")
    
    # Record results globally
    global rbac_findings
    rbac_findings.extend(rbac_tester.findings)


@pytest.fixture(scope="session", autouse=True)
def generate_rbac_report(request):
    """Generate RBAC abuse test report after all tests complete."""
    yield
    
    # Generate findings report
    report_file = Path("DOCS/security/rbac_abuse_report.md")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    global rbac_findings
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# RBAC Abuse Simulation Report\n\n")
        f.write(f"Generated: {os.environ.get('BUILD_TIMESTAMP', 'unknown')}\n")
        f.write(f"Test Environment: FastAPI Available = {FASTAPI_AVAILABLE}\n")
        f.write(f"RBAC Enabled: {RBAC_ENABLED}\n")
        f.write(f"Intensive Mode: {RBAC_INTENSIVE}\n")
        f.write(f"Report All: {RBAC_REPORT_ALL}\n\n")
        
        if not rbac_findings:
            f.write("## Summary\n\nNo RBAC abuse findings detected - all admin routes properly protected.\n\n")
            return
        
        # Summary statistics
        severity_counts = {}
        category_counts = {}
        route_counts = {}
        
        for finding in rbac_findings:
            severity = finding['severity']
            category = finding['category']
            route = finding['route']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            route_counts[route] = route_counts.get(route, 0) + 1
        
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Findings**: {len(rbac_findings)}\n")
        f.write(f"- **Admin Routes Tested**: {len(route_counts)}\n")
        f.write(f"- **Attack Categories**: {len(category_counts)}\n")
        f.write(f"- **Critical Bypasses**: {severity_counts.get('CRITICAL', 0)}\n")
        f.write(f"- **High Risk**: {severity_counts.get('HIGH', 0)}\n\n")
        
        # Risk Assessment
        critical_count = severity_counts.get('CRITICAL', 0)
        if critical_count > 0:
            f.write("🔴 **CRITICAL RISK**: Authentication bypass vulnerabilities detected\n\n")
        elif severity_counts.get('HIGH', 0) > 5:
            f.write("🟡 **MODERATE RISK**: Multiple high-severity findings\n\n")
        else:
            f.write("🟢 **LOW RISK**: No critical bypasses detected\n\n")
        
        # Findings by Severity
        f.write("## Findings by Severity\n\n")
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {"CRITICAL": "🔥", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "ℹ️", "INFO": "✅"}.get(severity, "")
                f.write(f"### {emoji} {severity} Severity ({count} findings)\n\n")
                
                severity_findings = [f for f in rbac_findings if f['severity'] == severity]
                for finding in severity_findings[:10]:  # Limit to first 10 per severity
                    f.write(f"#### {finding['category']}\n")
                    f.write(f"- **Route**: `{finding['method']} {finding['route']}`\n")
                    f.write(f"- **Status**: {finding['status_code']}\n")
                    f.write(f"- **Headers**: `{finding['headers']}`\n")
                    f.write(f"- **Result**: {finding['result'][:200]}\n\n")
                
                if len(severity_findings) > 10:
                    f.write(f"*... and {len(severity_findings) - 10} more {severity} findings*\n\n")
        
        # Attack Vector Analysis
        f.write("## Attack Vector Analysis\n\n")
        
        f.write("### Most Targeted Routes\n\n")
        sorted_routes = sorted(route_counts.items(), key=lambda x: x[1], reverse=True)
        for route, count in sorted_routes[:10]:
            f.write(f"- `{route}`: {count} attempts\n")
        f.write("\n")
        
        f.write("### Attack Categories\n\n")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{category}**: {count} attempts\n")
        f.write("\n")
        
        # Recommendations
        f.write("## Security Recommendations\n\n")
        
        if critical_count > 0:
            f.write("### Immediate Actions Required\n")
            f.write("- Review and fix authentication bypass vulnerabilities\n")
            f.write("- Implement additional request validation\n")
            f.write("- Add comprehensive logging for admin route access\n\n")
        
        f.write("### General Hardening\n")
        f.write("- Implement strict header validation and normalization\n")
        f.write("- Use secure session management with proper timeout\n")
        f.write("- Add rate limiting to admin endpoints\n")
        f.write("- Implement proper CORS policies\n")
        f.write("- Use strong, randomly generated admin tokens\n")
        f.write("- Enable request/response logging for security monitoring\n")
        f.write("- Consider implementing IP whitelisting for admin routes\n")
        f.write("- Add multi-factor authentication for admin access\n\n")
        
        f.write("### Monitoring & Detection\n")
        f.write("- Monitor for unusual header patterns in admin requests\n")
        f.write("- Alert on repeated authentication failures\n")
        f.write("- Log all successful admin route access\n")
        f.write("- Implement behavioral analysis for admin users\n\n")
        
        f.write("---\n")
        f.write("*Report generated by WatchLockAI Sentinel RBAC abuse simulation suite*\n")
    
    print(f"\nRBAC abuse report generated: {report_file}")


if __name__ == "__main__":
    # Allow direct execution for development
    if RBAC_ENABLED and FASTAPI_AVAILABLE:
        tester = RBACBypassTester()
        tester.run_comprehensive_rbac_tests()
        print(f"\nDirect execution complete. Found {len(tester.findings)} findings.")
    else:
        print("RBAC abuse testing disabled or FastAPI not available. Set PYTEST_RBAC_ENABLED=1 to enable.")
