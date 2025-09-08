#!/usr/bin/env python3
# Generate repo inventory with file hashes
import os
import json
import hashlib
from pathlib import Path

def sha256_of(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "error"

def generate_inventory():
    repo_root = Path(".")
    inventory = {}
    
    for path in repo_root.rglob("*"):
        if path.is_file():
            rel_path = str(path.relative_to(repo_root)).replace("\\", "/")
            # Skip some unnecessary files
            if any(skip in rel_path for skip in [".git/", "__pycache__/", ".pyc", "node_modules/"]):
                continue
            inventory[rel_path] = {
                "size": path.stat().st_size,
                "sha256": sha256_of(path)
            }
    
    return inventory

if __name__ == "__main__":
    inv = generate_inventory()
    with open("DOCS/report/repo_inventory.json", "w") as f:
        json.dump(inv, f, indent=2, sort_keys=True)
    print(f"Generated inventory for {len(inv)} files")
