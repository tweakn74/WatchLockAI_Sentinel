# File: self_upgrade.py
# Location: root
# Developer: Craig & GPT-4
# Version: 0.1.0
# Last Modified: 2025-07-18
# Purpose: Evaluate DevAgent Zero's codebase for missing headers, inconsistencies, stale files, and orphaned artifacts. Supports auto-repair and logging.

import re
import shutil
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()
PROJECT_ROOT = Path(".")
LOGS_DIR = Path("logs")
BACKUP_DIR = LOGS_DIR / "self_upgrade_backups"

REQUIRED_HEADER_KEYS = [
    "File",
    "Location",
    "Developer",
    "Version",
    "Last Modified",
    "Purpose",
]
TARGET_EXTENSIONS = [".py"]
ORPHANED_EXTENSIONS = [".json", ".log", ".gz", ".pointer"]


def scan_python_headers():
    missing_headers = []
    inconsistent_versions = []

    for file in PROJECT_ROOT.rglob("*.py"):
        if "__pycache__" in str(file):
            continue
        try:
            content = file.read_text(encoding="utf-8")
            header = content.split("\n\n", 1)[0]
            if not all(k.lower() in header.lower() for k in REQUIRED_HEADER_KEYS):
                missing_headers.append(file)

            # Version extraction
            match = re.search(r"Version:\s*(\d+\.\d+\.\d+)", header)
            if not match:
                inconsistent_versions.append(file)
        except Exception as e:
            console.print(f"[red]Error reading {file}: {e}[/red]")

    return missing_headers, inconsistent_versions


def scan_orphaned_files():
    session_ids = set(
        p.stem.replace("session_", "")
        for p in Path("memory_store").glob("session_*.json")
    )
    orphans = []

    for ext in ORPHANED_EXTENSIONS:
        for file in Path("memory_store").glob(f"*{ext}"):
            sid = re.findall(r"session_([\d_]+)", file.name)
            if not sid or sid[0] not in session_ids:
                orphans.append(file)

    return orphans


def scan_duplicate_logs():
    log_names = {}
    duplicates = []
    for file in LOGS_DIR.glob("*.log"):
        key = file.stem
        if key in log_names:
            duplicates.append(file)
        else:
            log_names[key] = file
    return duplicates


def backup_file(file: Path):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(file, BACKUP_DIR / f"{file.name}.{timestamp}.bak")


def auto_repair_headers(files):
    for file in files:
        try:
            backup_file(file)
            content = file.read_text(encoding="utf-8")
            filename = file.name
            header = f"""# File: {filename}\n# Location: {file.parent}\n# Developer: Craig & GPT-4\n# Version: 0.1.0\n# Last Modified: {datetime.now().strftime("%Y-%m-%d")}\n# Purpose: [ADD PURPOSE HERE]\n\n"""
            if not content.strip().startswith("# File"):
                file.write_text(header + content, encoding="utf-8")
                console.print(f"[green]✔ Repaired header:[/green] {filename}")
        except Exception as e:
            console.print(f"[red]❌ Failed to repair {file.name}: {e}[/red]")


def delete_orphans(orphans):
    for file in orphans:
        try:
            backup_file(file)
            file.unlink()
            console.print(f"[blue]🗑 Removed orphaned:[/blue] {file.name}")
        except Exception as e:
            console.print(f"[red]❌ Failed to delete {file.name}: {e}[/red]")


def run_self_upgrade():
    console.print(
        "\n[bold magenta]🔍 Running Self-Upgrade Diagnostic...[/bold magenta]"
    )

    headers, versions = scan_python_headers()
    orphans = scan_orphaned_files()
    dups = scan_duplicate_logs()

    table = Table(title="DevAgent Zero Codebase Issues", show_lines=True)
    table.add_column("Check")
    table.add_column("Files Affected")

    table.add_row("Missing Headers", str(len(headers)))
    table.add_row("Version Inconsistencies", str(len(versions)))
    table.add_row("Orphaned Memory Files", str(len(orphans)))
    table.add_row("Duplicate Logs", str(len(dups)))
    console.print(table)

    if headers:
        console.print("[yellow]Attempting header repairs...[/yellow]")
        auto_repair_headers(headers)

    if orphans:
        console.print("[yellow]Cleaning up orphaned memory files...[/yellow]")
        delete_orphans(orphans)

    console.print("\n[bold green]✅ Self-upgrade pass complete.[/bold green]\n")


if __name__ == "__main__":
    run_self_upgrade()

# End of Script: self_upgrade.py
