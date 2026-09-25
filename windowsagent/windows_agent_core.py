#!/usr/bin/env python3
'''
WatchLockAI Windows Agent Core
Real-time monitoring and protection agent for Windows systems
'''

import os
import sys
import json
import time
import threading
import sqlite3
import datetime
import hashlib
import subprocess
import socket
import psutil
import winreg
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WatchLockAI-Agent - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watchlockai_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitoringType(Enum):
    FILE_SYSTEM = "file_system"
    PROCESS = "process"
    NETWORK = "network"
    REGISTRY = "registry"
    BROWSER = "browser"
    MEMORY = "memory"

class EventSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AgentEvent:
    event_id: str
    timestamp: str
    monitoring_type: MonitoringType
    severity: EventSeverity
    source: str
    description: str
    details: Dict[str, Any]
    process_info: Optional[Dict[str, Any]] = None
    network_info: Optional[Dict[str, Any]] = None

class FileSystemMonitor:
    '''Monitor file system activities using Windows APIs'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.monitored_paths = [
            "C:\\Windows\\System32",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\Users"
        ]
        self.suspicious_extensions = ['.exe', '.dll', '.scr', '.bat', '.cmd', '.ps1', '.vbs']
        self.running = False
        
    def start_monitoring(self):
        '''Start file system monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_filesystem)
        thread.daemon = True
        thread.start()
        logger.info("File system monitoring started")
        
    def _monitor_filesystem(self):
        '''Monitor file system changes'''
        while self.running:
            try:
                # Monitor file system using DIR command with timestamp
                for path in self.monitored_paths:
                    if os.path.exists(path):
                        self._scan_directory_changes(path)
                        
                time.sleep(30)  # Scan every 30 seconds
                
            except Exception as e:
                logger.error(f"File system monitoring error: {e}")
                time.sleep(60)
                
    def _scan_directory_changes(self, directory: str):
        '''Scan directory for recent changes'''
        try:
            recent_threshold = datetime.datetime.now() - datetime.timedelta(minutes=5)
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat_info = os.stat(file_path)
                        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                        
                        # Check if file was recently modified
                        if modified_time > recent_threshold:
                            self._analyze_file_change(file_path, stat_info)
                            
                    except (OSError, PermissionError):
                        continue  # Skip files we can't access
                        
                # Only scan one level deep for performance
                if root != directory:
                    break
                    
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
            
    def _analyze_file_change(self, file_path: str, stat_info):
        '''Analyze file change for suspicious activity'''
        try:
            file_ext = Path(file_path).suffix.lower()
            file_size = stat_info.st_size
            
            # Check for suspicious characteristics
            is_suspicious = False
            reasons = []
            
            # Check file extension
            if file_ext in self.suspicious_extensions:
                is_suspicious = True
                reasons.append(f"Suspicious file extension: {file_ext}")
                
            # Check file location
            if "\\Temp\\" in file_path or "\\AppData\\" in file_path:
                is_suspicious = True
                reasons.append("File in temporary location")
                
            # Check file size (very small or very large executables)
            if file_ext == '.exe' and (file_size < 1024 or file_size > 100*1024*1024):
                is_suspicious = True
                reasons.append(f"Unusual executable size: {file_size} bytes")
                
            if is_suspicious:
                self._report_file_event(file_path, stat_info, reasons)
                
        except Exception as e:
            logger.error(f"Error analyzing file change: {e}")
            
    def _report_file_event(self, file_path: str, stat_info, reasons: List[str]):
        '''Report suspicious file event to AI Brain'''
        try:
            file_hash = self._calculate_file_hash(file_path)
            
            event = AgentEvent(
                event_id=f"file_{int(time.time())}_{hash(file_path) % 10000}",
                timestamp=datetime.datetime.now().isoformat(),
                monitoring_type=MonitoringType.FILE_SYSTEM,
                severity=EventSeverity.MEDIUM,
                source="FileSystemMonitor",
                description=f"Suspicious file activity: {Path(file_path).name}",
                details={
                    "file_path": file_path,
                    "file_size": stat_info.st_size,
                    "modified_time": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "file_hash": file_hash,
                    "reasons": reasons
                }
            )
            
            self._send_to_ai_brain(event)
            
        except Exception as e:
            logger.error(f"Error reporting file event: {e}")
            
    def _calculate_file_hash(self, file_path: str) -> str:
        '''Calculate MD5 hash of file'''
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return "unknown"
            
    def _send_to_ai_brain(self, event: AgentEvent):
        '''Send event to AI Brain for analysis'''
        try:
            event_data = {
                "timestamp": event.timestamp,
                "event_type": f"{event.monitoring_type.value}_{event.severity.value}",
                "source": event.source,
                "details": event.details,
                "threat_level": event.severity.value
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event_data, timeout=5)
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('threat_detected'):
                    logger.warning(f"AI Brain detected threat: {analysis.get('narrative')}")
                    
        except Exception as e:
            logger.error(f"Failed to send event to AI Brain: {e}")

class ProcessMonitor:
    '''Monitor process creation and termination'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        self.known_processes = set()
        self.suspicious_processes = [
            'mimikatz.exe', 'procdump.exe', 'psexec.exe', 'wce.exe',
            'pwdump.exe', 'fgdump.exe', 'gsecdump.exe', 'cachedump.exe'
        ]
        
    def start_monitoring(self):
        '''Start process monitoring'''
        self.running = True
        
        # Initialize known processes
        self._update_process_list()
        
        thread = threading.Thread(target=self._monitor_processes)
        thread.daemon = True
        thread.start()
        logger.info("Process monitoring started")
        
    def _monitor_processes(self):
        '''Monitor process activities'''
        while self.running:
            try:
                current_processes = set()
                
                for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'create_time']):
                    try:
                        proc_info = proc.info
                        proc_id = (proc_info['pid'], proc_info['name'])
                        current_processes.add(proc_id)
                        
                        # Check for new processes
                        if proc_id not in self.known_processes:
                            self._analyze_new_process(proc_info)
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # Update known processes
                terminated_processes = self.known_processes - current_processes
                for proc_id in terminated_processes:
                    self._handle_process_termination(proc_id)
                    
                self.known_processes = current_processes
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Process monitoring error: {e}")
                time.sleep(10)
                
    def _analyze_new_process(self, proc_info: Dict[str, Any]):
        '''Analyze newly created process'''
        try:
            proc_name = proc_info.get('name', '').lower()
            proc_exe = proc_info.get('exe', '')
            proc_cmdline = ' '.join(proc_info.get('cmdline', []))
            
            is_suspicious = False
            reasons = []
            
            # Check for known suspicious processes
            if proc_name in self.suspicious_processes:
                is_suspicious = True
                reasons.append(f"Known suspicious process: {proc_name}")
                
            # Check for suspicious command line patterns
            suspicious_cmdline_patterns = [
                '-enc ', '-encodedcommand', 'invoke-expression', 'downloadstring',
                'bypass', 'hidden', 'windowstyle', 'noprofile', 'noninteractive'
            ]
            
            for pattern in suspicious_cmdline_patterns:
                if pattern.lower() in proc_cmdline.lower():
                    is_suspicious = True
                    reasons.append(f"Suspicious command line pattern: {pattern}")
                    break
                    
            # Check for processes spawned from unusual locations
            if proc_exe and ("\\Temp\\" in proc_exe or "\\AppData\\" in proc_exe):
                is_suspicious = True
                reasons.append("Process spawned from temporary location")
                
            if is_suspicious:
                self._report_process_event(proc_info, reasons, "process_created")
                
        except Exception as e:
            logger.error(f"Error analyzing new process: {e}")
            
    def _handle_process_termination(self, proc_id: tuple):
        '''Handle process termination'''
        pid, name = proc_id
        logger.debug(f"Process terminated: {name} (PID: {pid})")
        
    def _report_process_event(self, proc_info: Dict[str, Any], reasons: List[str], event_type: str):
        '''Report suspicious process event'''
        try:
            event = AgentEvent(
                event_id=f"proc_{int(time.time())}_{proc_info.get('pid', 0)}",
                timestamp=datetime.datetime.now().isoformat(),
                monitoring_type=MonitoringType.PROCESS,
                severity=EventSeverity.HIGH,
                source="ProcessMonitor",
                description=f"Suspicious process {event_type}: {proc_info.get('name', 'unknown')}",
                details={
                    "process_name": proc_info.get('name'),
                    "process_id": proc_info.get('pid'),
                    "executable_path": proc_info.get('exe'),
                    "command_line": ' '.join(proc_info.get('cmdline', [])),
                    "creation_time": proc_info.get('create_time'),
                    "reasons": reasons
                },
                process_info=proc_info
            )
            
            self._send_to_ai_brain(event)
            
        except Exception as e:
            logger.error(f"Error reporting process event: {e}")
            
    def _send_to_ai_brain(self, event: AgentEvent):
        '''Send event to AI Brain for analysis'''
        try:
            event_data = {
                "timestamp": event.timestamp,
                "event_type": f"{event.monitoring_type.value}_{event.severity.value}",
                "source": event.source,
                "details": event.details,
                "threat_level": event.severity.value
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event_data, timeout=5)
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('threat_detected'):
                    logger.warning(f"AI Brain detected threat: {analysis.get('narrative')}")
                    
        except Exception as e:
            logger.error(f"Failed to send event to AI Brain: {e}")

class NetworkMonitor:
    '''Monitor network connections and traffic'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        self.known_connections = set()
        self.suspicious_ports = [4444, 5555, 6666, 8080, 9999, 31337, 1234]
        
    def start_monitoring(self):
        '''Start network monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_network)
        thread.daemon = True
        thread.start()
        logger.info("Network monitoring started")
        
    def _monitor_network(self):
        '''Monitor network connections'''
        while self.running:
            try:
                current_connections = set()
                
                for conn in psutil.net_connections():
                    if conn.status == 'ESTABLISHED':
                        conn_info = (conn.laddr, conn.raddr, conn.pid)
                        current_connections.add(conn_info)
                        
                        # Check for new connections
                        if conn_info not in self.known_connections:
                            self._analyze_new_connection(conn)
                            
                self.known_connections = current_connections
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                time.sleep(30)
                
    def _analyze_new_connection(self, conn):
        '''Analyze new network connection'''
        try:
            is_suspicious = False
            reasons = []
            
            # Check for suspicious ports
            if conn.raddr and conn.raddr.port in self.suspicious_ports:
                is_suspicious = True
                reasons.append(f"Connection to suspicious port: {conn.raddr.port}")
                
            # Check for connections to unusual IP ranges
            if conn.raddr and self._is_suspicious_ip(conn.raddr.ip):
                is_suspicious = True
                reasons.append(f"Connection to suspicious IP: {conn.raddr.ip}")
                
            # Check for process making connection
            if conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    proc_name = proc.name().lower()
                    
                    if proc_name in ['powershell.exe', 'cmd.exe', 'wscript.exe']:
                        is_suspicious = True
                        reasons.append(f"Network connection from scripting process: {proc_name}")
                        
                except psutil.NoSuchProcess:
                    pass
                    
            if is_suspicious:
                self._report_network_event(conn, reasons)
                
        except Exception as e:
            logger.error(f"Error analyzing network connection: {e}")
            
    def _is_suspicious_ip(self, ip: str) -> bool:
        '''Check if IP address is suspicious'''
        try:
            # Check for known suspicious IP patterns
            suspicious_patterns = [
                '10.0.0.',  # Common internal testing
                '192.168.1.1',  # Common router
                '127.0.0.',  # Localhost (unusual for external connections)
            ]
            
            for pattern in suspicious_patterns:
                if ip.startswith(pattern):
                    return True
                    
            return False
            
        except:
            return False
            
    def _report_network_event(self, conn, reasons: List[str]):
        '''Report suspicious network event'''
        try:
            event = AgentEvent(
                event_id=f"net_{int(time.time())}_{hash(str(conn.raddr)) % 10000}",
                timestamp=datetime.datetime.now().isoformat(),
                monitoring_type=MonitoringType.NETWORK,
                severity=EventSeverity.MEDIUM,
                source="NetworkMonitor",
                description=f"Suspicious network connection to {conn.raddr.ip}:{conn.raddr.port}",
                details={
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}",
                    "process_id": conn.pid,
                    "connection_status": conn.status,
                    "reasons": reasons
                },
                network_info={
                    "local_addr": conn.laddr,
                    "remote_addr": conn.raddr,
                    "protocol": "TCP"
                }
            )
            
            self._send_to_ai_brain(event)
            
        except Exception as e:
            logger.error(f"Error reporting network event: {e}")
            
    def _send_to_ai_brain(self, event: AgentEvent):
        '''Send event to AI Brain for analysis'''
        try:
            event_data = {
                "timestamp": event.timestamp,
                "event_type": f"{event.monitoring_type.value}_{event.severity.value}",
                "source": event.source,
                "details": event.details,
                "threat_level": event.severity.value
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event_data, timeout=5)
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('threat_detected'):
                    logger.warning(f"AI Brain detected threat: {analysis.get('narrative')}")
                    
        except Exception as e:
            logger.error(f"Failed to send event to AI Brain: {e}")

class RegistryMonitor:
    '''Monitor Windows Registry changes'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        self.monitored_keys = [
            r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services"
        ]
        
    def start_monitoring(self):
        '''Start registry monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_registry)
        thread.daemon = True
        thread.start()
        logger.info("Registry monitoring started")
        
    def _monitor_registry(self):
        '''Monitor registry changes'''
        while self.running:
            try:
                for key_path in self.monitored_keys:
                    self._check_registry_key(key_path)
                    
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Registry monitoring error: {e}")
                time.sleep(120)
                
    def _check_registry_key(self, key_path: str):
        '''Check specific registry key for changes'''
        try:
            # Parse key path
            hive, subkey = key_path.split('\\', 1)
            
            # Map hive names to constants
            hive_map = {
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT
            }
            
            if hive not in hive_map:
                return
                
            # Open registry key
            with winreg.OpenKey(hive_map[hive], subkey) as key:
                # Enumerate values
                i = 0
                while True:
                    try:
                        name, value, reg_type = winreg.EnumValue(key, i)
                        self._analyze_registry_value(key_path, name, value, reg_type)
                        i += 1
                    except OSError:
                        break  # No more values
                        
        except Exception as e:
            logger.debug(f"Registry key access error for {key_path}: {e}")
            
    def _analyze_registry_value(self, key_path: str, name: str, value: Any, reg_type: int):
        '''Analyze registry value for suspicious content'''
        try:
            is_suspicious = False
            reasons = []
            
            if isinstance(value, str):
                value_str = value.lower()
                
                # Check for suspicious patterns
                suspicious_patterns = [
                    'powershell', 'cmd.exe', 'wscript', 'cscript',
                    'rundll32', 'regsvr32', 'mshta', 'bitsadmin'
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in value_str:
                        is_suspicious = True
                        reasons.append(f"Suspicious executable in registry: {pattern}")
                        break
                        
                # Check for encoded commands
                if '-enc' in value_str or 'base64' in value_str:
                    is_suspicious = True
                    reasons.append("Potentially encoded command in registry")
                    
            if is_suspicious:
                self._report_registry_event(key_path, name, value, reasons)
                
        except Exception as e:
            logger.error(f"Error analyzing registry value: {e}")
            
    def _report_registry_event(self, key_path: str, name: str, value: Any, reasons: List[str]):
        '''Report suspicious registry event'''
        try:
            event = AgentEvent(
                event_id=f"reg_{int(time.time())}_{hash(key_path + name) % 10000}",
                timestamp=datetime.datetime.now().isoformat(),
                monitoring_type=MonitoringType.REGISTRY,
                severity=EventSeverity.HIGH,
                source="RegistryMonitor",
                description=f"Suspicious registry entry: {name}",
                details={
                    "registry_key": key_path,
                    "value_name": name,
                    "value_data": str(value)[:200],  # Truncate long values
                    "reasons": reasons
                }
            )
            
            self._send_to_ai_brain(event)
            
        except Exception as e:
            logger.error(f"Error reporting registry event: {e}")
            
    def _send_to_ai_brain(self, event: AgentEvent):
        '''Send event to AI Brain for analysis'''
        try:
            event_data = {
                "timestamp": event.timestamp,
                "event_type": f"{event.monitoring_type.value}_{event.severity.value}",
                "source": event.source,
                "details": event.details,
                "threat_level": event.severity.value
            }
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event_data, timeout=5)
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('threat_detected'):
                    logger.warning(f"AI Brain detected threat: {analysis.get('narrative')}")
                    
        except Exception as e:
            logger.error(f"Failed to send event to AI Brain: {e}")

class WindowsAgentCore:
    '''Main Windows Agent orchestrating all monitoring components'''
    
    def __init__(self, config_file: str = "agent_config.json"):
        self.config = self._load_config(config_file)
        self.ai_brain_url = self.config.get('ai_brain_url', 'http://localhost:9999')
        
        # Initialize monitors
        self.file_monitor = FileSystemMonitor(self.ai_brain_url)
        self.process_monitor = ProcessMonitor(self.ai_brain_url)
        self.network_monitor = NetworkMonitor(self.ai_brain_url)
        self.registry_monitor = RegistryMonitor(self.ai_brain_url)
        
        # Agent state
        self.running = False
        self.start_time = None
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        '''Load agent configuration'''
        default_config = {
            "ai_brain_url": "http://localhost:9999",
            "monitoring_enabled": {
                "file_system": True,
                "processes": True,
                "network": True,
                "registry": True
            },
            "reporting_interval": 300,  # 5 minutes
            "log_level": "INFO"
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logger.warning(f"Could not load config file {config_file}: {e}")
            
        return default_config
        
    def start_agent(self):
        '''Start the Windows Agent'''
        logger.info("Starting WatchLockAI Windows Agent...")
        
        self.running = True
        self.start_time = datetime.datetime.now()
        
        # Start monitoring components
        if self.config['monitoring_enabled']['file_system']:
            self.file_monitor.start_monitoring()
            
        if self.config['monitoring_enabled']['processes']:
            self.process_monitor.start_monitoring()
            
        if self.config['monitoring_enabled']['network']:
            self.network_monitor.start_monitoring()
            
        if self.config['monitoring_enabled']['registry']:
            self.registry_monitor.start_monitoring()
            
        # Start status reporting
        self._start_status_reporting()
        
        logger.info("[PASS] WatchLockAI Windows Agent started successfully")
        
    def _start_status_reporting(self):
        '''Start periodic status reporting'''
        def report_status():
            while self.running:
                try:
                    self._send_agent_status()
                    time.sleep(self.config['reporting_interval'])
                except Exception as e:
                    logger.error(f"Error in status reporting: {e}")
                    time.sleep(60)
                    
        thread = threading.Thread(target=report_status)
        thread.daemon = True
        thread.start()
        
    def _send_agent_status(self):
        '''Send agent status to AI Brain'''
        try:
            uptime = (datetime.datetime.now() - self.start_time).total_seconds()
            
            status = {
                "agent_id": socket.gethostname(),
                "status": "operational",
                "uptime_seconds": uptime,
                "monitoring_active": {
                    "file_system": self.file_monitor.running,
                    "processes": self.process_monitor.running,
                    "network": self.network_monitor.running,
                    "registry": self.registry_monitor.running
                },
                "system_info": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('C:\\').percent
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Send status to AI Brain (if available)
            response = requests.post(f"{self.ai_brain_url}/status", json=status, timeout=5)
            if response.status_code == 200:
                logger.debug("Agent status reported successfully")
                
        except Exception as e:
            logger.debug(f"Could not report status to AI Brain: {e}")
            
    def stop_agent(self):
        '''Stop the Windows Agent'''
        logger.info("Stopping WatchLockAI Windows Agent...")
        
        self.running = False
        self.file_monitor.running = False
        self.process_monitor.running = False
        self.network_monitor.running = False
        self.registry_monitor.running = False
        
        logger.info("[PASS] WatchLockAI Windows Agent stopped")
        
    def get_agent_status(self) -> Dict[str, Any]:
        '''Get current agent status'''
        if not self.start_time:
            return {"status": "not_started"}
            
        uptime = (datetime.datetime.now() - self.start_time).total_seconds()
        
        return {
            "status": "operational" if self.running else "stopped",
            "uptime_seconds": uptime,
            "monitors": {
                "file_system": self.file_monitor.running,
                "processes": self.process_monitor.running,
                "network": self.network_monitor.running,
                "registry": self.registry_monitor.running
            },
            "config": self.config
        }

def main():
    '''Main entry point for Windows Agent'''
    print("[U+1F5A5] WatchLockAI Windows Agent Core")
    print("Real-time monitoring and protection for Windows systems")
    print()
    
    try:
        # Initialize and start agent
        agent = WindowsAgentCore()
        agent.start_agent()
        
        print("[RELOAD] Monitoring active:")
        print("   * File System - Real-time file monitoring")
        print("   * Processes - Process creation/termination tracking")
        print("   * Network - Connection monitoring and analysis")
        print("   * Registry - Registry change detection")
        print()
        print("[SCOUT] Sending events to AI Brain for analysis...")
        print("Press Ctrl+C to stop the agent")
        
        # Keep agent running
        while agent.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[U+1F6D1] Shutting down Windows Agent...")
        agent.stop_agent()
        
    except Exception as e:
        logger.error(f"Agent error: {e}")

if __name__ == "__main__":
    main()
