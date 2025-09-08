# File: manifest_manager.py
# Developer: Craig and ChatGPT 4o
# Location: root
# Version: 1.0.0
# Created Date: 2025-07-29
# Purpose: Full inventory and placement validation for DevAgentZero
# Recent Change: Implemented Stage 1 features (inventory + placement validation)

"""
Blueprint and roadmap for manifest_manager.py is documented above this code section.
See design block for full details (future Stage 2: hashing, malware defense, etc.).
"""

import json
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()

# Paths
ROOT_DIR = Path(".")
MANIFEST_FILE = Path("manifest.json")
MASTER_NAMES_FILE = Path("Blueprints/master_new_names.txt")
EXCLUDE_DIRS = {"backups", "logs", "__pycache__"}

# Supported file types
TRACKED_EXTENSIONS = [".py", ".txt", ".json", ".docx"]

# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------


def load_canonical_names():
    """
    Load canonical names from master_new_names.txt if available.
    Returns a dict of {filename: canonical_path or None}.
    """
    canonical = {}
    if MASTER_NAMES_FILE.exists():
        lines = MASTER_NAMES_FILE.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if "→" in line:
                parts = line.split("→")
                if len(parts) == 2:
                    canonical_name = parts[1].strip()
                    canonical[canonical_name] = canonical_name
            else:
                # Fallback: treat entire line as canonical name
                canonical[line.strip()] = line.strip()
    return canonical


def extract_metadata(file_path: Path):
    """
    Extract metadata: version (header) and char count.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        content = ""
    char_count = len(content)
    version = "unknown"
    for line in content.splitlines()[:10]:
        if line.lower().startswith("# version"):
            version = line.split(":")[1].strip()
            break
    return version, char_count


def scan_all_files():
    """
    Scan all files recursively under ROOT_DIR (excluding backups/logs).
    Returns dict keyed by relative file path with metadata.
    """
    inventory = {}
    for file_path in ROOT_DIR.rglob("*"):
        if file_path.is_file() and file_path.suffix in TRACKED_EXTENSIONS:
            if any(excl in file_path.parts for excl in EXCLUDE_DIRS):
                continue
            rel_path = str(file_path.relative_to(ROOT_DIR))
            version, char_count = extract_metadata(file_path)
            inventory[rel_path] = {
                "canonical_path": rel_path,  # Will refine with canonical matching
                "actual_path": rel_path,
                "status": "unknown",  # updated later
                "version": version,
                "char_count": char_count,
                "hash": None,  # future stage
            }
    return inventory


def classify_files(inventory, canonical_names):
    """
    Determine canonical vs supplemental status for files based on master_new_names.txt
    """
    for rel_path, meta in inventory.items():
        file_name = Path(rel_path).name
        if file_name in canonical_names:
            meta["status"] = "canonical"
        else:
            meta["status"] = "supplemental"
    return inventory


def compare_with_existing(inventory):
    """
    Compare current inventory to existing manifest.json if present.
    Return new, missing, and misplaced files.
    """
    new_files = []
    missing_files = []
    misplaced_files = []

    if MANIFEST_FILE.exists():
        old_manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        old_files = old_manifest.get("files", {})

        # New files
        for path in inventory:
            if path not in old_files:
                new_files.append(path)

        # Missing files
        for path in old_files:
            if path not in inventory:
                missing_files.append(path)

        # Misplaced files (same name, different folder)
        for path in inventory:
            for old_path in old_files:
                if Path(path).name == Path(old_path).name and path != old_path:
                    misplaced_files.append(path)
    else:
        new_files = list(inventory.keys())  # everything is new if no manifest exists

    return new_files, missing_files, misplaced_files


def save_manifest(inventory):
    """
    Save manifest.json with header and summary.
    """
    summary = {
        "total_files": len(inventory),
        "canonical_files": sum(
            1 for v in inventory.values() if v["status"] == "canonical"
        ),
        "supplemental_files": sum(
            1 for v in inventory.values() if v["status"] == "supplemental"
        ),
    }

    manifest = {
        "_header": {
            "file": "manifest.json",
            "version": "1.0.0",
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "developer": "Craig and ChatGPT 4o",
            "purpose": "Full canonical inventory and placement validation for DevAgentZero",
        },
        "files": inventory,
        "summary": summary,
    }

    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    console.print(f"[green]Manifest saved with {len(inventory)} files.[/green]")


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------


def run_manifest_manager():
    console.print(
        "[cyan]Running Manifest Manager: Stage 1 Inventory + Placement Validation[/cyan]"
    )

    canonical_names = load_canonical_names()
    inventory = scan_all_files()
    inventory = classify_files(inventory, canonical_names)

    new_files, missing_files, misplaced_files = compare_with_existing(inventory)

    # Reporting
    console.print(
        f"[yellow]New files detected:[/yellow] {new_files}"
        if new_files
        else "[green]No new files.[/green]"
    )
    console.print(
        f"[red]Missing files:[/red] {missing_files}"
        if missing_files
        else "[green]No missing files.[/green]"
    )
    console.print(
        f"[magenta]Misplaced files:[/magenta] {misplaced_files}"
        if misplaced_files
        else "[green]No misplaced files.[/green]"
    )

    # Save manifest
    save_manifest(inventory)


if __name__ == "__main__":
    run_manifest_manager()

# End of Script: manifest_manager.py
# Version: 1.0.0
# Created Date: 2025-07-29
# Pre-alpha Character Count: TBD
