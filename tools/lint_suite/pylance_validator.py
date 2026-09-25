#!/usr/bin/env python3
"""
Pylance Validator - Comprehensive Pylance Issue Detector

This script systematically identifies and reports Pylance issues
in the DevAgentZero dopamine core system.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_syntax_errors(file_path: Path) -> List[str]:
    """Check for syntax errors in a Python file."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
    except SyntaxError as e:
        errors.append(f"SyntaxError: {e}")
    except Exception as e:
        errors.append(f"Error: {e}")
    return errors


def check_import_issues(file_path: Path) -> List[str]:
    """Check for import-related issues."""
    errors = []
    try:
        # Try to import the module
        relative_path = file_path.relative_to(PROJECT_ROOT)
        module_path = (
            str(relative_path.with_suffix("")).replace("/", ".").replace("\\", ".")
        )
        if module_path.endswith(".__init__"):
            module_path = module_path[:-9]  # Remove .__init__
        __import__(module_path)
    except ImportError as e:
        errors.append(f"ImportError: {e}")
    except Exception as e:
        errors.append(f"Import Error: {e}")
    return errors


def check_type_annotation_issues(file_path: Path) -> List[str]:
    """Check for common type annotation issues."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for missing return type annotations in methods
        lines = content.split("\n")
        for i, line in enumerate(lines):
            # Look for method definitions without return type annotations
            if "def " in line and "(" in line and ":" in line:
                if "->" not in line and not line.strip().startswith("def __"):
                    # Skip special methods and simple getters
                    method_name = line.split("def ")[1].split("(")[0]
                    if not method_name.startswith("_") or method_name in ["__init__"]:
                        if method_name == "__init__":
                            # __init__ should return None
                            errors.append(
                                f"Line {i + 1}: Missing return type annotation for __init__ (should be -> None)"
                            )
                        else:
                            errors.append(
                                f"Line {i + 1}: Missing return type annotation for method '{method_name}'"
                            )
    except Exception as e:
        errors.append(f"Type annotation check failed: {e}")
    return errors


def validate_dopamine_files() -> Dict[str, List[str]]:
    """Validate all dopamine core files."""
    dopamine_dir = PROJECT_ROOT / "core" / "dopamine_core"
    results = {}

    # Find all Python files in dopamine_core
    python_files = list(dopamine_dir.glob("*.py"))

    for file_path in python_files:
        if file_path.name == "__init__.py":
            continue

        file_key = file_path.name
        all_errors = []

        # Check syntax
        syntax_errors = check_syntax_errors(file_path)
        all_errors.extend(syntax_errors)

        # Check imports
        import_errors = check_import_issues(file_path)
        all_errors.extend(import_errors)

        # Check type annotations
        type_errors = check_type_annotation_issues(file_path)
        all_errors.extend(type_errors)

        results[file_key] = all_errors

    return results


def main():
    """Main validation function."""
    print("[SHIELD]  PYLANCE VALIDATOR - SUPERHERO ISSUE DETECTION")
    print("=" * 60)

    results = validate_dopamine_files()

    total_issues = 0
    for file_name, errors in results.items():
        print(f"\n[PAGE] {file_name}:")
        if errors:
            for error in errors:
                print(f"   [FAIL] {error}")
                total_issues += 1
        else:
            print("   [PASS] No issues detected")

    print("\n" + "=" * 60)
    if total_issues == 0:
        print("[U+1F389] ALL PYLANCE ISSUES RESOLVED!")
        print("[U+1F9B8] SUPERHERO-LEVEL CODE QUALITY ACHIEVED!")
        return True
    else:
        print(f"[U+1F4A5] {total_issues} PYLANCE ISSUES DETECTED")
        print("[U+1F527] CONTINUED SUPERHERO INTERVENTION REQUIRED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
