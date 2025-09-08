# File: manifest_generator.py
# Developer: Craig and Chatgpt 4o
# Location: root
# Version: 1.0.0
# Created Date: 2025-07-23
# Purpose: Generate and refresh manifest.json entries using version + character count system for all tracked files (.py, .json) in DevAgentZero.
# Recent Change: Migrated from checksum-based approach to header/footer integrity (version + char count). Added Sentinel telemetry and robust error handling.

import json
from pathlib import Path
from rich.console import Console
from datetime import datetime

console = Console()

# Manifest and target directories
MANIFEST_PATH = Path("manifest.json")
TARGET_DIRS = [".", "agent_core"]
TRACKED_EXTENSIONS = [".py", ".json"]

# Sentinel telemetry log
SENTINEL_TELEMETRY_FILE = Path("logs/sentinel_telemetry.json")


def log_to_sentinel(event: str, details: dict):
    """Log manifest generation events to Sentinel telemetry JSON."""
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


def extract_file_metadata(file_path: Path):
    """
    Extract version and character count from file header/footer.
    Returns dict with version and char_count.
    """
    version = "0.0.0"
    try:
        content = file_path.read_text(encoding="utf-8")
        total_chars = len(content)
        # Look for header version
        for line in content.splitlines()[:10]:
            if line.startswith("# Version:"):
                version = line.split(":")[1].strip()
                break
        return {"version": version, "char_count": total_chars}
    except Exception:
        return {"version": "missing", "char_count": 0}


def generate_manifest():
    """
    Scan all tracked files and generate manifest.json entries with version + char_count.
    """
    manifest = {}

    for folder in TARGET_DIRS:
        for file in Path(folder).rglob("*"):
            if file.suffix in TRACKED_EXTENSIONS and file.is_file():
                rel_path = str(file.relative_to(Path(".")))
                metadata = extract_file_metadata(file)
                manifest[rel_path] = metadata

    return manifest


def save_manifest(manifest):
    """
    Save manifest.json to disk with header/footer metadata.
    """
    try:
        header = {
            "_header": {
                "file": "manifest.json",
                "developer": "Craig and Chatgpt 4o",
                "location": "root",
                "version": "1.0.0",
                "generated_date": datetime.now().strftime("%Y-%m-%d"),
                "purpose": "Tracks DevAgentZero core files with version and character count for integrity management",
                "recent_change": "Initial migration to pre-alpha integrity system",
            }
        }
        manifest_with_header = {**header, **manifest}
        MANIFEST_PATH.write_text(
            json.dumps(manifest_with_header, indent=2), encoding="utf-8"
        )
        console.print(
            f"[green]Manifest generated and saved successfully:[/green] {MANIFEST_PATH}"
        )
        log_to_sentinel("manifest_generated", {"files": len(manifest)})
    except Exception as e:
        console.print(f"[red]Failed to write manifest.json:[/red] {e}")


if __name__ == "__main__":
    manifest = generate_manifest()
    save_manifest(manifest)

# End of Script: manifest_generator.py
# Version: 1.0.0
# Created Date: 2025-07-23
# Pre-alpha Character Count: 3018
