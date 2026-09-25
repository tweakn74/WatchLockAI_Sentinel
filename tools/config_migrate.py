# File: tools/config_migrate.py  
# Purpose: Configuration migration utility with backup functionality (P3-001)

from __future__ import annotations
import os
import sys
import shutil
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ConfigMigrator:
    """Configuration migration utility with backup support"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize migrator
        
        Args:
            config_file: Path to config file (defaults to environment scan only)
        """
        self.config_file = Path(config_file) if config_file else None
        self.backup_dir = Path("config_backups")
        self.migration_rules = self._build_migration_rules()
    
    def _build_migration_rules(self) -> Dict[str, str]:
        """Build mapping of old configuration keys to new keys"""
        return {
            # Legacy key migrations (examples for future use)
            "ENABLE_HEALTH": "HEALTH_ENDPOINT_ENABLED",
            "DEBUG_METRICS": "METRICS_DEBUG_ENABLED", 
            "HOT_RELOAD": "CONFIG_HOT_RELOAD_ENABLED",
            "ADMIN_ENABLE": "ADMIN_AUTH_ENABLED",
            "RATE_LIMIT": "RATE_LIMIT_ENABLED",
            "ANOMALY_DETECT": "ANOMALY_ENABLED",
            "FILE_QUARANTINE": "QUARANTINE_ENABLED",
            "AUTH_ENABLE": "CONSOLE_AUTH_ENABLED",
            "AUTH_KEY": "CONSOLE_AUTH_SESSION_KEY",
            "STREAM_ENABLE": "STREAM_ENABLED",
            "LOG_SIZE": "LOG_MAX_BYTES",
            "LOG_COUNT": "LOG_BACKUPS",
            "REDACT_LOGS": "LOG_REDACT_SECRETS",
            "PLUGIN_ENABLE": "PLUGINS_ENABLED",
            "EXPORT_ENABLE": "EXPORT_ENABLED",
            
            # Value transformations
            "QUARANTINE_PATH": "QUARANTINE_DIR",
            "AUTH_DB": "CONSOLE_AUTH_USER_DB",
            "PLUGIN_PATH": "PLUGINS_DIR",
        }
    
    def scan_environment(self) -> Dict[str, str]:
        """Scan current environment for configuration variables"""
        config_vars = {}
        
        # Scan for all variables that might be configuration
        for key, value in os.environ.items():
            if any(key.startswith(prefix) for prefix in [
                "HEALTH_", "METRICS_", "CONFIG_", "ADMIN_", "RATE_", 
                "ANOMALY_", "QUARANTINE_", "CONSOLE_", "STREAM_", 
                "LOG_", "SERVICE_", "PLUGINS_", "EXPORT_"
            ]):
                config_vars[key] = value
            
            # Check for legacy keys
            if key in self.migration_rules:
                config_vars[key] = value
        
        return config_vars
    
    def scan_config_file(self) -> Dict[str, str]:
        """Scan configuration file for variables"""
        if not self.config_file or not self.config_file.exists():
            return {}
        
        config_vars = {}
        
        try:
            if self.config_file.suffix.lower() == '.json':
                # JSON configuration file
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            config_vars[key] = str(value)
            else:
                # Assume key=value format (like .env)
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"\'')
                                config_vars[key] = value
                            
        except Exception as e:
            print(f"Warning: Failed to parse config file {self.config_file}: {e}")
        
        return config_vars
    
    def detect_migrations_needed(self) -> List[Tuple[str, str, str]]:
        """Detect configuration migrations needed
        
        Returns:
            List of (old_key, new_key, current_value) tuples
        """
        migrations_needed = []
        
        # Scan environment
        env_vars = self.scan_environment()
        
        # Scan config file if provided
        if self.config_file:
            file_vars = self.scan_config_file()
            env_vars.update(file_vars)
        
        # Check for legacy keys that need migration
        for old_key, new_key in self.migration_rules.items():
            if old_key in env_vars:
                current_value = env_vars[old_key]
                # Check if new key already exists
                if new_key not in env_vars:
                    migrations_needed.append((old_key, new_key, current_value))
                else:
                    print(f"Info: {old_key} found but {new_key} already exists, skipping migration")
        
        return migrations_needed
    
    def create_backup(self, source_type: str = "environment") -> Optional[str]:
        """Create backup of current configuration
        
        Args:
            source_type: Type of backup ("environment", "file", or "both")
            
        Returns:
            Path to backup file or None if backup failed
        """
        try:
            self.backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if source_type in ["environment", "both"]:
                # Backup environment variables
                env_backup_file = self.backup_dir / f"environment_{timestamp}.json"
                env_vars = self.scan_environment()
                
                with open(env_backup_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "backup_type": "environment",
                        "timestamp": timestamp,
                        "variables": env_vars
                    }, f, indent=2)
                
                print(f"Environment backup created: {env_backup_file}")
            
            if source_type in ["file", "both"] and self.config_file and self.config_file.exists():
                # Backup config file  
                file_backup = self.backup_dir / f"{self.config_file.name}_{timestamp}.bak"
                shutil.copy2(self.config_file, file_backup)
                print(f"Config file backup created: {file_backup}")
                return str(file_backup)
            
            return str(env_backup_file) if source_type == "environment" else None
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def apply_migrations(self, dry_run: bool = False) -> Dict[str, any]:
        """Apply detected configuration migrations
        
        Args:
            dry_run: If True, only show what would be migrated without applying changes
            
        Returns:
            Migration results dictionary
        """
        migrations_needed = self.detect_migrations_needed()
        
        if not migrations_needed:
            return {
                "success": True,
                "message": "No migrations needed",
                "migrations_applied": [],
                "backup_path": None
            }
        
        print(f"Found {len(migrations_needed)} migrations needed:")
        for old_key, new_key, value in migrations_needed:
            print(f"  {old_key} -> {new_key} (value: {value})")
        
        if dry_run:
            return {
                "success": True,
                "message": f"Dry run: {len(migrations_needed)} migrations would be applied",
                "migrations_applied": [],
                "migrations_planned": migrations_needed,
                "backup_path": None
            }
        
        # Create backup before applying migrations
        backup_path = self.create_backup("both")
        
        applied_migrations = []
        errors = []
        
        try:
            # Apply environment variable migrations
            for old_key, new_key, value in migrations_needed:
                try:
                    # Set new environment variable
                    os.environ[new_key] = value
                    
                    # Remove old environment variable
                    if old_key in os.environ:
                        del os.environ[old_key]
                    
                    applied_migrations.append((old_key, new_key, value))
                    print(f"Migrated: {old_key} -> {new_key}")
                    
                except Exception as e:
                    errors.append(f"Failed to migrate {old_key}: {e}")
            
            # Update config file if present
            if self.config_file and self.config_file.exists():
                self._update_config_file(migrations_needed)
            
            success = len(errors) == 0
            message = f"Successfully applied {len(applied_migrations)} migrations"
            if errors:
                message += f" with {len(errors)} errors"
            
            return {
                "success": success,
                "message": message,
                "migrations_applied": applied_migrations,
                "errors": errors,
                "backup_path": backup_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Migration failed: {e}",
                "migrations_applied": applied_migrations,
                "errors": [str(e)],
                "backup_path": backup_path
            }
    
    def _update_config_file(self, migrations: List[Tuple[str, str, str]]):
        """Update configuration file with migrated keys"""
        if not self.config_file or not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply text replacements for key=value format
            updated_content = content
            for old_key, new_key, _ in migrations:
                # Replace key=value lines
                pattern = rf'^{re.escape(old_key)}\s*=(.*)$'
                replacement = f'{new_key}=\\1'
                updated_content = re.sub(pattern, replacement, updated_content, flags=re.MULTILINE)
            
            # Write updated content
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"Updated config file: {self.config_file}")
            
        except Exception as e:
            print(f"Warning: Failed to update config file {self.config_file}: {e}")
    
    def list_current_config(self) -> Dict[str, any]:
        """List current configuration state"""
        env_vars = self.scan_environment()
        file_vars = self.scan_config_file() if self.config_file else {}
        
        return {
            "environment_variables": env_vars,
            "config_file_variables": file_vars,
            "config_file": str(self.config_file) if self.config_file else None,
            "migration_rules": self.migration_rules,
            "total_env_vars": len(env_vars),
            "total_file_vars": len(file_vars)
        }


def main():
    """Command line interface for config migration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WatchLockAI Sentinel Configuration Migration Tool")
    parser.add_argument("--config-file", "-f", help="Path to configuration file")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be migrated without applying")
    parser.add_argument("--list", "-l", action="store_true", help="List current configuration")
    parser.add_argument("--backup", "-b", action="store_true", help="Create backup only")
    
    args = parser.parse_args()
    
    migrator = ConfigMigrator(args.config_file)
    
    if args.list:
        config_state = migrator.list_current_config()
        print("\n=== Current Configuration ===")
        print(f"Environment variables: {config_state['total_env_vars']}")
        print(f"Config file variables: {config_state['total_file_vars']}")
        if config_state['config_file']:
            print(f"Config file: {config_state['config_file']}")
        
        if config_state['environment_variables']:
            print("\nEnvironment Variables:")
            for key, value in sorted(config_state['environment_variables'].items()):
                print(f"  {key}={value}")
        
        if config_state['config_file_variables']:
            print("\nConfig File Variables:")
            for key, value in sorted(config_state['config_file_variables'].items()):
                print(f"  {key}={value}")
        
        return
    
    if args.backup:
        backup_path = migrator.create_backup("both")
        if backup_path:
            print(f"Backup created successfully: {backup_path}")
        else:
            print("Backup creation failed")
        return
    
    # Run migration
    result = migrator.apply_migrations(dry_run=args.dry_run)
    
    print(f"\n=== Migration Result ===")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result.get('migrations_applied'):
        print(f"Applied migrations:")
        for old_key, new_key, value in result['migrations_applied']:
            print(f"  {old_key} -> {new_key}")
    
    if result.get('migrations_planned'):
        print(f"Planned migrations:")
        for old_key, new_key, value in result['migrations_planned']:
            print(f"  {old_key} -> {new_key} (value: {value})")
    
    if result.get('errors'):
        print("Errors:")
        for error in result['errors']:
            print(f"  {error}")
    
    if result.get('backup_path'):
        print(f"Backup created: {result['backup_path']}")


if __name__ == "__main__":
    main()
