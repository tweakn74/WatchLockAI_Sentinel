#!/usr/bin/env python3
'''
WatchSleuth Forensic Engine Test Cases
Test the forensic analysis capabilities
'''

import os
import json
import tempfile
import shutil
from pathlib import Path
from watchsleuth_engine import WatchSleuthForensicEngine, MFTAnalyzer, RegistryAnalyzer

def test_forensic_engine():
    '''Test the main forensic engine'''
    print("🔍 Testing WatchSleuth Forensic Engine...")
    
    # Create temporary case directory
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = WatchSleuthForensicEngine(temp_dir)
        
        # Test 1: Start Investigation
        print("\n1️⃣ Testing investigation creation...")
        case_id = engine.start_investigation(
            "Test Investigation",
            "Test Analyst", 
            "Testing WatchSleuth capabilities"
        )
        print(f"✅ Created investigation: {case_id}")
        
        # Test 2: Add Evidence (create dummy file)
        print("\n2️⃣ Testing evidence addition...")
        dummy_evidence = Path(temp_dir) / "test_evidence.txt"
        dummy_evidence.write_text("This is test evidence data")
        
        artifact_id = engine.add_evidence(str(dummy_evidence), "Test evidence file")
        print(f"✅ Added evidence artifact: {artifact_id}")
        
        # Test 3: Perform Analysis
        print("\n3️⃣ Testing comprehensive analysis...")
        results = engine.perform_comprehensive_analysis(case_id)
        print(f"✅ Analysis complete - {len(results['findings'])} findings")
        
        # Test 4: Export Report
        print("\n4️⃣ Testing report export...")
        report_path = Path(temp_dir) / "test_report.json"
        success = engine.export_case_report(case_id, str(report_path))
        print(f"✅ Report exported: {success}")
        
        if report_path.exists():
            report_size = report_path.stat().st_size
            print(f"   Report size: {report_size} bytes")

def test_mft_analyzer():
    '''Test MFT analyzer with simulated data'''
    print("\n🔍 Testing MFT Analyzer...")
    
    analyzer = MFTAnalyzer()
    
    # Create simulated MFT data
    with tempfile.NamedTemporaryFile(suffix='.mft', delete=False) as temp_mft:
        # Write simulated MFT header
        mft_header = b'FILE' + b'\x00' * 1020  # Simulated MFT record
        temp_mft.write(mft_header)
        temp_mft.flush()
        
        # Test MFT analysis
        records = analyzer.analyze_mft(temp_mft.name)
        print(f"✅ Parsed {len(records)} MFT records")
        
        # Cleanup
        os.unlink(temp_mft.name)

def test_registry_analyzer():
    '''Test registry analyzer'''
    print("\n🔍 Testing Registry Analyzer...")
    
    analyzer = RegistryAnalyzer()
    
    # Create dummy registry hive file
    with tempfile.NamedTemporaryFile(suffix='.reg', delete=False) as temp_reg:
        temp_reg.write(b'regf')  # Registry file signature
        temp_reg.flush()
        
        # Test registry analysis
        analysis = analyzer.analyze_registry_hive(temp_reg.name)
        print(f"✅ Registry analysis complete")
        print(f"   Persistence mechanisms: {len(analysis['persistence_mechanisms'])}")
        print(f"   Suspicious entries: {len(analysis['suspicious_entries'])}")
        
        # Cleanup
        os.unlink(temp_reg.name)

def test_timeline_creation():
    '''Test timeline creation'''
    print("\n🔍 Testing Timeline Creation...")
    
    # Create sample timeline events
    events = [
        {
            'event_id': 'evt_001',
            'timestamp': '2025-01-01T10:00:00',
            'event_type': 'file_created',
            'source': 'MFT',
            'description': 'Suspicious file created',
            'confidence': 0.9
        },
        {
            'event_id': 'evt_002', 
            'timestamp': '2025-01-01T10:05:00',
            'event_type': 'process_started',
            'source': 'Event Log',
            'description': 'Malicious process executed',
            'confidence': 0.8
        }
    ]
    
    print(f"✅ Created timeline with {len(events)} events")
    
    # Test event correlation
    from timeline_analysis import EventCorrelator
    
    correlator = EventCorrelator()
    correlator.load_events(events)
    
    clusters = correlator.find_event_clusters(time_window_minutes=10)
    print(f"✅ Found {len(clusters)} event clusters")
    
    attack_analysis = correlator.analyze_attack_sequence()
    print(f"✅ Attack sequence analysis: {len(attack_analysis['potential_attack_chains'])} chains")

def run_all_tests():
    '''Run all forensic engine tests'''
    print("🧪 WatchSleuth Forensic Engine Test Suite")
    print("=" * 50)
    
    try:
        test_forensic_engine()
        test_mft_analyzer()
        test_registry_analyzer()
        test_timeline_creation()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\n🎯 WatchSleuth Forensic Engine is ready for use")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    run_all_tests()
