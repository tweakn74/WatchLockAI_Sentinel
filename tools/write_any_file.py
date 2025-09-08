# File: tools/write_any_file.py
# Developer: Craig and Chatgpt 4o
# Location: tools/
# Version: 1.0.0
# Created or Last Modified Date: 2025-09-06
# Purpose: Atomic, non-regressive writer. Writes UTF-8 text with optional ASCII-safe
#          mode, creates parent dirs, backups existing file, and guards by expected
#          hash to prevent accidental overwrite if the source changed.
# Recent Change: Initial creation.

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import time
from typing import Optional


EXIT_OK = 0
EXIT_RUNTIME = 1
EXIT_USAGE = 2


def _stdout(s: str, ascii_safe: bool = False) -> None:
    if ascii_safe:
        sys.stdout.write(s.encode("ascii", "backslashreplace").decode("ascii"))
    else:
        try:
            sys.stdout.write(s)
        except UnicodeEncodeError:
            sys.stdout.write(s.encode("ascii", "backslashreplace").decode("ascii"))
    sys.stdout.flush()


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def _sha256(data: bytes) -> str:
    import hashlib as _hashlib

    h = _hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _atomic_write(target: str, data: bytes) -> None:
    parent = os.path.dirname(os.path.abspath(target))
    _ensure_dir(parent)
    with tempfile.NamedTemporaryFile(dir=parent, delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name
    os.replace(tmp_path, target)


def _backup_if_exists(target: str, backup_dir: Optional[str]) -> Optional[str]:
    if not os.path.exists(target):
        return None
    if not backup_dir:
        return None
    _ensure_dir(backup_dir)
    base = os.path.basename(target)
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"{base}.{ts}.bak")
    shutil.copy2(target, backup_path)
    return backup_path


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="Atomic writer with backup and hash guard. Reads from stdin or --from-file."
    )
    p.add_argument("--path", required=True, help="Target file to write")
    p.add_argument(
        "--from-file", default=None, help="Optional source file instead of stdin"
    )
    p.add_argument(
        "--ascii", action="store_true", help="ASCII-safe output on logs only"
    )
    p.add_argument(
        "--newline",
        choices=["unix", "windows", "keep"],
        default="keep",
        help="Normalize line endings",
    )
    p.add_argument("--encoding", default="utf-8", help="Text encoding for write")
    p.add_argument(
        "--backup-dir",
        default=os.path.join(os.path.dirname(__file__), "backups"),
        help="Backup directory",
    )
    p.add_argument(
        "--expect-hash",
        default=None,
        help="If set, fail if current target hash differs",
    )
    p.add_argument("--no-backup", action="store_true", help="Do not create backups")
    args = p.parse_args(argv)

    try:
        # Gather input bytes
        if args.from_file:
            with open(args.from_file, "rb") as f:
                data = f.read()
        else:
            data = sys.stdin.buffer.read()

        # Normalize newlines if needed
        txt = data.decode("utf-8", errors="replace")
        if args.newline == "unix":
            txt = txt.replace("\r\n", "\n").replace("\r", "\n")
        elif args.newline == "windows":
            txt = txt.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
        out_bytes = txt.encode(args.encoding, errors="replace")

        # Non-regression guard if target exists
        if os.path.exists(args.path) and args.expect_hash:
            current = _sha256_of_file(args.path)
            if current != args.expect_hash:
                _stdout(
                    "Refusing to overwrite: expect-hash mismatch.\n", ascii_safe=True
                )
                return EXIT_USAGE

        # Backup
        backup_path = None
        if not args.no_backup:
            backup_path = _backup_if_exists(args.path, args.backup_dir)

        # Atomic write
        _atomic_write(args.path, out_bytes)

        # Report
        msg = "Wrote file"
        if backup_path:
            msg += f" (backup at {backup_path})"
        msg += f": {args.path}\n"
        _stdout(msg, ascii_safe=args.ascii)

        return EXIT_OK
    except Exception as e:
        _stdout(f"Write error: {e}\n", ascii_safe=True)
        return EXIT_RUNTIME


if __name__ == "__main__":
    sys.exit(main())
