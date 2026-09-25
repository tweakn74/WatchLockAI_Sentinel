#!/usr/bin/env python3
'''
WatchLockAI Security Integration Testing Suite
Tests integration with Windows security APIs and third-party tools
'''

import asyncio
import subprocess
import winreg
import ctypes
import psutil
import wmi
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityIntegrationTester:
    def __init__(self):
        self.test_results = []
        self.wmi_connection = None
    
    def __enter__(self):
        try:
            self.wmi_connection = wmi.WMI()
        except Exception as e:
            logger.warning(f"Failed to initialize WMI connection: {e}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def test_windows_defender_integration(self) -> Dict[str, Any]:
        '''Test Windows Defender API integration'''
        logger.info("Testing Windows Defender integration...")
        
        try:
            # Test Defender status query
            if self.wmi_connection:
                defender_status = list(self.wmi_connection.query(
                    "SELECT * FROM MSFT_MpComputerStatus", 
                    namespace="root/Microsoft/Windows/Defender"
                ))
                
                if defender_status:
                    status = defender_status[0]
                    result = {
                        "test": "Windows Defender Integration",
                        "success": True,
                        "message": "Successfully queried Defender status",
                        "details": {
                            "antivirus_enabled": getattr(status, 'AntivirusEnabled', None),
                            "real_time_protection": getattr(status, 'RealTimeProtectionEnabled', None),
                            "signature_version": getattr(status, 'AntivirusSignatureVersion', None)
                        }
                    }
                else:
                    result = {
                        "test": "Windows Defender Integration",
                        "success": False,
                        "message": "No Defender status information available"
                    }
            else:
                result = {
                    "test": "Windows Defender Integration",
                    "success": False,
                    "message": "WMI connection not available"
                }
        
        except Exception as e:
            result = {
                "test": "Windows Defender Integration",
                "success": False,
                "message": f"Defender integration test failed: {str(e)}"
            }
        
        self.test_results.append(result)
        return result
    
    def test_windows_firewall_integration(self) -> Dict[str, Any]:
        '''Test Windows Firewall API integration'''
        logger.info("Testing Windows Firewall integration...")
        
        try:
            # Test firewall rule creation (simulation)
            test_rule_name = "WatchLockAI-Test-Rule"
            
            # Create test firewall rule
            create_cmd = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={test_rule_name}",
                "dir=out",
                "action=allow",
                "protocol=TCP",
                "remoteport=443"
            ]
            
            create_result = subprocess.run(
                create_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if create_result.returncode == 0:
                # Test rule listing
                list_cmd = [
                    "netsh", "advfirewall", "firewall", "show", "rule",
                    f"name={test_rule_name}"
                ]
                
                list_result = subprocess.run(
                    list_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Clean up test rule
                delete_cmd = [
                    "netsh", "advfirewall", "firewall", "delete", "rule",
                    f"name={test_rule_name}"
                ]
                
                subprocess.run(delete_cmd, capture_output=True, timeout=30)
                
                result = {
                    "test": "Windows Firewall Integration",
                    "success": True,
                    "message": "Successfully created, listed, and deleted firewall rule",
                    "details": {
                        "create_success": create_result.returncode == 0,
                        "list_success": list_result.returncode == 0,
                        "rule_found": test_rule_name in list_result.stdout
                    }
                }
            else:
                result = {
                    "test": "Windows Firewall Integration",
                    "success": False,
                    "message": f"Failed to create test firewall rule: {create_result.stderr}"
                }
        
        except Exception as e:
            result = {
                "test": "Windows Firewall Integration",
                "success": False,
                "message": f"Firewall integration test failed: {str(e)}"
            }
        
        self.test_results.append(result)
        return result
    
    def test_event_log_integration(self) -> Dict[str, Any]:
        '''Test Windows Event Log integration'''
        logger.info("Testing Windows Event Log integration...")
        
        try:
            # Test event log source creation and writing
            import win32evtlogutil
            import win32evtlog
            
            # Create test event log entry
            test_message = f"WatchLockAI test event - {time.time()}"
            
            try:
                win32evtlogutil.ReportEvent(
                    "WatchLockAI",
                    1001,
                    eventCategory=0,
                    eventType=win32evtlog.EVENTLOG_INFORMATION_TYPE,
                    strings=[test_message],
                    data="Test data".encode()
                )
                
                result = {
                    "test": "Windows Event Log Integration",
                    "success": True,
                    "message": "Successfully wrote test event to Event Log",
                    "details": {
                        "event_source": "WatchLockAI",
                        "event_id": 1001,
                        "message": test_message
                    }
                }
            
            except Exception as e:
                result = {
                    "test": "Windows Event Log Integration", 
                    "success": False,
                    "message": f"Failed to write test event: {str(e)}"
                }
        
        except ImportError:
            result = {
                "test": "Windows Event Log Integration",
                "success": False,
                "message": "pywin32 not available - Event Log testing skipped"
            }
        
        except Exception as e:
            result = {
                "test": "Windows Event Log Integration",
                "success": False,
                "message": f"Event Log integration test failed: {str(e)}"
            }
        
        self.test_results.append(result)
        return result
    
    def test_registry_monitoring(self) -> Dict[str, Any]:
        '''Test Windows Registry monitoring capabilities'''
        logger.info("Testing Registry monitoring...")
        
        try:
            # Test registry key creation and monitoring
            test_key_path = r"SOFTWARE\WatchLockAI\Test"
            test_value_name = "TestValue"
            test_value_data = f"test_data_{int(time.time())}"
            
            # Create test registry key
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, test_key_path) as key:
                    winreg.SetValueEx(key, test_value_name, 0, winreg.REG_SZ, test_value_data)
                
                # Read back the value
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, test_key_path) as key:
                    value, value_type = winreg.QueryValueEx(key, test_value_name)
                
                # Clean up
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, test_key_path)
                
                result = {
                    "test": "Registry Monitoring",
                    "success": True,
                    "message": "Successfully created, read, and deleted registry key",
                    "details": {
                        "key_path": test_key_path,
                        "value_name": test_value_name,
                        "value_data": value,
                        "value_type": value_type
                    }
                }
            
            except Exception as e:
                result = {
                    "test": "Registry Monitoring",
                    "success": False,
                    "message": f"Registry operations failed: {str(e)}"
                }
        
        except Exception as e:
            result = {
                "test": "Registry Monitoring",
                "success": False,
                "message": f"Registry monitoring test failed: {str(e)}"
            }
        
        self.test_results.append(result)
        return result
    
    def test_process_monitoring(self) -> Dict[str, Any]:
        '''Test process monitoring capabilities'''
        logger.info("Testing Process monitoring...")
        
        try:
            # Test process enumeration and information gathering
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'create_time']):
                try:
                    proc_info = proc.info
                    if proc_info['name']:  # Skip system processes without names
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'exe': proc_info['exe'],
                            'cmdline': proc_info['cmdline'],
                            'create_time': proc_info['create_time']
                        })
                        
                        # Only collect first 10 for testing
                        if len(processes) >= 10:
                            break
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            result = {
                "test": "Process Monitoring",
                "success": True,
                "message": f"Successfully enumerated {len(processes)} processes",
                "details": {
                    "process_count": len(processes),
                    "sample_processes": processes[:3]  # First 3 processes
                }
            }
        
        except Exception as e:
            result = {
                "test": "Process Monitoring",
                "success": False,
                "message": f"Process monitoring test failed: {str(e)}"
            }
        
        self.test_results.append(result)
        return result
    
    def test_network_monitoring(self) -> Dict[str, Any]:
        '''Test network monitoring capabilities'''
        logger.info("Testing Network monitoring...")
        
        try:
            # Test network connection enumeration
            connections = []
            
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_ESTABLISHED:  # Only established connections
                    connections.append({
                        'family': conn.family.name,
                        'type': conn.type.name,
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status,
                        'pid': conn.pid
                    })
                    
                    # Limit for testing
                    if len(connections) >= 10:
                        break
            
            # Test network interface information
            interfaces = {}
            for iface, addrs in psutil.net_if_addrs().items():
                interfaces[iface] = [
                    {
                        'family': addr.family.name,
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    for addr in addrs
                ]
            
            result = {
                "test": "Network Monitoring",
                "success": True,
                "message": f"Successfully monitored {len(connections)} connections and {len(interfaces)} interfaces",
                "details": {
                    "connection_count": len(connections),
                    "interface_count": len(interfaces),
                    "sample_connections": connections[:3],
                    "interfaces": list(interfaces.keys())
                }
            }
        
        except Exception as e:
            result = {
                "test": "Network Monitoring",
                "success": False,
                "message": f"Network monitoring test failed: {str(e)}"
            }
        
        self.test_results.append(result)
        return result
    
    def test_performance_monitoring(self) -> Dict[str, Any]:
        '''Test system performance monitoring'''
        logger.info("Testing Performance monitoring...")
        
        try:
            # Test system resource monitoring
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')
            
            performance_data = {
                "cpu_usage_percent": cpu_percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2)
            }
            
            result = {
                "test": "Performance Monitoring",
                "success": True,
                "message": "Successfully collected system performance metrics",
                "details": performance_data
            }
        
        except Exception as e:
            result = {
                "test": "Performance Monitoring",
                "success": False,
                "message": f"Performance monitoring test failed: {str(e)}"
            }
        
        self.test_results.append(result)
        return result
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        '''Run all security integration tests'''
        logger.info("Starting WatchLockAI Security Integration Tests...")
        
        tests = [
            self.test_windows_defender_integration,
            self.test_windows_firewall_integration,
            self.test_event_log_integration,
            self.test_registry_monitoring,
            self.test_process_monitoring,
            self.test_network_monitoring,
            self.test_performance_monitoring
        ]
        
        for test in tests:
            try:
                result = test()
                status = "[PASS] PASS" if result["success"] else "[FAIL] FAIL"
                logger.info(f"{status} {result['test']}: {result['message']}")
                
                if not result["success"]:
                    logger.error(f"Failure details: {result.get('details', 'No additional details')}")
            
            except Exception as e:
                logger.error(f"[FAIL] FAIL {test.__name__}: Test execution failed: {str(e)}")
                self.test_results.append({
                    "test": test.__name__,
                    "success": False,
                    "message": f"Test execution failed: {str(e)}"
                })
        
        return self.test_results
    
    def print_summary(self):
        '''Print test results summary'''
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print("\n" + "="*60)
        print("WatchLockAI Security Integration Test Summary")
        print("="*60)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n[U+1F389] All security integration tests passed!")
            print("   WatchLockAI agent is ready for Windows security API integration.")
        else:
            print("\n[WARN]  Some tests failed. Security integrations may need attention.")
            
            failed_tests = [r for r in self.test_results if not r["success"]]
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        print("="*60)

def main():
    '''Main test execution'''
    import argparse
    
    parser = argparse.ArgumentParser(description='WatchLockAI Security Integration Tester')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--output', '-o', help='Output results to JSON file')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    with SecurityIntegrationTester() as tester:
        results = tester.run_all_tests()
        tester.print_summary()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results saved to {args.output}")
        
        # Return exit code based on results
        failed_count = sum(1 for r in results if not r["success"])
        return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
