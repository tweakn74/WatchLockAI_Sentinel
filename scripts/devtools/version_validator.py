# File: version_validator.py
# Location: root
# Developer: Craig & GPT-4
# Version: 0.2.0
# Last Modified: 2025-07-18
# Purpose: Validate current DevAgent Zero files against manifest and trigger repair if mismatched

import hashlib
import json
from pathlib import Path
from rich.console import Console
from restore_manager import restore_file

MANIFEST_PATH = Path("manifest.json")
RESTORE_LOG = Path("logs/restore.log")
console = Console()


def compute_checksum(path: Path) -> str:
    hash_func = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def load_manifest():
    if not MANIFEST_PATH.exists():
        console.print(
            "[red]Manifest file missing. Run manifest_generator.py first.[/red]"
        )
        return None
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Failed to load manifest:[/red] {e}")
        return None


def log_restore_event(path: Path, reason: str, success: bool):
    RESTORE_LOG.parent.mkdir(parents=True, exist_ok=True)
    status = "RESTORED" if success else "FAILED"
    with open(RESTORE_LOG, "a", encoding="utf-8") as f:
        f.write(f"{path} | {reason} | {status}\n")


def validate_files(dry_run=False):
    manifest = load_manifest()
    if not manifest:
        return

    console.print("[bold cyan]\n[Manifest Validation][/bold cyan]")

    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        expected_hash = entry["checksum"]
        reason = None

        if not path.exists():
            reason = "missing"
        else:
            try:
                current_hash = compute_checksum(path)
                if current_hash != expected_hash:
                    reason = "hash mismatch"
            except Exception:
                reason = "corrupt"

        if reason:
            console.print(f"[yellow]Repair needed:[/yellow] {path} ({reason})")
            if not dry_run:
                restored = restore_file(path)
                if restored:
                    try:
                        # Post-restore re-check
                        new_hash = compute_checksum(path)
                        if new_hash == expected_hash:
                            console.print(
                                f"[green]Verified after restore:[/green] {path}"
                            )
                        else:
                            console.print(
                                f"[red]Restore mismatch remains for:[/red] {path}"
                            )
                    except Exception as e:
                        console.print(f"[red]Still unreadable after restore:[/red] {e}")
                log_restore_event(path, reason, restored)
        else:
            console.print(f"[green]OK:[/green] {path}")


if __name__ == "__main__":
    import sys

    dry = "--dry-run" in sys.argv
    validate_files(dry_run=dry)

# End of Script: version_validator.py
