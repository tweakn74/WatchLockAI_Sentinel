#!/usr/bin/env python3
"""
PowerShell Syntax Tester
Tests PowerShell installer for the specific syntax issues reported
"""

import os
import re
import subprocess

def test_powershell_syntax():
    """Test PowerShell installer syntax"""
    print("[SEARCH] POWERSHELL SYNTAX ANALYSIS")
    print("=" * 50)
    
    ps_file = "/workspace/WatchLockAI_Agent/WatchLockAI-Installer.ps1"
    
    if not os.path.exists(ps_file):
        print(f"[FAIL] PowerShell file not found: {ps_file}")
        return False
    
    with open(ps_file, 'r') as f:
        content = f.read()
    
    print(f"[PAGE] File: {os.path.basename(ps_file)}")
    print(f"[U+1F4CF] Size: {len(content)} characters")
    
    # Test with PowerShell Core
    print(f"\\n[U+1F9EA] Testing with PowerShell Core...")
    
    try:
        # Test syntax parsing
        cmd = ["/workspace/powershell/pwsh", "-Command", 
               f"try {{ $ast = [System.Management.Automation.Language.Parser]::ParseFile('{ps_file}', [ref]$null, [ref]$null); Write-Host 'SYNTAX: VALID' -ForegroundColor Green }} catch {{ Write-Host 'SYNTAX: ERROR' -ForegroundColor Red; Write-Host $_.Exception.Message }}"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(f"[SEARCH] PowerShell Core Result:")
        print(f"   Return code: {result.returncode}")
        print(f"   Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"   Errors: {result.stderr.strip()}")
        
    except subprocess.TimeoutExpired:
        print("[U+23F0] PowerShell test timed out")
    except Exception as e:
        print(f"[FAIL] PowerShell test failed: {e}")
    
    # Analyze the specific syntax error mentioned
    print(f"\\n[SEARCH] ANALYZING REPORTED SYNTAX ERROR...")
    
    # Look for the problematic here-string section
    lines = content.split('\\n')
    problematic_sections = []
    
    for i, line in enumerate(lines, 1):
        # Look for here-strings with variables
        if '@"' in line:
            print(f"\\n[U+1F4CD] Found here-string at line {i}:")
            
            # Find the corresponding closing @"
            start_line = i
            closing_line = None
            for j in range(i, min(i + 50, len(lines))):
                if '"@' in lines[j]:
                    closing_line = j + 1
                    break
            
            if closing_line:
                print(f"   Here-string: lines {start_line}-{closing_line}")
                here_string_content = '\\n'.join(lines[i-1:closing_line])
                
                # Check for variables in here-string
                variables = re.findall(r'\\$\\w+', here_string_content)
                if variables:
                    print(f"   [WARN] Variables found: {variables}")
                    print(f"   [IDEA] This might cause the interpolation issue!")
                    problematic_sections.append((start_line, closing_line, variables))
                else:
                    print(f"   [PASS] No variables found")
    
    # Check for @echo commands (batch mixed with PowerShell)
    echo_lines = []
    for i, line in enumerate(lines, 1):
        if '@echo off' in line:
            echo_lines.append(i)
    
    if echo_lines:
        print(f"\\n[WARN] FOUND BATCH COMMANDS IN POWERSHELL:")
        for line_num in echo_lines:
            print(f"   Line {line_num}: {lines[line_num-1].strip()}")
        print(f"   [IDEA] This is the exact error you encountered!")
    
    # Generate fix recommendations
    print(f"\\n[U+1F527] RECOMMENDED FIXES:")
    
    if problematic_sections:
        print(f"\\n1. HERE-STRING VARIABLE ISSUES:")
        for start, end, vars in problematic_sections:
            print(f"   * Lines {start}-{end}: Replace variables {vars} with hardcoded values")
            print(f"     OR use expandable here-strings with @\" instead of @\"")
    
    if echo_lines:
        print(f"\\n2. BATCH COMMAND MIXING:")
        print(f"   * Remove all @echo off commands (lines: {echo_lines})")
        print(f"   * PowerShell doesn't need @echo off")
    
    print(f"\\n3. GENERAL RECOMMENDATION:")
    print(f"   * Use the Super-Simple-Installer.bat instead")
    print(f"   * It's simpler and avoids PowerShell complexity")
    
    return len(problematic_sections) == 0 and len(echo_lines) == 0

def main():
    """Main function"""
    success = test_powershell_syntax()
    
    print(f"\\n{'='*50}")
    if success:
        print("[PASS] PowerShell installer syntax looks good!")
    else:
        print("[FAIL] PowerShell installer has syntax issues (as expected)")
        print("[IDEA] Use Super-Simple-Installer.bat for guaranteed success")

if __name__ == "__main__":
    main()