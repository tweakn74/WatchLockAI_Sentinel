# =====================================================================
# File: scan_imports.py
# Developer: Craig and ChatGPT 4o
# Location: root
# Version: 2.3.0
# Modified: 2025-07-29
# Purpose:
#   Scan DevAgentZero for non-namespaced imports and optionally fix
#   them interactively with user confirmation. Always scans from
#   DevAgentZero project root (script location).
# =====================================================================

import os
import re
import json
from pathlib import Path
import shutil

# Directories to skip
EXCLUDE_DIRS = {"venv", "__pycache__", "backups", "logs"}

# Internal modules that MUST be namespaced
CORE_MODULES = [
    "planner",
    "executor",
    "generator",
    "tone_interpreter",
    "reflection_engine",
    "personality_core",
    "task_manager",
    "risk_engine",
    "system_diagnostics",
    "llm_mesh_orchestrator",
    "model_manager",
    "pointer_resolver",
    "user_profile",
    "sentinel_event_taxonomy",
]

IMPORT_PATTERN = re.compile(r"^\s*(from|import)\s+([\w\.]+)")
issues_found = []


def scan_file(file_path: Path):
    """Scan file for bad imports."""
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                match = IMPORT_PATTERN.match(line)
                if match:
                    module_name = match.group(2).split(".")[0]
                    if module_name in CORE_MODULES and not line.strip().startswith(
                        "from agent_core"
                    ):
                        issues_found.append(
                            {
                                "file": str(file_path),
                                "line": line_num,
                                "content": line.rstrip(),
                            }
                        )
    except Exception as e:
        print(f"[ERROR] Could not scan {file_path}: {e}")


def scan_directory(root_dir: Path):
    """Recursively scan for Python files starting from root_dir."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for file in filenames:
            if file.endswith(".py"):
                scan_file(Path(dirpath) / file)


def apply_fixes():
    """Apply agent_core prefix fixes to offending lines and show before/after."""
    if not issues_found:
        print("[OK] No issues to fix.")
        return

    # Group issues by file
    issues_by_file = {}
    for issue in issues_found:
        issues_by_file.setdefault(issue["file"], []).append(issue)

    print("\n=== Fix Summary ===")
    print(f"Files to patch: {len(issues_by_file)}")
    print(f"Total lines to patch: {len(issues_found)}")
    print("-------------------")

    for file_path, file_issues in issues_by_file.items():
        path = Path(file_path)
        backup_path = path.with_suffix(path.suffix + ".bak")
        print(f"\n[FIX] Backing up and patching: {file_path}")

        shutil.copy2(path, backup_path)

        lines = path.read_text(encoding="utf-8").splitlines()

        for issue in file_issues:
            idx = issue["line"] - 1
            old_line = lines[idx]
            if "from " in old_line:
                new_line = old_line.replace("from ", "from agent_core.")
            elif "import " in old_line and not old_line.startswith("from"):
                new_line = old_line.replace("import ", "import agent_core.")
            else:
                continue

            print(f"  Line {issue['line']}:")
            print(f"    - {old_line}")
            print(f"    + {new_line}")

            lines[idx] = new_line

        path.write_text("\n".join(lines), encoding="utf-8")

    print(
        f"\n[INFO] Fix applied to {len(issues_by_file)} files. Backups saved with .bak suffix."
    )


def main():
    # Lock scan root to script's location
    root_dir = Path(__file__).resolve().parent
    print("=== DevAgentZero Import Scanner/Fixer ===")
    print(f"Scanning full project from: {root_dir}\n")

    scan_directory(root_dir)

    if issues_found:
        print(f"\n[!] Found {len(issues_found)} non-namespaced imports:\n")
        for issue in issues_found:
            print(f"{issue['file']}:{issue['line']} -> {issue['content']}")

        # Save detailed report
        output_path = root_dir / "logs/import_scan_report.json"
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(json.dumps(issues_found, indent=2), encoding="utf-8")
        print(f"\n[INFO] Detailed report saved to {output_path.resolve()}")

        # Prompt to fix
        choice = input("\nApply fixes now? (Y/N): ").strip().lower()
        if choice == "y":
            apply_fixes()
        else:
            print("\n[INFO] No changes made.")
    else:
        print("\n[OK] All imports are properly namespaced.")


if __name__ == "__main__":
    main()

# =====================================================================
# End of Script
# Version: 2.3.0
# =====================================================================
