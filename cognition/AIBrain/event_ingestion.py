#!/usr/bin/env python3
'''
WatchLockAI - Event Ingestion System
Collects and processes security events from multiple Windows sources
'''

import json
import time
import threading
import subprocess
import re
import win32evtlog
import win32evtlogutil
import win32con
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WindowsEventCollector:
    '''Collects events from Windows Event Log'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.event_sources = [
            'Security',
            'System', 
            'Application',
            'Microsoft-Windows-PowerShell/Operational',
            'Microsoft-Windows-WMI-Activity/Operational'
        ]
        self.running = False
        
    def start_collection(self):
        '''Start event collection from Windows Event Log'''
        self.running = True
        
        for source in self.event_sources:
            thread = threading.Thread(target=self._collect_from_source, args=(source,))
            thread.daemon = True
            thread.start()
            
        logger.info("Windows Event Collection started")
        
    def _collect_from_source(self, source: str):
        '''Collect events from specific event log source'''
        try:
            hand = win32evtlog.OpenEventLog(None, source)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            while self.running:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                
                if events:
                    for event in events:
                        self._process_event(source, event)
                        
                time.sleep(1)  # Poll every second
                
        except Exception as e:
            logger.error(f"Error collecting from {source}: {e}")
            
    def _process_event(self, source: str, event):
        '''Process individual event'''
        try:
            # Extract event data
            event_id = event.EventID
            event_type = event.EventType
            time_generated = event.TimeGenerated
            
            # Convert to security event format
            security_event = {
                "timestamp": time_generated.isoformat(),
                "event_type": f"windows_event_{event_id}",
                "source": source,
                "details": {
                    "event_id": event_id,
                    "event_type": event_type,
                    "computer": event.ComputerName,
                    "source_name": event.SourceName,
                    "strings": event.StringInserts if event.StringInserts else [],
                    "data": event.Data.hex() if event.Data else None
                },
                "threat_level": "low"  # Default, AI will reassess
            }
            
            # Send to AI Brain for analysis
            self._send_to_ai_brain(security_event)
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            
    def _send_to_ai_brain(self, event: Dict[str, Any]):
        '''Send event to AI Brain for analysis'''
        try:
            import requests
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event, timeout=5)
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('threat_detected'):
                    logger.warning(f"Threat detected: {analysis.get('narrative')}")
                    
        except Exception as e:
            logger.error(f"Failed to send event to AI Brain: {e}")

class PowerShellMonitor:
    '''Monitors PowerShell execution for suspicious activity'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        
    def start_monitoring(self):
        '''Start PowerShell monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_powershell)
        thread.daemon = True
        thread.start()
        logger.info("PowerShell monitoring started")
        
    def _monitor_powershell(self):
        '''Monitor PowerShell execution'''
        while self.running:
            try:
                # Get PowerShell processes
                result = subprocess.run([
                    'wmic', 'process', 'where', 'name="powershell.exe"',
                    'get', 'ProcessId,CommandLine,ParentProcessId', '/format:csv'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('
')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            self._analyze_powershell_process(line)
                            
            except Exception as e:
                logger.error(f"PowerShell monitoring error: {e}")
                
            time.sleep(5)  # Check every 5 seconds
            
    def _analyze_powershell_process(self, process_line: str):
        '''Analyze PowerShell process for suspicious patterns'''
        parts = process_line.split(',')
        if len(parts) >= 3:
            command_line = parts[1] if len(parts) > 1 else ""
            process_id = parts[2] if len(parts) > 2 else ""
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'-enc.*command',  # Encoded commands
                r'-nop.*-w.*hidden',  # Hidden execution
                r'IEX.*downloadstring',  # Download and execute
                r'invoke-.*expression',  # Invoke expressions
                r'bypass.*executionpolicy',  # Bypass execution policy
                r'frombase64string',  # Base64 decoding
                r'system\.net\.webclient',  # Web client usage
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, command_line, re.IGNORECASE):
                    self._report_suspicious_powershell(command_line, process_id, pattern)
                    break
                    
    def _report_suspicious_powershell(self, command_line: str, process_id: str, pattern: str):
        '''Report suspicious PowerShell activity'''
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "suspicious_powershell",
            "source": "PowerShellMonitor",
            "details": {
                "command_line": command_line,
                "process_id": process_id,
                "suspicious_pattern": pattern,
                "risk_level": "high"
            },
            "threat_level": "high"
        }
        
        try:
            import requests
            requests.post(f"{self.ai_brain_url}/analyze", json=event, timeout=5)
            logger.warning(f"Suspicious PowerShell detected: {pattern}")
        except Exception as e:
            logger.error(f"Failed to report PowerShell event: {e}")

class NetworkMonitor:
    '''Monitors network connections for suspicious activity'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        
    def start_monitoring(self):
        '''Start network monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_connections)
        thread.daemon = True
        thread.start()
        logger.info("Network monitoring started")
        
    def _monitor_connections(self):
        '''Monitor network connections'''
        while self.running:
            try:
                # Get network connections
                result = subprocess.run([
                    'netstat', '-ano'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self._analyze_connections(result.stdout)
                    
            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                
            time.sleep(10)  # Check every 10 seconds
            
    def _analyze_connections(self, netstat_output: str):
        '''Analyze network connections for suspicious patterns'''
        lines = netstat_output.strip().split('
')
        
        for line in lines:
            if 'ESTABLISHED' in line:
                parts = line.split()
                if len(parts) >= 5:
                    local_addr = parts[1]
                    remote_addr = parts[2]
                    pid = parts[4]
                    
                    # Check for suspicious destinations
                    if self._is_suspicious_connection(remote_addr):
                        self._report_suspicious_connection(local_addr, remote_addr, pid)
                        
    def _is_suspicious_connection(self, remote_addr: str) -> bool:
        '''Check if connection is suspicious'''
        # Extract IP from address
        ip = remote_addr.split(':')[0]
        
        # Check for suspicious IP patterns
        suspicious_patterns = [
            r'^10\.0\.0\.1$',  # Localhost variations
            r'^192\.168\.1\.1$',  # Common router IPs
            # Add more suspicious IP patterns
        ]
        
        # Check for non-standard ports
        if ':' in remote_addr:
            port = remote_addr.split(':')[1]
            suspicious_ports = ['4444', '8080', '9999', '1337', '31337']
            if port in suspicious_ports:
                return True
                
        return False
        
    def _report_suspicious_connection(self, local_addr: str, remote_addr: str, pid: str):
        '''Report suspicious network connection'''
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "suspicious_network_connection",
            "source": "NetworkMonitor",
            "details": {
                "local_address": local_addr,
                "remote_address": remote_addr,
                "process_id": pid,
                "connection_type": "outbound_suspicious"
            },
            "threat_level": "medium"
        }
        
        try:
            import requests
            requests.post(f"{self.ai_brain_url}/analyze", json=event, timeout=5)
            logger.warning(f"Suspicious connection: {local_addr} -> {remote_addr}")
        except Exception as e:
            logger.error(f"Failed to report network event: {e}")

def main():
    '''Main event collection service'''
    print("[SEARCH] Starting WatchLockAI Event Ingestion System...")
    
    # Initialize collectors
    windows_collector = WindowsEventCollector()
    powershell_monitor = PowerShellMonitor()
    network_monitor = NetworkMonitor()
    
    # Start collection
    windows_collector.start_collection()
    powershell_monitor.start_monitoring()
    network_monitor.start_monitoring()
    
    print("[PASS] Event collection started")
    print("[SCOUT] Monitoring:")
    print("   - Windows Event Logs")
    print("   - PowerShell Execution") 
    print("   - Network Connections")
    print()
    print("[RELOAD] Events will be sent to AI Brain for analysis...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[U+1F6D1] Stopping event collection...")
        windows_collector.running = False
        powershell_monitor.running = False
        network_monitor.running = False

if __name__ == "__main__":
    main()
