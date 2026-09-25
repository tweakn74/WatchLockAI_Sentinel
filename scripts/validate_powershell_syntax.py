#!/usr/bin/env python3
"""
PowerShell Syntax Validator
This script validates PowerShell syntax by checking for common issues.
"""

import os
import re
from pathlib import Path

class PowerShellSyntaxValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_file(self, file_path):
        """Validate a PowerShell file for syntax issues"""
        print(f"Validating PowerShell file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        self.errors = []
        self.warnings = []
        
        # Check for common syntax issues
        self._check_unicode_characters(content, lines)
        self._check_try_catch_blocks(content, lines)
        self._check_here_strings(content, lines)
        self._check_variable_syntax(content, lines)
        self._check_string_quotes(content, lines)
        self._check_parentheses_balance(content, lines)
        self._check_braces_balance(content, lines)
        
        return len(self.errors) == 0
    
    def _check_unicode_characters(self, content, lines):
        """Check for problematic Unicode characters"""
        problematic_chars = ['[x]', '[FAIL]', '*', '->', '<-', '↑', '↓']
        
        for i, line in enumerate(lines, 1):
            for char in problematic_chars:
                if char in line:
                    self.errors.append(f"Line {i}: Unicode character '{char}' may cause parsing errors")
    
    def _check_try_catch_blocks(self, content, lines):
        """Check for proper try-catch-finally block structure"""
        try_pattern = r'\btry\s*{'
        catch_pattern = r'\bcatch\s*{'
        finally_pattern = r'\bfinally\s*{'
        
        try_positions = []
        for i, line in enumerate(lines, 1):
            if re.search(try_pattern, line, re.IGNORECASE):
                try_positions.append(i)
        
        # Check if each try has corresponding catch or finally
        for try_line in try_positions:
            has_catch = False
            has_finally = False
            
            # Look for catch/finally in subsequent lines (simplified check)
            for j in range(try_line, min(try_line + 50, len(lines))):
                if j < len(lines):
                    if re.search(catch_pattern, lines[j], re.IGNORECASE):
                        has_catch = True
                    if re.search(finally_pattern, lines[j], re.IGNORECASE):
                        has_finally = True
            
            if not has_catch and not has_finally:
                self.errors.append(f"Line {try_line}: try block missing catch or finally block")
    
    def _check_here_strings(self, content, lines):
        """Check for proper here-string syntax"""
        here_string_start = r'@["\']'
        here_string_end = r'^["\']@'
        
        in_here_string = False
        here_string_start_line = 0
        
        for i, line in enumerate(lines, 1):
            if re.search(here_string_start, line):
                if in_here_string:
                    self.errors.append(f"Line {i}: Nested here-string detected")
                in_here_string = True
                here_string_start_line = i
                
                # Check if here-string starts correctly (should be at end of line)
                if not line.strip().endswith(('@"', "@'")):
                    self.warnings.append(f"Line {i}: Here-string should start at end of line")
            
            if re.match(here_string_end, line.strip()):
                if not in_here_string:
                    self.errors.append(f"Line {i}: Here-string end without start")
                in_here_string = False
                
                # Check if here-string ends correctly (should be at start of line)
                if not line.strip() in ['"@', "'@"]:
                    self.warnings.append(f"Line {i}: Here-string end should be at start of line")
        
        if in_here_string:
            self.errors.append(f"Line {here_string_start_line}: Unclosed here-string")
    
    def _check_variable_syntax(self, content, lines):
        """Check for variable syntax issues"""
        # Check for invalid variable names - but exclude subexpressions $(..)
        invalid_var_pattern = r'\$[^a-zA-Z_\(][a-zA-Z0-9_]*'
        
        for i, line in enumerate(lines, 1):
            # Skip lines with subexpressions
            if '$(' in line:
                continue
                
            matches = re.finditer(invalid_var_pattern, line)
            for match in matches:
                self.errors.append(f"Line {i}: Invalid variable name '{match.group()}'")
        
        # Check for colon issues in variable references - but be more specific
        colon_issue_pattern = r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*[^\\"]'
        for i, line in enumerate(lines, 1):
            # Skip common valid patterns
            if 'Out-File' in line or 'Join-Path' in line or '::' in line:
                continue
            if re.search(colon_issue_pattern, line):
                self.warnings.append(f"Line {i}: Potential variable colon syntax issue")
    
    def _check_string_quotes(self, content, lines):
        """Check for quote balance and escaping"""
        for i, line in enumerate(lines, 1):
            # Count quotes (simplified check)
            single_quotes = line.count("'")
            double_quotes = line.count('"')
            
            # Check for unescaped quotes in strings
            if single_quotes % 2 != 0 and not line.strip().endswith('\\'):
                self.warnings.append(f"Line {i}: Unbalanced single quotes")
            
            if double_quotes % 2 != 0 and not line.strip().endswith('\\'):
                self.warnings.append(f"Line {i}: Unbalanced double quotes")
    
    def _check_parentheses_balance(self, content, lines):
        """Check for balanced parentheses"""
        paren_count = 0
        
        for i, line in enumerate(lines, 1):
            line_paren_count = line.count('(') - line.count(')')
            paren_count += line_paren_count
            
            if paren_count < 0:
                self.errors.append(f"Line {i}: Unmatched closing parenthesis")
                paren_count = 0  # Reset to continue checking
        
        if paren_count > 0:
            self.errors.append(f"File: {paren_count} unclosed parentheses")
    
    def _check_braces_balance(self, content, lines):
        """Check for balanced braces"""
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            line_brace_count = line.count('{') - line.count('}')
            brace_count += line_brace_count
            
            if brace_count < 0:
                self.errors.append(f"Line {i}: Unmatched closing brace")
                brace_count = 0  # Reset to continue checking
        
        if brace_count > 0:
            self.errors.append(f"File: {brace_count} unclosed braces")
    
    def print_results(self):
        """Print validation results"""
        print("\n" + "="*60)
        print("POWERSHELL SYNTAX VALIDATION RESULTS")
        print("="*60)
        
        if self.errors:
            print(f"\n[FAIL] ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  * {error}")
        
        if self.warnings:
            print(f"\n[WARN]  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  * {warning}")
        
        if not self.errors and not self.warnings:
            print("\n[PASS] NO SYNTAX ISSUES DETECTED")
        elif not self.errors:
            print(f"\n[PASS] NO CRITICAL ERRORS (only {len(self.warnings)} warnings)")
        else:
            print(f"\n[FAIL] VALIDATION FAILED ({len(self.errors)} errors, {len(self.warnings)} warnings)")
        
        print("="*60)

def main():
    validator = PowerShellSyntaxValidator()
    
    # Test the bulletproof-final installer
    installer_path = Path("/workspace/WatchLockAI_Agent/installers/BULLETPROOF-FINAL-Installer.ps1")
    
    if installer_path.exists():
        print(f"Testing PowerShell installer: {installer_path}")
        is_valid = validator.validate_file(installer_path)
        validator.print_results()
        
        if is_valid:
            print("\n[U+1F389] INSTALLER SYNTAX VALIDATION PASSED!")
            print("The PowerShell script should now work on real Windows systems.")
        else:
            print("\n[U+1F4A5] INSTALLER SYNTAX VALIDATION FAILED!")
            print("The script needs further fixes before deployment.")
            
        return is_valid
    else:
        print(f"[FAIL] Installer file not found: {installer_path}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
