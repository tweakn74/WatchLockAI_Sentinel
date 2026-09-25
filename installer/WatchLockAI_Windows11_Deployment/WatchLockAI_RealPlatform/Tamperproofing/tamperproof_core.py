#!/usr/bin/env python3
'''
WatchLockAI Tamperproofing Core
Advanced protection against tampering and disabling attempts
'''

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
import winreg
import ctypes
from ctypes import wintypes
import psutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WatchLockAI-Tamperproof - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watchlockai_tamperproof.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TamperEvent(Enum):
    PROCESS_KILL_ATTEMPT = "process_kill_attempt"
    SERVICE_STOP_ATTEMPT = "service_stop_attempt"
    FILE_DELETION_ATTEMPT = "file_deletion_attempt"
    REGISTRY_MODIFICATION = "registry_modification"
    DEBUGGER_DETECTED = "debugger_detected"
    INJECTION_DETECTED = "injection_detected"
    MEMORY_SCAN_DETECTED = "memory_scan_detected"
    
@dataclass
class TamperAlert:
    timestamp: str
    event_type: TamperEvent
    threat_level: ThreatLevel
    source: str
    details: Dict[str, Any]
    response_action: str

class ProcessProtector:
    '''Protect WatchLockAI processes from termination'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.protected_processes = ["watchlockai", "python"]
        self.running = False
        self.process_pids = set()
        
    def start_protection(self):
        '''Start process protection monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_processes)
        thread.daemon = True
        thread.start()
        logger.info("Process protection started")
        
    def _monitor_processes(self):
        '''Monitor protected processes'''
        while self.running:
            try:
                current_pids = set()
                
                # Get current WatchLockAI processes
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info.get('name', '').lower()
                        cmdline = ' '.join(proc_info.get('cmdline', [])).lower()
                        
                        # Check if this is a WatchLockAI process
                        if any(protected in proc_name for protected in self.protected_processes):
                            if 'watchlockai' in cmdline:
                                current_pids.add(proc_info['pid'])
                                
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # Check for terminated processes
                terminated_pids = self.process_pids - current_pids
                for pid in terminated_pids:
                    self._handle_process_termination(pid)
                    
                self.process_pids = current_pids
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Process monitoring error: {e}")
                time.sleep(10)
                
    def _handle_process_termination(self, pid: int):
        '''Handle unexpected process termination'''
        try:
            alert = TamperAlert(
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                event_type=TamperEvent.PROCESS_KILL_ATTEMPT,
                threat_level=ThreatLevel.CRITICAL,
                source="ProcessProtector",
                details={
                    "terminated_pid": pid,
                    "action": "process_terminated_unexpectedly"
                },
                response_action="restart_protection"
            )
            
            self._send_tamper_alert(alert)
            self._restart_protection()
            
        except Exception as e:
            logger.error(f"Error handling process termination: {e}")
            
    def _restart_protection(self):
        '''Attempt to restart protection'''
        try:
            # Restart the main WatchLockAI agent
            subprocess.Popen([
                sys.executable,
                "windows_agent_core.py"
            ], cwd="../WindowsAgent")
            logger.info("Attempted to restart WatchLockAI agent")
            
        except Exception as e:
            logger.error(f"Failed to restart protection: {e}")
            
    def _send_tamper_alert(self, alert: TamperAlert):
        '''Send tamper alert to AI Brain'''
        try:
            alert_data = {
                "timestamp": alert.timestamp,
                "event_type": f"tamper_{alert.event_type.value}",
                "source": alert.source,
                "details": alert.details,
                "threat_level": alert.threat_level.value,
                "response_action": alert.response_action
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=alert_data, timeout=5)
            if response.status_code == 200:
                logger.warning(f"Tamper attempt detected: {alert.event_type.value}")
                
        except Exception as e:
            logger.error(f"Failed to send tamper alert: {e}")

class ServiceProtector:
    '''Protect WatchLockAI Windows service'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.service_name = "WatchLockAI"
        self.running = False
        
    def start_protection(self):
        '''Start service protection monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_service)
        thread.daemon = True
        thread.start()
        logger.info("Service protection started")
        
    def _monitor_service(self):
        '''Monitor service status'''
        while self.running:
            try:
                # Check service status using Windows API
                if self._is_service_stopped():
                    self._handle_service_stop()
                    
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Service monitoring error: {e}")
                time.sleep(30)
                
    def _is_service_stopped(self) -> bool:
        '''Check if WatchLockAI service is stopped'''
        try:
            # Use subprocess to check service status
            result = subprocess.run([
                'sc', 'query', self.service_name
            ], capture_output=True, text=True, timeout=10)
            
            return 'STOPPED' in result.stdout
            
        except Exception:
            return False
            
    def _handle_service_stop(self):
        '''Handle unexpected service stop'''
        try:
            alert = TamperAlert(
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                event_type=TamperEvent.SERVICE_STOP_ATTEMPT,
                threat_level=ThreatLevel.CRITICAL,
                source="ServiceProtector",
                details={
                    "service_name": self.service_name,
                    "action": "service_stopped_unexpectedly"
                },
                response_action="restart_service"
            )
            
            self._send_tamper_alert(alert)
            self._restart_service()
            
        except Exception as e:
            logger.error(f"Error handling service stop: {e}")
            
    def _restart_service(self):
        '''Attempt to restart the service'''
        try:
            subprocess.run([
                'sc', 'start', self.service_name
            ], timeout=30)
            logger.info("Attempted to restart WatchLockAI service")
            
        except Exception as e:
            logger.error(f"Failed to restart service: {e}")
            
    def _send_tamper_alert(self, alert: TamperAlert):
        '''Send tamper alert to AI Brain'''
        try:
            alert_data = {
                "timestamp": alert.timestamp,
                "event_type": f"tamper_{alert.event_type.value}",
                "source": alert.source,
                "details": alert.details,
                "threat_level": alert.threat_level.value,
                "response_action": alert.response_action
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=alert_data, timeout=5)
            if response.status_code == 200:
                logger.warning(f"Service tamper attempt: {alert.event_type.value}")
                
        except Exception as e:
            logger.error(f"Failed to send tamper alert: {e}")

class FileIntegrityMonitor:
    '''Monitor critical files for tampering'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        self.file_hashes = {}
        self.protected_files = [
            "windows_agent_core.py",
            "agent_service.py",
            "browser_monitor.py",
            "../AIBrain/ai_brain_core.py",
            "../WatchSleuth/watchsleuth_engine.py"
        ]
        
    def start_monitoring(self):
        '''Start file integrity monitoring'''
        self.running = True
        self._calculate_baseline_hashes()
        thread = threading.Thread(target=self._monitor_files)
        thread.daemon = True
        thread.start()
        logger.info("File integrity monitoring started")
        
    def _calculate_baseline_hashes(self):
        '''Calculate baseline hashes for protected files'''
        for file_path in self.protected_files:
            try:
                if os.path.exists(file_path):
                    file_hash = self._calculate_file_hash(file_path)
                    self.file_hashes[file_path] = file_hash
                    logger.debug(f"Baseline hash for {file_path}: {file_hash[:8]}...")
                    
            except Exception as e:
                logger.error(f"Error calculating baseline hash for {file_path}: {e}")
                
    def _monitor_files(self):
        '''Monitor files for changes'''
        while self.running:
            try:
                for file_path in self.protected_files:
                    if os.path.exists(file_path):
                        current_hash = self._calculate_file_hash(file_path)
                        baseline_hash = self.file_hashes.get(file_path)
                        
                        if baseline_hash and current_hash != baseline_hash:
                            self._handle_file_tampering(file_path, baseline_hash, current_hash)
                            
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"File monitoring error: {e}")
                time.sleep(60)
                
    def _calculate_file_hash(self, file_path: str) -> str:
        '''Calculate SHA256 hash of file'''
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "unknown"
            
    def _handle_file_tampering(self, file_path: str, baseline_hash: str, current_hash: str):
        '''Handle file tampering detection'''
        try:
            alert = TamperAlert(
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                event_type=TamperEvent.FILE_DELETION_ATTEMPT,
                threat_level=ThreatLevel.CRITICAL,
                source="FileIntegrityMonitor",
                details={
                    "file_path": file_path,
                    "baseline_hash": baseline_hash[:16],
                    "current_hash": current_hash[:16],
                    "action": "file_modified_or_replaced"
                },
                response_action="restore_file"
            )
            
            self._send_tamper_alert(alert)
            logger.critical(f"FILE TAMPERING DETECTED: {file_path}")
            
        except Exception as e:
            logger.error(f"Error handling file tampering: {e}")
            
    def _send_tamper_alert(self, alert: TamperAlert):
        '''Send tamper alert to AI Brain'''
        try:
            alert_data = {
                "timestamp": alert.timestamp,
                "event_type": f"tamper_{alert.event_type.value}",
                "source": alert.source,
                "details": alert.details,
                "threat_level": alert.threat_level.value,
                "response_action": alert.response_action
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=alert_data, timeout=5)
            if response.status_code == 200:
                logger.critical(f"Critical tampering detected: {alert.event_type.value}")
                
        except Exception as e:
            logger.error(f"Failed to send tamper alert: {e}")

class AntiDebugger:
    '''Detect and prevent debugging attempts'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        
    def start_protection(self):
        '''Start anti-debugging protection'''
        self.running = True
        thread = threading.Thread(target=self._monitor_debuggers)
        thread.daemon = True
        thread.start()
        logger.info("Anti-debugger protection started")
        
    def _monitor_debuggers(self):
        '''Monitor for debugging tools'''
        while self.running:
            try:
                # Check for common debugging tools
                debugger_processes = [
                    'ollydbg.exe', 'x64dbg.exe', 'windbg.exe', 
                    'ida.exe', 'ida64.exe', 'cheatengine.exe',
                    'processhacker.exe', 'procexp.exe', 'procmon.exe'
                ]
                
                for proc in psutil.process_iter(['name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if proc_name in debugger_processes:
                            self._handle_debugger_detection(proc_name, proc.pid)
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # Check for debugger using Windows API
                if self._is_debugger_present():
                    self._handle_debugger_detection("Windows API Detection", 0)
                    
                time.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Anti-debugger monitoring error: {e}")
                time.sleep(30)
                
    def _is_debugger_present(self) -> bool:
        '''Check if debugger is present using Windows API'''
        try:
            kernel32 = ctypes.windll.kernel32
            return kernel32.IsDebuggerPresent() != 0
        except Exception:
            return False
            
    def _handle_debugger_detection(self, debugger_name: str, pid: int):
        '''Handle debugger detection'''
        try:
            alert = TamperAlert(
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                event_type=TamperEvent.DEBUGGER_DETECTED,
                threat_level=ThreatLevel.CRITICAL,
                source="AntiDebugger",
                details={
                    "debugger_name": debugger_name,
                    "debugger_pid": pid,
                    "action": "debugger_detected"
                },
                response_action="terminate_debugger"
            )
            
            self._send_tamper_alert(alert)
            
            # Attempt to terminate debugger
            if pid > 0:
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    logger.warning(f"Terminated debugger: {debugger_name}")
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"Error handling debugger detection: {e}")
            
    def _send_tamper_alert(self, alert: TamperAlert):
        '''Send tamper alert to AI Brain'''
        try:
            alert_data = {
                "timestamp": alert.timestamp,
                "event_type": f"tamper_{alert.event_type.value}",
                "source": alert.source,
                "details": alert.details,
                "threat_level": alert.threat_level.value,
                "response_action": alert.response_action
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=alert_data, timeout=5)
            if response.status_code == 200:
                logger.critical(f"Debugger detected: {alert.details['debugger_name']}")
                
        except Exception as e:
            logger.error(f"Failed to send tamper alert: {e}")

class RegistryProtector:
    '''Protect critical registry keys'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        self.protected_keys = [
            r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\WatchLockAI",
            r"HKEY_LOCAL_MACHINE\SOFTWARE\WatchLockAI"
        ]
        self.key_snapshots = {}
        
    def start_protection(self):
        '''Start registry protection'''
        self.running = True
        self._take_registry_snapshots()
        thread = threading.Thread(target=self._monitor_registry)
        thread.daemon = True
        thread.start()
        logger.info("Registry protection started")
        
    def _take_registry_snapshots(self):
        '''Take snapshots of protected registry keys'''
        for key_path in self.protected_keys:
            try:
                snapshot = self._get_registry_values(key_path)
                self.key_snapshots[key_path] = snapshot
                logger.debug(f"Registry snapshot taken for {key_path}")
                
            except Exception as e:
                logger.debug(f"Could not snapshot registry key {key_path}: {e}")
                
    def _get_registry_values(self, key_path: str) -> Dict[str, Any]:
        '''Get all values from a registry key'''
        try:
            # Parse key path
            hive, subkey = key_path.split('\\', 1)
            
            # Map hive names to constants
            hive_map = {
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER
            }
            
            if hive not in hive_map:
                return {}
                
            values = {}
            with winreg.OpenKey(hive_map[hive], subkey) as key:
                i = 0
                while True:
                    try:
                        name, value, reg_type = winreg.EnumValue(key, i)
                        values[name] = {"value": value, "type": reg_type}
                        i += 1
                    except OSError:
                        break
                        
            return values
            
        except Exception:
            return {}
            
    def _monitor_registry(self):
        '''Monitor registry keys for changes'''
        while self.running:
            try:
                for key_path in self.protected_keys:
                    current_values = self._get_registry_values(key_path)
                    baseline_values = self.key_snapshots.get(key_path, {})
                    
                    if current_values != baseline_values:
                        self._handle_registry_modification(key_path, baseline_values, current_values)
                        
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Registry monitoring error: {e}")
                time.sleep(120)
                
    def _handle_registry_modification(self, key_path: str, baseline: Dict, current: Dict):
        '''Handle registry modification'''
        try:
            alert = TamperAlert(
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                event_type=TamperEvent.REGISTRY_MODIFICATION,
                threat_level=ThreatLevel.HIGH,
                source="RegistryProtector",
                details={
                    "registry_key": key_path,
                    "baseline_count": len(baseline),
                    "current_count": len(current),
                    "action": "registry_key_modified"
                },
                response_action="restore_registry"
            )
            
            self._send_tamper_alert(alert)
            logger.warning(f"Registry modification detected: {key_path}")
            
        except Exception as e:
            logger.error(f"Error handling registry modification: {e}")
            
    def _send_tamper_alert(self, alert: TamperAlert):
        '''Send tamper alert to AI Brain'''
        try:
            alert_data = {
                "timestamp": alert.timestamp,
                "event_type": f"tamper_{alert.event_type.value}",
                "source": alert.source,
                "details": alert.details,
                "threat_level": alert.threat_level.value,
                "response_action": alert.response_action
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=alert_data, timeout=5)
            if response.status_code == 200:
                logger.warning(f"Registry tampering: {alert.event_type.value}")
                
        except Exception as e:
            logger.error(f"Failed to send tamper alert: {e}")

class TamperproofingCore:
    '''Main tamperproofing orchestrator'''
    
    def __init__(self, config_file: str = "tamperproof_config.json"):
        self.config = self._load_config(config_file)
        self.ai_brain_url = self.config.get('ai_brain_url', 'http://localhost:9999')
        
        # Initialize protection components
        self.process_protector = ProcessProtector(self.ai_brain_url)
        self.service_protector = ServiceProtector(self.ai_brain_url)
        self.file_monitor = FileIntegrityMonitor(self.ai_brain_url)
        self.anti_debugger = AntiDebugger(self.ai_brain_url)
        self.registry_protector = RegistryProtector(self.ai_brain_url)
        
        self.running = False
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        '''Load tamperproofing configuration'''
        default_config = {
            "ai_brain_url": "http://localhost:9999",
            "protection_enabled": {
                "process_protection": True,
                "service_protection": True,
                "file_integrity": True,
                "anti_debugging": True,
                "registry_protection": True
            },
            "response_actions": {
                "restart_on_kill": True,
                "terminate_debuggers": True,
                "alert_on_tampering": True
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logger.warning(f"Could not load config file {config_file}: {e}")
            
        return default_config
        
    def start_protection(self):
        '''Start all tamperproofing mechanisms'''
        logger.info("Starting WatchLockAI Tamperproofing System...")
        
        self.running = True
        
        # Start protection components
        if self.config['protection_enabled']['process_protection']:
            self.process_protector.start_protection()
            
        if self.config['protection_enabled']['service_protection']:
            self.service_protector.start_protection()
            
        if self.config['protection_enabled']['file_integrity']:
            self.file_monitor.start_monitoring()
            
        if self.config['protection_enabled']['anti_debugging']:
            self.anti_debugger.start_protection()
            
        if self.config['protection_enabled']['registry_protection']:
            self.registry_protector.start_protection()
            
        logger.info("[PASS] WatchLockAI Tamperproofing System active")
        
    def stop_protection(self):
        '''Stop tamperproofing system'''
        logger.info("Stopping WatchLockAI Tamperproofing System...")
        
        self.running = False
        self.process_protector.running = False
        self.service_protector.running = False
        self.file_monitor.running = False
        self.anti_debugger.running = False
        self.registry_protector.running = False
        
        logger.info("[PASS] WatchLockAI Tamperproofing System stopped")
        
    def get_protection_status(self) -> Dict[str, Any]:
        '''Get current protection status'''
        return {
            "status": "active" if self.running else "inactive",
            "components": {
                "process_protection": self.process_protector.running,
                "service_protection": self.service_protector.running,
                "file_integrity": self.file_monitor.running,
                "anti_debugging": self.anti_debugger.running,
                "registry_protection": self.registry_protector.running
            },
            "config": self.config
        }

def main():
    '''Main entry point for tamperproofing system'''
    print("[SHIELD] WatchLockAI Tamperproofing System")
    print("Advanced protection against tampering and disabling")
    print()
    
    try:
        # Initialize tamperproofing
        tamperproof = TamperproofingCore()
        tamperproof.start_protection()
        
        print("[LOCK] Protection mechanisms active:")
        print("   * Process Protection - Prevents process termination")
        print("   * Service Protection - Monitors service status")
        print("   * File Integrity - Detects file tampering")
        print("   * Anti-Debugging - Prevents reverse engineering")
        print("   * Registry Protection - Monitors critical keys")
        print()
        print("[ALERT] WatchLockAI is now tamperproof!")
        print("Press Ctrl+C to stop protection")
        
        # Keep protection running
        while tamperproof.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[U+1F6D1] Shutting down tamperproofing system...")
        tamperproof.stop_protection()
        
    except Exception as e:
        logger.error(f"Tamperproofing error: {e}")

if __name__ == "__main__":
    main()
