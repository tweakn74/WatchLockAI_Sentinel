#!/usr/bin/env python3
"""
Unicode Normalization Tests v4.0 - NFC/NFD/RTL hardening tests
Part of Credits Overdrive v4.0 (Proof-Oriented, Fail-Closed)

Tests Unicode normalization handling across:
- Authentication headers (Authorization, X-Admin-Token)
- Filenames in quarantine operations
- Query parameters in API endpoints
- Request payload validation

Covers normalization attacks, RTL markers, zero-width characters, and encoding bypasses.
"""

import unittest
import sys
import os
import unicodedata
from typing import List, Dict, Any, Optional
import importlib.util

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class UnicodeNormalizationTests(unittest.TestCase):
    """Test suite for Unicode normalization security"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.test_client = None
        cls.app = None
        
        # Unicode test patterns
        cls.unicode_attacks = cls._generate_unicode_test_patterns()
        
        # Try to initialize FastAPI test client
        cls._init_test_client()
    
    @classmethod
    def _generate_unicode_test_patterns(cls) -> Dict[str, List[str]]:
        """Generate comprehensive Unicode attack patterns"""
        return {
            'normalization_attacks': [
                # NFC vs NFD attacks
                'café',  # NFC: Single é character
                'cafe\u0301',  # NFD: e + combining acute accent
                'caf\u00E9',  # Another NFC variant
                'caf\u0065\u0301',  # Another NFD variant
                
                # Mixed normalization
                'café\u0301',  # Mixed NFC + combining
                'caf\u00E9\u0301',  # Double accent
                
                # Different Unicode representations of same visual
                'A',  # U+0041 Latin Capital Letter A
                'Α',  # U+0391 Greek Capital Letter Alpha
                'А',  # U+0410 Cyrillic Capital Letter A
                
                # Filename attacks
                'test\u0300.txt',  # Combining grave accent
                'te\u0300st.txt',  # Mid-name combining
                'test.\u200Btxt',  # Zero-width space in extension
            ],
            
            'rtl_attacks': [
                # RTL override attacks  
                'admin\u202Edekcah',  # RTL override (shows as "adminhacked")
                '\u202Enimda',  # Full RTL (shows as "admin")
                'user\u202E\u0441\u043E\u043C\u043C\u043E\u043D\u202D',  # RTL with Cyrillic
                
                # RTL in paths
                '/api/\u202Enimda',  # RTL in URL path
                'file\u202Eexe.',  # Extension confusion
                
                # RTL with Arabic/Hebrew
                'admin\u0627\u062F\u0645\u06CC\u0646',  # Admin with Arabic
                'user\u05D0\u05D3\u05DE\u05D9\u05DF',  # User with Hebrew
            ],
            
            'zero_width_attacks': [
                # Zero-width characters
                'admin\u200B',  # Zero-width space
                'ad\u200Cmin',  # Zero-width non-joiner  
                'admin\u200D',  # Zero-width joiner
                'user\uFEFF',  # Zero-width no-break space (BOM)
                '\u2060admin',  # Word joiner
                
                # Multiple zero-width
                'a\u200B\u200C\u200Ddmin',  # Multiple ZW chars
                'user\u200B\u200B\u200B',  # Multiple ZW spaces
                
                # Zero-width in sensitive contexts
                'password\u200B123',  # ZW in password
                'token\u200C\u200Dabc',  # ZW in token
            ],
            
            'encoding_bypasses': [
                # Overlong UTF-8 sequences (as strings, not actual bytes)
                '%C0%AF',  # Overlong encoding of /
                '%E0%80%AF',  # Another overlong /
                '%F0%80%80%AF',  # Even longer overlong /
                
                # UTF-8 BOM
                '\uFEFFadmin',  # BOM prefix
                'user\uFEFF',  # BOM suffix
                
                # High surrogates (as safe representations)
                'test\uD800\uDC00data',  # Valid surrogate pair
                
                # Normalization with combining sequences
                'e\u0301\u0302\u0303',  # Multiple combining marks
                'a\u0300\u0301\u0302\u0303\u0304',  # Many combining marks
            ],
            
            'filename_attacks': [
                # Directory traversal with Unicode
                '..\u002Fpasswd',  # Unicode slash
                '..\u005Cpasswd',  # Unicode backslash
                '..%2Fpasswd',  # URL encoded slash
                
                # Filename confusion
                'test\u200Etxt.exe',  # Extension hiding
                'safe.txt\u200E.exe',  # Hidden executable
                
                # Case folding attacks
                'İnstaller.exe',  # Turkish I (folds to different case)
                'ſſ.txt',  # Long s characters
                
                # Confusable characters in filenames
                'admin.txt',  # Normal
                'аdmin.txt',  # Cyrillic 'а' 
                'αdmin.txt',  # Greek alpha
            ]
        }
    
    @classmethod
    def _init_test_client(cls):
        """Initialize FastAPI test client if available"""
        try:
            fastapi_spec = importlib.util.find_spec("fastapi")
            web_api_spec = importlib.util.find_spec("console.web_api")
            
            if not fastapi_spec or not web_api_spec:
                print("⚠️  FastAPI or console.web_api not available - Unicode tests will be limited")
                return
            
            from fastapi.testclient import TestClient
            from console.web_api import SentinelWebAPI
            
            api = SentinelWebAPI()
            cls.app = api.app
            cls.test_client = TestClient(api.app)
            
            print("✅ FastAPI TestClient initialized for Unicode testing")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize TestClient: {e}")
    
    def test_auth_header_normalization(self):
        """Test Authorization header Unicode normalization"""
        if not self.test_client:
            self.skipTest("FastAPI TestClient not available")
        
        # Test various Unicode patterns in Authorization header
        for category, patterns in self.unicode_attacks.items():
            for pattern in patterns[:3]:  # Test first 3 of each category
                with self.subTest(category=category, pattern=repr(pattern)):
                    # Test with Bearer token
                    malicious_token = f"Bearer token_{pattern}"
                    response = self._make_authenticated_request("/api/status", malicious_token)
                    
                    # Should either normalize safely or reject
                    self.assertIn(response.status_code, [200, 401, 400], 
                                f"Unexpected status for Unicode in auth header: {pattern}")
                    
                    # Test with X-Admin-Token
                    admin_headers = {"X-Admin-Token": f"admin_{pattern}"}
                    response = self._make_request_with_headers("/api/admin/config/schema", admin_headers)
                    
                    # Should handle Unicode in admin token safely
                    self.assertIn(response.status_code, [200, 401, 403, 400],
                                f"Unexpected status for Unicode in admin token: {pattern}")
    
    def test_query_parameter_normalization(self):
        """Test Unicode normalization in query parameters"""
        if not self.test_client:
            self.skipTest("FastAPI TestClient not available")
        
        # Test endpoints that accept query parameters
        test_endpoints = [
            "/api/ti/search",
            "/api/detections", 
            "/api/actions/pause"
        ]
        
        for endpoint in test_endpoints:
            for category, patterns in self.unicode_attacks.items():
                for pattern in patterns[:2]:  # Test first 2 of each category
                    with self.subTest(endpoint=endpoint, category=category, pattern=repr(pattern)):
                        # Test Unicode in query parameter values
                        params = {"query": pattern, "limit": "10"}
                        response = self._make_request_with_params(endpoint, params)
                        
                        # Should handle Unicode gracefully
                        self.assertIn(response.status_code, [200, 400, 422],
                                    f"Endpoint {endpoint} failed on Unicode pattern: {pattern}")
    
    def test_filename_normalization(self):
        """Test Unicode normalization in filename operations"""
        # Test filename validation without actual file operations
        for category, patterns in self.unicode_attacks.items():
            if category == 'filename_attacks':
                for pattern in patterns:
                    with self.subTest(filename=repr(pattern)):
                        # Test filename normalization
                        normalized = self._normalize_filename(pattern)
                        
                        # Should not contain dangerous characters after normalization
                        self.assertNotIn('..', normalized, f"Path traversal in normalized filename: {pattern}")
                        self.assertNotIn('\x00', normalized, f"Null byte in normalized filename: {pattern}")
                        
                        # Should not contain RTL/ZW characters that could cause confusion
                        dangerous_chars = ['\u202E', '\u202D', '\u200B', '\u200C', '\u200D']
                        for char in dangerous_chars:
                            self.assertNotIn(char, normalized, 
                                           f"Dangerous Unicode character {repr(char)} in normalized filename")
    
    def test_request_body_normalization(self):
        """Test Unicode normalization in request bodies"""
        if not self.test_client:
            self.skipTest("FastAPI TestClient not available")
        
        # Test POST endpoints with JSON bodies
        test_data_sets = []
        
        # Create test payloads with Unicode attacks
        for category, patterns in self.unicode_attacks.items():
            for pattern in patterns[:2]:
                test_data_sets.extend([
                    {"username": pattern, "password": "test123"},
                    {"filename": pattern, "content": "test data"},
                    {"query": pattern, "filters": ["test"]},
                    {"setting_key": f"test_{pattern}", "setting_value": "value"},
                ])
        
        # Test against POST endpoints
        post_endpoints = [
            "/api/auth/login",
            "/api/admin/config/reload", 
            "/api/actions/pause"
        ]
        
        for endpoint in post_endpoints:
            for i, test_data in enumerate(test_data_sets[:5]):  # Test first 5 datasets
                with self.subTest(endpoint=endpoint, data_index=i):
                    response = self._make_post_request(endpoint, test_data)
                    
                    # Should handle Unicode in JSON safely
                    self.assertIn(response.status_code, [200, 400, 401, 403, 422],
                                f"Endpoint {endpoint} failed on Unicode JSON data")
    
    def test_normalization_consistency(self):
        """Test that Unicode normalization is consistent across operations"""
        test_strings = [
            ('café', 'cafe\u0301'),  # NFC vs NFD
            ('A', 'Α'),  # Latin vs Greek
            ('test\u200B', 'test'),  # With and without zero-width space
        ]
        
        for original, variant in test_strings:
            with self.subTest(original=repr(original), variant=repr(variant)):
                # Normalize both versions
                norm_original = self._normalize_string(original)
                norm_variant = self._normalize_string(variant)
                
                # Different representations should normalize to same result when appropriate
                if original == 'café' and variant == 'cafe\u0301':
                    # These should normalize to the same thing
                    self.assertEqual(norm_original, norm_variant,
                                   "NFC and NFD forms should normalize consistently")
                elif original == 'test\u200B' and variant == 'test':
                    # Zero-width characters should be removed
                    self.assertEqual(norm_variant, norm_original,
                                   "Zero-width characters should be removed in normalization")
    
    def test_security_header_validation(self):
        """Test that security-sensitive headers properly validate Unicode"""
        if not self.test_client:
            self.skipTest("FastAPI TestClient not available")
        
        # Security-sensitive headers that should be strictly validated
        security_headers = [
            "Authorization",
            "X-Admin-Token", 
            "X-API-Key",
            "Cookie",
        ]
        
        # High-risk Unicode patterns
        high_risk_patterns = [
            '\u202Eadmin',  # RTL override
            'token\u200B',  # Zero-width space
            'admin\u0000',  # Null byte
            'user\uFEFF',   # BOM
        ]
        
        for header_name in security_headers:
            for pattern in high_risk_patterns:
                with self.subTest(header=header_name, pattern=repr(pattern)):
                    headers = {header_name: f"test_{pattern}"}
                    response = self._make_request_with_headers("/api/status", headers)
                    
                    # Security headers with suspicious Unicode should be rejected
                    self.assertIn(response.status_code, [400, 401, 403],
                                f"Security header {header_name} should reject suspicious Unicode")
    
    def test_quarantine_path_validation(self):
        """Test Unicode validation in quarantine file operations"""
        # Test quarantine path validation (without actual file operations)
        quarantine_paths = [
            "quarantine/test.txt",
            "quarantine/sub/file.dat",
            "/tmp/quarantine/test.txt",
        ]
        
        # Attack patterns specifically for path manipulation
        path_attacks = [
            "quarantine/../../../etc/passwd",
            "quarantine/\u202E/..passwd",  # RTL in path
            "quarantine/test\u200B.exe",    # Hidden characters
            "quarantine/\uFEFFmalware.exe", # BOM in filename
        ]
        
        for safe_path in quarantine_paths:
            # Test that safe paths remain safe after normalization
            normalized = self._normalize_quarantine_path(safe_path)
            self.assertTrue(self._is_safe_quarantine_path(normalized),
                          f"Safe path became unsafe after normalization: {safe_path}")
        
        for attack_path in path_attacks:
            # Test that attack paths are neutralized
            normalized = self._normalize_quarantine_path(attack_path)
            self.assertFalse(self._is_safe_quarantine_path(normalized),
                           f"Attack path not neutralized: {attack_path}")
    
    def test_unicode_case_folding_attacks(self):
        """Test resistance to Unicode case folding attacks"""
        # Case folding can bypass case-sensitive security checks
        case_folding_pairs = [
            ('ADMIN', 'admin'),
            ('İNSTALLER', 'installer'),  # Turkish I
            ('ſſ', 'ss'),  # Long s to regular s
            ('ROOT', 'root'),
            ('SYSTEM', 'system'),
        ]
        
        for upper, lower in case_folding_pairs:
            with self.subTest(upper=upper, lower=lower):
                # Both forms should be treated consistently for security
                upper_normalized = self._normalize_for_security(upper)
                lower_normalized = self._normalize_for_security(lower)
                
                # Security-sensitive normalization should make them equivalent
                self.assertEqual(upper_normalized, lower_normalized,
                               f"Case folding inconsistency: {upper} vs {lower}")
    
    # Helper methods
    
    def _make_authenticated_request(self, path: str, auth_header: str):
        """Make request with specific Authorization header"""
        headers = {"Authorization": auth_header}
        return self.test_client.get(path, headers=headers)
    
    def _make_request_with_headers(self, path: str, headers: Dict[str, str]):
        """Make request with custom headers"""
        return self.test_client.get(path, headers=headers)
    
    def _make_request_with_params(self, path: str, params: Dict[str, str]):
        """Make request with query parameters"""
        return self.test_client.get(path, params=params)
    
    def _make_post_request(self, path: str, data: Dict[str, Any]):
        """Make POST request with JSON data"""
        return self.test_client.post(path, json=data)
    
    def _normalize_filename(self, filename: str) -> str:
        """Normalize filename for security (example implementation)"""
        # Example normalization - real implementation should be more comprehensive
        normalized = unicodedata.normalize('NFC', filename)
        
        # Remove dangerous characters
        dangerous_chars = ['\u202E', '\u202D', '\u200B', '\u200C', '\u200D', '\uFEFF', '\x00']
        for char in dangerous_chars:
            normalized = normalized.replace(char, '')
        
        # Replace path separators that could be Unicode variants
        normalized = normalized.replace('\u002F', '/').replace('\u005C', '\\')
        
        return normalized
    
    def _normalize_string(self, s: str) -> str:
        """General string normalization"""
        # NFC normalization
        normalized = unicodedata.normalize('NFC', s)
        
        # Remove zero-width characters
        zero_width_chars = ['\u200B', '\u200C', '\u200D', '\uFEFF', '\u2060']
        for char in zero_width_chars:
            normalized = normalized.replace(char, '')
        
        return normalized
    
    def _normalize_quarantine_path(self, path: str) -> str:
        """Normalize path for quarantine operations"""
        # Comprehensive path normalization
        normalized = unicodedata.normalize('NFC', path)
        
        # Remove dangerous Unicode characters
        dangerous_chars = ['\u202E', '\u202D', '\u200B', '\u200C', '\u200D', '\uFEFF', '\x00']
        for char in dangerous_chars:
            normalized = normalized.replace(char, '')
        
        # Resolve path traversal attempts
        parts = normalized.split('/')
        safe_parts = []
        for part in parts:
            if part == '..':
                continue  # Remove path traversal
            elif part and part != '.':
                safe_parts.append(part)
        
        return '/'.join(safe_parts)
    
    def _is_safe_quarantine_path(self, path: str) -> bool:
        """Check if path is safe for quarantine operations"""
        # Must be within quarantine directory
        if not path.startswith('quarantine/') and not path.startswith('/tmp/quarantine/'):
            return False
        
        # Must not contain path traversal
        if '..' in path:
            return False
        
        # Must not contain dangerous characters
        dangerous_chars = ['\x00', '\u202E', '\u202D']
        for char in dangerous_chars:
            if char in path:
                return False
        
        return True
    
    def _normalize_for_security(self, s: str) -> str:
        """Security-focused normalization"""
        # Case folding for security comparisons
        normalized = s.lower()
        
        # Unicode normalization
        normalized = unicodedata.normalize('NFKC', normalized)  # Use NFKC for security
        
        # Remove zero-width and formatting characters
        formatting_chars = ['\u200B', '\u200C', '\u200D', '\uFEFF', '\u2060', '\u202E', '\u202D']
        for char in formatting_chars:
            normalized = normalized.replace(char, '')
        
        return normalized


def run_unicode_tests():
    """Run Unicode normalization tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(UnicodeNormalizationTests)
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("📊 UNICODE NORMALIZATION TEST SUMMARY")
    print("="*60)
    print(f"Tests Run:      {result.testsRun}")
    print(f"Failures:       {len(result.failures)}")
    print(f"Errors:         {len(result.errors)}")
    print(f"Skipped:        {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
    print("="*60)
    
    return result


if __name__ == "__main__":
    result = run_unicode_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
