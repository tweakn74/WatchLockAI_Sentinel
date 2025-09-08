# File: manifest_checker.py
# Developer: Craig and Chatgpt 4o
# Location: root
# Version: 1.0.0
# Created Date: 2025-07-23
# Purpose: Validate DevAgentZero files against manifest.json using version + character count system; logs results to Sentinel.
# Recent Change: Upgraded from version-only check to combined version + char count integrity; added Sentinel telemetry and missing file detection.

import json
from pathlib import Path
from rich.console import Console
from datetime import datetime

console = Console()

MANIFEST_PATH = Path("manifest.json")
SENTINEL_TELEMETRY_FILE = Path("logs/sentinel_telemetry.json")


def log_to_sentinel(event: str, details: dict):
    """Log manifest check results to Sentinel telemetry JSON."""
    try:
        SENTINEL_TELEMETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = (
            json.loads(SENTINEL_TELEMETRY_FILE.read_text(encoding="utf-8"))
            if SENTINEL_TELEMETRY_FILE.exists()
            else []
        )
        data.append(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event": event,
                "details": details,
            }
        )
        SENTINEL_TELEMETRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        console.print(f"[red]Failed to log to Sentinel:[/red] {e}")


def load_manifest():
    """Load manifest.json and return file metadata entries."""
    try:
        with MANIFEST_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            # Remove header if present
            return {k: v for k, v in data.items() if not k.startswith("_")}
    except Exception as e:
        console.print(f"[red]Failed to load manifest:[/red] {e}")
        return {}


def read_file_metadata(file_path: str):
    """
    Extract version and character count from file for comparison.
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
        total_chars = len(content)
        version = "0.0.0"
        for line in content.splitlines()[:10]:
            if line.startswith("# Version:"):
                version = line.split(":")[1].strip()
                break
        return {"version": version, "char_count": total_chars}
    except FileNotFoundError:
        return {"version": "missing", "char_count": 0}
    except Exception:
        return {"version": "error", "char_count": 0}


def validate_manifest():
    """
    Validate each file's version and character count against manifest entries.
    """
    manifest = load_manifest()
    if not manifest:
        console.print("[red]Manifest is empty or missing.[/red]")
        return

    console.print("\n[bold cyan]Validating files against manifest.json...[/bold cyan]")

    mismatches = []
    for file, expected in manifest.items():
        metadata = read_file_metadata(file)
        if metadata != expected:
            mismatches.append((file, expected, metadata))
            console.print(
                f"[red]Mismatch:[/red] {file} | Expected: {expected} | Found: {metadata}"
            )
        else:
            console.print(f"[green]Match:[/green] {file} ({metadata})")

    log_to_sentinel(
        "manifest_validation_completed",
        {"mismatches": len(mismatches), "checked": len(manifest)},
    )

    if mismatches:
        console.print(
            f"[yellow]Integrity check completed with {len(mismatches)} mismatches.[/yellow]"
        )
    else:
        console.print("[green]All files match manifest entries.[/green]")


if __name__ == "__main__":
    validate_manifest()

# End of Script: manifest_checker.py
# Version: 1.0.0
# Created Date: 2025-07-23
# Pre-alpha Character Count: 2759
