#!/usr/bin/env python3
'''
WatchSleuth Forensic Tools Launcher
Quick access to specific forensic analysis tools
'''

import sys
import json
import argparse
from pathlib import Path
from watchsleuth_engine import WatchSleuthForensicEngine, MFTAnalyzer, RegistryAnalyzer, BrowserForensics

def mft_analysis(mft_file: str, output_file: str = None):
    '''Analyze MFT file'''
    print(f"[SEARCH] Analyzing MFT file: {mft_file}")
    
    analyzer = MFTAnalyzer()
    records = analyzer.analyze_mft(mft_file)
    
    print(f"[PASS] Analyzed {len(records)} MFT records")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(records, f, indent=2)
        print(f"[PAGE] Results saved to: {output_file}")
    else:
        # Print summary
        print("\n[BARS] MFT Analysis Summary:")
        print(f"   Total Records: {len(records)}")
        
        # Show recent files
        recent_files = [r for r in records if 'filename' in r and 'created_time' in r][:10]
        print(f"   Recent Files:")
        for file_record in recent_files:
            print(f"     {file_record.get('filename', 'unknown')} - {file_record.get('created_time', 'unknown')}")

def registry_analysis(hive_file: str, output_file: str = None):
    '''Analyze Windows registry hive'''
    print(f"[SEARCH] Analyzing registry hive: {hive_file}")
    
    analyzer = RegistryAnalyzer()
    analysis = analyzer.analyze_registry_hive(hive_file)
    
    print(f"[PASS] Registry analysis complete")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"[PAGE] Results saved to: {output_file}")
    else:
        # Print summary
        print("\n[BARS] Registry Analysis Summary:")
        print(f"   Persistence Mechanisms: {len(analysis['persistence_mechanisms'])}")
        print(f"   Suspicious Entries: {len(analysis['suspicious_entries'])}")
        
        for entry in analysis['suspicious_entries'][:5]:
            print(f"     [WARN]  {entry['pattern']} - {entry['risk_level']}")

def browser_analysis(history_db: str, browser_type: str = 'chrome', output_file: str = None):
    '''Analyze browser history'''
    print(f"[SEARCH] Analyzing {browser_type} history: {history_db}")
    
    forensics = BrowserForensics()
    analysis = forensics.analyze_browser_history(browser_type, history_db)
    
    print(f"[PASS] Browser analysis complete")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"[PAGE] Results saved to: {output_file}")
    else:
        # Print summary
        print("\n[BARS] Browser Analysis Summary:")
        print(f"   Total Visits: {analysis.get('visit_count', 0)}")
        print(f"   Suspicious URLs: {len(analysis.get('suspicious_urls', []))}")
        
        top_urls = analysis.get('top_urls', [])[:5]
        print(f"   Top Visited URLs:")
        for url_data in top_urls:
            print(f"     {url_data[0][:50]}... - {url_data[1]} visits")

def full_investigation(evidence_dir: str, case_name: str, investigator: str):
    '''Perform full forensic investigation'''
    print(f"[SEARCH] Starting full investigation: {case_name}")
    print(f"   Investigator: {investigator}")
    print(f"   Evidence Directory: {evidence_dir}")
    
    # Initialize engine
    engine = WatchSleuthForensicEngine("./investigations")
    
    # Start investigation
    case_id = engine.start_investigation(case_name, investigator, f"Investigation of evidence in {evidence_dir}")
    
    # Add all evidence files
    evidence_path = Path(evidence_dir)
    evidence_count = 0
    
    for file_path in evidence_path.rglob('*'):
        if file_path.is_file():
            try:
                artifact_id = engine.add_evidence(str(file_path), f"Evidence file: {file_path.name}")
                evidence_count += 1
                print(f"   [PAGE] Added evidence: {file_path.name}")
            except Exception as e:
                print(f"   [FAIL] Failed to add {file_path.name}: {e}")
    
    print(f"\n[PASS] Added {evidence_count} evidence files")
    
    # Perform comprehensive analysis
    print("\n[U+1F52C] Performing comprehensive analysis...")
    results = engine.perform_comprehensive_analysis(case_id)
    
    # Export report
    report_path = f"investigation_report_{case_id}.json"
    if engine.export_case_report(case_id, report_path):
        print(f"\n[PAGE] Investigation report: {report_path}")
    
    # Print summary
    print("\n[BARS] Investigation Summary:")
    print(f"   Case ID: {case_id}")
    print(f"   Evidence Files: {evidence_count}")
    print(f"   Timeline Events: {len(results.get('timeline', []))}")
    print(f"   Key Findings: {len(results.get('findings', []))}")
    
    for finding in results.get('findings', []):
        print(f"     [SEARCH] {finding}")

def main():
    '''Main CLI interface'''
    parser = argparse.ArgumentParser(description='WatchSleuth Forensic Tools')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # MFT Analysis
    mft_parser = subparsers.add_parser('mft', help='Analyze MFT file')
    mft_parser.add_argument('file', help='MFT file path')
    mft_parser.add_argument('-o', '--output', help='Output JSON file')
    
    # Registry Analysis
    reg_parser = subparsers.add_parser('registry', help='Analyze registry hive')
    reg_parser.add_argument('file', help='Registry hive file path')
    reg_parser.add_argument('-o', '--output', help='Output JSON file')
    
    # Browser Analysis
    browser_parser = subparsers.add_parser('browser', help='Analyze browser history')
    browser_parser.add_argument('file', help='Browser history database file')
    browser_parser.add_argument('-t', '--type', default='chrome', choices=['chrome', 'firefox'], help='Browser type')
    browser_parser.add_argument('-o', '--output', help='Output JSON file')
    
    # Full Investigation
    investigate_parser = subparsers.add_parser('investigate', help='Perform full investigation')
    investigate_parser.add_argument('evidence_dir', help='Evidence directory path')
    investigate_parser.add_argument('-n', '--name', required=True, help='Investigation case name')
    investigate_parser.add_argument('-i', '--investigator', required=True, help='Investigator name')
    
    args = parser.parse_args()
    
    if args.command == 'mft':
        mft_analysis(args.file, args.output)
    elif args.command == 'registry':
        registry_analysis(args.file, args.output)
    elif args.command == 'browser':
        browser_analysis(args.file, args.type, args.output)
    elif args.command == 'investigate':
        full_investigation(args.evidence_dir, args.name, args.investigator)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
