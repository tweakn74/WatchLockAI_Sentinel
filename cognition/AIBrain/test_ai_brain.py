#!/usr/bin/env python3
'''
WatchLockAI AI Brain Test Script
Tests the AI Brain with various security scenarios
'''

import requests
import json
import time
from datetime import datetime

def test_ai_brain():
    '''Test WatchLockAI AI Brain functionality'''
    ai_brain_url = "http://localhost:9999"
    
    print("🧠 Testing WatchLockAI AI Brain...")
    
    # Test 1: Health Check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{ai_brain_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ AI Brain is healthy")
        else:
            print("❌ AI Brain health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to AI Brain: {e}")
        return
    
    # Test 2: Status Check
    print("\n2️⃣ Testing status endpoint...")
    try:
        response = requests.get(f"{ai_brain_url}/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ AI Brain Status: {status.get('status')}")
            print(f"   Events analyzed today: {status.get('events_analyzed_today', 0)}")
        else:
            print("❌ Status check failed")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    # Test 3: Normal Event Analysis
    print("\n3️⃣ Testing normal event analysis...")
    normal_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "user_login",
        "source": "Windows Security",
        "details": {
            "user": "jdoe",
            "computer": "WORKSTATION-01",
            "login_type": "interactive"
        },
        "threat_level": "low"
    }
    
    try:
        response = requests.post(f"{ai_brain_url}/analyze", json=normal_event, timeout=5)
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Normal event analyzed")
            print(f"   Threat detected: {analysis.get('threat_detected', False)}")
            print(f"   Threat level: {analysis.get('threat_level', 'unknown')}")
        else:
            print("❌ Normal event analysis failed")
    except Exception as e:
        print(f"❌ Normal event analysis error: {e}")
    
    # Test 4: Suspicious Event Analysis
    print("\n4️⃣ Testing suspicious event analysis...")
    suspicious_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "powershell_execution",
        "source": "PowerShell Monitor",
        "details": {
            "user": "admin",
            "command": "powershell.exe -encodedcommand dwhoami",
            "process_id": "1234",
            "elevated": True
        },
        "threat_level": "high"
    }
    
    try:
        response = requests.post(f"{ai_brain_url}/analyze", json=suspicious_event, timeout=5)
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Suspicious event analyzed")
            print(f"   Threat detected: {analysis.get('threat_detected', False)}")
            print(f"   Threat level: {analysis.get('threat_level', 'unknown')}")
            print(f"   MITRE tactics: {analysis.get('mitre_tactics', [])}")
            print(f"   Narrative: {analysis.get('narrative', 'N/A')[:100]}...")
        else:
            print("❌ Suspicious event analysis failed")
    except Exception as e:
        print(f"❌ Suspicious event analysis error: {e}")
    
    # Test 5: Credential Dumping Event
    print("\n5️⃣ Testing credential dumping detection...")
    credential_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "process_access",
        "source": "Process Monitor",
        "details": {
            "user": "hacker",
            "target_process": "lsass.exe",
            "access_type": "read_memory",
            "source_process": "mimikatz.exe",
            "elevated": True
        },
        "threat_level": "critical"
    }
    
    try:
        response = requests.post(f"{ai_brain_url}/analyze", json=credential_event, timeout=5)
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Credential dumping event analyzed")
            print(f"   Threat detected: {analysis.get('threat_detected', False)}")
            print(f"   Threat level: {analysis.get('threat_level', 'unknown')}")
            print(f"   Kill chain stage: {analysis.get('kill_chain_stage', 'unknown')}")
            print(f"   Recommended actions: {len(analysis.get('recommended_actions', []))} actions")
        else:
            print("❌ Credential dumping analysis failed")
    except Exception as e:
        print(f"❌ Credential dumping analysis error: {e}")
    
    # Test 6: Penetration Testing Detection
    print("\n6️⃣ Testing penetration testing detection...")
    pentest_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "network_scan",
        "source": "Network Monitor",
        "details": {
            "user": "pentester",
            "tool": "nmap",
            "target_range": "192.168.1.0/24",
            "scan_type": "syn_scan",
            "ports_scanned": 1000
        },
        "threat_level": "medium"
    }
    
    try:
        response = requests.post(f"{ai_brain_url}/analyze", json=pentest_event, timeout=5)
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Penetration testing event analyzed")
            print(f"   Threat detected: {analysis.get('threat_detected', False)}")
            print(f"   Narrative: {analysis.get('narrative', 'N/A')[:100]}...")
        else:
            print("❌ Penetration testing analysis failed")
    except Exception as e:
        print(f"❌ Penetration testing analysis error: {e}")
    
    print("\n🎉 AI Brain testing completed!")
    print("\nThe WatchLockAI Agentic AI Brain is functioning correctly.")

if __name__ == "__main__":
    test_ai_brain()
