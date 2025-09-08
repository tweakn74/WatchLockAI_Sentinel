# File: console/auth.py
# Purpose: Web console authentication system with session-based auth and PBKDF2 password hashing

from __future__ import annotations
import os
import json
import hashlib
import secrets
import hmac
from typing import Dict, Optional, Tuple
from pathlib import Path


class AuthConfig:
    """Configuration for console authentication system"""
    
    def __init__(self):
        self.enabled = os.environ.get("CONSOLE_AUTH_ENABLED", "0") == "1"
        self.session_key = os.environ.get("CONSOLE_AUTH_SESSION_KEY", "")
        self.user_db_path = os.environ.get("CONSOLE_AUTH_USER_DB", "data/auth/users.json")
        
        # Validate session key when enabled
        if self.enabled and (not self.session_key or len(self.session_key) < 64):
            raise ValueError("CONSOLE_AUTH_SESSION_KEY must be 32+ bytes hex (64+ chars) when auth enabled")


class UserDatabase:
    """Flat file user database with PBKDF2 password hashing"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file and directory exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._save_users({})
    
    def _load_users(self) -> Dict[str, str]:
        """Load users from JSON file"""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict[str, str]):
        """Save users to JSON file"""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using PBKDF2 with random salt"""
        salt = secrets.token_bytes(16)
        iterations = 100000  # Minimum 100k iterations for security
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        
        # Format: pbkdf2$sha256$iterations$salt$hash (all hex encoded)
        return f"pbkdf2$sha256${iterations}${salt.hex()}${key.hex()}"
    
    def _verify_password(self, password: str, pw_hash: str) -> bool:
        """Verify password against stored hash using constant-time comparison"""
        try:
            parts = pw_hash.split('$')
            if len(parts) != 5 or parts[0] != 'pbkdf2' or parts[1] != 'sha256':
                return False
            
            iterations = int(parts[2])
            salt = bytes.fromhex(parts[3])
            stored_key = bytes.fromhex(parts[4])
            
            # Recompute hash with same parameters
            computed_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
            
            # Constant-time comparison
            return hmac.compare_digest(stored_key, computed_key)
        except (ValueError, IndexError):
            return False
    
    def add_user(self, username: str, password: str) -> bool:
        """Add new user to database"""
        users = self._load_users()
        if username in users:
            return False  # User already exists
        
        users[username] = self._hash_password(password)
        self._save_users(users)
        return True
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        users = self._load_users()
        if username not in users:
            return False
        
        return self._verify_password(password, users[username])
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        users = self._load_users()
        return username in users


class SessionManager:
    """Cookie-based session management with signed sessions"""
    
    def __init__(self, session_key: str):
        if not session_key:
            raise ValueError("Session key required")
        self.session_key = bytes.fromhex(session_key)
        self.cookie_name = "sentinel_session"
    
    def create_session_token(self, username: str) -> str:
        """Create signed session token for user"""
        # Simple session format: username:timestamp:signature
        import time
        timestamp = str(int(time.time()))
        message = f"{username}:{timestamp}"
        
        # Sign with HMAC
        signature = hmac.new(self.session_key, message.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"{message}:{signature}"
    
    def verify_session_token(self, token: str) -> Optional[str]:
        """Verify session token and return username if valid"""
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return None
            
            username, timestamp, signature = parts
            message = f"{username}:{timestamp}"
            
            # Verify signature
            expected_signature = hmac.new(self.session_key, message.encode('utf-8'), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Check if session is not too old (24 hours)
            import time
            session_time = int(timestamp)
            if time.time() - session_time > 86400:  # 24 hours
                return None
            
            return username
        except (ValueError, IndexError):
            return None
    
    def get_cookie_config(self) -> Dict[str, any]:
        """Get cookie configuration for secure session cookies"""
        return {
            "httponly": True,
            "secure": True,  # HTTPS only in production
            "samesite": "strict",
            "max_age": 86400  # 24 hours
        }


class ConsoleAuth:
    """Main authentication manager"""
    
    def __init__(self):
        self.config = AuthConfig()
        self.enabled = self.config.enabled
        
        if self.enabled:
            self.user_db = UserDatabase(self.config.user_db_path)
            self.session_manager = SessionManager(self.config.session_key)
        else:
            self.user_db = None
            self.session_manager = None
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        if not self.enabled or not self.user_db:
            return False
        return self.user_db.verify_user(username, password)
    
    def create_session(self, username: str) -> str:
        """Create session token for authenticated user"""
        if not self.enabled or not self.session_manager:
            raise ValueError("Authentication not enabled")
        return self.session_manager.create_session_token(username)
    
    def verify_session(self, token: str) -> Optional[str]:
        """Verify session token and return username"""
        if not self.enabled or not self.session_manager:
            return None
        return self.session_manager.verify_session_token(token)
    
    def get_cookie_config(self) -> Dict[str, any]:
        """Get secure cookie configuration"""
        if not self.enabled or not self.session_manager:
            return {}
        return self.session_manager.get_cookie_config()
    
    @property
    def cookie_name(self) -> str:
        """Get session cookie name"""
        if not self.enabled or not self.session_manager:
            return ""
        return self.session_manager.cookie_name


# Global auth instance
_global_auth = None

def get_auth() -> ConsoleAuth:
    """Get global auth instance"""
    global _global_auth
    if _global_auth is None:
        _global_auth = ConsoleAuth()
    return _global_auth


# Utility functions for FastAPI integration
def get_session_user(request) -> Optional[str]:
    """Extract and verify user from session cookie"""
    try:
        auth = get_auth()
        if not auth.enabled:
            return None
            
        # Try to get session cookie
        token = request.cookies.get(auth.cookie_name)
        if not token:
            return None
            
        return auth.verify_session(token)
    except Exception:
        return None


def create_default_admin_user():
    """Create default admin user if none exist (for initial setup)"""
    auth = get_auth()
    if not auth.enabled or not auth.user_db:
        return
    
    # Check if any users exist
    users = auth.user_db._load_users()
    if users:
        return  # Users already exist
    
    # Create default admin with secure random password
    default_password = secrets.token_urlsafe(16)
    auth.user_db.add_user("admin", default_password)
    
    # Log the default credentials (in real deployment, this should be handled securely)
    print(f"Created default admin user - Username: admin, Password: {default_password}")
    print("Please change the default password immediately!")
