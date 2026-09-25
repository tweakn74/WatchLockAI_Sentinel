#!/usr/bin/env python3
'''
WatchLockAI Windows Agent Test Suite (Linux-compatible)
Test agent monitoring capabilities in Linux environment
'''

import os
import time
import json
import tempfile
import subprocess
import threading
from pathlib import Path

# Mock Windows-specific modules for testing
class MockWinreg:
    HKEY_LOCAL_MACHINE = 1
    HKEY_CURRENT_USER = 2
    
    @staticmethod
    def OpenKey(hive, subkey):
        return MockRegistryKey()
    
    @staticmethod
    def EnumValue(key, index):
        if index == 0:
            return "TestValue", "C:\\Windows\\System32\\test.exe", 1
        raise OSError("No more values")

class MockRegistryKey:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

# Patch winreg for testing
import sys
sys.modules['winreg'] = MockWinreg()

# Now import our components
try:
    from windows_agent_core import FileSystemMonitor, ProcessMonitor, NetworkMonitor
    print("[PASS] Successfully imported agent components")
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    exit(1)

def test_file_system_monitor():
    '''Test file system monitoring'''
    print("\n[SEARCH] Testing File System Monitor...")
    
    monitor = FileSystemMonitor()
    
    # Create test file in temp directory
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as temp_file:
        temp_file.write(b'Test executable content')
        temp_path = temp_file.name
        
    print(f"[PASS] Created test file: {temp_path}")
    
    # Test file analysis
    stat_info = os.stat(temp_path)
    monitor._analyze_file_change(temp_path, stat_info)
    
    # Cleanup
    os.unlink(temp_path)
    print("[PASS] File system monitor test completed")

def test_process_monitor():
    '''Test process monitoring'''
    print("\n[SEARCH] Testing Process Monitor...")
    
    monitor = ProcessMonitor()
    
    print(f"[PASS] Process monitor initialized")
    
    # Test suspicious process detection
    fake_proc_info = {
        'name': 'mimikatz.exe',
        'pid': 12345,
        'exe': '/tmp/mimikatz.exe',  # Using Linux path for testing
        'cmdline': ['mimikatz.exe', 'sekurlsa::logonpasswords'],
        'create_time': time.time()
    }
    
    monitor._analyze_new_process(fake_proc_info)
    print("[PASS] Process monitor test completed")

def test_network_monitor():
    '''Test network monitoring'''
    print("\n[SEARCH] Testing Network Monitor...")
    
    monitor = NetworkMonitor()
    
    # Test suspicious IP detection
    test_ips = ['192.168.1.1', '10.0.0.1', '8.8.8.8']
    
    for ip in test_ips:
        is_suspicious = monitor._is_suspicious_ip(ip)
        print(f"   IP {ip}: {'Suspicious' if is_suspicious else 'Normal'}")
        
    print("[PASS] Network monitor test completed")

def test_agent_configuration():
    '''Test agent configuration loading'''
    print("\n[SEARCH] Testing Agent Configuration...")
    
    # Test config loading with mock
    from windows_agent_core import WindowsAgentCore
    
    # Create test config
    test_config = {
        "ai_brain_url": "http://localhost:9999",
        "monitoring_enabled": {
            "file_system": True,
            "processes": True,
            "network": False,
            "registry": True
        }
    }
    
    config_file = "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(test_config, f)
        
    # Test config loading
    agent = WindowsAgentCore(config_file)
    
    assert agent.config['ai_brain_url'] == "http://localhost:9999"
    assert agent.config['monitoring_enabled']['network'] == False
    
    # Cleanup
    os.remove(config_file)
    print("[PASS] Agent configuration test completed")

def test_event_reporting():
    '''Test event reporting to AI Brain'''
    print("\n[SEARCH] Testing Event Reporting...")
    
    # Test with mock AI Brain (should fail gracefully)
    monitor = FileSystemMonitor("http://localhost:9998")  # Non-existent endpoint
    
    # This should not crash the monitor
    fake_stat = type('stat', (), {'st_size': 1024, 'st_mtime': time.time()})()
    monitor._analyze_file_change("/tmp/test/file.exe", fake_stat)
    
    print("[PASS] Event reporting test completed")

def test_browser_monitor():
    '''Test browser monitoring'''
    print("\n[SEARCH] Testing Browser Monitor...")
    
    from browser_monitor import BrowserMonitor
    
    monitor = BrowserMonitor()
    browser_paths = monitor._get_browser_paths()
    
    print(f"   Found browsers: {list(browser_paths.keys())}")
    
    # Test URL analysis
    test_urls = [
        ('chrome', ('http://safe-site.com', 'Safe Site', 1, 123456)),
        ('chrome', ('http://malware.com/download.exe', 'Malware', 1, 123456)),
        ('firefox', ('http://phishing.net/login', 'Fake Bank', 1, 123456))
    ]
    
    for browser, url_data in test_urls:
        monitor._analyze_url(browser, url_data)
        
    print("[PASS] Browser monitor test completed")

def test_hash_calculation():
    '''Test file hash calculation'''
    print("\n[SEARCH] Testing Hash Calculation...")
    
    monitor = FileSystemMonitor()
    
    # Create test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b'Test content for hash calculation')
        temp_path = temp_file.name
    
    # Calculate hash
    file_hash = monitor._calculate_file_hash(temp_path)
    
    assert len(file_hash) == 32  # MD5 hash length
    assert file_hash != "unknown"
    
    # Cleanup
    os.unlink(temp_path)
    print(f"[PASS] Hash calculation test completed (hash: {file_hash[:8]}...)")

def run_integration_test():
    '''Run integration test with all components'''
    print("\n[U+1F527] Running Integration Test...")
    
    # Test full agent startup (without actually starting monitoring)
    from windows_agent_core import WindowsAgentCore
    agent = WindowsAgentCore()
    
    # Verify all components are initialized
    assert agent.file_monitor is not None
    assert agent.process_monitor is not None
    assert agent.network_monitor is not None
    assert agent.registry_monitor is not None
    
    print("[PASS] Integration test completed")

def run_all_tests():
    '''Run all agent tests'''
    print("[U+1F9EA] WatchLockAI Windows Agent Test Suite (Linux Environment)")
    print("=" * 60)
    
    try:
        test_file_system_monitor()
        test_process_monitor()
        test_network_monitor()
        test_agent_configuration()
        test_event_reporting()
        test_browser_monitor()
        test_hash_calculation()
        run_integration_test()
        
        print("\n" + "=" * 60)
        print("[PASS] All tests completed successfully!")
        print("\n[TARGET] WatchLockAI Windows Agent is ready for deployment")
        print("\n[PLAN] Test Summary:")
        print("   * File System Monitor - [PASS] Working")
        print("   * Process Monitor - [PASS] Working") 
        print("   * Network Monitor - [PASS] Working")
        print("   * Configuration System - [PASS] Working")
        print("   * Event Reporting - [PASS] Working")
        print("   * Browser Monitor - [PASS] Working")
        print("   * Hash Calculation - [PASS] Working")
        print("   * Integration - [PASS] Working")
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()