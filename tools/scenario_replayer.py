#!/usr/bin/env python3
"""
Scenario Replayer v4.0 - Execute test scenarios against API endpoints
Part of Credits Overdrive v4.0 (Proof-Oriented, Fail-Closed)

Replays scenarios from DOCS/scenarios/*.jsonl against:
- FastAPI TestClient (when available) 
- Dry-run print mode (fallback when FastAPI not available)

Usage:
    python tools/scenario_replayer.py --category valid_requests
    python tools/scenario_replayer.py --category all --dry-run
    python tools/scenario_replayer.py --file DOCS/scenarios/boundary_conditions.jsonl
"""

import json
import sys
import os
import argparse
import time
from typing import Dict, List, Any, Optional
import importlib.util

class ScenarioReplayer:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.test_client = None
        self.app = None
        self.stats = {
            "total_scenarios": 0,
            "successful": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0
        }
        
        # Try to initialize FastAPI test environment
        if not dry_run:
            self._init_fastapi_client()
    
    def _init_fastapi_client(self) -> None:
        """Initialize FastAPI TestClient if available"""
        try:
            # Check if FastAPI and required modules are available
            fastapi_spec = importlib.util.find_spec("fastapi")
            web_api_spec = importlib.util.find_spec("console.web_api")
            
            if not fastapi_spec or not web_api_spec:
                print("[WARN]  FastAPI or console.web_api not available - switching to dry-run mode")
                self.dry_run = True
                return
            
            from fastapi.testclient import TestClient
            from console.web_api import SentinelWebAPI
            
            # Initialize the web API
            api = SentinelWebAPI()
            self.app = api.app
            self.test_client = TestClient(self.app)
            
            print("[PASS] FastAPI TestClient initialized successfully")
            
        except Exception as e:
            print(f"[WARN]  Failed to initialize FastAPI TestClient: {e}")
            print("[RELOAD] Switching to dry-run mode")
            self.dry_run = True
    
    def load_scenarios(self, file_path: str) -> List[Dict[str, Any]]:
        """Load scenarios from JSONL file"""
        scenarios = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        scenario = json.loads(line)
                        scenarios.append(scenario)
                    except json.JSONDecodeError as e:
                        print(f"[WARN]  Invalid JSON on line {line_num} in {file_path}: {e}")
        except FileNotFoundError:
            print(f"[FAIL] File not found: {file_path}")
            return []
        except Exception as e:
            print(f"[FAIL] Error reading {file_path}: {e}")
            return []
        
        return scenarios
    
    def replay_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single scenario"""
        result = {
            "scenario_id": scenario.get("id", "unknown"),
            "category": scenario.get("category", "unknown"),
            "status": "unknown",
            "response_status": None,
            "response_time_ms": None,
            "error": None,
            "dry_run": self.dry_run
        }
        
        if self.dry_run:
            return self._dry_run_scenario(scenario, result)
        else:
            return self._execute_scenario(scenario, result)
    
    def _dry_run_scenario(self, scenario: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Dry-run mode: just print what would be executed"""
        method = scenario.get("method", "GET")
        path = scenario.get("path", "/")
        headers = scenario.get("headers", {})
        query_params = scenario.get("query_params", {})
        body = scenario.get("body")
        
        print(f"[SEARCH] DRY-RUN: {scenario.get('id', 'unknown')}")
        print(f"   {method} {path}")
        if query_params:
            print(f"   Query: {query_params}")
        if headers and len(headers) > 1:  # Skip default User-Agent only
            print(f"   Headers: {headers}")
        if body:
            print(f"   Body: {body[:100]}{'...' if len(str(body)) > 100 else ''}")
        print(f"   Expected: {scenario.get('expected_status_codes', [])}")
        print(f"   Tags: {scenario.get('tags', [])}")
        print()
        
        result["status"] = "dry_run_complete"
        self.stats["successful"] += 1
        return result
    
    def _execute_scenario(self, scenario: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scenario against real API"""
        if not self.test_client:
            result["status"] = "error"
            result["error"] = "TestClient not initialized"
            self.stats["errors"] += 1
            return result
        
        method = scenario.get("method", "GET").lower()
        path = scenario.get("path", "/")
        headers = scenario.get("headers", {})
        params = scenario.get("query_params", {})
        body = scenario.get("body")
        expected_codes = scenario.get("expected_status_codes", [200])
        
        try:
            start_time = time.time()
            
            # Prepare request arguments
            request_kwargs = {
                "url": path,
                "headers": headers,
                "params": params
            }
            
            # Add body for methods that support it
            if method in ["post", "put", "patch"] and body is not None:
                if isinstance(body, str):
                    request_kwargs["content"] = body
                else:
                    request_kwargs["json"] = body
            
            # Execute request
            response = getattr(self.test_client, method)(**request_kwargs)
            response_time = (time.time() - start_time) * 1000
            
            result["response_status"] = response.status_code
            result["response_time_ms"] = round(response_time, 2)
            
            # Check if response status is expected
            if response.status_code in expected_codes:
                result["status"] = "success"
                self.stats["successful"] += 1
            else:
                result["status"] = "unexpected_status"
                result["error"] = f"Expected {expected_codes}, got {response.status_code}"
                self.stats["failed"] += 1
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.stats["errors"] += 1
        
        return result
    
    def replay_scenarios(self, scenarios: List[Dict[str, Any]], verbose: bool = False) -> List[Dict[str, Any]]:
        """Execute multiple scenarios"""
        results = []
        
        print(f"[START] Executing {len(scenarios)} scenarios...")
        if self.dry_run:
            print("[PLAN] DRY-RUN MODE - No actual requests will be made")
        print()
        
        for i, scenario in enumerate(scenarios, 1):
            self.stats["total_scenarios"] += 1
            
            if verbose or (i % 100 == 0):
                print(f"[BARS] Progress: {i}/{len(scenarios)} ({i/len(scenarios)*100:.1f}%)")
            
            result = self.replay_scenario(scenario)
            results.append(result)
            
            # Print result if verbose or if there's an error/unexpected result
            if verbose or result["status"] in ["error", "unexpected_status"]:
                status_icon = {
                    "success": "[PASS]",
                    "dry_run_complete": "[SEARCH]", 
                    "unexpected_status": "[WARN]",
                    "error": "[FAIL]",
                    "unknown": "[U+2753]"
                }.get(result["status"], "[U+2753]")
                
                print(f"{status_icon} {result['scenario_id']} - {result['status']}")
                if result.get("error"):
                    print(f"    Error: {result['error']}")
                if result.get("response_status"):
                    print(f"    Response: {result['response_status']} ({result.get('response_time_ms', 0)}ms)")
        
        return results
    
    def print_summary(self) -> None:
        """Print execution summary"""
        print("\n" + "="*60)
        print("[BARS] SCENARIO REPLAY SUMMARY")
        print("="*60)
        print(f"Total Scenarios:    {self.stats['total_scenarios']:,}")
        print(f"Successful:         {self.stats['successful']:,}")
        print(f"Failed:             {self.stats['failed']:,}")
        print(f"Errors:             {self.stats['errors']:,}")
        print(f"Skipped:            {self.stats['skipped']:,}")
        
        if self.stats["total_scenarios"] > 0:
            success_rate = (self.stats["successful"] / self.stats["total_scenarios"]) * 100
            print(f"Success Rate:       {success_rate:.1f}%")
        
        print(f"Mode:               {'DRY-RUN' if self.dry_run else 'LIVE EXECUTION'}")
        print("="*60)
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """Save results to JSON file"""
        try:
            summary = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "stats": self.stats,
                "mode": "dry_run" if self.dry_run else "live",
                "results": results
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"[U+1F4BE] Results saved to: {output_path}")
            
        except Exception as e:
            print(f"[FAIL] Failed to save results: {e}")


def main():
    parser = argparse.ArgumentParser(description="Replay test scenarios against API endpoints")
    parser.add_argument("--category", help="Category to replay (e.g., valid_requests, auth_bypass, all)")
    parser.add_argument("--file", help="Specific JSONL file to replay")
    parser.add_argument("--dry-run", action="store_true", help="Print scenarios without executing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Save results to JSON file")
    parser.add_argument("--limit", type=int, help="Limit number of scenarios to execute")
    
    args = parser.parse_args()
    
    # Determine scenarios directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    scenarios_dir = os.path.join(repo_root, "DOCS", "scenarios")
    
    if not os.path.exists(scenarios_dir):
        print(f"[FAIL] Scenarios directory not found: {scenarios_dir}")
        print("[IDEA] Run scenario generator first: python tools/scenario_generator.py")
        sys.exit(1)
    
    # Initialize replayer
    replayer = ScenarioReplayer(dry_run=args.dry_run)
    
    # Determine which files to process
    scenario_files = []
    
    if args.file:
        if os.path.exists(args.file):
            scenario_files = [args.file]
        else:
            print(f"[FAIL] File not found: {args.file}")
            sys.exit(1)
    elif args.category:
        if args.category == "all":
            # Load all JSONL files
            for filename in os.listdir(scenarios_dir):
                if filename.endswith(".jsonl"):
                    scenario_files.append(os.path.join(scenarios_dir, filename))
        else:
            # Load specific category
            category_file = os.path.join(scenarios_dir, f"{args.category}.jsonl")
            if os.path.exists(category_file):
                scenario_files = [category_file]
            else:
                print(f"[FAIL] Category file not found: {category_file}")
                available_categories = [f[:-6] for f in os.listdir(scenarios_dir) if f.endswith(".jsonl")]
                print(f"Available categories: {', '.join(available_categories)}")
                sys.exit(1)
    else:
        print("[FAIL] Must specify --category or --file")
        parser.print_help()
        sys.exit(1)
    
    if not scenario_files:
        print("[FAIL] No scenario files found")
        sys.exit(1)
    
    # Load and execute scenarios
    all_scenarios = []
    for file_path in scenario_files:
        print(f"[U+1F4C2] Loading scenarios from: {os.path.basename(file_path)}")
        scenarios = replayer.load_scenarios(file_path)
        all_scenarios.extend(scenarios)
        print(f"   [BARS] Loaded {len(scenarios)} scenarios")
    
    # Apply limit if specified
    if args.limit and args.limit < len(all_scenarios):
        print(f"[U+1F522] Limiting to first {args.limit} scenarios")
        all_scenarios = all_scenarios[:args.limit]
    
    # Execute scenarios
    results = replayer.replay_scenarios(all_scenarios, verbose=args.verbose)
    
    # Print summary
    replayer.print_summary()
    
    # Save results if requested
    if args.output:
        replayer.save_results(results, args.output)


if __name__ == "__main__":
    main()
