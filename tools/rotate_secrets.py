"""P4-002: Secret rotation toolkit for WatchLockAI Sentinel.

Provides secure rotation of authentication keys and secrets.
"""

from __future__ import annotations

import os
import secrets
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Feature flags
ROTATE_ENABLED = os.getenv("ROTATE_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}


class SecretRotator:
    """Manages rotation of secrets and authentication keys."""
    
    def __init__(self):
        """Initialize secret rotator."""
        self.rotation_log = []
    
    def rotate_console_auth_session_key(self) -> Dict[str, Any]:
        """Generate new CONSOLE_AUTH_SESSION_KEY.
        
        Returns:
            dict: Rotation result with new key info
        """
        if not ROTATE_ENABLED:
            return {
                "status": "disabled",
                "message": "Secret rotation is disabled",
                "enabled": False
            }
        
        try:
            # Generate new 32-byte (256-bit) session key
            new_key = secrets.token_hex(32)  # 64 hex chars = 32 bytes
            
            # Validate key format
            if len(new_key) != 64:
                return {
                    "status": "error",
                    "error": "Generated key has incorrect length",
                    "enabled": True
                }
            
            # Get current key for comparison
            current_key = os.getenv("CONSOLE_AUTH_SESSION_KEY", "")
            
            result = {
                "status": "generated",
                "secret_type": "CONSOLE_AUTH_SESSION_KEY", 
                "new_key_length": len(new_key),
                "new_key_preview": f"{new_key[:8]}...{new_key[-8:]}",
                "key_changed": new_key != current_key,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "enabled": True
            }
            
            # Add rotation log entry
            self.rotation_log.append({
                "secret_type": "CONSOLE_AUTH_SESSION_KEY",
                "action": "generate",
                "timestamp": result["timestamp"],
                "key_changed": result["key_changed"]
            })
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def rotate_admin_token(self) -> Dict[str, Any]:
        """Generate new ADMIN_TOKEN.
        
        Returns:
            dict: Rotation result with new token info
        """
        if not ROTATE_ENABLED:
            return {
                "status": "disabled",
                "message": "Secret rotation is disabled",
                "enabled": False
            }
        
        try:
            # Generate new admin token (32 random bytes as base64)
            import base64
            new_token_bytes = secrets.token_bytes(32)
            new_token = base64.b64encode(new_token_bytes).decode('ascii')
            
            # Get current token for comparison
            current_token = os.getenv("ADMIN_TOKEN", "")
            
            result = {
                "status": "generated",
                "secret_type": "ADMIN_TOKEN",
                "new_token_length": len(new_token),
                "new_token_preview": f"{new_token[:8]}...{new_token[-8:]}",
                "token_changed": new_token != current_token,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "enabled": True
            }
            
            # Add rotation log entry
            self.rotation_log.append({
                "secret_type": "ADMIN_TOKEN",
                "action": "generate", 
                "timestamp": result["timestamp"],
                "token_changed": result["token_changed"]
            })
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def generate_salt(self, name: str, length: int = 16) -> Dict[str, Any]:
        """Generate cryptographic salt.
        
        Args:
            name: Salt identifier/name
            length: Salt length in bytes (default 16)
            
        Returns:
            dict: Salt generation result
        """
        if not ROTATE_ENABLED:
            return {
                "status": "disabled",
                "message": "Secret rotation is disabled",
                "enabled": False
            }
        
        try:
            if length < 8 or length > 64:
                return {
                    "status": "error",
                    "error": "Salt length must be between 8 and 64 bytes",
                    "enabled": True
                }
            
            # Generate cryptographic salt
            salt_bytes = secrets.token_bytes(length)
            salt_hex = salt_bytes.hex()
            
            result = {
                "status": "generated",
                "secret_type": "SALT",
                "name": name,
                "salt_length": length,
                "salt_hex": salt_hex,
                "salt_preview": f"{salt_hex[:8]}...{salt_hex[-8:]}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "enabled": True
            }
            
            # Add rotation log entry
            self.rotation_log.append({
                "secret_type": "SALT",
                "name": name,
                "action": "generate",
                "timestamp": result["timestamp"],
                "length": length
            })
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def preview_rotation_plan(self) -> Dict[str, Any]:
        """Preview what secrets would be rotated without executing.
        
        Returns:
            dict: Rotation plan without execution
        """
        if not ROTATE_ENABLED:
            return {
                "status": "disabled",
                "message": "Secret rotation is disabled",
                "enabled": False
            }
        
        try:
            plan = []
            
            # Check current secrets and plan rotations
            current_session_key = os.getenv("CONSOLE_AUTH_SESSION_KEY", "")
            plan.append({
                "secret_type": "CONSOLE_AUTH_SESSION_KEY",
                "current_exists": bool(current_session_key),
                "current_length": len(current_session_key) if current_session_key else 0,
                "recommended_action": "rotate" if current_session_key else "generate",
                "new_length": 64  # 32 bytes as hex
            })
            
            current_admin_token = os.getenv("ADMIN_TOKEN", "")
            plan.append({
                "secret_type": "ADMIN_TOKEN",
                "current_exists": bool(current_admin_token),
                "current_length": len(current_admin_token) if current_admin_token else 0,
                "recommended_action": "rotate" if current_admin_token else "generate",
                "new_length": 44  # 32 bytes base64 encoded
            })
            
            return {
                "status": "preview",
                "plan": plan,
                "secrets_count": len(plan),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "enabled": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def execute_rotation(self, secret_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rotation of specified secrets.
        
        Args:
            secret_types: List of secret types to rotate, or None for all
            
        Returns:
            dict: Execution result with rotated secrets
        """
        if not ROTATE_ENABLED:
            return {
                "status": "disabled",
                "message": "Secret rotation is disabled",
                "enabled": False
            }
        
        # Default to all secret types if none specified
        if secret_types is None:
            secret_types = ["CONSOLE_AUTH_SESSION_KEY", "ADMIN_TOKEN"]
        
        try:
            results = []
            
            if "CONSOLE_AUTH_SESSION_KEY" in secret_types:
                result = self.rotate_console_auth_session_key()
                results.append(result)
            
            if "ADMIN_TOKEN" in secret_types:
                result = self.rotate_admin_token()
                results.append(result)
            
            # Count successful rotations
            successful = sum(1 for r in results if r.get("status") == "generated")
            failed = len(results) - successful
            
            return {
                "status": "completed" if failed == 0 else "partial",
                "results": results,
                "successful_count": successful,
                "failed_count": failed,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "enabled": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def get_rotation_history(self) -> Dict[str, Any]:
        """Get history of secret rotations.
        
        Returns:
            dict: Rotation history log
        """
        if not ROTATE_ENABLED:
            return {
                "status": "disabled",
                "history": [],
                "enabled": False
            }
        
        return {
            "status": "ok",
            "history": self.rotation_log,
            "entries_count": len(self.rotation_log),
            "enabled": True
        }


# Global instance
_secret_rotator = None


def get_secret_rotator() -> SecretRotator:
    """Get global secret rotator instance.
    
    Returns:
        SecretRotator: Global secret rotator
    """
    global _secret_rotator
    if _secret_rotator is None:
        _secret_rotator = SecretRotator()
    return _secret_rotator


# CLI interface
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Secret rotation toolkit for WatchLockAI Sentinel")
    parser.add_argument("--action", choices=["preview", "execute", "history"], required=True,
                       help="Action to perform")
    parser.add_argument("--secrets", nargs="*", 
                       choices=["CONSOLE_AUTH_SESSION_KEY", "ADMIN_TOKEN"],
                       help="Specific secrets to rotate (default: all)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    rotator = get_secret_rotator()
    
    if args.action == "preview":
        result = rotator.preview_rotation_plan()
    elif args.action == "execute":
        result = rotator.execute_rotation(args.secrets)
    elif args.action == "history":
        result = rotator.get_rotation_history()
    
    if args.verbose:
        print(json.dumps(result, indent=2))
    else:
        print(f"Status: {result.get('status')}")
        if result.get('status') == 'error':
            print(f"Error: {result.get('error')}")
            sys.exit(1)
