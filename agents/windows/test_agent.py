#!/usr/bin/env python3
'''
WatchLockAI Windows Agent Test Suite
Test all agent monitoring capabilities
'''

import os
import time
import json
import tempfile
import subprocess
import threading
from pathlib import Path
from windows_agent_core import WindowsAgentCore, FileSystemMonitor, ProcessMonitor, NetworkMonitor

def test_file_system_monitor():
    '''Test file system monitoring'''
    print("\n🔍 Testing File System Monitor...")
    
    monitor = FileSystemMonitor()
    
    # Create test file in temp directory
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as temp_file:
        temp_file.write(b'Test executable content')
        temp_path = temp_file.name
        
    print(f"✅ Created test file: {temp_path}")
    
    # Test file analysis
    stat_info = os.stat(temp_path)
    monitor._analyze_file_change(temp_path, stat_info)
    
    # Cleanup
    os.unlink(temp_path)
    print("✅ File system monitor test completed")

def test_process_monitor():
    '''Test process monitoring'''
    print("\n🔍 Testing Process Monitor...")
    
    monitor = ProcessMonitor()
    monitor._update_process_list()
    
    print(f"✅ Process monitor initialized with {len(monitor.known_processes)} processes")
    
    # Test suspicious process detection
    fake_proc_info = {
        'name': 'mimikatz.exe',
        'pid': 12345,
        'exe': 'C:\\Temp\\mimikatz.exe',
        'cmdline': ['mimikatz.exe', 'sekurlsa::logonpasswords'],
        'create_time': time.time()
    }
    
    monitor._analyze_new_process(fake_proc_info)
    print("✅ Process monitor test completed")

def test_network_monitor():
    '''Test network monitoring'''
    print("\n🔍 Testing Network Monitor...")
    
    monitor = NetworkMonitor()
    
    # Test suspicious IP detection
    test_ips = ['192.168.1.1', '10.0.0.1', '8.8.8.8']
    
    for ip in test_ips:
        is_suspicious = monitor._is_suspicious_ip(ip)
        print(f"   IP {ip}: {'Suspicious' if is_suspicious else 'Normal'}")
        
    print("✅ Network monitor test completed")

def test_agent_configuration():
    '''Test agent configuration loading'''
    print("\n🔍 Testing Agent Configuration...")
    
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
    print("✅ Agent configuration test completed")

def test_agent_status():
    '''Test agent status functionality'''
    print("\n🔍 Testing Agent Status...")
    
    agent = WindowsAgentCore()
    
    # Test initial status
    status = agent.get_agent_status()
    assert status['status'] == 'not_started'
    
    print("✅ Agent status test completed")

def test_event_reporting():
    '''Test event reporting to AI Brain'''
    print("\n🔍 Testing Event Reporting...")
    
    # Test with mock AI Brain (should fail gracefully)
    monitor = FileSystemMonitor("http://localhost:9998")  # Non-existent endpoint
    
    # This should not crash the monitor
    fake_stat = type('stat', (), {'st_size': 1024, 'st_mtime': time.time()})()
    monitor._analyze_file_change("C:\\test\\file.exe", fake_stat)
    
    print("✅ Event reporting test completed")

def test_browser_monitor():
    '''Test browser monitoring'''
    print("\n🔍 Testing Browser Monitor...")
    
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
        
    print("✅ Browser monitor test completed")

def run_integration_test():
    '''Run integration test with all components'''
    print("\n🔧 Running Integration Test...")
    
    # Test full agent startup (without actually starting monitoring)
    agent = WindowsAgentCore()
    
    # Verify all components are initialized
    assert agent.file_monitor is not None
    assert agent.process_monitor is not None
    assert agent.network_monitor is not None
    assert agent.registry_monitor is not None
    
    print("✅ Integration test completed")

def run_all_tests():
    '''Run all agent tests'''
    print("🧪 WatchLockAI Windows Agent Test Suite")
    print("=" * 50)
    
    try:
        test_file_system_monitor()
        test_process_monitor()
        test_network_monitor()
        test_agent_configuration()
        test_agent_status()
        test_event_reporting()
        test_browser_monitor()
        run_integration_test()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\n🎯 WatchLockAI Windows Agent is ready for deployment")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
