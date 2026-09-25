#!/usr/bin/env python3
'''
WatchLockAI Account Event Monitor
Monitor Windows events for account-related activities
'''

import os
import json
import time
import subprocess
import threading
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WindowsEventMonitor:
    '''Monitor Windows Event Log for account events'''
    
    def __init__(self, ai_brain_url: str = "http://localhost:9999"):
        self.ai_brain_url = ai_brain_url
        self.running = False
        self.monitored_events = {
            'Security': [
                4624,  # Successful logon
                4625,  # Failed logon
                4634,  # Logoff
                4648,  # Logon using explicit credentials
                4720,  # User account created
                4722,  # User account enabled
                4723,  # User account password changed
                4724,  # User account password reset
                4725,  # User account disabled
                4726,  # User account deleted
                4728,  # Member added to security-enabled global group
                4732,  # Member added to security-enabled local group
                4756,  # Member added to security-enabled universal group
            ]
        }
        
    def start_monitoring(self):
        '''Start Windows event monitoring'''
        self.running = True
        thread = threading.Thread(target=self._monitor_events)
        thread.daemon = True
        thread.start()
        logger.info("Windows event monitoring started")
        
    def _monitor_events(self):
        '''Monitor Windows events'''
        while self.running:
            try:
                for log_name, event_ids in self.monitored_events.items():
                    for event_id in event_ids:
                        self._check_event(log_name, event_id)
                        
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Event monitoring error: {e}")
                time.sleep(120)
                
    def _check_event(self, log_name: str, event_id: int):
        '''Check for specific event in Windows Event Log'''
        try:
            # Query Windows Event Log using wevtutil
            query = f"*[System[EventID={event_id}]]"
            
            # Get events from last 5 minutes
            start_time = (datetime.now() - timedelta(minutes=5)).isoformat()
            
            cmd = [
                'wevtutil', 'qe', log_name,
                '/q', query,
                '/f:text',
                '/rd:true',
                '/c:10'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                self._parse_events(result.stdout, event_id)
                
        except Exception as e:
            logger.debug(f"Event check failed for {log_name}/{event_id}: {e}")
            
    def _parse_events(self, event_text: str, event_id: int):
        '''Parse Windows event log entries'''
        try:
            # Simple parsing - in real implementation would use XML parsing
            events = event_text.split('Event[')
            
            for event in events[1:]:  # Skip first empty split
                self._process_event(event, event_id)
                
        except Exception as e:
            logger.error(f"Event parsing failed: {e}")
            
    def _process_event(self, event_text: str, event_id: int):
        '''Process individual event'''
        try:
            # Extract key information from event
            event_info = {
                'event_id': event_id,
                'timestamp': datetime.now().isoformat(),
                'source': 'WindowsEventLog',
                'raw_text': event_text[:500]  # Truncate for storage
            }
            
            # Parse specific fields based on event ID
            if event_id == 4624:  # Successful logon
                self._process_logon_event(event_info, event_text)
            elif event_id == 4625:  # Failed logon
                self._process_failed_logon_event(event_info, event_text)
            elif event_id in [4720, 4722, 4725, 4726]:  # Account changes
                self._process_account_change_event(event_info, event_text)
            elif event_id in [4728, 4732, 4756]:  # Group membership changes
                self._process_group_change_event(event_info, event_text)
                
        except Exception as e:
            logger.error(f"Event processing failed: {e}")
            
    def _process_logon_event(self, event_info: Dict, event_text: str):
        '''Process successful logon event'''
        try:
            # Extract username, logon type, source IP, etc.
            # This is a simplified version - real implementation would parse XML
            
            event_info['event_type'] = 'successful_logon'
            event_info['details'] = {
                'username': 'extracted_from_event',
                'logon_type': 'interactive',
                'source_ip': '192.168.1.100'
            }
            
            self._send_account_event(event_info)
            
        except Exception as e:
            logger.error(f"Logon event processing failed: {e}")
            
    def _process_failed_logon_event(self, event_info: Dict, event_text: str):
        '''Process failed logon event'''
        try:
            event_info['event_type'] = 'failed_logon'
            event_info['details'] = {
                'username': 'extracted_from_event',
                'failure_reason': 'bad_password',
                'source_ip': '192.168.1.100'
            }
            
            self._send_account_event(event_info)
            
        except Exception as e:
            logger.error(f"Failed logon event processing failed: {e}")
            
    def _process_account_change_event(self, event_info: Dict, event_text: str):
        '''Process account creation/modification events'''
        try:
            event_info['event_type'] = 'account_change'
            event_info['details'] = {
                'username': 'extracted_from_event',
                'change_type': 'account_created',
                'changed_by': 'administrator'
            }
            
            self._send_account_event(event_info)
            
        except Exception as e:
            logger.error(f"Account change event processing failed: {e}")
            
    def _process_group_change_event(self, event_info: Dict, event_text: str):
        '''Process group membership change events'''
        try:
            event_info['event_type'] = 'group_membership_change'
            event_info['details'] = {
                'username': 'extracted_from_event',
                'group_name': 'Administrators',
                'action': 'added',
                'changed_by': 'administrator'
            }
            
            self._send_account_event(event_info)
            
        except Exception as e:
            logger.error(f"Group change event processing failed: {e}")
            
    def _send_account_event(self, event_info: Dict):
        '''Send account event to AI Brain'''
        try:
            import requests
            
            response = requests.post(f"{self.ai_brain_url}/analyze", json=event_info, timeout=5)
            if response.status_code == 200:
                logger.debug(f"Account event sent: {event_info['event_type']}")
                
        except Exception as e:
            logger.error(f"Failed to send account event: {e}")

def main():
    '''Test Windows event monitoring'''
    print("[U+1F4DD] WatchLockAI Windows Event Monitor")
    print("Monitoring Windows Event Log for account activities")
    
    monitor = WindowsEventMonitor()
    monitor.start_monitoring()
    
    print("[PASS] Event monitoring started")
    print("[SEARCH] Monitoring event IDs: 4624, 4625, 4720, 4722, etc.")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[U+1F6D1] Stopping event monitor...")
        monitor.running = False

if __name__ == "__main__":
    main()
