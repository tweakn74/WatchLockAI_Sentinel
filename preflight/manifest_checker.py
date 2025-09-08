#!/usr/bin/env python3
# preflight/manifest_checker.py

from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(manifest_path: Path) -> Dict:
    if not manifest_path.exists():
        return {"files": []}
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_manifest(root: Path, manifest_path: Path) -> Tuple[bool, List[Dict]]:
    """
    Returns (ok, issues)
    issues entries: {"file": str, "expected": str, "actual": str, "status": "missing|mismatch|ok"}
    """
    manifest = load_manifest(manifest_path)
    issues: List[Dict] = []

    for entry in manifest.get("files", []):
        rel = entry.get("path")
        expected = entry.get("sha256")
        target = (root / rel).resolve()
        if not target.exists():
            issues.append(
                {"file": rel, "expected": expected, "actual": None, "status": "missing"}
            )
            continue
        actual = sha256_file(target)
        if expected and expected.lower() != actual.lower():
            issues.append(
                {
                    "file": rel,
                    "expected": expected,
                    "actual": actual,
                    "status": "mismatch",
                }
            )
        else:
            issues.append(
                {"file": rel, "expected": expected, "actual": actual, "status": "ok"}
            )

    ok = all(i["status"] == "ok" for i in issues) if issues else True
    return ok, issues
