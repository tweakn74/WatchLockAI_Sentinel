# File: memory_reader.py
# Developer: Craig and ChatGPT 4o
# Location: root
# Version: 2.3.0
# Modified: 2025-07-23
# Purpose: Reads and merges memory sessions, supports pointer-aware restoration and continuous personality state (AURA readiness).
# Recent Change: Added session merging across archives, pointer-aware access, and enhanced error handling with usage summaries.

from pathlib import Path
import json
from agent_core.pointer_resolver import scan_for_reference
from rich.console import Console

console = Console()

MEMORY_DIR = Path("memory_store")


def load_session(file_path: Path):
    """
    Safely loads a session JSON file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[memory_reader] Failed to load {file_path.name}: {e}")
        return None


def merge_sessions(session_files: list):
    """
    Merges multiple session files into a single unified structure.
    - Combines prompts, plans, outputs.
    - Deduplicates and preserves chronological order.
    """
    merged = {"prompt": [], "plan": [], "outputs": [], "timestamp": []}

    for file in session_files:
        data = load_session(file)
        if not data:
            continue

        if "prompt" in data and data["prompt"] not in merged["prompt"]:
            merged["prompt"].append(data["prompt"])

        merged["plan"].extend(
            step for step in data.get("plan", []) if step not in merged["plan"]
        )
        merged["outputs"].extend(
            o for o in data.get("outputs", []) if o not in merged["outputs"]
        )
        merged["timestamp"].append(data.get("timestamp", "[unknown]"))

    return merged


def list_sessions(n=3, merge=False):
    """
    Lists recent memory sessions or merges them for continuous view.
    - merge=True will merge last N sessions into a unified summary (AURA mode).
    """
    if not MEMORY_DIR.exists():
        console.print("[memory_reader] memory_store folder does not exist.")
        return

    # Look for both restored and active sessions
    sessions = sorted(MEMORY_DIR.glob("session_*.json")) + sorted(
        MEMORY_DIR.glob("session_*_restored.json")
    )
    sessions = sorted(sessions, reverse=True)[:n]

    if not sessions:
        console.print("[memory_reader] No session files found.")
        return

    if merge:
        merged_data = merge_sessions(sessions)
        _print_merged_summary(merged_data, sessions)
        return

    for session_file in sessions:
        _print_single_session(session_file)


def _print_single_session(session_file: Path):
    """
    Prints a summary of a single session file.
    """
    data = load_session(session_file)
    if not data:
        return

    console.print(f"\n[memory_reader] Session: {session_file.name}")
    console.print(f"  Timestamp : {data.get('timestamp', '[missing]')}")
    console.print(f"  Prompt    : {data.get('prompt', '[missing]')}")
    console.print("  Plan      :")
    for i, step in enumerate(data.get("plan", []), 1):
        console.print(f"    {i}. {step}")

    outputs = data.get("outputs", [])
    if outputs:
        console.print("  Output Files:")
        for o in outputs:
            console.print(f"    - {o}")


def _print_merged_summary(merged_data: dict, session_files: list):
    """
    Prints a merged summary of multiple sessions for AURA continuous personality context.
    """
    console.print("\n[memory_reader] Merged Session View (AURA Mode)")
    console.print(f"  Included Sessions: {len(session_files)}")
    console.print(f"  Combined Prompts  : {', '.join(merged_data['prompt'])}")
    console.print("  Combined Plan     :")
    for i, step in enumerate(merged_data["plan"], 1):
        console.print(f"    {i}. {step}")
    if merged_data["outputs"]:
        console.print("  Combined Outputs  :")
        for o in merged_data["outputs"]:
            console.print(f"    - {o}")


def restore_session_from_reference(text: str):
    """
    Attempts to find and restore session context from provided text (pointer-aware).
    """
    restored = scan_for_reference(text)
    if restored:
        console.print(
            f"[memory_reader] Restored session from reference in text: {restored.name}"
        )
        return restored
    else:
        console.print("[memory_reader] No matching session reference found.")
        return None


if __name__ == "__main__":
    # Example: List last 3 sessions merged for continuous context
    list_sessions(n=3, merge=True)

# End of Script: memory_reader.py
# Version: 2.3.0
# Modified: 2025-07-23
