# File: tools/api_contract_check.py
# Purpose: API contract freezer to detect breaking changes (P3-007)

from __future__ import annotations
import os
import sys
import json
import hashlib
import importlib.util
import inspect
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
import argparse
import logging
from datetime import datetime
from dataclasses import dataclass

# Add the project root to Python path to enable imports
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class APIEndpoint:
    """Represents an API endpoint"""
    path: str
    method: str
    handler: str
    parameters: List[str]
    response_fields: List[str]
    auth_required: bool
    feature_flag: Optional[str] = None


@dataclass
class APIContractDiff:
    """Represents differences between API contracts"""
    removed_endpoints: List[APIEndpoint]
    modified_endpoints: List[Tuple[APIEndpoint, APIEndpoint]]  # (old, new)
    added_endpoints: List[APIEndpoint]
    breaking_changes: List[str]
    non_breaking_changes: List[str]


class APIContractAnalyzer:
    """Analyzes API contracts and detects breaking changes"""
    
    def __init__(self):
        """Initialize API contract analyzer"""
        self.current_contract = {}
        self.baseline_contract = {}
        
    def extract_fastapi_routes(self) -> Dict[str, APIEndpoint]:
        """Extract API routes from FastAPI application
        
        Returns:
            dict: Mapping of route identifiers to endpoints
        """
        endpoints = {}
        
        try:
            # Import the FastAPI app
            from console.web_api import SentinelWebAPI
            from fastapi.routing import APIRoute
            
            # Create app instance
            web_api = SentinelWebAPI()
            app = web_api.app
            
            # Get all registered routes
            for route in app.routes:
                if isinstance(route, APIRoute) and route.path.startswith('/api/'):
                    # Extract endpoint details
                    path = route.path
                    methods = route.methods or {'GET'}
                    
                    for method in methods:
                        if method in {'OPTIONS', 'HEAD'}:
                            continue
                            
                        endpoint_id = f"{method}:{path}"
                        
                        # Get handler function
                        handler_func = route.endpoint
                        handler_name = f"{handler_func.__module__}.{handler_func.__name__}" if handler_func else "unknown"
                        
                        # Extract parameters from route path and function signature
                        parameters = []
                        
                        # Path parameters
                        if route.path_regex:
                            import re
                            path_params = re.findall(r'\{([^}]+)\}', path)
                            parameters.extend(path_params)
                        
                        # Function parameters (query, body, etc.)
                        if handler_func:
                            try:
                                sig = inspect.signature(handler_func)
                                for param_name, param in sig.parameters.items():
                                    if param_name not in parameters and param_name not in ['request', 'response']:
                                        parameters.append(param_name)
                            except (TypeError, ValueError):
                                pass
                        
                        # Determine if auth is required (basic heuristic)
                        auth_required = self._check_auth_required(handler_func, path)
                        
                        # Extract feature flag (basic heuristic)
                        feature_flag = self._extract_feature_flag(handler_func, path)
                        
                        # Analyze response structure (basic analysis)
                        response_fields = self._analyze_response_fields(handler_func)
                        
                        endpoint = APIEndpoint(
                            path=path,
                            method=method,
                            handler=handler_name,
                            parameters=sorted(parameters),
                            response_fields=sorted(response_fields),
                            auth_required=auth_required,
                            feature_flag=feature_flag
                        )
                        
                        endpoints[endpoint_id] = endpoint
                        
        except ImportError as e:
            logger.error(f"Could not import FastAPI app: {e}")
        except Exception as e:
            logger.error(f"Error extracting FastAPI routes: {e}")
            
        return endpoints
    
    def _check_auth_required(self, view_func: Any, path: str) -> bool:
        """Check if endpoint requires authentication
        
        Args:
            view_func: FastAPI view function
            path: Endpoint path
            
        Returns:
            bool: True if authentication required
        """
        # Basic heuristics for auth detection
        if '/admin/' in path:
            return True
            
        # Check for auth decorators (basic analysis)
        if hasattr(view_func, '__wrapped__'):
            # Look for common auth decorator patterns
            wrapper_names = []
            func = view_func
            while hasattr(func, '__wrapped__'):
                if hasattr(func, '__name__'):
                    wrapper_names.append(func.__name__)
                func = func.__wrapped__
                
            auth_indicators = ['auth_required', 'login_required', 'require_auth']
            return any(indicator in name.lower() for name in wrapper_names 
                      for indicator in auth_indicators)
        
        return False
    
    def _extract_feature_flag(self, view_func: Any, path: str) -> Optional[str]:
        """Extract feature flag from endpoint
        
        Args:
            view_func: FastAPI view function  
            path: Endpoint path
            
        Returns:
            str: Feature flag name or None
        """
        # Basic heuristics for feature flag detection
        flag_mapping = {
            '/api/auth/': 'CONSOLE_AUTH_ENABLED',
            '/api/stream/': 'STREAM_ENABLED', 
            '/api/admin/': 'ADMIN_AUTH_ENABLED',
            '/api/metrics/': 'HEALTH_ENDPOINT_ENABLED',
            '/api/plugins/': 'PLUGINS_ENABLED',
            '/api/export/': 'EXPORT_ENABLED'
        }
        
        for path_prefix, flag in flag_mapping.items():
            if path.startswith(path_prefix):
                return flag
                
        return None
    
    def _analyze_response_fields(self, view_func: Any) -> List[str]:
        """Analyze response fields from view function
        
        Args:
            view_func: FastAPI view function
            
        Returns:
            list: List of response field names
        """
        # This is a basic analysis - in a real implementation,
        # you might parse the function source code or use runtime analysis
        fields = []
        
        # Common response field patterns
        if hasattr(view_func, '__name__'):
            name = view_func.__name__.lower()
            if 'status' in name or 'health' in name:
                fields.extend(['status', 'timestamp'])
            if 'login' in name or 'auth' in name:
                fields.extend(['success', 'message', 'session_id'])
            if 'metrics' in name:
                fields.extend(['metrics', 'timestamp'])
            if 'stream' in name:
                fields.extend(['data', 'event_type'])
                
        return fields
    
    def generate_contract(self) -> Dict[str, Any]:
        """Generate current API contract
        
        Returns:
            dict: API contract specification
        """
        endpoints = self.extract_fastapi_routes()
        
        contract = {
            "version": "1.0",
            "generated_at": str(datetime.utcnow().isoformat()),
            "endpoints": {},
            "summary": {
                "total_endpoints": len(endpoints),
                "auth_required_count": sum(1 for ep in endpoints.values() if ep.auth_required),
                "feature_flagged_count": sum(1 for ep in endpoints.values() if ep.feature_flag)
            }
        }
        
        for endpoint_id, endpoint in endpoints.items():
            contract["endpoints"][endpoint_id] = {
                "path": endpoint.path,
                "method": endpoint.method,
                "handler": endpoint.handler,
                "parameters": endpoint.parameters,
                "response_fields": endpoint.response_fields,
                "auth_required": endpoint.auth_required,
                "feature_flag": endpoint.feature_flag
            }
            
        return contract
    
    def load_baseline_contract(self, baseline_file: str) -> Dict[str, Any]:
        """Load baseline contract from file
        
        Args:
            baseline_file: Path to baseline contract file
            
        Returns:
            dict: Baseline contract
        """
        baseline_path = Path(baseline_file)
        
        if not baseline_path.exists():
            logger.warning(f"Baseline contract file not found: {baseline_file}")
            return {}
            
        try:
            with open(baseline_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load baseline contract: {e}")
            return {}
    
    def save_contract(self, contract: Dict[str, Any], output_file: str) -> bool:
        """Save contract to file
        
        Args:
            contract: Contract specification
            output_file: Output file path
            
        Returns:
            bool: True if successful
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(contract, f, indent=2, sort_keys=True)
                
            logger.info(f"Contract saved to: {output_file}")
            return True
            
        except IOError as e:
            logger.error(f"Failed to save contract: {e}")
            return False
    
    def compare_contracts(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> APIContractDiff:
        """Compare two API contracts
        
        Args:
            baseline: Baseline contract
            current: Current contract
            
        Returns:
            APIContractDiff: Contract differences
        """
        baseline_endpoints = {ep_id: self._dict_to_endpoint(ep_data) 
                             for ep_id, ep_data in baseline.get("endpoints", {}).items()}
        current_endpoints = {ep_id: self._dict_to_endpoint(ep_data)
                            for ep_id, ep_data in current.get("endpoints", {}).items()}
        
        baseline_ids = set(baseline_endpoints.keys())
        current_ids = set(current_endpoints.keys())
        
        # Find changes
        removed_endpoints = [baseline_endpoints[ep_id] for ep_id in baseline_ids - current_ids]
        added_endpoints = [current_endpoints[ep_id] for ep_id in current_ids - baseline_ids]
        
        modified_endpoints = []
        for ep_id in baseline_ids & current_ids:
            baseline_ep = baseline_endpoints[ep_id]
            current_ep = current_endpoints[ep_id]
            
            if self._endpoints_differ(baseline_ep, current_ep):
                modified_endpoints.append((baseline_ep, current_ep))
        
        # Analyze breaking changes
        breaking_changes = []
        non_breaking_changes = []
        
        # Removed endpoints are breaking
        for endpoint in removed_endpoints:
            breaking_changes.append(f"Removed endpoint: {endpoint.method} {endpoint.path}")
        
        # Analyze modifications
        for old_ep, new_ep in modified_endpoints:
            changes = self._analyze_endpoint_changes(old_ep, new_ep)
            breaking_changes.extend(changes["breaking"])
            non_breaking_changes.extend(changes["non_breaking"])
        
        # Added endpoints are non-breaking
        for endpoint in added_endpoints:
            non_breaking_changes.append(f"Added endpoint: {endpoint.method} {endpoint.path}")
        
        return APIContractDiff(
            removed_endpoints=removed_endpoints,
            modified_endpoints=modified_endpoints,
            added_endpoints=added_endpoints,
            breaking_changes=breaking_changes,
            non_breaking_changes=non_breaking_changes
        )
    
    def _dict_to_endpoint(self, ep_data: Dict[str, Any]) -> APIEndpoint:
        """Convert dictionary to APIEndpoint object
        
        Args:
            ep_data: Endpoint data dictionary
            
        Returns:
            APIEndpoint: Endpoint object
        """
        return APIEndpoint(
            path=ep_data["path"],
            method=ep_data["method"],
            handler=ep_data["handler"],
            parameters=ep_data.get("parameters", []),
            response_fields=ep_data.get("response_fields", []),
            auth_required=ep_data.get("auth_required", False),
            feature_flag=ep_data.get("feature_flag")
        )
    
    def _endpoints_differ(self, ep1: APIEndpoint, ep2: APIEndpoint) -> bool:
        """Check if two endpoints differ
        
        Args:
            ep1: First endpoint
            ep2: Second endpoint
            
        Returns:
            bool: True if endpoints differ
        """
        return (ep1.handler != ep2.handler or
                ep1.parameters != ep2.parameters or
                ep1.response_fields != ep2.response_fields or
                ep1.auth_required != ep2.auth_required or
                ep1.feature_flag != ep2.feature_flag)
    
    def _analyze_endpoint_changes(self, old_ep: APIEndpoint, new_ep: APIEndpoint) -> Dict[str, List[str]]:
        """Analyze changes between two endpoints
        
        Args:
            old_ep: Original endpoint
            new_ep: New endpoint
            
        Returns:
            dict: Breaking and non-breaking changes
        """
        breaking = []
        non_breaking = []
        
        endpoint_desc = f"{old_ep.method} {old_ep.path}"
        
        # Handler changes are potentially breaking
        if old_ep.handler != new_ep.handler:
            breaking.append(f"Handler changed for {endpoint_desc}: {old_ep.handler} -> {new_ep.handler}")
        
        # Parameter changes
        old_params = set(old_ep.parameters)
        new_params = set(new_ep.parameters)
        
        removed_params = old_params - new_params
        added_params = new_params - old_params
        
        for param in removed_params:
            breaking.append(f"Parameter removed from {endpoint_desc}: {param}")
            
        for param in added_params:
            non_breaking.append(f"Parameter added to {endpoint_desc}: {param}")
        
        # Response field changes  
        old_fields = set(old_ep.response_fields)
        new_fields = set(new_ep.response_fields)
        
        removed_fields = old_fields - new_fields
        added_fields = new_fields - old_fields
        
        for field in removed_fields:
            breaking.append(f"Response field removed from {endpoint_desc}: {field}")
            
        for field in added_fields:
            non_breaking.append(f"Response field added to {endpoint_desc}: {field}")
        
        # Auth requirement changes
        if old_ep.auth_required != new_ep.auth_required:
            if new_ep.auth_required:
                breaking.append(f"Authentication now required for {endpoint_desc}")
            else:
                non_breaking.append(f"Authentication no longer required for {endpoint_desc}")
        
        # Feature flag changes
        if old_ep.feature_flag != new_ep.feature_flag:
            breaking.append(f"Feature flag changed for {endpoint_desc}: {old_ep.feature_flag} -> {new_ep.feature_flag}")
        
        return {"breaking": breaking, "non_breaking": non_breaking}


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="API Contract Checker for WatchLockAI Sentinel")
    parser.add_argument("--action", choices=["generate", "check"], required=True,
                       help="Action to perform")
    parser.add_argument("--baseline", default="DOCS/report/api_contract_baseline.json",
                       help="Baseline contract file")
    parser.add_argument("--output", default="DOCS/report/api_contract_current.json", 
                       help="Output contract file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose logging")
    parser.add_argument("--fail-on-breaking", action="store_true",
                       help="Exit with error code if breaking changes detected")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    analyzer = APIContractAnalyzer()
    
    if args.action == "generate":
        # Generate current contract
        logger.info("Generating API contract...")
        contract = analyzer.generate_contract()
        
        if analyzer.save_contract(contract, args.output):
            logger.info(f"Generated contract with {contract['summary']['total_endpoints']} endpoints")
            return 0
        else:
            return 1
            
    elif args.action == "check":
        # Check for breaking changes
        logger.info("Checking for API contract changes...")
        
        # Load baseline
        baseline = analyzer.load_baseline_contract(args.baseline)
        if not baseline:
            logger.error("Could not load baseline contract")
            return 1
        
        # Generate current contract
        current = analyzer.generate_contract()
        
        # Compare contracts
        diff = analyzer.compare_contracts(baseline, current)
        
        # Report results
        print("\n=== API Contract Analysis ===")
        print(f"Baseline: {args.baseline}")
        print(f"Current:  {len(current.get('endpoints', {}))} endpoints")
        
        if diff.breaking_changes:
            print(f"\n[FAIL] BREAKING CHANGES DETECTED ({len(diff.breaking_changes)}):")
            for change in diff.breaking_changes:
                print(f"  * {change}")
        
        if diff.non_breaking_changes:
            print(f"\n[PASS] Non-breaking changes ({len(diff.non_breaking_changes)}):")
            for change in diff.non_breaking_changes:
                print(f"  * {change}")
        
        if not diff.breaking_changes and not diff.non_breaking_changes:
            print("\n[PASS] No API changes detected")
        
        # Save updated contract
        if analyzer.save_contract(current, args.output):
            logger.info(f"Updated contract saved to: {args.output}")
        
        # Exit code
        if diff.breaking_changes and args.fail_on_breaking:
            print("\n[FAIL] Failing due to breaking changes")
            return 1
        
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[FAIL] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
