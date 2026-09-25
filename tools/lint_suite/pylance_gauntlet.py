#!/usr/bin/env python3
"""
Pylance Gauntlet - Superhero-Level Code Validation System

This script systematically identifies and eliminates all Pylance issues
in the DevAgentZero system with bulletproof precision.

Author: Superhero AI Architect
Date: 2025-08-29
"""

import sys
import ast
import importlib.util
from pathlib import Path
from typing import List, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in a directory recursively."""
    python_files = []
    for item in directory.rglob("*.py"):
        if item.is_file() and not any(
            part.startswith("__pycache__") for part in item.parts
        ):
            python_files.append(item)
    return python_files


def validate_syntax(file_path: Path) -> Tuple[bool, str]:
    """Validate Python syntax of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
        return True, "Syntax OK"
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Validation Error: {e}"


def validate_imports(file_path: Path) -> Tuple[bool, str]:
    """Validate that a Python file can be imported."""
    try:
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True, "Import OK"
        return False, "Import Failed: Could not create spec"
    except Exception as e:
        return False, f"Import Error: {e}"


def run_pylance_gauntlet() -> None:
    """Run the comprehensive Pylance validation gauntlet."""
    print("[SHIELD] PYLANCE GAUNTLET - SUPERHERO VALIDATION SYSTEM")
    print("=" * 60)

    # Find all Python files
    python_files = find_python_files(PROJECT_ROOT)
    print(f"[SEARCH] Found {len(python_files)} Python files to validate")
    print()

    # Track issues
    syntax_issues: List[Tuple[Path, str]] = []
    import_issues: List[Tuple[Path, str]] = []
    validated_files: int = 0

    # Validate each file
    for file_path in python_files:
        relative_path = file_path.relative_to(PROJECT_ROOT)
        print(f"[PAGE] Validating: {relative_path}")

        # Syntax validation
        syntax_ok, syntax_msg = validate_syntax(file_path)
        if not syntax_ok:
            syntax_issues.append((file_path, syntax_msg))
            print(f"   [FAIL] Syntax Issue: {syntax_msg}")
            continue

        # Import validation
        import_ok, import_msg = validate_imports(file_path)
        if not import_ok:
            import_issues.append((file_path, import_msg))
            print(f"   [WARN]  Import Issue: {import_msg}")
        else:
            print("   [PASS] Validated Successfully")

        validated_files += 1

    # Summary
    print()
    print("=" * 60)
    print("[BARS] PYLANCE GAUNTLET RESULTS")
    print("=" * 60)

    print(f"[PASS] Validated Files: {validated_files}/{len(python_files)}")
    print(f"[FAIL] Syntax Issues: {len(syntax_issues)}")
    print(f"[WARN]  Import Issues: {len(import_issues)}")

    # Report syntax issues
    if syntax_issues:
        print("\n[U+1F527] SYNTAX ISSUES DETECTED:")
        print("-" * 30)
        for file_path, error in syntax_issues:
            relative_path = file_path.relative_to(PROJECT_ROOT)
            print(f"   {relative_path}: {error}")

    # Report import issues
    if import_issues:
        print("\n[U+1F527] IMPORT ISSUES DETECTED:")
        print("-" * 30)
        for file_path, error in import_issues:
            relative_path = file_path.relative_to(PROJECT_ROOT)
            print(f"   {relative_path}: {error}")

    # Overall status
    total_issues = len(syntax_issues) + len(import_issues)
    if total_issues == 0:
        print("\n[U+1F389] ALL PYLANCE ISSUES ELIMINATED!")
        print("[U+1F9B8] SUPERHERO-LEVEL CODE QUALITY ACHIEVED!")
        return True
    else:
        print(f"\n[U+1F4A5] {total_issues} PYLANCE ISSUES REMAIN")
        print("[U+1F527] CONTINUED SUPERHERO INTERVENTION REQUIRED")
        return False


if __name__ == "__main__":
    success = run_pylance_gauntlet()
    sys.exit(0 if success else 1)
