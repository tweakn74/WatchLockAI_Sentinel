# File: pycache_manager.py
# Location: root
# Developer: Craig & GPT-4
# Version: 1.0.0
# Last Modified: 2025-07-18
# Purpose: Evaluate and clean or archive __pycache__ folders by judging file freshness and relevance

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()
PROJECT_ROOT = Path(".")
LOG_FILE = Path("logs/pycache_maintenance.log")
ARCHIVE_DIR = Path("logs/pycache_archives")


def log_action(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")


def scan_pycache():
    to_delete = []
    to_archive = []
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        if "__pycache__" in dirnames:
            pycache_path = Path(dirpath) / "__pycache__"
            for file in pycache_path.glob("*.pyc"):
                source_name = file.stem.split(".")[0] + ".py"
                source_path = file.parent.parent / source_name
                if not source_path.exists():
                    console.print(f"[yellow]Orphaned:[/yellow] {file} — source missing")
                    to_delete.append(file)
                    log_action(f"Orphaned .pyc scheduled for deletion: {file}")
                elif source_path.stat().st_mtime > file.stat().st_mtime:
                    console.print(f"[yellow]Stale:[/yellow] {file} — source is newer")
                    to_delete.append(file)
                    log_action(f"Stale .pyc scheduled for deletion: {file}")
                else:
                    console.print(f"[green]Valid:[/green] {file}")

            # Archive whole __pycache__ if all files are outdated or orphaned
            if all(f in to_delete for f in pycache_path.glob("*.pyc")):
                to_archive.append(pycache_path)

    return to_delete, to_archive


def delete_files(files):
    for file in files:
        try:
            file.unlink()
            console.print(f"[red]Deleted:[/red] {file}")
            log_action(f"Deleted: {file}")
        except Exception as e:
            console.print(f"[red]Failed to delete {file}: {e}[/red]")
            log_action(f"Failed to delete {file}: {e}")


def archive_folders(folders):
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for folder in folders:
        archive_name = (
            ARCHIVE_DIR
            / f"{folder.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        try:
            with zipfile.ZipFile(archive_name, "w") as zipf:
                for pyc_file in folder.glob("*.pyc"):
                    zipf.write(pyc_file, arcname=pyc_file.name)
            shutil.rmtree(folder)
            console.print(
                f"[blue]Archived and removed:[/blue] {folder} → {archive_name.name}"
            )
            log_action(f"Archived {folder} to {archive_name.name}")
        except Exception as e:
            console.print(f"[red]Failed to archive {folder}: {e}[/red]")
            log_action(f"Failed to archive {folder}: {e}")


def run_pycache_maintenance():
    console.print("\n[bold cyan]Starting __pycache__ maintenance scan...[/bold cyan]")
    to_delete, to_archive = scan_pycache()
    delete_files(to_delete)
    archive_folders(to_archive)
    console.print("\n[bold green]__pycache__ maintenance complete.[/bold green]")


if __name__ == "__main__":
    run_pycache_maintenance()
