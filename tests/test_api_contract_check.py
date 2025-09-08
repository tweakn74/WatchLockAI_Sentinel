# File: tests/test_api_contract_check.py
# Purpose: Unit tests for API contract checker (P3-007)

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.api_contract_check import (
    APIEndpoint, APIContractDiff, APIContractAnalyzer
)


class TestAPIEndpoint(unittest.TestCase):
    """Test API endpoint data structure"""
    
    def test_endpoint_creation(self):
        """Test creating API endpoint"""
        endpoint = APIEndpoint(
            path="/api/test",
            method="GET",
            handler="test.handler",
            parameters=["param1", "param2"],
            response_fields=["field1", "field2"],
            auth_required=True,
            feature_flag="TEST_ENABLED"
        )
        
        self.assertEqual(endpoint.path, "/api/test")
        self.assertEqual(endpoint.method, "GET")
        self.assertEqual(endpoint.handler, "test.handler")
        self.assertEqual(endpoint.parameters, ["param1", "param2"])
        self.assertEqual(endpoint.response_fields, ["field1", "field2"])
        self.assertTrue(endpoint.auth_required)
        self.assertEqual(endpoint.feature_flag, "TEST_ENABLED")


class TestAPIContractAnalyzer(unittest.TestCase):
    """Test API contract analyzer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = APIContractAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample endpoints for testing
        self.endpoint1 = APIEndpoint(
            path="/api/test1",
            method="GET", 
            handler="test.handler1",
            parameters=["id"],
            response_fields=["data", "status"],
            auth_required=False,
            feature_flag="TEST1_ENABLED"
        )
        
        self.endpoint2 = APIEndpoint(
            path="/api/test2",
            method="POST",
            handler="test.handler2", 
            parameters=["data", "format"],
            response_fields=["result", "timestamp"],
            auth_required=True,
            feature_flag="TEST2_ENABLED"
        )
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_check_auth_required_admin_path(self):
        """Test auth detection for admin paths"""
        view_func = MagicMock()
        
        result = self.analyzer._check_auth_required(view_func, "/api/admin/users")
        
        self.assertTrue(result)
    
    def test_check_auth_required_regular_path(self):
        """Test auth detection for regular paths"""
        view_func = MagicMock()
        
        result = self.analyzer._check_auth_required(view_func, "/api/public/data")
        
        self.assertFalse(result)
    
    def test_extract_feature_flag(self):
        """Test feature flag extraction"""
        view_func = MagicMock()
        
        # Test known patterns
        self.assertEqual(
            self.analyzer._extract_feature_flag(view_func, "/api/auth/login"),
            "CONSOLE_AUTH_ENABLED"
        )
        self.assertEqual(
            self.analyzer._extract_feature_flag(view_func, "/api/stream/health"),
            "STREAM_ENABLED"
        )
        self.assertEqual(
            self.analyzer._extract_feature_flag(view_func, "/api/metrics/health"),
            "HEALTH_ENDPOINT_ENABLED"
        )
        
        # Test unknown pattern
        self.assertIsNone(
            self.analyzer._extract_feature_flag(view_func, "/api/unknown/endpoint")
        )
    
    def test_analyze_response_fields(self):
        """Test response field analysis"""
        view_func = MagicMock()
        view_func.__name__ = "health_status"
        
        fields = self.analyzer._analyze_response_fields(view_func)
        
        self.assertIn("status", fields)
        self.assertIn("timestamp", fields)
    
    @patch('tools.api_contract_check.datetime')
    def test_generate_contract(self, mock_datetime):
        """Test contract generation"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2025-09-04T10:29:27"
        
        # Mock FastAPI app and routes
        with patch.object(self.analyzer, 'extract_fastapi_routes') as mock_extract:
            mock_extract.return_value = {
                "GET:/api/test1": self.endpoint1,
                "POST:/api/test2": self.endpoint2
            }
            
            contract = self.analyzer.generate_contract()
            
            self.assertEqual(contract["version"], "1.0")
            self.assertEqual(contract["generated_at"], "2025-09-04T10:29:27")
            self.assertEqual(contract["summary"]["total_endpoints"], 2)
            self.assertEqual(contract["summary"]["auth_required_count"], 1)
            self.assertEqual(contract["summary"]["feature_flagged_count"], 2)
            
            # Check endpoints
            endpoints = contract["endpoints"]
            self.assertIn("GET:/api/test1", endpoints)
            self.assertIn("POST:/api/test2", endpoints)
            
            test1_endpoint = endpoints["GET:/api/test1"]
            self.assertEqual(test1_endpoint["path"], "/api/test1")
            self.assertEqual(test1_endpoint["method"], "GET")
            self.assertFalse(test1_endpoint["auth_required"])
    
    def test_save_contract(self):
        """Test saving contract to file"""
        contract = {
            "version": "1.0",
            "endpoints": {"test": "data"}
        }
        
        output_file = os.path.join(self.temp_dir, "contract.json")
        
        result = self.analyzer.save_contract(contract, output_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify content
        with open(output_file, 'r') as f:
            loaded = json.load(f)
            
        self.assertEqual(loaded, contract)
    
    def test_load_baseline_contract(self):
        """Test loading baseline contract"""
        baseline = {
            "version": "1.0",
            "endpoints": {"test": "baseline"}
        }
        
        baseline_file = os.path.join(self.temp_dir, "baseline.json")
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f)
        
        result = self.analyzer.load_baseline_contract(baseline_file)
        
        self.assertEqual(result, baseline)
    
    def test_load_baseline_contract_missing(self):
        """Test loading missing baseline contract"""
        missing_file = os.path.join(self.temp_dir, "missing.json")
        
        result = self.analyzer.load_baseline_contract(missing_file)
        
        self.assertEqual(result, {})
    
    def test_dict_to_endpoint(self):
        """Test converting dictionary to endpoint"""
        ep_data = {
            "path": "/api/test",
            "method": "GET",
            "handler": "test.handler",
            "parameters": ["param1"],
            "response_fields": ["field1"],
            "auth_required": True,
            "feature_flag": "TEST_FLAG"
        }
        
        endpoint = self.analyzer._dict_to_endpoint(ep_data)
        
        self.assertEqual(endpoint.path, "/api/test")
        self.assertEqual(endpoint.method, "GET")
        self.assertEqual(endpoint.handler, "test.handler")
        self.assertEqual(endpoint.parameters, ["param1"])
        self.assertEqual(endpoint.response_fields, ["field1"])
        self.assertTrue(endpoint.auth_required)
        self.assertEqual(endpoint.feature_flag, "TEST_FLAG")
    
    def test_endpoints_differ_same(self):
        """Test endpoint comparison for identical endpoints"""
        ep1 = APIEndpoint("/api/test", "GET", "handler", ["param"], ["field"], True, "FLAG")
        ep2 = APIEndpoint("/api/test", "GET", "handler", ["param"], ["field"], True, "FLAG")
        
        result = self.analyzer._endpoints_differ(ep1, ep2)
        
        self.assertFalse(result)
    
    def test_endpoints_differ_different(self):
        """Test endpoint comparison for different endpoints"""
        ep1 = APIEndpoint("/api/test", "GET", "handler1", ["param"], ["field"], True, "FLAG")
        ep2 = APIEndpoint("/api/test", "GET", "handler2", ["param"], ["field"], True, "FLAG")
        
        result = self.analyzer._endpoints_differ(ep1, ep2)
        
        self.assertTrue(result)
    
    def test_analyze_endpoint_changes(self):
        """Test analyzing changes between endpoints"""
        old_ep = APIEndpoint(
            "/api/test", "GET", "old_handler", 
            ["old_param", "shared"], ["old_field", "shared"],
            False, "OLD_FLAG"
        )
        new_ep = APIEndpoint(
            "/api/test", "GET", "new_handler",
            ["new_param", "shared"], ["new_field", "shared"],
            True, "NEW_FLAG"
        )
        
        changes = self.analyzer._analyze_endpoint_changes(old_ep, new_ep)
        
        # Check breaking changes
        breaking = changes["breaking"]
        self.assertTrue(any("Handler changed" in change for change in breaking))
        self.assertTrue(any("Parameter removed" in change for change in breaking))
        self.assertTrue(any("Response field removed" in change for change in breaking))
        self.assertTrue(any("Authentication now required" in change for change in breaking))
        self.assertTrue(any("Feature flag changed" in change for change in breaking))
        
        # Check non-breaking changes
        non_breaking = changes["non_breaking"]
        self.assertTrue(any("Parameter added" in change for change in non_breaking))
        self.assertTrue(any("Response field added" in change for change in non_breaking))
    
    def test_compare_contracts(self):
        """Test comparing two contracts"""
        baseline = {
            "endpoints": {
                "GET:/api/old": {
                    "path": "/api/old", "method": "GET", "handler": "old.handler",
                    "parameters": [], "response_fields": [], 
                    "auth_required": False, "feature_flag": None
                },
                "GET:/api/shared": {
                    "path": "/api/shared", "method": "GET", "handler": "old.shared",
                    "parameters": ["old_param"], "response_fields": ["old_field"],
                    "auth_required": False, "feature_flag": None
                }
            }
        }
        
        current = {
            "endpoints": {
                "GET:/api/new": {
                    "path": "/api/new", "method": "GET", "handler": "new.handler",
                    "parameters": [], "response_fields": [],
                    "auth_required": False, "feature_flag": None
                },
                "GET:/api/shared": {
                    "path": "/api/shared", "method": "GET", "handler": "new.shared",
                    "parameters": ["new_param"], "response_fields": ["new_field"],
                    "auth_required": False, "feature_flag": None
                }
            }
        }
        
        diff = self.analyzer.compare_contracts(baseline, current)
        
        # Check structure
        self.assertEqual(len(diff.removed_endpoints), 1)
        self.assertEqual(diff.removed_endpoints[0].path, "/api/old")
        
        self.assertEqual(len(diff.added_endpoints), 1)
        self.assertEqual(diff.added_endpoints[0].path, "/api/new")
        
        self.assertEqual(len(diff.modified_endpoints), 1)
        old_shared, new_shared = diff.modified_endpoints[0]
        self.assertEqual(old_shared.path, "/api/shared")
        self.assertEqual(new_shared.path, "/api/shared")
        
        # Check breaking/non-breaking changes
        self.assertTrue(len(diff.breaking_changes) > 0)
        self.assertTrue(len(diff.non_breaking_changes) > 0)
        
        # Check specific change types
        self.assertTrue(any("Removed endpoint" in change for change in diff.breaking_changes))
        self.assertTrue(any("Added endpoint" in change for change in diff.non_breaking_changes))


class TestAPIContractDiff(unittest.TestCase):
    """Test API contract diff data structure"""
    
    def test_contract_diff_creation(self):
        """Test creating contract diff"""
        endpoint1 = APIEndpoint("/api/test1", "GET", "handler1", [], [], False)
        endpoint2 = APIEndpoint("/api/test2", "POST", "handler2", [], [], True)
        
        diff = APIContractDiff(
            removed_endpoints=[endpoint1],
            modified_endpoints=[(endpoint1, endpoint2)],
            added_endpoints=[endpoint2],
            breaking_changes=["Test breaking change"],
            non_breaking_changes=["Test non-breaking change"]
        )
        
        self.assertEqual(len(diff.removed_endpoints), 1)
        self.assertEqual(len(diff.modified_endpoints), 1)
        self.assertEqual(len(diff.added_endpoints), 1)
        self.assertEqual(len(diff.breaking_changes), 1)
        self.assertEqual(len(diff.non_breaking_changes), 1)


if __name__ == "__main__":
    unittest.main()
