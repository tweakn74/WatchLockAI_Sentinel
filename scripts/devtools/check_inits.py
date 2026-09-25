# __version__ = "1.0.0"
# __author__ = "CG & AI assistant"
# __creation_date__ = "2025-08-25"
# __modification_date__ = "2025-08-27"
# __purpose__ = "Walks a directory tree and creates a manifest of __init__.py files,"
# ruff: noqa: E402
from __future__ import annotations

"""
__version__ = "0.1.0"
Purpose: Walks a directory tree and creates a manifest of __init__.py files,
Last Modified: 2025-08-25 17:21:54
"""
# file: check_inits.py
import os
import argparse

# Directories to exclude from the analysis
EXCLUDE_DIRS = {
    "venv",
    "__pycache__",
    ".git",
    "backups",
    "blueprint",
    "blueprints",
    "docs",
    "ffmpeg",
    "prompts",
    ".vscode",
    "tests",
}


def create_init_manifest(root_dir: str):
    """
    Walks a directory tree and creates a manifest of __init__.py files,
    highlighting directories that are missing one.
    """
    print(f"[SEARCH] Analyzing packages in: {os.path.abspath(root_dir)}\n")

    missing_inits = []
    found_inits = []

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # This line prevents the walker from descending into excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        # Check if the current directory itself is in the exclude list (for the root case)
        if os.path.basename(dirpath) in EXCLUDE_DIRS:
            continue

        # Check if the directory contains any Python source files
        has_py_files = any(fname.endswith(".py") for fname in filenames)

        # We only care about directories intended to be packages
        if not has_py_files:
            continue

        has_init_py = "__init__.py" in filenames

        relative_path = os.path.relpath(dirpath, root_dir)
        # Use '.' for the root directory itself for clarity
        if relative_path == ".":
            relative_path = "(root directory)"

        if has_init_py:
            found_inits.append(relative_path)
        else:
            missing_inits.append(relative_path)

    # --- Print the Final Report ---
    print("--- `__init__.py` Manifest ---")

    if found_inits:
        print("\n[PASS] Found `__init__.py` in the following packages:")
        for path in sorted(found_inits):
            print(f"   - {path}")

    if missing_inits:
        print("\n[WARN]  WARNING: Missing `__init__.py` in these directories:")
        for path in sorted(missing_inits):
            print(f"   - {path}  <-- ACTION REQUIRED")
        print("\nThese directories may not be treated as regular packages.")

    if not found_inits and not missing_inits:
        print("\nNo Python packages were found to analyze.")

    print("\n" + "-" * 31)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyzes a project for missing __init__.py files."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="The project directory to analyze. Defaults to the current directory.",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: Directory not found at '{args.directory}'")
    else:
        create_init_manifest(args.directory)
