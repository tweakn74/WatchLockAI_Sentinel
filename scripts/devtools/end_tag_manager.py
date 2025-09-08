# File: end_tag_manager.py
# Developer: Craig and ChatGPT 4o
# Location: root
# Version: 0.2.0
# Modified: 2025-07-23
# Purpose: Ensure all Python scripts in the project contain correct "# End of Script" tags.
#          Integrates Sentinel telemetry and preflight reporting to track compliance and health.
# Recent Change: Added Sentinel telemetry hooks, preflight integration, and enhanced error handling.

import json
from pathlib import Path
from datetime import datetime
from rich.console import Console

# Sentinel telemetry configuration
SENTINEL_LOG = Path("logs/sentinel_telemetry.json")
PROJECT_ROOT = Path(".").resolve()
LOG_FILE = Path("logs/end_tag_log.txt")
TAG_PREFIX = "# End of Script: "

console = Console()


def scan_py_files():
    """Recursively locate all Python files in project (excluding __pycache__)."""
    return [p for p in PROJECT_ROOT.rglob("*.py") if "__pycache__" not in str(p)]


def has_correct_end_tag(file_path: Path):
    """Check if file ends with correct End of Script tag."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return False
            last_line = lines[-1].strip()
            return last_line.startswith(TAG_PREFIX) and file_path.name in last_line
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return False


def append_end_tag(file_path: Path):
    """Append proper End of Script tag to a file and log the change."""
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n{TAG_PREFIX}{file_path.name}\n")
        log_change(file_path, "Appended end tag")
        console.print(f"[green]Fixed:[/green] {file_path.relative_to(PROJECT_ROOT)}")
    except Exception as e:
        console.print(f"[red]Failed to update {file_path.name} — {e}[/red]")


def log_change(file_path: Path, action: str):
    """Log end tag changes to end_tag_log.txt and send to Sentinel telemetry."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": timestamp, "action": action, "file": str(file_path)}
    # Write to log file
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {action}: {file_path}\n")
    # Send to Sentinel telemetry
    send_to_sentinel(entry)


def send_to_sentinel(data: dict):
    """Send telemetry data to Sentinel log (aggregates JSON for preflight reporting)."""
    try:
        SENTINEL_LOG.parent.mkdir(parents=True, exist_ok=True)
        if SENTINEL_LOG.exists():
            with open(SENTINEL_LOG, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = []
        existing.append(data)
        with open(SENTINEL_LOG, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
    except Exception as e:
        console.print(f"[red]Failed to update Sentinel telemetry: {e}[/red]")


def generate_preflight_report():
    """Generate summary report for preflight check integration."""
    summary = {"checked_files": 0, "fixed_files": 0, "compliant_files": 0}
    py_files = scan_py_files()

    for py_file in py_files:
        summary["checked_files"] += 1
        if has_correct_end_tag(py_file):
            summary["compliant_files"] += 1
        else:
            summary["fixed_files"] += 1

    # Save summary for preflight reporting
    preflight_report = Path("logs/preflight_end_tag_report.json")
    with open(preflight_report, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def fix_script_endings():
    """Main function: ensure all .py files have correct end tags and log actions."""
    console.print(
        "\n[bold cyan]Scanning .py files for end tag compliance...[/bold cyan]\n"
    )
    py_files = scan_py_files()
    modified = 0

    for py_file in py_files:
        if not has_correct_end_tag(py_file):
            append_end_tag(py_file)
            modified += 1

    if modified == 0:
        console.print("[green]All scripts already have correct end tags.[/green]")
    else:
        console.print(f"\n[yellow]Added end tags to {modified} files.[/yellow]")

    # Generate preflight report
    report = generate_preflight_report()
    console.print(f"\n[bold cyan]Preflight End Tag Report:[/bold cyan] {report}")


if __name__ == "__main__":
    fix_script_endings()

# End of Script: end_tag_manager.py
# Version: 0.2.0
# Modified: 2025-07-23
