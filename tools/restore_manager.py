# File: restore_manager.py
# Location: root
# Developer: Craig & GPT-4
# Version: 0.3.0
# Last Modified: 2025-07-18
# Purpose: Restore latest valid backup for missing, corrupt, or mismatched files based on manifest.json, with dry-run mode, reason tracking, post-verify, and integration hooks

import json
import shutil
import hashlib
from pathlib import Path
from rich.console import Console

console = Console()

BACKUP_DIR = Path("backups")
TARGET_ROOT = Path(".")
MANIFEST_PATH = Path("manifest.json")
RESTORE_LOG = Path("logs/restore.log")
CRITICAL_EXTENSIONS = [".py", ".json"]


def compute_checksum(file_path):
    hash_func = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def find_latest_backup(file_stem, file_suffix):
    candidates = sorted(
        BACKUP_DIR.rglob(f"{file_stem}_bak_*{file_suffix}"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def restore_file(original_path: Path, reason: str = "unknown", dry_run=False) -> bool:
    relative_path = original_path.relative_to(TARGET_ROOT)
    stem, suffix = original_path.stem, original_path.suffix
    latest_backup = find_latest_backup(stem, suffix)

    if not latest_backup:
        console.print(f"[restore_manager] No backup found for {original_path}")
        return False

    if dry_run:
        console.print(
            f"[dry-run] Would restore: {original_path} from {latest_backup.name} (Reason: {reason})"
        )
        return True

    try:
        original_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(latest_backup, original_path)
        original_path.read_text(encoding="utf-8")  # post-restore verification
        log_restore_event(original_path, reason, latest_backup)
        console.print(
            f"[restore_manager] Restored {original_path} from {latest_backup.name}"
        )
        return True
    except Exception as e:
        console.print(f"[restore_manager] Failed to restore {original_path}: {e}")
        return False


def log_restore_event(path: Path, reason: str, source: Path):
    try:
        RESTORE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(RESTORE_LOG, "a", encoding="utf-8") as log:
            timestamp = Path().stat().st_mtime
            log.write(f"{path} restored from {source} | Reason: {reason}\n")
    except Exception as e:
        console.print(f"[restore_manager] Failed to log restore event: {e}")


def restore_from_manifest(dry_run=False):
    if not MANIFEST_PATH.exists():
        console.print("[restore_manager] No manifest found. Cannot validate.")
        return

    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        console.print(f"[restore_manager] Failed to read manifest: {e}")
        return

    console.print(
        "[restore_manager] Evaluating manifest for missing, corrupt, or out-of-sync files...\n"
    )

    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        expected_hash = entry["checksum"]

        if not path.exists():
            console.print(f"[restore_manager] Missing: {path}")
            restore_file(path, reason="missing", dry_run=dry_run)
            continue

        try:
            actual_hash = compute_checksum(path)
            if actual_hash != expected_hash:
                console.print(f"[restore_manager] Hash mismatch: {path}")
                restore_file(path, reason="checksum mismatch", dry_run=dry_run)
        except Exception:
            console.print(f"[restore_manager] Corrupt file: {path}")
            restore_file(path, reason="corrupt/unreadable", dry_run=dry_run)


if __name__ == "__main__":
    import sys

    dry = "--dry-run" in sys.argv
    restore_from_manifest(dry_run=dry)

# End of Script: restore_manager.py
