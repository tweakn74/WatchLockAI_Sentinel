#!/usr/bin/env python3
'''
WatchLockAI Watchdog Service
Nested watchdog protection with multiple layers
'''

import os
import sys
import time
import json
import threading
import subprocess
import psutil
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WatchLockAI-Watchdog - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watchlockai_watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WatchdogService:
    '''Multi-layered watchdog protection service'''
    
    def __init__(self):
        self.running = False
        self.monitored_services = [
            "WatchLockAI",
            "WatchLockAI-Agent",
            "WatchLockAI-Tamperproof"
        ]
        self.monitored_processes = [
            "windows_agent_core.py",
            "tamperproof_core.py",
            "ai_brain_core.py"
        ]
        self.restart_attempts = {}
        self.max_restart_attempts = 5
        
    def start_watchdog(self):
        '''Start the watchdog service'''
        logger.info("Starting WatchLockAI Watchdog Service...")
        
        self.running = True
        
        # Start monitoring threads
        service_thread = threading.Thread(target=self._monitor_services)
        process_thread = threading.Thread(target=self._monitor_processes)
        health_thread = threading.Thread(target=self._health_monitor)
        
        service_thread.daemon = True
        process_thread.daemon = True
        health_thread.daemon = True
        
        service_thread.start()
        process_thread.start()
        health_thread.start()
        
        logger.info("[PASS] Watchdog Service active - monitoring all components")
        
    def _monitor_services(self):
        '''Monitor Windows services'''
        while self.running:
            try:
                for service_name in self.monitored_services:
                    if not self._is_service_running(service_name):
                        self._restart_service(service_name)
                        
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Service monitoring error: {e}")
                time.sleep(60)
                
    def _monitor_processes(self):
        '''Monitor critical processes'''
        while self.running:
            try:
                for process_name in self.monitored_processes:
                    if not self._is_process_running(process_name):
                        self._restart_process(process_name)
                        
                time.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Process monitoring error: {e}")
                time.sleep(30)
                
    def _health_monitor(self):
        '''Monitor system health and AI Brain connectivity'''
        while self.running:
            try:
                # Check AI Brain health
                import requests
                try:
                    response = requests.get("http://localhost:9999/health", timeout=5)
                    if response.status_code != 200:
                        logger.warning("AI Brain health check failed")
                        self._restart_process("ai_brain_core.py")
                except Exception:
                    logger.warning("AI Brain not responding")
                    self._restart_process("ai_brain_core.py")
                    
                time.sleep(60)  # Health check every minute
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(120)
                
    def _is_service_running(self, service_name: str) -> bool:
        '''Check if Windows service is running'''
        try:
            result = subprocess.run([
                'sc', 'query', service_name
            ], capture_output=True, text=True, timeout=10)
            
            return 'RUNNING' in result.stdout
            
        except Exception:
            return False
            
    def _is_process_running(self, process_name: str) -> bool:
        '''Check if process is running'''
        try:
            for proc in psutil.process_iter(['cmdline']):
                cmdline = ' '.join(proc.info.get('cmdline', []))
                if process_name in cmdline:
                    return True
            return False
        except Exception:
            return False
            
    def _restart_service(self, service_name: str):
        '''Restart a Windows service'''
        try:
            attempts = self.restart_attempts.get(service_name, 0)
            if attempts >= self.max_restart_attempts:
                logger.error(f"Max restart attempts reached for service {service_name}")
                return
                
            logger.warning(f"Restarting service: {service_name}")
            
            # Stop service first
            subprocess.run(['sc', 'stop', service_name], timeout=30)
            time.sleep(5)
            
            # Start service
            result = subprocess.run(['sc', 'start', service_name], timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Successfully restarted service: {service_name}")
                self.restart_attempts[service_name] = 0  # Reset counter
            else:
                self.restart_attempts[service_name] = attempts + 1
                logger.error(f"Failed to restart service: {service_name}")
                
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {e}")
            
    def _restart_process(self, process_name: str):
        '''Restart a process'''
        try:
            attempts = self.restart_attempts.get(process_name, 0)
            if attempts >= self.max_restart_attempts:
                logger.error(f"Max restart attempts reached for process {process_name}")
                return
                
            logger.warning(f"Restarting process: {process_name}")
            
            # Determine the correct restart command
            if "ai_brain_core.py" in process_name:
                cwd = "../AIBrain"
                command = [sys.executable, "ai_brain_core.py"]
            elif "windows_agent_core.py" in process_name:
                cwd = "../WindowsAgent"
                command = [sys.executable, "windows_agent_core.py"]
            elif "tamperproof_core.py" in process_name:
                cwd = "."
                command = [sys.executable, "tamperproof_core.py"]
            else:
                logger.error(f"Unknown process: {process_name}")
                return
                
            # Start the process
            subprocess.Popen(command, cwd=cwd)
            
            self.restart_attempts[process_name] = 0  # Reset counter
            logger.info(f"Successfully restarted process: {process_name}")
            
        except Exception as e:
            attempts = self.restart_attempts.get(process_name, 0)
            self.restart_attempts[process_name] = attempts + 1
            logger.error(f"Error restarting process {process_name}: {e}")
            
    def stop_watchdog(self):
        '''Stop the watchdog service'''
        logger.info("Stopping WatchLockAI Watchdog Service...")
        self.running = False
        logger.info("[PASS] Watchdog Service stopped")
        
    def get_status(self) -> Dict[str, Any]:
        '''Get watchdog status'''
        return {
            "running": self.running,
            "monitored_services": self.monitored_services,
            "monitored_processes": self.monitored_processes,
            "restart_attempts": self.restart_attempts
        }

def main():
    '''Main entry point'''
    print("[U+1F415] WatchLockAI Watchdog Service")
    print("Nested protection against system failures")
    print()
    
    try:
        watchdog = WatchdogService()
        watchdog.start_watchdog()
        
        print("[RELOAD] Monitoring components:")
        print("   * Windows Services - Service status monitoring")
        print("   * Critical Processes - Process availability checking")
        print("   * AI Brain Health - Connectivity and responsiveness")
        print("   * Automatic Restart - Failed component recovery")
        print()
        print("[SHIELD] Watchdog protection active!")
        print("Press Ctrl+C to stop")
        
        while watchdog.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[U+1F6D1] Stopping watchdog...")
        watchdog.stop_watchdog()
        
    except Exception as e:
        logger.error(f"Watchdog error: {e}")

if __name__ == "__main__":
    main()
