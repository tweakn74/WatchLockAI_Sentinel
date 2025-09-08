# File: memory_archiver.py
# Developer: Craig and ChatGPT 4o
# Location: root
# Version: 3.1.0
# Modified: 2025-07-24
# Purpose: Archives session memory logs, compresses them, and generates pointer files with metadata.
#          Returns the count of archived sessions for Sentinel telemetry integration during preflight.
# Recent Change: Updated run_memory_archiver() to return archived_count for telemetry logging.

import json
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
from typing import Dict, Optional

# Directory for memory storage
MEMORY_STORE = Path("memory_store")
POINTER_INDEX_FILE = MEMORY_STORE / "pointer_index.json"

# Lifecycle settings
POINTER_RETENTION_DAYS = 30  # Cleanup pointers older than this
POINTER_VERSION = "v3.1"


def compute_checksum(file_path: Path) -> str:
    """
    Computes SHA256 checksum for a given file to ensure integrity verification.
    """
    hash_func = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except (OSError, IOError):
        return ""


def archive_session(session_file: Path) -> Optional[Path]:
    """
    Compresses a session JSON file into a .gz archive for storage efficiency.
    Returns the path to the compressed file or None if archiving fails.
    """
    if not session_file.exists():
        print(f"[memory_archiver] Error: Session file not found: {session_file}")
        return None

    compressed_path = session_file.with_suffix(".json.gz")
    try:
        with open(session_file, "rb") as src:
            with gzip.open(compressed_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
        print(f"[memory_archiver] Archived session: {compressed_path.name}")
        return compressed_path
    except (OSError, IOError) as e:
        print(f"[memory_archiver] Error compressing session {session_file.name}: {e}")
        return None


def create_pointer(
    original_path: Path, compressed_path: Path, session_data: Dict
) -> Optional[Path]:
    """
    Creates a .pointer file with metadata about the archived session for rehydration.
    Includes lifecycle versioning and usage tracking fields.
    """
    pointer_path = original_path.with_suffix(".pointer")

    try:
        session_id = original_path.stem.replace("session_", "")
        topics = (
            session_data.get("prompt", "unknown_topic")[:50]
            if session_data
            else "unknown"
        )

        pointer_data = {
            "session_id": session_id,
            "archived_file": compressed_path.name,
            "archived_at_ts": datetime.now().isoformat(),
            "checksum_gz": compute_checksum(compressed_path),
            "topics": topics,
            "version": POINTER_VERSION,
            "last_accessed_ts": None,
            "access_count": 0,
        }

        with open(pointer_path, "w", encoding="utf-8") as f:
            json.dump(pointer_data, f, indent=2)

        print(f"[memory_archiver] Pointer created: {pointer_path.name}")
        return pointer_path

    except (OSError, IOError, json.JSONDecodeError) as e:
        print(f"[memory_archiver] Error creating pointer for {original_path.name}: {e}")
        return None


def archive_and_pointer(session_file: Path) -> Optional[Path]:
    """
    High-level function to archive a session file and generate its pointer.
    Updates pointer index and triggers lifecycle cleanup.
    """
    MEMORY_STORE.mkdir(parents=True, exist_ok=True)

    compressed_path = archive_session(session_file)
    if not compressed_path:
        return None

    session_data = {}
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
    except (OSError, IOError, json.JSONDecodeError):
        print(
            "[memory_archiver] Warning: Unable to load session data for pointer metadata."
        )

    pointer_path = create_pointer(session_file, compressed_path, session_data)
    if pointer_path:
        update_pointer_index(pointer_path)
        cleanup_old_pointers()
    return pointer_path


def update_pointer_index(pointer_path: Path):
    """
    Adds or updates pointer entry in pointer_index.json for fast lookups.
    """
    index = {}
    if POINTER_INDEX_FILE.exists():
        try:
            index = json.loads(POINTER_INDEX_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            index = {}

    pointer_data = json.loads(pointer_path.read_text(encoding="utf-8"))
    index[pointer_data["session_id"]] = str(pointer_path)

    POINTER_INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")


def cleanup_old_pointers():
    """
    Removes pointer files older than retention threshold along with associated archives.
    """
    cutoff_date = datetime.now() - timedelta(days=POINTER_RETENTION_DAYS)
    for pointer_file in MEMORY_STORE.glob("session_*.pointer"):
        try:
            data = json.loads(pointer_file.read_text(encoding="utf-8"))
            archived_at = datetime.fromisoformat(
                data.get("archived_at_ts", datetime.now().isoformat())
            )
            if archived_at < cutoff_date:
                archive_file = MEMORY_STORE / data.get("archived_file", "")
                if archive_file.exists():
                    archive_file.unlink()
                pointer_file.unlink()
                print(
                    f"[memory_archiver] Removed stale pointer and archive: {pointer_file.name}"
                )
        except Exception:
            continue


def run_memory_archiver() -> int:
    """
    Scans memory_store for unarchived session files, archives them, and creates pointers.
    Returns the count of archived sessions for telemetry logging.
    """
    MEMORY_STORE.mkdir(parents=True, exist_ok=True)
    archived_count = 0

    # Find session JSON files that are not archived (no matching .json.gz or .pointer)
    for session_file in MEMORY_STORE.glob("session_*.json"):
        pointer_file = session_file.with_suffix(".pointer")
        compressed_file = session_file.with_suffix(".json.gz")

        if pointer_file.exists() and compressed_file.exists():
            continue  # Already archived and indexed

        if archive_and_pointer(session_file):
            archived_count += 1

    print(
        f"[memory_archiver] run_memory_archiver completed: {archived_count} sessions archived."
    )
    return archived_count


if __name__ == "__main__":
    count = run_memory_archiver()
    print(f"Archived {count} sessions in standalone mode.")

# End of Script: memory_archiver.py
# Version: 3.1.0
# Modified: 2025-07-24
# Pre-alpha Character Count: 6415
