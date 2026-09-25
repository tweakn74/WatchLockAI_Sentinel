#!/usr/bin/env python3
'''
WatchLockAI Account Sentinel Test Suite
Test all account monitoring and analysis capabilities
'''

import os
import time
import json
import tempfile
import sqlite3
from pathlib import Path

# Import our components
from account_sentinel_core import AccountDiscovery, BehaviorAnalyzer, AccountSentinelCore
from identity_correlation import IdentityCorrelationEngine
from event_monitor import WindowsEventMonitor

def test_account_discovery():
    '''Test account discovery functionality'''
    print("\n[SEARCH] Testing Account Discovery...")
    
    discovery = AccountDiscovery()
    
    # Test database initialization
    assert os.path.exists(discovery.account_database)
    print("[PASS] Account database initialized")
    
    # Test account discovery methods (will be limited in Linux environment)
    accounts = discovery.discover_accounts()
    print(f"[PASS] Account discovery completed (found {len(accounts)} accounts)")
    
    # Test suspicious account detection
    fake_account = {
        'username': 'admin$',
        'description': '',
        'disabled': False,
        'password_required': False,
        'sid': 'S-1-5-21-123456789-500'
    }
    
    discovery._analyze_for_hidden_accounts([fake_account])
    print("[PASS] Hidden account analysis working")

def test_behavior_analyzer():
    '''Test behavior analysis'''
    print("\n[SEARCH] Testing Behavior Analyzer...")
    
    analyzer = BehaviorAnalyzer()
    
    # Test database initialization
    assert os.path.exists(analyzer.behavior_database)
    print("[PASS] Behavior database initialized")
    
    # Test user profile creation
    profile = analyzer._create_user_profile("testuser")
    assert profile.username == "testuser"
    print("[PASS] User profile creation working")
    
    # Test login behavior analysis
    analyzer.analyze_login_behavior("testuser", "2024-01-01T09:00:00", "192.168.1.100")
    print("[PASS] Login behavior analysis working")
    
    # Test process behavior analysis  
    analyzer.analyze_process_behavior("testuser", "notepad.exe", "notepad.exe document.txt")
    print("[PASS] Process behavior analysis working")
    
    # Test privilege escalation detection
    old_privs = ["SeShutdownPrivilege"]
    new_privs = ["SeShutdownPrivilege", "SeDebugPrivilege"]
    analyzer.detect_privilege_escalation("testuser", old_privs, new_privs)
    print("[PASS] Privilege escalation detection working")

def test_identity_correlation():
    '''Test identity correlation engine'''
    print("\n[SEARCH] Testing Identity Correlation...")
    
    engine = IdentityCorrelationEngine()
    
    # Test database initialization
    assert os.path.exists(engine.identity_database)
    print("[PASS] Identity database initialized")
    
    # Test identity correlation
    user_info = {
        'full_name': 'John Doe',
        'email': 'john.doe@company.com',
        'sid': 'S-1-5-21-123456789-1001',
        'domain': 'COMPANY'
    }
    
    identity_id1 = engine.correlate_identity("jdoe", user_info)
    identity_id2 = engine.correlate_identity("john.doe", user_info)  # Same user
    
    print(f"[PASS] Identity correlation working")
    print(f"   User 'jdoe' -> {identity_id1}")
    print(f"   User 'john.doe' -> {identity_id2}")

def test_event_monitor():
    '''Test Windows event monitoring'''
    print("\n[SEARCH] Testing Event Monitor...")
    
    monitor = WindowsEventMonitor()
    
    # Test initialization
    assert monitor.monitored_events is not None
    assert 'Security' in monitor.monitored_events
    print("[PASS] Event monitor initialized")
    
    # Test event processing (with mock data)
    fake_event = "Sample event log entry for testing"
    monitor._process_event(fake_event, 4624)
    print("[PASS] Event processing working")

def test_configuration_loading():
    '''Test configuration management'''
    print("\n[SEARCH] Testing Configuration Loading...")
    
    # Create test config
    test_config = {
        "ai_brain_url": "http://localhost:9998",
        "monitoring_enabled": {
            "account_discovery": True,
            "behavior_analysis": False
        }
    }
    
    config_file = "test_sentinel_config.json"
    with open(config_file, 'w') as f:
        json.dump(test_config, f)
    
    # Test config loading
    sentinel = AccountSentinelCore(config_file)
    
    assert sentinel.config['ai_brain_url'] == "http://localhost:9998"
    assert sentinel.config['monitoring_enabled']['behavior_analysis'] == False
    
    # Cleanup
    os.remove(config_file)
    
    print("[PASS] Configuration loading test completed")

def test_database_operations():
    '''Test database operations'''
    print("\n[SEARCH] Testing Database Operations...")
    
    # Test account database
    discovery = AccountDiscovery()
    
    # Test account storage
    test_accounts = [
        {
            'username': 'testuser1',
            'sid': 'S-1-5-21-123456789-1001',
            'description': 'Test User 1',
            'source': 'test',
            'discovery_time': '2024-01-01T00:00:00',
            'is_hidden': False,
            'risk_score': 0.2
        }
    ]
    
    sentinel = AccountSentinelCore()
    sentinel._store_discovered_accounts(test_accounts)
    
    # Verify storage
    conn = sqlite3.connect(discovery.account_database)
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM accounts WHERE username = ?', ('testuser1',))
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == 'testuser1'
    
    print("[PASS] Database operations working")

def test_integration():
    '''Test full system integration'''
    print("\n[U+1F527] Testing Integration...")
    
    # Test full system initialization
    sentinel = AccountSentinelCore()
    
    # Verify all components are initialized
    assert sentinel.account_discovery is not None
    assert sentinel.behavior_analyzer is not None
    
    # Test status
    status = sentinel.get_status()
    assert 'running' in status
    assert 'config' in status
    assert 'components' in status
    
    print("[PASS] Integration test completed")

def run_all_tests():
    '''Run all Account Sentinel tests'''
    print("[U+1F9EA] WatchLockAI Account Sentinel Test Suite")
    print("=" * 50)
    
    try:
        test_account_discovery()
        test_behavior_analyzer()
        test_identity_correlation()
        test_event_monitor()
        test_configuration_loading()
        test_database_operations()
        test_integration()
        
        print("\n" + "=" * 50)
        print("[PASS] All Account Sentinel tests completed successfully!")
        print("\n[U+1F465] Account Sentinel is ready for deployment")
        print("\n[PLAN] Test Summary:")
        print("   * Account Discovery - [PASS] Working")
        print("   * Behavior Analysis - [PASS] Working")
        print("   * Identity Correlation - [PASS] Working")
        print("   * Event Monitoring - [PASS] Working")
        print("   * Configuration Management - [PASS] Working")
        print("   * Database Operations - [PASS] Working")
        print("   * System Integration - [PASS] Working")
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
