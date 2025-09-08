#!/usr/bin/env python3
"""
JSON Schema Generator v4.0 - Generate formal response contracts
Part of Credits Overdrive v4.0 (Proof-Oriented, Fail-Closed)

Generates JSON Schema contracts for all API routes from routing_atlas.json.
Creates schema files: DOCS/api/schema/<method>_<path_sanitized>.schema.json

Schemas define expected response structure while allowing additive properties
(responses can have additional keys beyond the schema).
"""

import json
import os
import re
from typing import Dict, List, Any, Optional

class JSONSchemaGenerator:
    def __init__(self, routing_atlas_path: str, schema_output_dir: str):
        self.routing_atlas_path = routing_atlas_path
        self.schema_output_dir = schema_output_dir
        self.routing_atlas = self._load_routing_atlas()
        self.generated_schemas = []
        
        # Common schema patterns for different response types
        self.common_schemas = {
            "success_response": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["success", "ok"]},
                    "message": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "additionalProperties": True
            },
            "error_response": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": ["string", "integer"]},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "additionalProperties": True
            },
            "health_response": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["healthy", "unhealthy", "degraded"]},
                    "uptime": {"type": "number", "minimum": 0},
                    "checks": {
                        "type": "object",
                        "additionalProperties": {"type": "boolean"}
                    }
                },
                "required": ["status"],
                "additionalProperties": True
            },
            "metrics_response": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time"},
                    "data": {"type": "object", "additionalProperties": True}
                },
                "additionalProperties": True
            },
            "list_response": {
                "type": "object",
                "properties": {
                    "items": {"type": "array"},
                    "total": {"type": "integer", "minimum": 0},
                    "page": {"type": "integer", "minimum": 1},
                    "limit": {"type": "integer", "minimum": 1}
                },
                "required": ["items"],
                "additionalProperties": True
            },
            "action_response": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "status": {"type": "string", "enum": ["success", "failed", "pending"]},
                    "result": {"type": ["object", "string", "null"]},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "required": ["action", "status"],
                "additionalProperties": True
            }
        }

    def _load_routing_atlas(self) -> Dict:
        """Load routing atlas JSON"""
        with open(self.routing_atlas_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _sanitize_path_for_filename(self, method: str, path: str) -> str:
        """Sanitize method + path for filename"""
        # Replace path separators and special characters
        sanitized = f"{method.lower()}_{path}"
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)  # Collapse multiple underscores
        sanitized = sanitized.strip('_')
        return sanitized

    def _infer_response_schema(self, route: Dict[str, Any]) -> Dict[str, Any]:
        """Infer appropriate JSON schema based on route characteristics"""
        method = route.get("method", "GET")
        path = route.get("path", "/")
        function_name = route.get("function_name", "")
        summary = route.get("summary", "")
        responses = route.get("responses", [])
        
        # Analyze path and function to determine response type
        path_lower = path.lower()
        func_lower = function_name.lower()
        summary_lower = summary.lower()
        
        # Health check endpoints
        if any(keyword in path_lower for keyword in ["health", "status", "ping"]):
            return self.common_schemas["health_response"].copy()
        
        # Metrics endpoints
        if any(keyword in path_lower for keyword in ["metrics", "stats", "statistics"]):
            return self.common_schemas["metrics_response"].copy()
        
        # List/collection endpoints
        if any(keyword in func_lower for keyword in ["list", "get_all"]) or path.endswith("s"):
            return self.common_schemas["list_response"].copy()
        
        # Action endpoints (pause, resume, etc.)
        if method in ["POST", "PUT", "PATCH"] and any(keyword in path_lower for keyword in ["actions", "pause", "resume", "start", "stop", "execute"]):
            return self.common_schemas["action_response"].copy()
        
        # Admin endpoints - often return success/error responses
        if "admin" in path_lower:
            if method in ["POST", "PUT", "PATCH", "DELETE"]:
                return self.common_schemas["action_response"].copy()
            else:
                return self.common_schemas["success_response"].copy()
        
        # API endpoints vs web pages
        if path.startswith("/api/"):
            # Default API response schema
            return self.common_schemas["success_response"].copy()
        else:
            # Web page responses (HTML or JSON)
            return {
                "type": ["object", "string"],
                "description": "Web page response - may be HTML or JSON",
                "additionalProperties": True
            }

    def _create_multi_status_schema(self, route: Dict[str, Any]) -> Dict[str, Any]:
        """Create schema that handles multiple possible response status codes"""
        responses = route.get("responses", [])
        base_schema = self._infer_response_schema(route)
        
        if len(responses) <= 1:
            return base_schema
        
        # Create oneOf schema for different status codes
        schema_variants = []
        
        for response in responses:
            status_code = response.get("status_code", 200)
            content_type = response.get("content_type", "application/json")
            
            if status_code >= 400:
                # Error response
                variant = self.common_schemas["error_response"].copy()
                variant["description"] = f"Error response (HTTP {status_code})"
            else:
                # Success response  
                variant = base_schema.copy()
                variant["description"] = f"Success response (HTTP {status_code})"
            
            schema_variants.append(variant)
        
        if len(schema_variants) > 1:
            return {
                "oneOf": schema_variants,
                "description": f"Response schema for {route.get('method', 'GET')} {route.get('path', '/')}"
            }
        else:
            return schema_variants[0] if schema_variants else base_schema

    def _enhance_schema_with_route_specifics(self, schema: Dict[str, Any], route: Dict[str, Any]) -> Dict[str, Any]:
        """Add route-specific enhancements to the schema"""
        path = route.get("path", "/")
        method = route.get("method", "GET")
        parameters = route.get("parameters", [])
        
        # Add metadata
        enhanced_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": f"{method} {path} Response",
            "description": f"JSON schema for {method} {path} endpoint response",
            **schema
        }
        
        # Add examples based on route type
        if "health" in path.lower():
            enhanced_schema["examples"] = [
                {"status": "healthy", "uptime": 3600.5},
                {"status": "unhealthy", "checks": {"database": False}}
            ]
        elif "metrics" in path.lower():
            enhanced_schema["examples"] = [
                {"timestamp": "2025-01-01T00:00:00Z", "data": {"count": 100}}
            ]
        elif method in ["POST", "PUT", "PATCH"] and "actions" in path.lower():
            enhanced_schema["examples"] = [
                {"action": "pause", "status": "success", "timestamp": "2025-01-01T00:00:00Z"}
            ]
        
        return enhanced_schema

    def generate_schemas_for_all_routes(self) -> None:
        """Generate JSON schemas for all routes in the atlas"""
        print("🎯 Generating JSON schemas for all API routes...")
        
        routes = self._extract_routes()
        print(f"📊 Found {len(routes)} routes to process")
        
        os.makedirs(self.schema_output_dir, exist_ok=True)
        
        for route in routes:
            method = route.get("method", "GET")
            path = route.get("path", "/")
            
            # Generate base schema
            base_schema = self._infer_response_schema(route)
            
            # Handle multiple response codes
            final_schema = self._create_multi_status_schema(route)
            
            # Enhance with route-specific details
            enhanced_schema = self._enhance_schema_with_route_specifics(final_schema, route)
            
            # Generate filename
            filename = f"{self._sanitize_path_for_filename(method, path)}.schema.json"
            output_path = os.path.join(self.schema_output_dir, filename)
            
            # Save schema
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_schema, f, indent=2, ensure_ascii=False)
            
            self.generated_schemas.append({
                "method": method,
                "path": path,
                "filename": filename,
                "schema_file": output_path
            })
            
            print(f"   ✅ {method} {path} → {filename}")
        
        print(f"\n📈 Generated {len(self.generated_schemas)} JSON schemas")
        
        # Generate index file
        self._generate_schema_index()

    def _extract_routes(self) -> List[Dict]:
        """Extract all routes from routing atlas"""
        routes = []
        for group_path, route_list in self.routing_atlas.get("route_groups", {}).items():
            for route in route_list:
                routes.append(route)
        return routes

    def _generate_schema_index(self) -> None:
        """Generate index file listing all schemas"""
        index_path = os.path.join(self.schema_output_dir, "index.json")
        
        index_data = {
            "generator": "JSON Schema Generator v4.0",
            "timestamp": self.routing_atlas.get("metadata", {}).get("timestamp", "unknown"),
            "total_schemas": len(self.generated_schemas),
            "schemas": self.generated_schemas
        }
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Schema index → {index_path}")

    def generate_property_test_data_generator(self) -> str:
        """Generate Python code for property test data generator"""
        generator_code = '''#!/usr/bin/env python3
"""
Property Test Data Generator v4.0 - Generate test data from JSON schemas
Part of Credits Overdrive v4.0 (Proof-Oriented, Fail-Closed)

Generates semantically valid test data variants from JSON schemas for property testing.
Uses only stdlib - no external dependencies.
"""

import json
import random
import string
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

class PropertyTestGenerator:
    def __init__(self, schema_dir: str):
        self.schema_dir = schema_dir
        self.schemas = self._load_all_schemas()
    
    def _load_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load all JSON schemas from directory"""
        schemas = {}
        if not os.path.exists(self.schema_dir):
            return schemas
        
        for filename in os.listdir(self.schema_dir):
            if filename.endswith('.schema.json'):
                schema_path = os.path.join(self.schema_dir, filename)
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema = json.load(f)
                        schemas[filename[:-12]] = schema  # Remove .schema.json
                except Exception as e:
                    print(f"Warning: Failed to load {filename}: {e}")
        
        return schemas
    
    def generate_from_schema(self, schema: Dict[str, Any], num_variants: int = 5) -> List[Any]:
        """Generate multiple data variants that conform to a schema"""
        variants = []
        for _ in range(num_variants):
            try:
                variant = self._generate_value(schema)
                variants.append(variant)
            except Exception as e:
                # Skip failed generations
                continue
        return variants
    
    def _generate_value(self, schema: Dict[str, Any]) -> Any:
        """Generate a single value that conforms to the schema"""
        if "oneOf" in schema:
            # Pick one of the alternatives
            chosen_schema = random.choice(schema["oneOf"])
            return self._generate_value(chosen_schema)
        
        if "anyOf" in schema:
            chosen_schema = random.choice(schema["anyOf"])
            return self._generate_value(chosen_schema)
        
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            return self._generate_object(schema)
        elif schema_type == "array":
            return self._generate_array(schema)
        elif schema_type == "string":
            return self._generate_string(schema)
        elif schema_type == "integer":
            return self._generate_integer(schema)
        elif schema_type == "number":
            return self._generate_number(schema)
        elif schema_type == "boolean":
            return random.choice([True, False])
        elif schema_type == "null":
            return None
        elif isinstance(schema_type, list):
            # Multiple types allowed - pick one
            chosen_type = random.choice(schema_type)
            return self._generate_value({"type": chosen_type, **{k: v for k, v in schema.items() if k != "type"}})
        else:
            return None
    
    def _generate_object(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate object that conforms to schema"""
        obj = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Generate required properties
        for prop in required:
            if prop in properties:
                obj[prop] = self._generate_value(properties[prop])
        
        # Optionally generate some non-required properties
        optional_props = [p for p in properties.keys() if p not in required]
        num_optional = random.randint(0, min(3, len(optional_props)))
        selected_optional = random.sample(optional_props, num_optional)
        
        for prop in selected_optional:
            obj[prop] = self._generate_value(properties[prop])
        
        # Add some additional properties if allowed
        if schema.get("additionalProperties", False):
            num_additional = random.randint(0, 2)
            for _ in range(num_additional):
                key = f"extra_{random.choice(string.ascii_lowercase)}{random.randint(1,99)}"
                obj[key] = self._generate_random_value()
        
        return obj
    
    def _generate_array(self, schema: Dict[str, Any]) -> List[Any]:
        """Generate array that conforms to schema"""
        items_schema = schema.get("items", {"type": "string"})
        min_items = schema.get("minItems", 0)
        max_items = schema.get("maxItems", 10)
        
        length = random.randint(min_items, min(max_items, 5))
        return [self._generate_value(items_schema) for _ in range(length)]
    
    def _generate_string(self, schema: Dict[str, Any]) -> str:
        """Generate string that conforms to schema"""
        if "enum" in schema:
            return random.choice(schema["enum"])
        
        format_type = schema.get("format")
        if format_type == "date-time":
            # Generate realistic datetime string
            base_time = datetime.now()
            offset_hours = random.randint(-24, 24)
            timestamp = base_time + timedelta(hours=offset_hours)
            return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif format_type == "email":
            domains = ["example.com", "test.org", "sample.net"]
            username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
            return f"{username}@{random.choice(domains)}"
        elif format_type == "uri":
            return f"https://example.com/{self._random_string(8)}"
        
        # Generate regular string
        min_length = max(1, schema.get("minLength", 1))
        max_length = min(100, schema.get("maxLength", 20))
        length = random.randint(min_length, max_length)
        
        # Choose character set based on context
        if "status" in schema.get("description", "").lower():
            return random.choice(["success", "error", "pending", "active", "inactive"])
        elif "message" in schema.get("description", "").lower():
            messages = ["Operation completed", "Request processed", "Action successful", "Task finished"]
            return random.choice(messages)
        else:
            return self._random_string(length)
    
    def _generate_integer(self, schema: Dict[str, Any]) -> int:
        """Generate integer that conforms to schema"""
        minimum = schema.get("minimum", -1000)
        maximum = schema.get("maximum", 1000)
        return random.randint(minimum, maximum)
    
    def _generate_number(self, schema: Dict[str, Any]) -> float:
        """Generate number that conforms to schema"""
        minimum = schema.get("minimum", -1000.0)
        maximum = schema.get("maximum", 1000.0)
        return random.uniform(minimum, maximum)
    
    def _random_string(self, length: int) -> str:
        """Generate random string of specified length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_random_value(self) -> Any:
        """Generate a random value of random type"""
        value_types = ["string", "integer", "boolean", "array"]
        chosen_type = random.choice(value_types)
        
        if chosen_type == "string":
            return self._random_string(random.randint(3, 15))
        elif chosen_type == "integer":
            return random.randint(1, 1000)
        elif chosen_type == "boolean":
            return random.choice([True, False])
        elif chosen_type == "array":
            return [self._random_string(5) for _ in range(random.randint(1, 3))]
    
    def generate_for_endpoint(self, method: str, path: str, num_variants: int = 5) -> List[Any]:
        """Generate test data for specific endpoint"""
        # Find schema file for this endpoint
        sanitized_name = self._sanitize_endpoint_name(method, path)
        
        if sanitized_name in self.schemas:
            return self.generate_from_schema(self.schemas[sanitized_name], num_variants)
        else:
            print(f"Warning: No schema found for {method} {path}")
            return []
    
    def _sanitize_endpoint_name(self, method: str, path: str) -> str:
        """Sanitize endpoint name to match schema filename"""
        import re
        sanitized = f"{method.lower()}_{path}"
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_')


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        schema_dir = sys.argv[1]
    else:
        schema_dir = os.path.join(os.path.dirname(__file__), "..", "DOCS", "api", "schema")
    
    generator = PropertyTestGenerator(schema_dir)
    
    # Generate some example data
    print("🎲 Property Test Data Generator")
    print(f"📁 Schema directory: {schema_dir}")
    print(f"📊 Loaded {len(generator.schemas)} schemas")
    
    # Show examples for first few schemas
    for i, (name, schema) in enumerate(list(generator.schemas.items())[:3]):
        print(f"\\n🔧 Generating data for: {name}")
        variants = generator.generate_from_schema(schema, 2)
        for j, variant in enumerate(variants):
            print(f"   Variant {j+1}: {json.dumps(variant, indent=2)}")
'''
        return generator_code


if __name__ == "__main__":
    # Configuration
    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    routing_atlas_path = os.path.join(REPO_ROOT, "DOCS/report/routing_atlas.json")
    schema_output_dir = os.path.join(REPO_ROOT, "DOCS/api/schema")
    
    # Generate schemas
    generator = JSONSchemaGenerator(routing_atlas_path, schema_output_dir)
    generator.generate_schemas_for_all_routes()
    
    # Save property test generator
    property_generator_code = generator.generate_property_test_data_generator()
    property_generator_path = os.path.join(REPO_ROOT, "tools", "property_test_generator.py")
    with open(property_generator_path, 'w', encoding='utf-8') as f:
        f.write(property_generator_code)
    
    print(f"🧪 Property test generator → {property_generator_path}")
    print(f"\n🎉 P15 Schema Generation Complete!")
    print(f"📊 Generated {len(generator.generated_schemas)} JSON schemas")
    print(f"📁 Schema directory: {schema_output_dir}")
