# __version__ = "1.0.0"
# __author__ = "CG & AI assistant"
# __creation_date__ = "2025-08-29"
# __modification_date__ = "2025-08-29"
# __purpose__ = "Utility script: audit_devagent.py"
# File: audit_devagent.py
# Location: root
# Developer: Craig & GPT-4
# Version: 1.1.0
# Last Modified: 2025-07-18
# Purpose: Audit DevAgentZero folder structure and required functions
# Notes: ASCII only, safe for CI output, no emojis

import ast
from pathlib import Path

REQUIRED_STRUCTURE = {
    "main.py": [],
    "agent_core": {
        "planner.py": ["plan_tasks"],
        "generator.py": ["generate_code"],
        "executor.py": ["execute_plan"],
    },
    "memory_store": {},
    "outputs": {},
    "logs": {},
}


def check_file_exists(path):
    try:
        return path.exists()
    except Exception:
        return False


def get_functions_in_file(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        return {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
    except Exception:
        return set()


def audit():
    root = Path.cwd()
    print(f"\n--- Auditing DevAgentZero structure at: {root} ---\n")

    for key, subitems in REQUIRED_STRUCTURE.items():
        key_path = root / key
        if isinstance(subitems, list):
            # This is a file
            if not check_file_exists(key_path):
                print(f"[MISSING] File: {key}")
                continue
            print(f"[OK] Found File: {key}")
            found_funcs = get_functions_in_file(key_path)
            for func in subitems:
                if func in found_funcs:
                    print(f"   [OK] Function: {func}()")
                else:
                    print(f"   [MISSING] Function: {func}()")
        elif isinstance(subitems, dict):
            # This is a folder
            if not check_file_exists(key_path):
                print(f"[MISSING] Folder: {key}/")
                continue
            print(f"[OK] Found Folder: {key}/")
            for subfile, funcs in subitems.items():
                file_path = key_path / subfile
                if not check_file_exists(file_path):
                    try:
                        alt_name = next(
                            (
                                f.name
                                for f in key_path.glob("*.py")
                                if f.name.lower() == subfile.lower()
                            ),
                            None,
                        )
                        if alt_name:
                            print(
                                f"   [WARN] Found '{alt_name}', but wrong casing. Rename to '{subfile}'"
                            )
                        else:
                            print(f"   [MISSING] File: {subfile}")
                    except Exception as e:
                        print(f"   [ERROR] Could not check for {subfile}: {e}")
                    continue
                print(f"   [OK] Found File: {subfile}")
                found_funcs = get_functions_in_file(file_path)
                for func in funcs:
                    if func in found_funcs:
                        print(f"       [OK] Function: {func}()")
                    else:
                        print(f"       [MISSING] Function: {func}()")


if __name__ == "__main__":
    audit()
