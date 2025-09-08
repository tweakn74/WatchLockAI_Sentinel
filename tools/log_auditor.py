# File: log_auditor.py
# Location: root
# Developer: Craig & GPT-4
# Version: 1.1.0
# Last Modified: 2025-07-18
# Purpose: Validate, repair, and report status of DevAgent Zero session logs
# Notes: Removed emojis, improved error tolerance, and audit feedback

from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import json
import os
import datetime

console = Console()

REQUIRED_FIELDS = ["timestamp", "prompt", "plan", "outputs"]
FIX_LOG = Path("logs/fix_history.log")


def log_fix(entry):
    try:
        FIX_LOG.parent.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with FIX_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {entry}\n")
    except Exception as e:
        console.print(f"[log_auditor] Error logging fix entry: {e}")


def repair_session_file(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        console.print(f"[log_auditor] Unreadable JSON: {path.name}")
        rename_path = path.with_name(f"corrupt_{path.name}")
        try:
            path.rename(rename_path)
            log_fix(f"Renamed corrupt log: {path.name} -> {rename_path.name}")
        except Exception as e:
            console.print(f"[log_auditor] Failed to rename corrupt log: {e}")
        return False
    except Exception as e:
        console.print(f"[log_auditor] Failed to open {path.name}: {e}")
        return False

    repaired = False
    missing = [field for field in REQUIRED_FIELDS if field not in data]

    if missing:
        console.print(
            f"[log_auditor] Missing fields in {path.name}: {', '.join(missing)}"
        )
        approve = Prompt.ask(
            f"Attempt to repair '{path.name}'?", choices=["y", "n"], default="y"
        )
        if approve.lower() == "y":
            try:
                if "timestamp" not in data:
                    data["timestamp"] = datetime.datetime.fromtimestamp(
                        path.stat().st_mtime
                    ).isoformat()
                if "outputs" not in data:
                    data["outputs"] = []
                if "prompt" not in data:
                    data["prompt"] = "[unknown prompt]"
                if "plan" not in data:
                    data["plan"] = []

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)

                console.print(f"[log_auditor] Repaired: {path.name}")
                log_fix(
                    f"Repaired session: {path.name} — Fields fixed: {', '.join(missing)}"
                )
                repaired = True
            except Exception as e:
                console.print(f"[log_auditor] Failed to repair {path.name}: {e}")
    return repaired


def audit_session_logs():
    memory_dir = Path("memory_store")
    try:
        session_files = list(memory_dir.glob("session_*.json"))
    except Exception as e:
        console.print(f"[log_auditor] Could not list session files: {e}")
        return

    if not session_files:
        console.print("[log_auditor] No session logs found.")
        return

    console.print("\n[log_auditor] Auditing memory_store logs...")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Filename")
    table.add_column("Status")
    table.add_column("Size (KB)", justify="right")
    table.add_column("Missing Fields", justify="center")

    for file in session_files:
        try:
            size_kb = os.path.getsize(file) / 1024
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            missing = [field for field in REQUIRED_FIELDS if field not in data]
            if missing:
                table.add_row(
                    file.name, "Missing Fields", f"{size_kb:.1f}", ", ".join(missing)
                )
                repair_session_file(file)
            else:
                table.add_row(file.name, "OK", f"{size_kb:.1f}", "-")
        except Exception as e:
            table.add_row(file.name, f"Corrupt ({e.__class__.__name__})", "-", "?")
            repair_session_file(file)

    console.print(table)


if __name__ == "__main__":
    audit_session_logs()
