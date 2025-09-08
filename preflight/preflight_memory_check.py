#!/usr/bin/env python3
# preflight/preflight_memory_check.py
"""
Passive memory validation for startup:
- Scans memory.json
- Attempts automatic recovery from backups if needed
- Prints a machine-readable JSON report
- Never halts the process (advisory only)
"""

from __future__ import annotations
import json
from memory.safe_store import SafeStore, DEFAULT_MEMORY_PATH, DEFAULT_BACKUP_DIR


def run() -> dict:
    ss = SafeStore(memory_path=DEFAULT_MEMORY_PATH, backup_dir=DEFAULT_BACKUP_DIR)
    ok, msg = ss.validate_and_recover_on_boot()
    report = {
        "component": "memory",
        "ok": ok,
        "message": msg,
        "path": str(DEFAULT_MEMORY_PATH),
    }
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    run()
