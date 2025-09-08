# File: manifest_tools.py
# Developer: Craig and ChatGPT 4o
# Location: root
# Version: 2.0.0
# Modified: 2025-07-24
# Purpose: Unified manifest generator and validator for DevAgentZero. Now parses footer metadata (version, modified) from tracked files, including requirements.txt, for accurate cross-checking with preflight.
# Recent Change: Added footer metadata extraction and validation; upgraded mismatch reporting to include footer discrepancies.

import json
from pathlib import Path
from rich.console import Console
from datetime import datetime
import argparse

console = Console()

# Global paths and settings
MANIFEST_PATH = Path("manifest.json")
SENTINEL_TELEMETRY_FILE = Path("logs/sentinel_telemetry.json")
TARGET_DIRS = [".", "agent_core"]
TRACKED_EXTENSIONS = [".py", ".json", ".txt"]  # include requirements.txt

# ---------------------------
# Sentinel Logging
# ---------------------------


def log_to_sentinel(event: str, details: dict):
    """Append manifest tool events to Sentinel telemetry log."""
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


# ---------------------------
# Metadata Extraction
# ---------------------------


def extract_file_metadata(file_path: Path):
    """
    Extract metadata from file:
    - Version: from header or footer (# Version:)
    - Modified: from footer (# Modified:)
    - Char count: total file size
    """
    version = "0.0.0"
    modified = "unknown"
    total_chars = 0

    try:
        content = file_path.read_text(encoding="utf-8")
        total_chars = len(content)
        lines = content.splitlines()

        # Look for version in header (first 10 lines)
        for line in lines[:10]:
            if line.startswith("# Version:"):
                version = line.split(":")[1].strip()

        # Look for version/modified in footer (last 10 lines)
        for line in lines[-10:]:
            if line.startswith("# Version:"):
                version = line.split(":")[1].strip()
            if line.startswith("# Modified:"):
                modified = line.split(":")[1].strip()

        return {"version": version, "modified": modified, "char_count": total_chars}
    except FileNotFoundError:
        return {"version": "missing", "modified": "missing", "char_count": 0}
    except Exception:
        return {"version": "error", "modified": "error", "char_count": 0}


# ---------------------------
# Manifest Generation
# ---------------------------


def generate_manifest():
    """Scan tracked directories and create manifest entries including footer metadata."""
    manifest = {}
    for folder in TARGET_DIRS:
        for file in Path(folder).rglob("*"):
            if file.suffix in TRACKED_EXTENSIONS and file.is_file():
                rel_path = str(file.relative_to(Path(".")))
                manifest[rel_path] = extract_file_metadata(file)
    return manifest


def save_manifest(manifest):
    """Save manifest.json with header metadata and entries."""
    header = {
        "_header": {
            "file": "manifest.json",
            "developer": "Craig and Chatgpt 4o",
            "location": "root",
            "version": "2.0.0",
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "purpose": "Tracks DevAgentZero core files using version, modified date, and character count for integrity validation",
            "recent_change": "Added footer metadata support and enhanced validation",
        }
    }
    manifest_with_header = {**header, **manifest}
    MANIFEST_PATH.write_text(
        json.dumps(manifest_with_header, indent=2), encoding="utf-8"
    )
    console.print(
        f"[green]Manifest generated with {len(manifest)} entries (footer metadata included).[/green]"
    )
    log_to_sentinel("manifest_generated", {"files": len(manifest)})


# ---------------------------
# Manifest Validation
# ---------------------------


def load_manifest():
    """Load manifest.json and strip header."""
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return {k: v for k, v in data.items() if not k.startswith("_")}
    except Exception as e:
        console.print(f"[red]Failed to load manifest:[/red] {e}")
        return {}


def validate_manifest():
    """
    Compare current file metadata (including footer) against manifest entries.
    """
    manifest = load_manifest()
    if not manifest:
        console.print("[red]Manifest missing or invalid.[/red]")
        return False

    mismatches = []
    for file, expected in manifest.items():
        metadata = extract_file_metadata(Path(file))
        if metadata != expected:
            mismatches.append((file, expected, metadata))
            console.print(
                f"[red]Mismatch:[/red] {file} | Expected: {expected} | Found: {metadata}"
            )
        else:
            console.print(f"[green]Match:[/green] {file} ({metadata})")

    log_to_sentinel(
        "manifest_validated", {"mismatches": len(mismatches), "checked": len(manifest)}
    )

    if mismatches:
        console.print(
            f"[yellow]Integrity check completed with {len(mismatches)} mismatches (footer-aware).[/yellow]"
        )
        return False
    else:
        console.print(
            "[green]All files validated successfully with footer metadata.[/green]"
        )
        return True


# ---------------------------
# CLI Entry
# ---------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Manifest Tools: Generate or Validate manifest.json for DevAgentZero"
    )
    parser.add_argument(
        "--generate",
        "-g",
        action="store_true",
        help="Generate a new manifest.json file (includes footer metadata)",
    )
    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        help="Validate current files against manifest.json (footer-aware)",
    )
    args = parser.parse_args()

    if args.generate:
        manifest = generate_manifest()
        save_manifest(manifest)
    elif args.validate:
        validate_manifest()
    else:
        console.print(
            "[yellow]No action specified. Use --generate or --validate.[/yellow]"
        )


if __name__ == "__main__":
    main()

# End of Script: manifest_tools.py
# Version: 2.0.0
# Modified: 2025-07-24
# Pre-alpha Character Count: 4530
