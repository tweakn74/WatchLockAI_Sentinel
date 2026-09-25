# File: restore_shell.py
# Location: root
# Developer: Craig & GPT-4
# Version: 0.2.0
# Last Modified: 2025-07-18
# Purpose: Interactive recovery shell to manually select and restore backups if auto-restore fails

import json
import shutil
import hashlib
from pathlib import Path
from rich.console import Console
from rich.prompt import IntPrompt

console = Console()

BACKUP_DIR = Path("backups")
TARGET_ROOT = Path(".")
MANIFEST_PATH = Path("manifest.json")
RESTORE_LOG = Path("logs/restore.log")


def compute_checksum(file_path: Path) -> str:
    hash_func = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def list_backup_versions(stem: str, suffix: str):
    return sorted(
        BACKUP_DIR.rglob(f"{stem}_bak_*{suffix}"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )


def restore_interactively(target_path: Path, dry_run: bool = False):
    stem, suffix = target_path.stem, target_path.suffix
    backups = list_backup_versions(stem, suffix)

    if not backups:
        console.print(f"[red]No backups found for {target_path}[/red]")
        return

    console.print(f"\n[bold cyan]Backups for {target_path}:[/bold cyan]")
    for idx, f in enumerate(backups):
        try:
            mtime = f.stat().st_mtime
        except Exception:
            mtime = 0
        console.print(f"  [{idx}] {f.name} -- {mtime:.0f}")

    selection = IntPrompt.ask("Select a version to restore (index)", default=0)
    try:
        selected = backups[selection]
    except IndexError:
        console.print("[red]Invalid selection.[/red]")
        return

    if dry_run:
        console.print(
            f"[yellow]Dry run:[/yellow] Would restore {target_path} from {selected}"
        )
        return

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(selected, target_path)
        target_path.read_text(encoding="utf-8")  # post-restore validation
        log_restore_event(target_path, "interactive restore", selected)
        console.print(f"[green]Restored:[/green] {target_path} from {selected.name}")
    except Exception as e:
        console.print(
            f"[red]Failed to restore {target_path} from {selected}: {e}[/red]"
        )


def log_restore_event(path: Path, reason: str, source: Path):
    try:
        RESTORE_LOG.parent.mkdir(exist_ok=True)
        with open(RESTORE_LOG, "a", encoding="utf-8") as log:
            log.write(f"{path} restored from {source} due to: {reason}\n")
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Failed to write restore log: {e}")


def interactive_shell(
    only_missing: bool = False, only_corrupt: bool = False, dry_run: bool = False
):
    if not MANIFEST_PATH.exists():
        console.print("[red]No manifest.json found. Cannot continue.[/red]")
        return

    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        console.print(f"[red]Failed to load manifest.json:[/red] {e}")
        return

    manifest_files = manifest.get("files", {})
    if not manifest_files:
        console.print("[red]Manifest is empty or malformed.[/red]")
        return

    console.print("[bold magenta]Interactive Restore Shell[/bold magenta]\n")

    for rel_path, meta in manifest_files.items():
        path = Path(rel_path)

        if not path.exists():
            if only_corrupt:
                continue
            console.print(f"[yellow]Missing:[/yellow] {path}")
            restore_interactively(path, dry_run=dry_run)
            continue

        try:
            actual_hash = compute_checksum(path)
            if actual_hash != meta["checksum"]:
                if only_missing:
                    continue
                console.print(f"[red]Hash mismatch:[/red] {path}")
                restore_interactively(path, dry_run=dry_run)
        except Exception:
            if only_missing:
                continue
            console.print(f"[red]Unreadable or corrupt:[/red] {path}")
            restore_interactively(path, dry_run=dry_run)


if __name__ == "__main__":
    import sys

    flags = sys.argv[1:]
    dry_run = "--dry-run" in flags
    only_missing = "--only-missing" in flags
    only_corrupt = "--only-corrupt" in flags

    interactive_shell(
        only_missing=only_missing, only_corrupt=only_corrupt, dry_run=dry_run
    )

# End of Script: restore_shell.py
