#!/usr/bin/env python3
"""
Fix broken string literals in AI Brain files
"""

import os
import re

def fix_broken_strings(file_path):
    """Fix broken string literals in file"""
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix broken print statements with newlines
    # Pattern: print(" followed by newline and then content
    pattern = r'print\("(\r?\n)([^"]*)"'
    
    def fix_match(match):
        newline = match.group(1)
        content = match.group(2)
        # Remove any leading/trailing whitespace from content
        content = content.strip()
        return f'print("\\n{content}"'
    
    fixed_content = re.sub(pattern, fix_match, content)
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"[PASS] Fixed {file_path}")

def main():
    """Fix all AI Brain files"""
    ai_brain_dir = "/workspace/WatchLockAI_RealPlatform/AIBrain"
    
    files_to_fix = [
        "ai_brain_core.py",
        "test_ai_brain.py",
        "event_ingestion.py"
    ]
    
    for file_name in files_to_fix:
        file_path = os.path.join(ai_brain_dir, file_name)
        if os.path.exists(file_path):
            fix_broken_strings(file_path)
        else:
            print(f"[FAIL] File not found: {file_path}")

if __name__ == "__main__":
    main()
