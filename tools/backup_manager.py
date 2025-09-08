# __version__ = "1.0.0"
# __author__ = "CG & AI assistant"
# __creation_date__ = "2025-08-29"
# __modification_date__ = "2025-08-29"
# __purpose__ = "Return SHA256 checksum of the file, or empty string if error occurs."
# File: backup_manager.py
# Developer: Craig and ChatGPT 4o
# Location: root
# Version: 3.1.0
# Created Date: 2025-07-24
# Purpose: Intelligent backup system for DevAgentZero with auto preflight backups, .bak conversion, hierarchy preservation, telemetry, and rollback metadata.
# Recent Change: Added rollback metadata recording, 24-hour freshness check, and auto-skip logic for redundant backups.

from pathlib import Path
import shutil
import hashlib
import datetime
import json
from rich.console import Console

console = Console()

# --- CONFIGURABLES ---
SOURCE_DIRS = [".", "agent_core", "memory_store"]
EXTRA_FILES = ["config.yaml", "pointer_index.json"]
BACKUP_BASE = Path("backups")
CRITICAL_EXTENSIONS = [".py", ".json", ".yaml"]

# Rollback metadata file
ROLLBACK_METADATA = BACKUP_BASE / "preflight_backup" / "rollback_info.json"


def compute_checksum(file_path: Path) -> str:
    """Return SHA256 checksum of the file, or empty string if error occurs."""
    try:
        hash_func = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        console.print(f"[backup_manager] Error computing checksum for {file_path}: {e}")
        return ""


def needs_backup(src: Path, backup: Path) -> bool:
    """Determine if the source file needs backup (nonexistent or checksum mismatch)."""
    try:
        if not backup.exists():
            return True
        return compute_checksum(src) != compute_checksum(backup)
    except Exception as e:
        console.print(f"[backup_manager] Error comparing checksums for {src}: {e}")
        return False


def backup_file(src: Path, dest_root: Path, use_bak_extension: bool = False) -> Path:
    """
    Backup a single file with preserved relative hierarchy.
    - Converts extension to `.bak` if use_bak_extension=True.
    - Adds timestamp for incremental backups (not for preflight).
    """
    try:
        relative_path = src.relative_to(Path("."))
        backup_path = dest_root / relative_path

        # Ensure directory exists
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # .bak conversion for preflight
        if use_bak_extension:
            backup_path = backup_path.with_suffix(backup_path.suffix + ".bak")
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_path.with_name(
                backup_path.stem + f"_bak_{timestamp}" + backup_path.suffix
            )

        # Copy only if needed
        if needs_backup(src, backup_path):
            shutil.copy2(src, backup_path)
            return backup_path
        return None
    except Exception as e:
        console.print(f"[backup_manager] Failed to backup {src}: {e}")
        return None


def record_rollback_metadata(files_backed_up: list):
    """
    Record metadata for rollback: timestamp, original paths, backup paths, and checksums.
    """
    metadata = {
        "timestamp": datetime.datetime.now().isoformat(),
        "files": [],
    }

    for entry in files_backed_up:
        src, backup = entry
        metadata["files"].append(
            {
                "source": str(src),
                "backup": str(backup),
                "checksum": compute_checksum(src),
            }
        )

    ROLLBACK_METADATA.parent.mkdir(parents=True, exist_ok=True)
    with ROLLBACK_METADATA.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def fresh_preflight_exists(hours=24) -> bool:
    """
    Check if a preflight backup exists and is fresh (younger than given hours).
    """
    if ROLLBACK_METADATA.exists():
        try:
            with ROLLBACK_METADATA.open("r", encoding="utf-8") as f:
                data = json.load(f)
                timestamp = datetime.datetime.fromisoformat(data["timestamp"])
                return (
                    datetime.datetime.now() - timestamp
                ).total_seconds() < hours * 3600
        except Exception:
            return False
    return False


def backup_critical_files():
    """Incremental backup for critical files (non-preflight)."""
    dest = BACKUP_BASE
    dest.mkdir(exist_ok=True)

    console.print("[backup_manager] Performing incremental backup...")

    # Backup critical files
    for folder in SOURCE_DIRS:
        for path in Path(folder).rglob("*"):
            if path.is_file() and path.suffix in CRITICAL_EXTENSIONS:
                backup_file(path, dest)

    # Extra files
    for extra in EXTRA_FILES:
        extra_path = Path(extra)
        if extra_path.exists():
            backup_file(extra_path, dest)


def preflight_backup(force=False):
    """
    Full preflight backup with .bak conversion and hierarchy preservation.
    Auto-skips if a fresh backup exists unless force=True.
    """
    if not force and fresh_preflight_exists():
        console.print(
            "[backup_manager] Skipping preflight backup (fresh backup exists)."
        )
        return

    dest = BACKUP_BASE / "preflight_backup" / "DevAgentZero"
    console.print(
        "[backup_manager] Performing preflight backup (.bak full hierarchy)..."
    )

    files_backed_up = []

    # Source directories
    for folder in SOURCE_DIRS:
        for path in Path(folder).rglob("*"):
            if path.is_file() and path.suffix in CRITICAL_EXTENSIONS:
                backup_path = backup_file(path, dest, use_bak_extension=True)
                if backup_path:
                    files_backed_up.append((path, backup_path))

    # Extra files
    for extra in EXTRA_FILES:
        extra_path = Path(extra)
        if extra_path.exists():
            backup_path = backup_file(extra_path, dest, use_bak_extension=True)
            if backup_path:
                files_backed_up.append((extra_path, backup_path))

    # Record rollback metadata
    record_rollback_metadata(files_backed_up)
    console.print("[backup_manager] Preflight backup completed with rollback metadata.")


if __name__ == "__main__":
    # Default behavior: incremental backup
    backup_critical_files()

# End of Script: backup_manager.py
# Version: 3.1.0
# Created Date: 2025-07-24
# Pre-alpha Character Count: 5160
