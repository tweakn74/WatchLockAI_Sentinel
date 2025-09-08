"""Data retention and prune jobs for WatchLockAI Sentinel (P5-002).

Implements stdlib-only pruning for quarantine, export, logs, and anomaly state.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_retention_days() -> int:
    """Get retention days from environment variable."""
    return int(os.getenv("RETENTION_DAYS", "14"))


def scan_directory_for_cleanup(
    directory: Path,
    retention_days: int,
    file_extensions: Optional[List[str]] = None
) -> List[Tuple[Path, float, int]]:
    """Scan directory for files older than retention period.
    
    Args:
        directory: Directory to scan
        retention_days: Files older than this many days are candidates
        file_extensions: Optional list of extensions to filter (e.g., ['.log', '.json'])
    
    Returns:
        List of tuples: (file_path, age_days, size_bytes)
    """
    if not directory.exists() or not directory.is_dir():
        return []
    
    cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
    candidates = []
    
    try:
        for item in directory.iterdir():
            if not item.is_file():
                continue
            
            # Filter by extensions if specified
            if file_extensions and item.suffix.lower() not in file_extensions:
                continue
            
            stat = item.stat()
            if stat.st_mtime < cutoff_time:
                age_days = (time.time() - stat.st_mtime) / (24 * 60 * 60)
                candidates.append((item, age_days, stat.st_size))
    
    except (OSError, PermissionError):
        # Skip directories we can't read
        pass
    
    return candidates


def prune_quarantine_files(retention_days: int, dry_run: bool = True) -> Dict:
    """Prune files from quarantine directory.
    
    Args:
        retention_days: Files older than this are removed
        dry_run: If True, only report what would be removed
    
    Returns:
        Dict with pruning results
    """
    quarantine_dir = Path("data/quarantine")
    candidates = scan_directory_for_cleanup(quarantine_dir, retention_days)
    
    removed_count = 0
    removed_size = 0
    errors = []
    
    for file_path, age_days, size_bytes in candidates:
        try:
            if not dry_run:
                file_path.unlink()
            removed_count += 1
            removed_size += size_bytes
        except (OSError, PermissionError) as e:
            errors.append(f"{file_path.name}: {e}")
    
    return {
        "type": "quarantine",
        "directory": str(quarantine_dir),
        "dry_run": dry_run,
        "removed_count": removed_count,
        "removed_size_bytes": removed_size,
        "retention_days": retention_days,
        "errors": errors
    }


def prune_export_files(retention_days: int, dry_run: bool = True) -> Dict:
    """Prune export files.
    
    Args:
        retention_days: Files older than this are removed
        dry_run: If True, only report what would be removed
    
    Returns:
        Dict with pruning results
    """
    export_dir = Path("data/export")
    candidates = scan_directory_for_cleanup(export_dir, retention_days, ['.json', '.zip', '.csv'])
    
    removed_count = 0
    removed_size = 0
    errors = []
    
    for file_path, age_days, size_bytes in candidates:
        try:
            if not dry_run:
                file_path.unlink()
            removed_count += 1
            removed_size += size_bytes
        except (OSError, PermissionError) as e:
            errors.append(f"{file_path.name}: {e}")
    
    return {
        "type": "export",
        "directory": str(export_dir),
        "dry_run": dry_run,
        "removed_count": removed_count,
        "removed_size_bytes": removed_size,
        "retention_days": retention_days,
        "errors": errors
    }


def prune_log_files(retention_days: int, dry_run: bool = True) -> Dict:
    """Prune rotated log files.
    
    Args:
        retention_days: Files older than this are removed
        dry_run: If True, only report what would be removed
    
    Returns:
        Dict with pruning results
    """
    logs_dir = Path("logs")
    candidates = scan_directory_for_cleanup(logs_dir, retention_days, ['.log', '.log.1', '.log.2', '.log.gz'])
    
    removed_count = 0
    removed_size = 0
    errors = []
    
    for file_path, age_days, size_bytes in candidates:
        # Don't remove current log files (without number suffix or .gz)
        if file_path.name.endswith('.log') and not any(c.isdigit() for c in file_path.name):
            continue
        
        try:
            if not dry_run:
                file_path.unlink()
            removed_count += 1
            removed_size += size_bytes
        except (OSError, PermissionError) as e:
            errors.append(f"{file_path.name}: {e}")
    
    return {
        "type": "logs",
        "directory": str(logs_dir),
        "dry_run": dry_run,
        "removed_count": removed_count,
        "removed_size_bytes": removed_size,
        "retention_days": retention_days,
        "errors": errors
    }


def prune_anomaly_state(retention_days: int, dry_run: bool = True) -> Dict:
    """Prune anomaly detection state files.
    
    Args:
        retention_days: Files older than this are removed
        dry_run: If True, only report what would be removed
    
    Returns:
        Dict with pruning results
    """
    anomaly_dir = Path("data/anomaly")
    candidates = scan_directory_for_cleanup(anomaly_dir, retention_days, ['.pkl', '.json', '.model'])
    
    removed_count = 0
    removed_size = 0
    errors = []
    
    for file_path, age_days, size_bytes in candidates:
        # Don't remove current/active model files
        if 'current' in file_path.name.lower() or 'active' in file_path.name.lower():
            continue
            
        try:
            if not dry_run:
                file_path.unlink()
            removed_count += 1
            removed_size += size_bytes
        except (OSError, PermissionError) as e:
            errors.append(f"{file_path.name}: {e}")
    
    return {
        "type": "anomaly_state",
        "directory": str(anomaly_dir),
        "dry_run": dry_run,
        "removed_count": removed_count,
        "removed_size_bytes": removed_size,
        "retention_days": retention_days,
        "errors": errors
    }


def run_retention_job(dry_run: bool = True, retention_days: Optional[int] = None) -> Dict:
    """Run complete retention job across all data directories.
    
    Args:
        dry_run: If True, only report what would be removed
        retention_days: Override default retention period
    
    Returns:
        Dict with comprehensive results
    """
    if retention_days is None:
        retention_days = get_retention_days()
    
    start_time = datetime.now()
    
    results = {
        "timestamp": start_time.isoformat(),
        "dry_run": dry_run,
        "retention_days": retention_days,
        "results": [],
        "summary": {
            "total_files": 0,
            "total_size_bytes": 0,
            "total_errors": 0
        }
    }
    
    # Run pruning for each data type
    prune_functions = [
        prune_quarantine_files,
        prune_export_files,
        prune_log_files,
        prune_anomaly_state
    ]
    
    for prune_func in prune_functions:
        try:
            result = prune_func(retention_days, dry_run)
            results["results"].append(result)
            
            # Update summary
            results["summary"]["total_files"] += result["removed_count"]
            results["summary"]["total_size_bytes"] += result["removed_size_bytes"]
            results["summary"]["total_errors"] += len(result["errors"])
            
        except Exception as e:
            error_result = {
                "type": prune_func.__name__.replace("prune_", "").replace("_files", ""),
                "error": str(e),
                "dry_run": dry_run,
                "removed_count": 0,
                "removed_size_bytes": 0,
                "errors": [str(e)]
            }
            results["results"].append(error_result)
            results["summary"]["total_errors"] += 1
    
    # Calculate execution time
    end_time = datetime.now()
    results["execution_time_seconds"] = (end_time - start_time).total_seconds()
    
    return results


def get_directory_stats() -> Dict:
    """Get current statistics for all retention directories.
    
    Returns:
        Dict with directory statistics
    """
    stats = {
        "timestamp": datetime.now().isoformat(),
        "directories": {}
    }
    
    directories = ["data/quarantine", "data/export", "logs", "data/anomaly"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_stats = {
            "exists": dir_path.exists(),
            "file_count": 0,
            "total_size_bytes": 0,
            "oldest_file": None,
            "newest_file": None
        }
        
        if dir_path.exists() and dir_path.is_dir():
            try:
                files = [f for f in dir_path.iterdir() if f.is_file()]
                dir_stats["file_count"] = len(files)
                
                if files:
                    # Calculate total size and find oldest/newest
                    total_size = 0
                    oldest_time = float('inf')
                    newest_time = 0
                    
                    for file_path in files:
                        stat = file_path.stat()
                        total_size += stat.st_size
                        
                        if stat.st_mtime < oldest_time:
                            oldest_time = stat.st_mtime
                            dir_stats["oldest_file"] = {
                                "name": file_path.name,
                                "age_days": (time.time() - stat.st_mtime) / (24 * 60 * 60)
                            }
                        
                        if stat.st_mtime > newest_time:
                            newest_time = stat.st_mtime
                            dir_stats["newest_file"] = {
                                "name": file_path.name,
                                "age_days": (time.time() - stat.st_mtime) / (24 * 60 * 60)
                            }
                    
                    dir_stats["total_size_bytes"] = total_size
                    
            except (OSError, PermissionError) as e:
                dir_stats["error"] = str(e)
        
        stats["directories"][dir_name] = dir_stats
    
    return stats
