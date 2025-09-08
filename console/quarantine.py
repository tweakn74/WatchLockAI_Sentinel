"""File quarantine and restore system with Windows ACL hardening.

Provides secure file quarantine operations with SHA256 tracking, 
audit logging, and optional Windows ACL tightening via icacls.

Feature flags:
- QUARANTINE_ENABLED=0 (default OFF)
- QUARANTINE_DIR (default data/quarantine)
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Feature flags
QUARANTINE_ENABLED = os.getenv("QUARANTINE_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
QUARANTINE_DIR = Path(os.getenv("QUARANTINE_DIR", "data/quarantine"))
AUDIT_LOG_FILE = QUARANTINE_DIR / "audit_log.jsonl"

# Thread-safe operations
_quarantine_lock = threading.Lock()


class QuarantineError(Exception):
    """Quarantine-specific exception."""
    pass


def compute_file_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        raise QuarantineError(f"Failed to compute SHA256 for {file_path}: {e}") from e


def write_audit_log(action: str, source_path: str, dest_path: str = "", 
                   sha256: str = "", error: str = "") -> None:
    """Write audit log entry."""
    try:
        QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "path_src": source_path,
            "path_dst": dest_path,
            "sha256": sha256,
            "error": error
        }
        
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        # Swallow audit logging errors to maintain operational stability
        pass


def apply_windows_acl_hardening(file_path: Path) -> bool:
    """Apply Windows ACL hardening using icacls subprocess (best-effort).
    
    Args:
        file_path: Path to the quarantined file
        
    Returns:
        True if ACL hardening succeeded, False if failed/unavailable
    """
    if not file_path.exists():
        return False
    
    try:
        # Check if we're on Windows and icacls is available
        if os.name != 'nt':
            return False
        
        # Remove all permissions except for SYSTEM and Administrators
        cmd = [
            "icacls", str(file_path),
            "/inheritance:r",  # Remove inheritance
            "/grant:r", "SYSTEM:(F)",  # Grant SYSTEM full control
            "/grant:r", "Administrators:(F)",  # Grant Administrators full control
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,
            check=False  # Don't raise on non-zero exit
        )
        
        return result.returncode == 0
        
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # icacls not available or failed
        return False
    except Exception:
        # Any other error
        return False


class QuarantineManager:
    """File quarantine and restore manager."""
    
    def __init__(self):
        self._quarantine_mapping: Dict[str, Dict[str, Any]] = {}
        self._load_mapping()
    
    def _load_mapping(self) -> None:
        """Load quarantine mapping from disk."""
        mapping_file = QUARANTINE_DIR / "mapping.json"
        try:
            if mapping_file.exists():
                with open(mapping_file, "r", encoding="utf-8") as f:
                    self._quarantine_mapping = json.load(f)
        except Exception:
            self._quarantine_mapping = {}
    
    def _save_mapping(self) -> None:
        """Save quarantine mapping to disk."""
        mapping_file = QUARANTINE_DIR / "mapping.json"
        try:
            QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(self._quarantine_mapping, f, indent=2)
        except Exception:
            pass  # Swallow errors to maintain stability
    
    def quarantine_file(self, source_path: str) -> Dict[str, Any]:
        """Quarantine a file with SHA256 tracking and ACL hardening.
        
        Args:
            source_path: Path to the file to quarantine
            
        Returns:
            Dictionary with quarantine status and metadata
        """
        if not QUARANTINE_ENABLED:
            return {"status": "disabled", "enabled": False}
        
        source = Path(source_path)
        
        if not source.exists():
            error_msg = f"Source file does not exist: {source_path}"
            write_audit_log("quarantine_failed", source_path, error=error_msg)
            return {"status": "error", "error": error_msg}
        
        if not source.is_file():
            error_msg = f"Source is not a regular file: {source_path}"
            write_audit_log("quarantine_failed", source_path, error=error_msg)
            return {"status": "error", "error": error_msg}
        
        with _quarantine_lock:
            try:
                # Compute SHA256
                sha256 = compute_file_sha256(source)
                
                # Create quarantine destination
                QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
                quarantine_filename = f"{source.name}_{sha256[:16]}_{int(time.time())}"
                dest_path = QUARANTINE_DIR / quarantine_filename
                
                # Move file to quarantine (atomic operation)
                shutil.move(str(source), str(dest_path))
                
                # Apply Windows ACL hardening (best-effort)
                acl_applied = apply_windows_acl_hardening(dest_path)
                
                # Update mapping
                self._quarantine_mapping[sha256] = {
                    "original_path": source_path,
                    "quarantine_path": str(dest_path),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sha256": sha256,
                    "acl_hardened": acl_applied
                }
                self._save_mapping()
                
                # Audit log
                write_audit_log(
                    "quarantine_success", 
                    source_path, 
                    str(dest_path), 
                    sha256
                )
                
                return {
                    "status": "quarantined",
                    "sha256": sha256,
                    "dst": str(dest_path),
                    "acl_hardened": acl_applied,
                    "enabled": True
                }
                
            except Exception as e:
                error_msg = f"Quarantine operation failed: {e}"
                write_audit_log("quarantine_failed", source_path, error=error_msg)
                return {"status": "error", "error": error_msg}
    
    def restore_file(self, sha256: str, target_path: Optional[str] = None) -> Dict[str, Any]:
        """Restore a quarantined file.
        
        Args:
            sha256: SHA256 hash of the file to restore
            target_path: Optional custom restore path (defaults to original path)
            
        Returns:
            Dictionary with restore status and metadata
        """
        if not QUARANTINE_ENABLED:
            return {"status": "disabled", "enabled": False}
        
        if sha256 not in self._quarantine_mapping:
            error_msg = f"File not found in quarantine: {sha256}"
            write_audit_log("restore_failed", sha256, error=error_msg)
            return {"status": "error", "error": error_msg}
        
        with _quarantine_lock:
            try:
                mapping_entry = self._quarantine_mapping[sha256]
                quarantine_path = Path(mapping_entry["quarantine_path"])
                original_path = mapping_entry["original_path"]
                
                if not quarantine_path.exists():
                    error_msg = f"Quarantined file not found on disk: {quarantine_path}"
                    write_audit_log("restore_failed", sha256, error=error_msg)
                    return {"status": "error", "error": error_msg}
                
                # Determine restore destination
                restore_path = target_path if target_path else original_path
                restore_dest = Path(restore_path)
                
                # Ensure destination directory exists
                restore_dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Verify file integrity before restore
                current_sha256 = compute_file_sha256(quarantine_path)
                if current_sha256 != sha256:
                    error_msg = f"File integrity check failed. Expected {sha256}, got {current_sha256}"
                    write_audit_log("restore_failed", sha256, error=error_msg)
                    return {"status": "error", "error": error_msg}
                
                # Check if destination already exists
                if restore_dest.exists():
                    error_msg = f"Restore destination already exists: {restore_path}"
                    write_audit_log("restore_failed", sha256, error=error_msg)
                    return {"status": "error", "error": error_msg}
                
                # Restore file (atomic move)
                shutil.move(str(quarantine_path), str(restore_dest))
                
                # Remove from mapping
                del self._quarantine_mapping[sha256]
                self._save_mapping()
                
                # Audit log
                write_audit_log(
                    "restore_success",
                    str(quarantine_path),
                    str(restore_dest),
                    sha256
                )
                
                return {
                    "status": "restored",
                    "sha256": sha256,
                    "restored_to": str(restore_dest),
                    "enabled": True
                }
                
            except Exception as e:
                error_msg = f"Restore operation failed: {e}"
                write_audit_log("restore_failed", sha256, error=error_msg)
                return {"status": "error", "error": error_msg}
    
    def list_quarantined_files(self) -> List[Dict[str, Any]]:
        """List all quarantined files."""
        if not QUARANTINE_ENABLED:
            return []
        
        with _quarantine_lock:
            return [
                {
                    "sha256": sha256,
                    "original_path": entry["original_path"],
                    "quarantine_path": entry["quarantine_path"],
                    "timestamp": entry["timestamp"],
                    "acl_hardened": entry.get("acl_hardened", False)
                }
                for sha256, entry in self._quarantine_mapping.items()
            ]
    
    def get_quarantine_status(self) -> Dict[str, Any]:
        """Get overall quarantine system status."""
        return {
            "enabled": QUARANTINE_ENABLED,
            "quarantine_dir": str(QUARANTINE_DIR),
            "quarantined_files": len(self._quarantine_mapping),
            "audit_log": str(AUDIT_LOG_FILE)
        }


# Global manager instance
_manager: Optional[QuarantineManager] = None


def get_manager() -> QuarantineManager:
    """Get or create global quarantine manager."""
    global _manager
    if _manager is None:
        _manager = QuarantineManager()
    return _manager


def quarantine_file(source_path: str) -> Dict[str, Any]:
    """Quarantine a file."""
    manager = get_manager()
    return manager.quarantine_file(source_path)


def restore_file(sha256: str, target_path: Optional[str] = None) -> Dict[str, Any]:
    """Restore a quarantined file."""
    manager = get_manager()
    return manager.restore_file(sha256, target_path)


def list_quarantined_files() -> List[Dict[str, Any]]:
    """List all quarantined files."""
    manager = get_manager()
    return manager.list_quarantined_files()


def get_quarantine_status() -> Dict[str, Any]:
    """Get quarantine system status."""
    manager = get_manager()
    return manager.get_quarantine_status()
