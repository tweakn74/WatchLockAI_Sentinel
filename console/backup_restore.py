"""P4-001: Backup & Restore system for WatchLockAI Sentinel.

Provides automated backup of configs/state/logs and restore functionality.
"""

from __future__ import annotations

import os
import json
import zipfile
import hashlib
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Feature flags
BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
BACKUP_DIR = os.getenv("BACKUP_DIR", "data/backups")


class BackupManager:
    """Manages backup and restore operations for Sentinel configuration and state."""
    
    def __init__(self, backup_dir: str = None):
        """Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups (default from BACKUP_DIR env var)
        """
        self.backup_dir = Path(backup_dir or BACKUP_DIR)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Define backup targets
        self.backup_targets = [
            "config.yaml",
            "data/auth",
            "data/anomaly", 
            "data/quarantine",
            "logs",
            "plugins/manifest.json"
        ]
    
    def create_backup(self, description: str = "") -> Dict[str, Any]:
        """Create timestamped backup archive.
        
        Args:
            description: Optional backup description
            
        Returns:
            dict: Backup result with path and metadata
        """
        if not BACKUP_ENABLED:
            return {
                "status": "disabled",
                "message": "Backup system is disabled",
                "enabled": False
            }
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"sentinel_backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup archive
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add metadata
                metadata = {
                    "timestamp": timestamp,
                    "description": description,
                    "version": "P4-001",
                    "targets": self.backup_targets,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                zf.writestr("metadata.json", json.dumps(metadata, indent=2))
                
                # Add backup targets
                files_backed_up = []
                for target in self.backup_targets:
                    target_path = Path(target)
                    
                    if target_path.exists():
                        if target_path.is_file():
                            # Add single file
                            zf.write(target_path, target)
                            files_backed_up.append(target)
                        elif target_path.is_dir():
                            # Add directory recursively  
                            for file_path in target_path.rglob("*"):
                                if file_path.is_file():
                                    arc_path = str(file_path)
                                    zf.write(file_path, arc_path)
                                    files_backed_up.append(arc_path)
            
            # Calculate SHA256
            sha256_hash = self._calculate_file_hash(backup_path)
            
            return {
                "status": "ok",
                "path": str(backup_path),
                "sha256": sha256_hash,
                "timestamp": timestamp,
                "files_count": len(files_backed_up),
                "size_bytes": backup_path.stat().st_size,
                "enabled": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def restore_backup(self, backup_path: str, confirm: bool = False) -> Dict[str, Any]:
        """Restore from backup archive.
        
        Args:
            backup_path: Path to backup archive
            confirm: If True, actually perform restore. If False, dry-run only.
            
        Returns:
            dict: Restore result and plan
        """
        if not BACKUP_ENABLED:
            return {
                "status": "disabled",
                "message": "Backup system is disabled",
                "enabled": False
            }
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            return {
                "status": "error",
                "error": f"Backup file not found: {backup_path}",
                "enabled": True
            }
        
        try:
            restore_plan = []
            
            # Validate backup archive
            with zipfile.ZipFile(backup_file, 'r') as zf:
                # Check for metadata
                if "metadata.json" not in zf.namelist():
                    return {
                        "status": "error", 
                        "error": "Invalid backup: missing metadata.json",
                        "enabled": True
                    }
                
                # Load metadata
                metadata_content = zf.read("metadata.json").decode('utf-8')
                metadata = json.loads(metadata_content)
                
                # Plan restore operations
                for file_info in zf.filelist:
                    if file_info.filename == "metadata.json":
                        continue
                        
                    restore_plan.append({
                        "file": file_info.filename,
                        "size": file_info.file_size,
                        "exists": Path(file_info.filename).exists()
                    })
                
                if not confirm:
                    return {
                        "status": "dry_run",
                        "plan": restore_plan,
                        "metadata": metadata,
                        "files_count": len(restore_plan),
                        "enabled": True
                    }
                
                # Perform actual restore
                restored_files = []
                for member in zf.filelist:
                    if member.filename == "metadata.json":
                        continue
                        
                    # Create parent directories
                    target_path = Path(member.filename)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Extract file
                    zf.extract(member, ".") 
                    restored_files.append(member.filename)
                
                return {
                    "status": "restored", 
                    "restored_files": restored_files,
                    "metadata": metadata,
                    "files_count": len(restored_files),
                    "enabled": True
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def list_backups(self) -> Dict[str, Any]:
        """List available backup files.
        
        Returns:
            dict: List of backup files with metadata
        """
        if not BACKUP_ENABLED:
            return {
                "status": "disabled",
                "backups": [],
                "enabled": False
            }
        
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("sentinel_backup_*.zip"):
                try:
                    # Get file stats
                    stat = backup_file.stat()
                    
                    # Try to read metadata
                    metadata = {}
                    try:
                        with zipfile.ZipFile(backup_file, 'r') as zf:
                            if "metadata.json" in zf.namelist():
                                metadata_content = zf.read("metadata.json").decode('utf-8')
                                metadata = json.loads(metadata_content)
                    except Exception:
                        pass  # Skip metadata errors
                    
                    backups.append({
                        "path": str(backup_file),
                        "name": backup_file.name,
                        "size_bytes": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
                        "metadata": metadata
                    })
                    
                except Exception:
                    continue  # Skip problematic files
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
            return {
                "status": "ok",
                "backups": backups,
                "count": len(backups),
                "enabled": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            str: SHA256 hex digest
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()


# Global instance
_backup_manager = None


def get_backup_manager() -> BackupManager:
    """Get global backup manager instance.
    
    Returns:
        BackupManager: Global backup manager
    """
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
