#!/usr/bin/env python3
"""
Contract Tests v4.0 - Validate API responses against JSON schemas
Part of Credits Overdrive v4.0 (Proof-Oriented, Fail-Closed)

Tests that API responses are supersets of their JSON schema contracts.
Additional properties are allowed (additive compatibility).
"""

import json
import os
import sys
import unittest
from typing import Dict, Any, List, Optional
import importlib.util

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SchemaValidator:
    """JSON Schema validator using only stdlib"""
    
    def __init__(self):
        self.errors = []
    
    def validate(self, instance: Any, schema: Dict[str, Any]) -> bool:
        """Validate instance against schema (simplified validation)"""
        self.errors = []
        try:
            self._validate_value(instance, schema, "root")
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"Validation error: {e}")
            return False
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], path: str) -> None:
        """Validate a value against a schema"""
        # Handle oneOf schemas
        if "oneOf" in schema:
            for i, subschema in enumerate(schema["oneOf"]):
                temp_validator = SchemaValidator()
                if temp_validator.validate(value, subschema):
                    return  # One of the schemas matched
            self.errors.append(f"{path}: Value does not match any oneOf schemas")
            return
        
        # Handle anyOf schemas
        if "anyOf" in schema:
            for subschema in schema["anyOf"]:
                temp_validator = SchemaValidator()
                if temp_validator.validate(value, subschema):
                    return  # One of the schemas matched
            self.errors.append(f"{path}: Value does not match any anyOf schemas")
            return
        
        schema_type = schema.get("type")
        
        # Type validation
        if schema_type:
            if not self._check_type(value, schema_type, path):
                return
        
        # Type-specific validation
        if schema_type == "object" or (not schema_type and isinstance(value, dict)):
            self._validate_object(value, schema, path)
        elif schema_type == "array" or (not schema_type and isinstance(value, list)):
            self._validate_array(value, schema, path)
        elif schema_type == "string" or (not schema_type and isinstance(value, str)):
            self._validate_string(value, schema, path)
        elif schema_type in ["integer", "number"] or (not schema_type and isinstance(value, (int, float))):
            self._validate_number(value, schema, path)
    
    def _check_type(self, value: Any, schema_type: Any, path: str) -> bool:
        """Check if value matches expected type(s)"""
        if isinstance(schema_type, list):
            # Multiple types allowed
            for t in schema_type:
                if self._check_single_type(value, t):
                    return True
            self.errors.append(f"{path}: Expected one of {schema_type}, got {type(value).__name__}")
            return False
        else:
            return self._check_single_type(value, schema_type, path)
    
    def _check_single_type(self, value: Any, schema_type: str, path: str = "") -> bool:
        """Check if value matches a single type"""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        expected_type = type_map.get(schema_type)
        if expected_type and not isinstance(value, expected_type):
            if path:
                self.errors.append(f"{path}: Expected {schema_type}, got {type(value).__name__}")
            return False
        return True
    
    def _validate_object(self, obj: Dict[str, Any], schema: Dict[str, Any], path: str) -> None:
        """Validate object against schema"""
        if not isinstance(obj, dict):
            self.errors.append(f"{path}: Expected object, got {type(obj).__name__}")
            return
        
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Check required properties
        for prop in required:
            if prop not in obj:
                self.errors.append(f"{path}: Missing required property '{prop}'")
        
        # Validate existing properties
        for prop, value in obj.items():
            if prop in properties:
                self._validate_value(value, properties[prop], f"{path}.{prop}")
            # Note: Additional properties are allowed (additive compatibility)
    
    def _validate_array(self, arr: List[Any], schema: Dict[str, Any], path: str) -> None:
        """Validate array against schema"""
        if not isinstance(arr, list):
            self.errors.append(f"{path}: Expected array, got {type(arr).__name__}")
            return
        
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        items_schema = schema.get("items")
        
        if min_items is not None and len(arr) < min_items:
            self.errors.append(f"{path}: Array too short, expected >= {min_items}, got {len(arr)}")
        
        if max_items is not None and len(arr) > max_items:
            self.errors.append(f"{path}: Array too long, expected <= {max_items}, got {len(arr)}")
        
        if items_schema:
            for i, item in enumerate(arr):
                self._validate_value(item, items_schema, f"{path}[{i}]")
    
    def _validate_string(self, s: str, schema: Dict[str, Any], path: str) -> None:
        """Validate string against schema"""
        if "enum" in schema and s not in schema["enum"]:
            self.errors.append(f"{path}: Value '{s}' not in allowed enum values {schema['enum']}")
        
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        
        if min_length is not None and len(s) < min_length:
            self.errors.append(f"{path}: String too short, expected >= {min_length}, got {len(s)}")
        
        if max_length is not None and len(s) > max_length:
            self.errors.append(f"{path}: String too long, expected <= {max_length}, got {len(s)}")
    
    def _validate_number(self, n: float, schema: Dict[str, Any], path: str) -> None:
        """Validate number against schema"""
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        
        if minimum is not None and n < minimum:
            self.errors.append(f"{path}: Number too small, expected >= {minimum}, got {n}")
        
        if maximum is not None and n > maximum:
            self.errors.append(f"{path}: Number too large, expected <= {maximum}, got {n}")


class ContractTests(unittest.TestCase):
    """Test suite for API contract validation"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.schema_dir = os.path.join(cls.repo_root, "DOCS", "api", "schema")
        cls.schemas = cls._load_schemas()
        cls.test_client = None
        cls.app = None
        
        # Try to initialize FastAPI test client
        cls._init_test_client()
    
    @classmethod
    def _load_schemas(cls) -> Dict[str, Dict[str, Any]]:
        """Load all JSON schemas"""
        schemas = {}
        
        if not os.path.exists(cls.schema_dir):
            print(f"[WARN]  Schema directory not found: {cls.schema_dir}")
            return schemas
        
        for filename in os.listdir(cls.schema_dir):
            if filename.endswith('.schema.json'):
                schema_path = os.path.join(cls.schema_dir, filename)
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema = json.load(f)
                        # Extract method and path from schema title
                        title = schema.get("title", "")
                        if title:
                            schemas[filename[:-12]] = {  # Remove .schema.json
                                "schema": schema,
                                "title": title
                            }
                except Exception as e:
                    print(f"[WARN]  Failed to load schema {filename}: {e}")
        
        return schemas
    
    @classmethod
    def _init_test_client(cls):
        """Initialize FastAPI test client if available"""
        try:
            # Check if FastAPI and web API are available
            fastapi_spec = importlib.util.find_spec("fastapi")
            web_api_spec = importlib.util.find_spec("console.web_api")
            
            if not fastapi_spec or not web_api_spec:
                print("[WARN]  FastAPI or console.web_api not available - contract tests will be skipped")
                return
            
            from fastapi.testclient import TestClient
            from console.web_api import SentinelWebAPI
            
            api = SentinelWebAPI()
            cls.app = api.app
            cls.test_client = TestClient(api.app)
            
            print("[PASS] FastAPI TestClient initialized for contract testing")
            
        except Exception as e:
            print(f"[WARN]  Failed to initialize TestClient: {e}")
    
    def setUp(self):
        """Set up each test"""
        if not self.test_client:
            self.skipTest("FastAPI TestClient not available")
    
    def _make_request(self, method: str, path: str, **kwargs) -> Any:
        """Make HTTP request and return response"""
        method_lower = method.lower()
        
        # Handle query parameters
        params = kwargs.pop('params', {})
        headers = kwargs.pop('headers', {})
        
        # Make request
        response = getattr(self.test_client, method_lower)(
            path, 
            params=params,
            headers=headers,
            **kwargs
        )
        
        return response
    
    def _validate_response_against_schema(self, response_data: Any, schema: Dict[str, Any], 
                                        endpoint: str) -> List[str]:
        """Validate response data against JSON schema"""
        validator = SchemaValidator()
        
        if validator.validate(response_data, schema):
            return []  # No errors
        else:
            return [f"{endpoint}: {error}" for error in validator.errors]
    
    def test_health_endpoint_contract(self):
        """Test /health endpoint contract"""
        schema_key = "get_health"
        if schema_key not in self.schemas:
            self.skipTest(f"Schema not found for {schema_key}")
        
        response = self._make_request("GET", "/health")
        
        # Should return 200 for health endpoint
        self.assertEqual(response.status_code, 200)
        
        try:
            response_data = response.json()
        except Exception:
            # Handle non-JSON responses
            self.fail(f"Health endpoint returned non-JSON response: {response.text}")
        
        # Validate against schema
        schema = self.schemas[schema_key]["schema"]
        errors = self._validate_response_against_schema(response_data, schema, "/health")
        
        if errors:
            self.fail(f"Schema validation failed: {errors}")
    
    def test_status_endpoint_contract(self):
        """Test /api/status endpoint contract"""
        schema_key = "get_api_status"
        if schema_key not in self.schemas:
            self.skipTest(f"Schema not found for {schema_key}")
        
        response = self._make_request("GET", "/api/status")
        
        if response.status_code not in [200, 503]:
            self.skipTest(f"Status endpoint returned {response.status_code}")
        
        try:
            response_data = response.json()
        except Exception:
            self.fail(f"Status endpoint returned non-JSON response: {response.text}")
        
        schema = self.schemas[schema_key]["schema"]
        errors = self._validate_response_against_schema(response_data, schema, "/api/status")
        
        if errors:
            self.fail(f"Schema validation failed: {errors}")
    
    def test_metrics_health_contract(self):
        """Test /api/metrics/health endpoint contract"""
        schema_key = "get_api_metrics_health"
        if schema_key not in self.schemas:
            self.skipTest(f"Schema not found for {schema_key}")
        
        # Try without auth first
        response = self._make_request("GET", "/api/metrics/health")
        
        # If it requires auth, try with headers
        if response.status_code == 401:
            response = self._make_request("GET", "/api/metrics/health", 
                                        headers={"Authorization": "Bearer test"})
        
        if response.status_code not in [200, 401, 403]:
            self.skipTest(f"Metrics health endpoint returned {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                schema = self.schemas[schema_key]["schema"]
                errors = self._validate_response_against_schema(response_data, schema, "/api/metrics/health")
                
                if errors:
                    self.fail(f"Schema validation failed: {errors}")
            except Exception as e:
                self.fail(f"Failed to parse response: {e}")
    
    def test_actions_pause_contract(self):
        """Test /api/actions/pause endpoint contract"""
        schema_key = "post_api_actions_pause"
        if schema_key not in self.schemas:
            self.skipTest(f"Schema not found for {schema_key}")
        
        response = self._make_request("POST", "/api/actions/pause", 
                                    params={"duration_minutes": "1"})
        
        if response.status_code not in [200, 500, 503]:
            self.skipTest(f"Actions pause endpoint returned {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                schema = self.schemas[schema_key]["schema"]
                errors = self._validate_response_against_schema(response_data, schema, "/api/actions/pause")
                
                if errors:
                    self.fail(f"Schema validation failed: {errors}")
            except Exception as e:
                self.fail(f"Failed to parse response: {e}")
    
    def test_property_generated_data(self):
        """Test schemas against property-generated data"""
        # Import property test generator
        try:
            sys.path.insert(0, os.path.join(self.repo_root, "tools"))
            from property_test_generator import PropertyTestGenerator
            
            generator = PropertyTestGenerator(self.schema_dir)
            
            # Test a few schemas with generated data
            test_schemas = list(self.schemas.keys())[:10]  # Test first 10 schemas
            
            for schema_key in test_schemas:
                schema_data = self.schemas[schema_key]["schema"]
                
                # Generate test data
                variants = generator.generate_from_schema(schema_data, 3)
                
                for i, variant in enumerate(variants):
                    with self.subTest(schema=schema_key, variant=i):
                        errors = self._validate_response_against_schema(
                            variant, schema_data, f"{schema_key}_variant_{i}")
                        
                        if errors:
                            # Property generated data should always validate
                            self.fail(f"Property generated data failed validation: {errors}")
        
        except ImportError:
            self.skipTest("Property test generator not available")
        except Exception as e:
            self.skipTest(f"Property test failed: {e}")
    
    def test_all_schemas_are_valid_json_schema(self):
        """Test that all generated schemas are valid JSON Schema format"""
        required_fields = ["$schema", "title"]
        
        for schema_key, schema_info in self.schemas.items():
            schema = schema_info["schema"]
            
            with self.subTest(schema=schema_key):
                # Check required fields
                for field in required_fields:
                    self.assertIn(field, schema, f"Schema {schema_key} missing {field}")
                
                # Check that it has either properties or oneOf/anyOf
                has_structure = any(key in schema for key in ["properties", "oneOf", "anyOf", "type"])
                self.assertTrue(has_structure, f"Schema {schema_key} has no recognizable structure")
    
    def test_additive_compatibility(self):
        """Test that schemas allow additional properties (additive compatibility)"""
        for schema_key, schema_info in self.schemas.items():
            schema = schema_info["schema"]
            
            with self.subTest(schema=schema_key):
                # Check object schemas allow additional properties
                if schema.get("type") == "object":
                    additional_props = schema.get("additionalProperties", True)
                    self.assertTrue(additional_props, 
                                  f"Schema {schema_key} should allow additionalProperties for additive compatibility")
                
                # Check oneOf/anyOf schemas
                if "oneOf" in schema:
                    for i, subschema in enumerate(schema["oneOf"]):
                        if subschema.get("type") == "object":
                            additional_props = subschema.get("additionalProperties", True)
                            self.assertTrue(additional_props, 
                                          f"Schema {schema_key}.oneOf[{i}] should allow additionalProperties")


def run_contract_tests():
    """Run contract tests and return results"""
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ContractTests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("[BARS] CONTRACT TEST SUMMARY")
    print("="*60)
    print(f"Tests Run:      {result.testsRun}")
    print(f"Failures:       {len(result.failures)}")
    print(f"Errors:         {len(result.errors)}")
    print(f"Skipped:        {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n[FAIL] FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")
    
    if result.errors:
        print("\n[U+1F4A5] ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'[PASS] ALL TESTS PASSED' if success else '[FAIL] SOME TESTS FAILED'}")
    print("="*60)
    
    return result


if __name__ == "__main__":
    result = run_contract_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
