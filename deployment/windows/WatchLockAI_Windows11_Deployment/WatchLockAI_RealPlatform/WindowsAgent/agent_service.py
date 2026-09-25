#!/usr/bin/env python3
'''
WatchLockAI Windows Agent Service Wrapper
Runs the agent as a Windows service
'''

import sys
import time
import json
import logging
import threading
from pathlib import Path

# Windows service imports (requires pywin32)
try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    WINDOWS_SERVICE_AVAILABLE = False
    
from windows_agent_core import WindowsAgentCore

class WatchLockAIService:
    '''Windows service wrapper for WatchLockAI Agent'''
    
    _svc_name_ = "WatchLockAI"
    _svc_display_name_ = "WatchLockAI Security Agent"
    _svc_description_ = "WatchLockAI real-time security monitoring and protection agent"
    
    def __init__(self):
        self.agent = None
        self.running = False
        
    def start_service(self):
        '''Start the agent service'''
        try:
            # Configure logging for service
            logging.basicConfig(
                filename='watchlockai_service.log',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            
            # Initialize and start agent
            self.agent = WindowsAgentCore()
            self.agent.start_agent()
            self.running = True
            
            logging.info("WatchLockAI Service started successfully")
            
            # Keep service running
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            logging.error(f"Service error: {e}")
            
    def stop_service(self):
        '''Stop the agent service'''
        try:
            self.running = False
            if self.agent:
                self.agent.stop_agent()
            logging.info("WatchLockAI Service stopped")
        except Exception as e:
            logging.error(f"Error stopping service: {e}")

# Windows Service Implementation
if WINDOWS_SERVICE_AVAILABLE:
    class WatchLockAIWindowsService(win32serviceutil.ServiceFramework):
        _svc_name_ = "WatchLockAI"
        _svc_display_name_ = "WatchLockAI Security Agent"
        _svc_description_ = "WatchLockAI real-time security monitoring and protection agent"
        
        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.service = WatchLockAIService()
            
        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.service.stop_service()
            win32event.SetEvent(self.hWaitStop)
            
        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            # Start service in separate thread
            service_thread = threading.Thread(target=self.service.start_service)
            service_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

def install_service():
    '''Install WatchLockAI as Windows service'''
    if not WINDOWS_SERVICE_AVAILABLE:
        print("[FAIL] Windows service functionality requires pywin32")
        print("   Install with: pip install pywin32")
        return False
        
    try:
        win32serviceutil.InstallService(
            WatchLockAIWindowsService,
            WatchLockAIWindowsService._svc_name_,
            WatchLockAIWindowsService._svc_display_name_,
            description=WatchLockAIWindowsService._svc_description_
        )
        print("[PASS] WatchLockAI service installed successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Service installation failed: {e}")
        return False

def uninstall_service():
    '''Uninstall WatchLockAI Windows service'''
    if not WINDOWS_SERVICE_AVAILABLE:
        print("[FAIL] Windows service functionality requires pywin32")
        return False
        
    try:
        win32serviceutil.RemoveService(WatchLockAIWindowsService._svc_name_)
        print("[PASS] WatchLockAI service uninstalled successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Service uninstallation failed: {e}")
        return False

def start_service():
    '''Start WatchLockAI service'''
    if not WINDOWS_SERVICE_AVAILABLE:
        print("[FAIL] Windows service functionality requires pywin32")
        return False
        
    try:
        win32serviceutil.StartService(WatchLockAIWindowsService._svc_name_)
        print("[PASS] WatchLockAI service started")
        return True
    except Exception as e:
        print(f"[FAIL] Service start failed: {e}")
        return False

def stop_service():
    '''Stop WatchLockAI service'''
    if not WINDOWS_SERVICE_AVAILABLE:
        print("[FAIL] Windows service functionality requires pywin32")
        return False
        
    try:
        win32serviceutil.StopService(WatchLockAIWindowsService._svc_name_)
        print("[PASS] WatchLockAI service stopped")
        return True
    except Exception as e:
        print(f"[FAIL] Service stop failed: {e}")
        return False

def main():
    '''Main service management interface'''
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'install':
            install_service()
        elif command == 'uninstall':
            uninstall_service()
        elif command == 'start':
            start_service()
        elif command == 'stop':
            stop_service()
        elif command == 'console':
            # Run as console application
            print("[U+1F5A5] Running WatchLockAI Agent in console mode...")
            service = WatchLockAIService()
            try:
                service.start_service()
            except KeyboardInterrupt:
                print("\n[U+1F6D1] Stopping agent...")
                service.stop_service()
        else:
            print("Usage: agent_service.py [install|uninstall|start|stop|console]")
    else:
        # Default Windows service behavior
        if WINDOWS_SERVICE_AVAILABLE:
            win32serviceutil.HandleCommandLine(WatchLockAIWindowsService)
        else:
            print("[FAIL] Windows service functionality requires pywin32")
            print("   Install with: pip install pywin32")
            print("   Or run with: python agent_service.py console")

if __name__ == "__main__":
    main()
