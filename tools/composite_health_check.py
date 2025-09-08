#!/usr/bin/env python3
# File: tools/composite_health_check.py
# Purpose: Composite health endpoint validation against RC-1 baseline

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

def load_rc1_baseline() -> Dict[str, Any]:
    """Load RC-1 evidence files as baseline"""
    baseline = {}
    report_dir = Path(REPO_ROOT) / "DOCS" / "report"
    
    try:
        # Load metadata
        with open(report_dir / "rc1_meta.json") as f:
            baseline["metadata"] = json.load(f)
            
        # Load hashes
        with open(report_dir / "rc1_hashes.json") as f:
            baseline["hashes"] = json.load(f)
            
        # Load flags
        with open(report_dir / "rc1_flags.json") as f:
            baseline["flags"] = json.load(f)
            
        # Load anti-skip status
        with open(report_dir / "rc1_anti_skip.txt") as f:
            baseline["anti_skip"] = f.read().strip()
            
        # Load proofs
        baseline["proofs"] = []
        with open(report_dir / "rc1_proofs.jsonl") as f:
            for line in f:
                baseline["proofs"].append(json.loads(line.strip()))
                
    except Exception as e:
        print(f"❌ Failed to load RC-1 baseline: {e}")
        return {}
        
    return baseline

def check_file_integrity(baseline_hashes: Dict[str, str]) -> Dict[str, Any]:
    """Verify file integrity against RC-1 baseline hashes"""
    results = {"status": "PASS", "violations": [], "checked": 0}
    
    for file_path, expected_hash in baseline_hashes.items():
        if expected_hash == "MISSING":
            continue
            
        try:
            full_path = Path(REPO_ROOT) / file_path
            if not full_path.exists():
                results["violations"].append(f"{file_path}: File disappeared since RC-1")
                continue
                
            with open(full_path, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
                
            if actual_hash != expected_hash:
                results["violations"].append(f"{file_path}: Hash mismatch (expected {expected_hash[:16]}..., got {actual_hash[:16]}...)")
            else:
                results["checked"] += 1
                
        except Exception as e:
            results["violations"].append(f"{file_path}: Error checking - {e}")
    
    if results["violations"]:
        results["status"] = "FAIL"
        
    return results

def check_flag_consistency(baseline_flags: Dict[str, str]) -> Dict[str, Any]:
    """Verify feature flags remain in expected state"""
    results = {"status": "PASS", "violations": [], "checked": 0}
    
    for flag_name, expected_value in baseline_flags.items():
        actual_value = os.getenv(flag_name, "0")
        if actual_value != expected_value:
            results["violations"].append(f"{flag_name}: Expected {expected_value}, got {actual_value}")
        else:
            results["checked"] += 1
    
    if results["violations"]:
        results["status"] = "FAIL"
        
    return results

def run_proof_consistency_check(baseline_proofs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Re-run key proofs and verify they still pass"""
    results = {"status": "PASS", "violations": [], "checked": 0}
    
    # Re-run verification claims
    try:
        os.chdir(REPO_ROOT)
        import subprocess
        
        # Check verify_minimax_claims
        result = subprocess.run([sys.executable, "tools/verify_minimax_claims.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0 or "VERIFICATION PASS" not in result.stdout:
            results["violations"].append("verify_minimax_claims: No longer passing")
        else:
            results["checked"] += 1
            
        # Check self_check
        result = subprocess.run([sys.executable, "tools/self_check.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0 or "All critical tests passed" not in result.stdout:
            results["violations"].append("self_check: No longer passing")
        else:
            results["checked"] += 1
            
    except Exception as e:
        results["violations"].append(f"Proof execution error: {e}")
        
    if results["violations"]:
        results["status"] = "FAIL"
        
    return results

def main():
    """Composite health validation against RC-1 baseline"""
    print("🏥 Composite Health Check vs RC-1 Baseline")
    print("=" * 50)
    
    # Load RC-1 baseline
    baseline = load_rc1_baseline()
    if not baseline:
        print("❌ Cannot proceed without RC-1 baseline")
        return 1
        
    print(f"✅ RC-1 baseline loaded: {baseline['metadata']['version']} from {baseline['metadata']['timestamp_utc']}")
    
    # Check file integrity
    print("\n🔍 File Integrity Check...")
    integrity_results = check_file_integrity(baseline["hashes"])
    print(f"   Status: {integrity_results['status']} ({integrity_results['checked']} files verified)")
    if integrity_results['violations']:
        for violation in integrity_results['violations'][:3]:  # Show first 3
            print(f"   ❌ {violation}")
        if len(integrity_results['violations']) > 3:
            print(f"   ... and {len(integrity_results['violations']) - 3} more violations")
    
    # Check flag consistency
    print("\n🏁 Feature Flag Consistency...")
    flag_results = check_flag_consistency(baseline["flags"])
    print(f"   Status: {flag_results['status']} ({flag_results['checked']} flags verified)")
    if flag_results['violations']:
        for violation in flag_results['violations']:
            print(f"   ❌ {violation}")
    
    # Check proof consistency
    print("\n🔬 Proof Re-execution...")
    proof_results = run_proof_consistency_check(baseline["proofs"])
    print(f"   Status: {proof_results['status']} ({proof_results['checked']} proofs verified)")
    if proof_results['violations']:
        for violation in proof_results['violations']:
            print(f"   ❌ {violation}")
    
    # Overall status
    all_checks = [integrity_results, flag_results, proof_results]
    overall_status = "PASS" if all(check["status"] == "PASS" for check in all_checks) else "FAIL"
    total_violations = sum(len(check["violations"]) for check in all_checks)
    
    print(f"\n" + "=" * 50)
    print(f"🏥 Composite Health: {overall_status}")
    if overall_status == "PASS":
        print("✅ System maintains RC-1 baseline integrity")
    else:
        print(f"❌ {total_violations} violations detected since RC-1")
    
    return 0 if overall_status == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
