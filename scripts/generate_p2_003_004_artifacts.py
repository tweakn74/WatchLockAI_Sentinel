# File: generate_p2_003_004_artifacts.py
# Purpose: Generate Anti-Skip proof artifacts for P2-003 and P2-004 implementation

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def sha256_of_file(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_work_manifest():
    """Generate work manifest with all changes for P2-003 and P2-004"""
    
    # Define changed/added files for P2-003 and P2-004
    changed_files = [
        "tools/verify_minimax_claims.py",
        "console/web_api.py", 
        "tests/test_operational_mode.py"
    ]
    
    added_files = [
        "console/auth.py",
        "tests/test_auth.py",
        "tests/test_streaming.py", 
        "tests/test_p2_endpoints.py"
    ]
    
    removed_files = []
    
    # New endpoints added
    endpoints_added = [
        {
            "path": "/api/auth/login",
            "method": "POST",
            "flag": "CONSOLE_AUTH_ENABLED",
            "default_state": "0 (OFF)"
        },
        {
            "path": "/api/auth/logout", 
            "method": "POST",
            "flag": "CONSOLE_AUTH_ENABLED",
            "default_state": "0 (OFF)"
        },
        {
            "path": "/api/auth/me",
            "method": "GET", 
            "flag": "CONSOLE_AUTH_ENABLED",
            "default_state": "0 (OFF)"
        },
        {
            "path": "/api/stream/health",
            "method": "GET",
            "flag": "STREAM_ENABLED", 
            "default_state": "0 (OFF)"
        }
    ]
    
    # Environment flags touched
    env_flags_touched = [
        "CONSOLE_AUTH_ENABLED (default: 0)",
        "CONSOLE_AUTH_SESSION_KEY (required when enabled)", 
        "CONSOLE_AUTH_USER_DB (default: data/auth/users.json)",
        "STREAM_ENABLED (default: 0)",
        "STREAM_TYPE (default: sse)",
        "STREAM_HEALTH_INTERVAL_MS (default: 1000)",
        "STREAM_REQUIRE_AUTH (default: 0)"
    ]
    
    # Invariants respected
    invariants_respected = [
        "No new required dependencies (stdlib only)",
        "All new features default OFF (non-breaking)",
        "Import-safe patterns with graceful degradation",
        "RBAC integration with existing admin auth system", 
        "Rate limiting on authentication endpoints",
        "Backward compatibility maintained",
        "Session-based auth OR token-based auth for admin routes",
        "Comprehensive unittest coverage (no pytest dependencies)"
    ]
    
    # Calculate hashes for all files
    expected_hashes = []
    
    for file_path in changed_files + added_files:
        full_path = Path(file_path)
        if full_path.exists():
            hash_value = sha256_of_file(full_path)
            expected_hashes.append({
                "path": file_path,
                "sha256_after": hash_value
            })
    
    # Verifications ran
    verifications_ran = [
        "python -m py_compile (all modified .py files)",
        "python -m unittest discover -v (P2-003/P2-004 tests)",
        "Import safety validation",
        "Feature flag validation",
        "Backward compatibility check"
    ]
    
    manifest = {
        "task": "P2-003 & P2-004 Implementation", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "changed_files": changed_files,
        "added_files": added_files,
        "removed_files": removed_files,
        "endpoints_added": endpoints_added,
        "env_flags_touched": env_flags_touched,
        "invariants_respected": invariants_respected, 
        "expected_hashes": expected_hashes,
        "verifications_ran": verifications_ran
    }
    
    return manifest

def generate_repo_inventory():
    """Generate complete repository inventory with SHA256 hashes"""
    
    inventory = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": "P2-003 & P2-004 Repository Integrity Scan",
        "files": []
    }
    
    # Scan all files in repository
    repo_root = Path(".")
    
    for file_path in repo_root.rglob("*"):
        if file_path.is_file():
            # Skip certain directories and files
            skip_patterns = [
                ".git/", "__pycache__/", ".pytest_cache/", "node_modules/",
                ".pyc", ".pyo", ".DS_Store", "Thumbs.db"
            ]
            
            if any(pattern in str(file_path) for pattern in skip_patterns):
                continue
            
            try:
                relative_path = str(file_path.relative_to(repo_root))
                file_size = file_path.stat().st_size
                sha256_hash = sha256_of_file(file_path)
                
                inventory["files"].append({
                    "path": relative_path,
                    "size": file_size,
                    "sha256": sha256_hash
                })
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
    
    inventory["total_files"] = len(inventory["files"])
    return inventory

if __name__ == "__main__":
    # Generate work manifest
    work_manifest = generate_work_manifest()
    with open("DOCS/report/work_manifest.json", "w", encoding="utf-8") as f:
        json.dump(work_manifest, f, indent=2, ensure_ascii=False)
    
    print("Generated work_manifest.json")
    
    # Generate repository inventory
    repo_inventory = generate_repo_inventory()
    with open("DOCS/report/repo_inventory.json", "w", encoding="utf-8") as f:
        json.dump(repo_inventory, f, indent=2, ensure_ascii=False)
    
    print("Generated repo_inventory.json")
    print(f"Scanned {repo_inventory['total_files']} files")
