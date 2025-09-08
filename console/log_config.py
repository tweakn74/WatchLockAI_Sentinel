# File: console/log_config.py
# Purpose: Log rotation and redaction configuration (P3-002)

from __future__ import annotations
import os
import re
import logging
import logging.handlers
from typing import Optional, Dict, Any
from pathlib import Path


class SecretRedactionFilter(logging.Filter):
    """Logging filter that redacts sensitive information from log messages"""
    
    def __init__(self, enabled: bool = True):
        super().__init__()
        self.enabled = enabled
        self._build_redaction_patterns()
    
    def _build_redaction_patterns(self):
        """Build regex patterns for common secret formats"""
        self.patterns = [
            # API keys and tokens - improved patterns
            (re.compile(r'(token["\s]*[:=]["\s]*)([a-zA-Z0-9_\-]{16,})', re.IGNORECASE), r'\1[REDACTED]'),
            (re.compile(r'([^a-zA-Z]key["\s]*[:=]["\s]*)([a-zA-Z0-9_\-]{16,})', re.IGNORECASE), r'\1[REDACTED]'),
            (re.compile(r'(api[_\-]?key["\s]*[:=]["\s]*)([a-zA-Z0-9_\-]{16,})', re.IGNORECASE), r'\1[REDACTED]'),
            
            # Authorization headers - simplified and working patterns  
            (re.compile(r'(authorization:\s*token\s+)([a-zA-Z0-9_\-\.]{12,})', re.IGNORECASE), r'\1[REDACTED]'),
            (re.compile(r'(authorization:\s*bearer\s+)([a-zA-Z0-9_\-\.]{16,})', re.IGNORECASE), r'\1[REDACTED]'),
            (re.compile(r'(bearer\s+)([a-zA-Z0-9_\-\.]{16,})', re.IGNORECASE), r'\1[REDACTED]'),
            
            # Session IDs and cookies
            (re.compile(r'(session[_\-]?id["\s]*[:=]["\s]*)([a-zA-Z0-9_\-]{16,})', re.IGNORECASE), r'\1[REDACTED]'),
            (re.compile(r'(cookie["\s]*[:=]["\s]*["\']?)([^"\';\s]{20,})', re.IGNORECASE), r'\1[REDACTED]'),
            
            # Passwords
            (re.compile(r'(password["\s]*[:=]["\s]*["\']?)([^"\';\s\n]{8,})', re.IGNORECASE), r'\1[REDACTED]'),
            (re.compile(r'(passwd["\s]*[:=]["\s]*["\']?)([^"\';\s\n]{8,})', re.IGNORECASE), r'\1[REDACTED]'),
            (re.compile(r'(pwd["\s]*[:=]["\s]*["\']?)([^"\';\s\n]{8,})', re.IGNORECASE), r'\1[REDACTED]'),
            
            # Database connection strings
            (re.compile(r'(://[^:]+:)([^@]+)(@)', re.IGNORECASE), r'\1[REDACTED]\3'),
            
            # Generic secret patterns
            (re.compile(r'(secret["\s]*[:=]["\s]*["\']?)([a-zA-Z0-9_\-]{16,})', re.IGNORECASE), r'\1[REDACTED]'),
            
            # Hex strings that might be keys/tokens (32+ chars)
            (re.compile(r'(["\s:=])([a-fA-F0-9]{32,})(["\s,\]}])', re.IGNORECASE), r'\1[REDACTED]\3'),
        ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record and redact sensitive information"""
        if not self.enabled:
            return True
        
        # Redact message
        if hasattr(record, 'message') and record.message:
            record.message = self._redact_text(record.message)
        
        # Redact args if present
        if record.args:
            try:
                # Handle string formatting args
                if isinstance(record.args, (list, tuple)):
                    record.args = tuple(self._redact_text(str(arg)) if isinstance(arg, str) else arg 
                                       for arg in record.args)
                elif isinstance(record.args, dict):
                    record.args = {k: self._redact_text(str(v)) if isinstance(v, str) else v 
                                  for k, v in record.args.items()}
            except Exception:
                # If redaction fails, don't break logging
                pass
        
        # Redact extra fields for structured logging
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if isinstance(value, str) and len(value) > 15:  # Only redact longer strings
                    setattr(record, key, self._redact_text(value))
        
        return True
    
    def _redact_text(self, text: str) -> str:
        """Apply redaction patterns to text"""
        if not isinstance(text, str) or len(text) < 10 or not self.enabled:
            return text
        
        redacted_text = text
        for pattern, replacement in self.patterns:
            redacted_text = pattern.sub(replacement, redacted_text)
        
        return redacted_text


class RotatingLogConfig:
    """Configuration for rotating log files with redaction"""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 max_bytes: int = 1048576,  # 1MB
                 backup_count: int = 5,
                 redact_secrets: bool = True):
        """Initialize log configuration
        
        Args:
            log_dir: Directory for log files
            max_bytes: Maximum size per log file
            backup_count: Number of backup files to keep
            redact_secrets: Enable secret redaction
        """
        self.log_dir = Path(log_dir)
        self.max_bytes = max(1024, min(max_bytes, 104857600))  # 1KB - 100MB range
        self.backup_count = max(1, min(backup_count, 50))  # 1-50 range
        self.redact_secrets = redact_secrets
        
        # Ensure log directory exists
        self.log_dir.mkdir(exist_ok=True)
        
        # Create redaction filter
        self.redaction_filter = SecretRedactionFilter(enabled=redact_secrets)
    
    def create_rotating_handler(self, log_name: str, 
                               level: int = logging.INFO,
                               format_string: Optional[str] = None) -> logging.handlers.RotatingFileHandler:
        """Create a rotating file handler with redaction
        
        Args:
            log_name: Name of the log file (without extension)
            level: Logging level
            format_string: Custom format string
            
        Returns:
            Configured RotatingFileHandler
        """
        log_file = self.log_dir / f"{log_name}.log"
        
        # Create rotating handler
        handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # Set level
        handler.setLevel(level)
        
        # Add redaction filter
        handler.addFilter(self.redaction_filter)
        
        # Set format
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        
        return handler
    
    def setup_logger(self, logger_name: str, 
                    log_file_name: str,
                    level: int = logging.INFO,
                    format_string: Optional[str] = None) -> logging.Logger:
        """Set up a logger with rotating file handler
        
        Args:
            logger_name: Name of the logger
            log_file_name: Name of the log file 
            level: Logging level
            format_string: Custom format string
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(logger_name)
        
        # Remove existing handlers to avoid duplication
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add rotating handler
        handler = self.create_rotating_handler(log_file_name, level, format_string)
        logger.addHandler(handler)
        logger.setLevel(level)
        
        # Prevent propagation to avoid duplicate logs
        logger.propagate = False
        
        return logger
    
    def get_log_status(self) -> Dict[str, Any]:
        """Get current logging configuration status"""
        return {
            "log_directory": str(self.log_dir),
            "max_bytes": self.max_bytes,
            "backup_count": self.backup_count,
            "redact_secrets": self.redact_secrets,
            "directory_exists": self.log_dir.exists(),
            "total_log_files": len(list(self.log_dir.glob("*.log*"))) if self.log_dir.exists() else 0
        }


# Global log config instance  
_global_log_config = None

def get_log_config() -> RotatingLogConfig:
    """Get global log configuration instance"""
    global _global_log_config
    if _global_log_config is None:
        # Read from environment variables
        max_bytes = int(os.getenv("LOG_MAX_BYTES", "1048576"))
        backup_count = int(os.getenv("LOG_BACKUPS", "5")) 
        redact_secrets = os.getenv("LOG_REDACT_SECRETS", "1").strip().lower() in {"1", "true", "yes", "on"}
        
        _global_log_config = RotatingLogConfig(
            max_bytes=max_bytes,
            backup_count=backup_count,
            redact_secrets=redact_secrets
        )
    return _global_log_config


def setup_application_logging():
    """Set up application-wide logging configuration"""
    log_config = get_log_config()
    
    # Set up main application logger
    app_logger = log_config.setup_logger(
        "sentinel.app", 
        "sentinel", 
        level=logging.INFO,
        format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up metrics logger
    metrics_logger = log_config.setup_logger(
        "sentinel.metrics",
        "metrics",
        level=logging.INFO,
        format_string='%(asctime)s - METRICS - %(message)s'
    )
    
    # Set up audit logger  
    audit_logger = log_config.setup_logger(
        "sentinel.audit",
        "audit", 
        level=logging.INFO,
        format_string='%(asctime)s - AUDIT - %(message)s'
    )
    
    return {
        "app": app_logger,
        "metrics": metrics_logger, 
        "audit": audit_logger,
        "config": log_config.get_log_status()
    }


def test_redaction():
    """Test function for redaction patterns"""
    test_messages = [
        "User logged in with token: abc123def456ghi789",
        "API_KEY=sk_test_1234567890abcdef1234567890abcdef",
        "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
        "password=supersecret123",
        "Database: postgresql://user:mypassword@localhost/db",
        "session_id=a1b2c3d4e5f6g7h8i9j0",
        "Normal log message without secrets"
    ]
    
    redaction_filter = SecretRedactionFilter(enabled=True)
    
    print("Testing redaction patterns:")
    for msg in test_messages:
        # Create a mock log record
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg=msg, args=(), exc_info=None
        )
        record.message = msg
        
        redaction_filter.filter(record)
        print(f"Original: {msg}")
        print(f"Redacted: {record.message}")
        print("-" * 50)


if __name__ == "__main__":
    # Test the redaction functionality
    test_redaction()
