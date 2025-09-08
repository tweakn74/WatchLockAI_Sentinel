#!/usr/bin/env python3
# memory/safe_store.py
"""
Safe, local persistence for DevAgentZero memory:
- Atomic writes (tmp + os.replace)
- Rotating backups with timestamped filenames
- Embedded SHA256 checksum for integrity
- Boot-time validation & automatic recovery
- Simple file lock (cross-platform, best-effort)
- Zero external dependencies
"""

from __future__ import annotations
import json
import os
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

DEFAULT_MEMORY_PATH = Path("data/memory.json")
DEFAULT_BACKUP_DIR = Path("backups")
DEFAULT_MAX_BACKUPS = 12  # keep last N backups

# ---------- Utilities ----------


def _now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_dict(d: Dict[str, Any]) -> str:
    # stable encoding to ensure deterministic hash
    blob = json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(blob)


def _ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.parent.mkdir(parents=True, exist_ok=True) if p.suffix else p.mkdir(
            parents=True, exist_ok=True
        )


# ---------- Lock (best-effort) ----------


class FileLock:
    """
    Simple advisory lock using a lockfile.
    Not bulletproof against crashes, but good enough for single-host agents.
    """

    def __init__(self, lock_path: Path, stale_seconds: int = 300):
        self.lock_path = lock_path
        self.stale_seconds = stale_seconds
        self._fd: Optional[int] = None

    def __enter__(self):
        _ensure_dirs(self.lock_path)
        while True:
            try:
                # O_CREAT|O_EXCL ensures we fail if it exists
                self._fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self._fd, str(os.getpid()).encode("utf-8"))
                return self
            except FileExistsError:
                try:
                    st = self.lock_path.stat()
                    if (time.time() - st.st_mtime) > self.stale_seconds:
                        # stale lock; remove it
                        self.lock_path.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                time.sleep(0.15)

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._fd is not None:
                os.close(self._fd)
        finally:
            self.lock_path.unlink(missing_ok=True)


# ---------- SafeStore ----------


class SafeStore:
    def __init__(
        self,
        memory_path: Path = DEFAULT_MEMORY_PATH,
        backup_dir: Path = DEFAULT_BACKUP_DIR,
        max_backups: int = DEFAULT_MAX_BACKUPS,
        lock_path: Optional[Path] = Path("data/memory.lock"),
    ):
        self.memory_path = memory_path
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self.lock_path = lock_path

        _ensure_dirs(self.memory_path, self.backup_dir)
        if self.lock_path:
            _ensure_dirs(self.lock_path)

    # ---------- Public API ----------

    def load(self) -> Dict[str, Any]:
        """
        Load memory.json; verify checksum.
        If corrupt, attempt recovery from backups.
        Returns a dict (empty if not found and no backups).
        """
        if not self.memory_path.exists():
            return {}

        with open(self.memory_path, "r", encoding="utf-8") as f:
            try:
                payload = json.load(f)
            except Exception:
                # unreadable → try recover
                self._recover(reason="json_decode_error")
                return self._safe_load_or_empty()

        data, ok, err = self._verify_payload(payload)
        if ok:
            return data

        # checksum mismatch → recover
        self._recover(reason=f"checksum_mismatch:{err}")
        return self._safe_load_or_empty()

    def save(self, data: Dict[str, Any]) -> None:
        """
        Save memory with atomic write, rotating backup, and checksum.
        """
        with self._maybe_lock():
            # 1) Backup current file (if exists)
            if self.memory_path.exists():
                self._backup_current()

            # 2) Construct payload with checksum
            payload = {
                "data": data,
                "_meta": {
                    "ts": _now_ts(),
                    "checksum": _sha256_dict(data),
                    "version": 1,
                },
            }

            # 3) Atomic write
            tmp = self.memory_path.with_suffix(".json.tmp")
            _ensure_dirs(tmp)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, sort_keys=True, indent=2)
            os.replace(tmp, self.memory_path)

            # 4) Rotate backups
            self._rotate_backups()

    def validate_and_recover_on_boot(self) -> Tuple[bool, str]:
        """
        Check memory.json & backups on boot; recover if needed.
        Returns (ok, message).
        """
        if not self.memory_path.exists():
            return True, "memory.json missing (ok)"

        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            _, ok, err = self._verify_payload(payload)
            if ok:
                return True, "memory.json valid"
            self._recover(reason=f"boot_checksum_mismatch:{err}")
            return False, "memory.json recovered from backup (checksum mismatch)"
        except Exception as e:
            self._recover(reason=f"boot_load_error:{e}")
            return False, "memory.json recovered from backup (load error)"

    # ---------- Internals ----------

    def _verify_payload(
        self, payload: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], bool, str]:
        if not isinstance(payload, dict):
            return {}, False, "payload_not_dict"
        if "data" not in payload or "_meta" not in payload:
            return {}, False, "missing_fields"
        data = payload["data"]
        meta = payload["_meta"]
        if not isinstance(data, dict) or not isinstance(meta, dict):
            return {}, False, "bad_types"
        checksum = meta.get("checksum")
        if not checksum:
            return {}, False, "missing_checksum"
        calc = _sha256_dict(data)
        if calc != checksum:
            return {}, False, "checksum_mismatch"
        return data, True, ""

    def _backup_current(self) -> Optional[Path]:
        try:
            ts = _now_ts()
            dest = self.backup_dir / f"memory_{ts}.json"
            _ensure_dirs(dest)
            # copy bytes to preserve exact content
            with open(self.memory_path, "rb") as src, open(dest, "wb") as dst:
                dst.write(src.read())
            return dest
        except Exception:
            return None

    def _rotate_backups(self) -> None:
        # keep only newest N
        backups = sorted(
            self.backup_dir.glob("memory_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for old in backups[self.max_backups :]:
            try:
                old.unlink(missing_ok=True)
            except Exception:
                pass

    def _recover(self, reason: str) -> None:
        """
        Try the newest valid backup; if none valid, leave file absent (empty state).
        """
        backups = sorted(
            self.backup_dir.glob("memory_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for candidate in backups:
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                data, ok, _ = self._verify_payload(payload)
                if ok:
                    # restore atomically
                    tmp = self.memory_path.with_suffix(".json.tmp")
                    with open(tmp, "w", encoding="utf-8") as out:
                        json.dump(
                            {
                                "data": data,
                                "_meta": {
                                    "ts": _now_ts(),
                                    "checksum": _sha256_dict(data),
                                    "version": 1,
                                },
                            },
                            out,
                            ensure_ascii=False,
                            sort_keys=True,
                            indent=2,
                        )
                    os.replace(tmp, self.memory_path)
                    return
            except Exception:
                continue
        # If we got here, recovery failed → remove broken file
        try:
            self.memory_path.unlink(missing_ok=True)
        except Exception:
            pass

    def _safe_load_or_empty(self) -> Dict[str, Any]:
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            data, ok, _ = self._verify_payload(payload)
            return data if ok else {}
        except Exception:
            return {}

    def _maybe_lock(self):
        return FileLock(self.lock_path) if self.lock_path else _NullContext()


class _NullContext:
    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        return False


# ---------- CLI utility ----------


def _print(msg: str) -> None:
    print(msg, flush=True)


def main():
    """
    Quick manual tests:
      python memory/safe_store.py validate
      python memory/safe_store.py write '{"hello": "world"}'
      python memory/safe_store.py read
    """
    import sys

    ss = SafeStore()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "validate":
        ok, msg = ss.validate_and_recover_on_boot()
        _print(json.dumps({"ok": ok, "msg": msg}))
    elif cmd == "write":
        if len(sys.argv) < 3:
            _print('usage: write \'{"k":"v"}\'')
            raise SystemExit(1)
        data = json.loads(sys.argv[2])
        ss.save(data)
        _print("ok")
    elif cmd == "read":
        _print(json.dumps(ss.load(), indent=2))
    else:
        _print("commands: validate | write <json> | read")


if __name__ == "__main__":
    main()
