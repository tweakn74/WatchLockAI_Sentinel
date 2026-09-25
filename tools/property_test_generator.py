#!/usr/bin/env python3
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
    print("[U+1F3B2] Property Test Data Generator")
    print(f"[U+1F4C1] Schema directory: {schema_dir}")
    print(f"[BARS] Loaded {len(generator.schemas)} schemas")
    
    # Show examples for first few schemas
    for i, (name, schema) in enumerate(list(generator.schemas.items())[:3]):
        print(f"\n[U+1F527] Generating data for: {name}")
        variants = generator.generate_from_schema(schema, 2)
        for j, variant in enumerate(variants):
            print(f"   Variant {j+1}: {json.dumps(variant, indent=2)}")
