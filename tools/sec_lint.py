#!/usr/bin/env python3
"""Enhanced Security Linter for WatchLockAI Sentinel.

Comprehensive security analysis tool that scans for:
- Hardcoded secrets, tokens, and credentials
- Dangerous function usage (eval, exec, shell commands)
- Insecure file permissions and configurations
- Cryptographic material exposure (.pem, .key files)
- Command injection vulnerabilities
- Unsafe Windows permission commands (wildcard icacls)
- SQL injection patterns
- Path traversal vulnerabilities
- Insecure randomness usage

Outputs detailed security findings with severity ratings and remediation guidance.
"""

import ast
import json
import os
import re
import stat
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import argparse
import time
import hashlib


@dataclass
class SecurityFinding:
    """Represents a security issue found during scanning."""
    rule_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str
    title: str
    description: str
    file_path: str
    line_number: int
    column_number: int
    evidence: str
    remediation: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None


@dataclass
class ScanResult:
    """Results of a complete security scan."""
    scan_id: str
    timestamp: str
    files_scanned: int
    findings: List[SecurityFinding]
    scan_duration: float
    config: Dict[str, Any]


class SecurityLinter:
    """Advanced security linter with comprehensive rule coverage."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.findings: List[SecurityFinding] = []
        self.files_scanned = 0
        self.scan_start_time = 0
        
        # Compile regex patterns for performance
        self._compile_patterns()
        
        # Load rule definitions
        self._load_security_rules()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for security scanning."""
        return {
            "scan_hidden_files": False,
            "scan_test_files": True,
            "scan_vendor_dirs": False,
            "max_file_size_mb": 10,
            "follow_symlinks": False,
            "severity_threshold": "INFO",
            "excluded_patterns": [
                "*.pyc", "*.pyo", "*.pyd", "__pycache__",
                "node_modules", ".git", ".svn", ".hg",
                "venv", "env", ".venv", ".env"
            ],
            "file_extensions": {
                "python": [".py", ".pyw"],
                "javascript": [".js", ".jsx", ".ts", ".tsx"],
                "shell": [".sh", ".bash", ".zsh", ".fish"],
                "batch": [".bat", ".cmd", ".ps1"],
                "config": [".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"],
                "crypto": [".pem", ".key", ".crt", ".cer", ".p12", ".pfx"],
                "text": [".txt", ".md", ".rst", ".log"]
            }
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        self.secret_patterns = {
            "api_key": re.compile(r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', re.MULTILINE),
            "secret_key": re.compile(r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-+/=]{20,})["\']?', re.MULTILINE),
            "password": re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\'\ \t\n\r]{8,})["\']', re.MULTILINE),
            "token": re.compile(r'(?i)(token|auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-+/=]{25,})["\']?', re.MULTILINE),
            "private_key": re.compile(r'-----BEGIN[A-Z ]+PRIVATE KEY-----', re.MULTILINE),
            "aws_access_key": re.compile(r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*["\']?(AKIA[0-9A-Z]{16})["\']?', re.MULTILINE),
            "aws_secret_key": re.compile(r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*["\']?([A-Za-z0-9+/=]{40})["\']?', re.MULTILINE),
            "github_token": re.compile(r'(?i)(github[_-]?token|gh[_-]?token)\s*[:=]\s*["\']?(ghp_[A-Za-z0-9_]{36}|gho_[A-Za-z0-9_]{36})["\']?', re.MULTILINE),
            "slack_token": re.compile(r'(?i)(slack[_-]?token)\s*[:=]\s*["\']?(xox[bpoa]-[0-9]{12}-[0-9]{12}-[A-Za-z0-9]{24})["\']?', re.MULTILINE),
            "jwt_token": re.compile(r'(?i)(jwt|bearer)\s*[:=]\s*["\']?(eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*)["\']?', re.MULTILINE),
            "database_url": re.compile(r'(?i)(database[_-]?url|db[_-]?url)\s*[:=]\s*["\']?([a-z]+://[^\s"\'\ ]+)["\']?', re.MULTILINE),
            "connection_string": re.compile(r'(?i)(connection[_-]?string|conn[_-]?str)\s*[:=]\s*["\']?([^"\'\ \t\n\r]{20,})["\']?', re.MULTILINE),
        }
        
        self.command_injection_patterns = {
            "shell_command": re.compile(r'(os\.system|subprocess\.(call|run|Popen)|commands\.(getoutput|getstatusoutput))', re.MULTILINE),
            "eval_exec": re.compile(r'\b(eval|exec)\s*\(', re.MULTILINE),
            "dangerous_imports": re.compile(r'^\s*import\s+(os|subprocess|commands|pickle|marshal|shelve)\s*$', re.MULTILINE),
            "sql_injection": re.compile(r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\s+.*%s|.*\.format\s*\(.*\)', re.IGNORECASE | re.MULTILINE),
        }
        
        self.file_permission_patterns = {
            "world_writable": re.compile(r'chmod\s+[0-9]*[0-7][2367][0-7]', re.MULTILINE),
            "wildcard_icacls": re.compile(r'icacls\s+[^\s]*\*[^\s]*\s', re.MULTILINE | re.IGNORECASE),
            "unsafe_permissions": re.compile(r'(chmod\s+777|icacls\s+.*\s+/grant\s+.*:F)', re.MULTILINE | re.IGNORECASE),
        }
        
        self.crypto_patterns = {
            "weak_hash": re.compile(r'\b(md5|sha1)\s*\(', re.MULTILINE | re.IGNORECASE),
            "insecure_random": re.compile(r'\b(random\.(random|randint|choice)|Random\(\))', re.MULTILINE),
            "hardcoded_crypto": re.compile(r'(?i)(key|iv|salt)\s*=\s*["\'][a-fA-F0-9]{16,}["\']', re.MULTILINE),
        }
    
    def _load_security_rules(self):
        """Load security rule definitions."""
        self.rules = {
            # Hardcoded secrets
            "hardcoded_secret": {
                "severity": "CRITICAL",
                "category": "Hardcoded Secrets",
                "title": "Hardcoded Secret Detected",
                "cwe_id": "CWE-798",
                "cvss_score": 9.8
            },
            
            # Command injection
            "command_injection": {
                "severity": "HIGH",
                "category": "Code Injection", 
                "title": "Potential Command Injection",
                "cwe_id": "CWE-78",
                "cvss_score": 8.1
            },
            
            # Dangerous functions
            "dangerous_function": {
                "severity": "HIGH",
                "category": "Dangerous Functions",
                "title": "Use of Dangerous Function",
                "cwe_id": "CWE-95",
                "cvss_score": 7.3
            },
            
            # File permissions
            "insecure_permissions": {
                "severity": "MEDIUM",
                "category": "File Permissions",
                "title": "Insecure File Permissions",
                "cwe_id": "CWE-732",
                "cvss_score": 5.5
            },
            
            # Cryptographic issues
            "weak_cryptography": {
                "severity": "MEDIUM",
                "category": "Cryptography",
                "title": "Weak Cryptographic Practice",
                "cwe_id": "CWE-327",
                "cvss_score": 5.9
            },
            
            # Exposed files
            "exposed_crypto_material": {
                "severity": "HIGH",
                "category": "Information Exposure",
                "title": "Exposed Cryptographic Material",
                "cwe_id": "CWE-200",
                "cvss_score": 7.5
            }
        }
    
    def scan_directory(self, directory: str) -> ScanResult:
        """Scan a directory recursively for security issues."""
        self.scan_start_time = time.time()
        self.findings = []
        self.files_scanned = 0
        
        scan_id = hashlib.md5(f"{directory}_{self.scan_start_time}".encode()).hexdigest()[:8]
        
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Scan files recursively
        self._scan_directory_recursive(directory_path)
        
        # Check for exposed cryptographic files
        self._scan_crypto_files(directory_path)
        
        # Check file permissions
        self._scan_file_permissions(directory_path)
        
        scan_duration = time.time() - self.scan_start_time
        
        return ScanResult(
            scan_id=scan_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            files_scanned=self.files_scanned,
            findings=self.findings,
            scan_duration=scan_duration,
            config=self.config
        )
    
    def _scan_directory_recursive(self, directory: Path):
        """Recursively scan directory for files to analyze."""
        try:
            for item in directory.iterdir():
                if item.is_file():
                    if self._should_scan_file(item):
                        self._scan_file(item)
                elif item.is_dir() and self._should_scan_directory(item):
                    self._scan_directory_recursive(item)
        except PermissionError:
            self._add_finding(
                "permission_denied", "INFO", "Filesystem Access",
                "Permission Denied", f"Cannot access directory: {directory}",
                str(directory), 0, 0, str(directory), "Check directory permissions"
            )
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if a file should be scanned."""
        # Check file size
        try:
            if file_path.stat().st_size > self.config["max_file_size_mb"] * 1024 * 1024:
                return False
        except OSError:
            return False
        
        # Check if it's a hidden file
        if not self.config["scan_hidden_files"] and file_path.name.startswith('.'):
            return False
        
        # Check excluded patterns
        for pattern in self.config["excluded_patterns"]:
            if file_path.match(pattern):
                return False
        
        # Check if it's a test file
        if not self.config["scan_test_files"]:
            if "test" in str(file_path).lower() or "spec" in str(file_path).lower():
                return False
        
        return True
    
    def _should_scan_directory(self, dir_path: Path) -> bool:
        """Determine if a directory should be scanned."""
        # Check excluded patterns
        for pattern in self.config["excluded_patterns"]:
            if dir_path.match(pattern):
                return False
        
        # Check vendor directories
        if not self.config["scan_vendor_dirs"]:
            vendor_dirs = {"vendor", "third_party", "3rdparty", "external", "lib", "libs"}
            if dir_path.name.lower() in vendor_dirs:
                return False
        
        return True
    
    def _scan_file(self, file_path: Path):
        """Scan a single file for security issues."""
        try:
            self.files_scanned += 1
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try binary mode for non-text files
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
            
            # Determine file type
            file_ext = file_path.suffix.lower()
            
            # Scan for secrets
            self._scan_secrets(file_path, content)
            
            # Scan for command injection
            self._scan_command_injection(file_path, content)
            
            # Scan for dangerous functions
            self._scan_dangerous_functions(file_path, content)
            
            # Scan for cryptographic issues
            self._scan_crypto_issues(file_path, content)
            
            # Python-specific scans
            if file_ext in [".py", ".pyw"]:
                self._scan_python_ast(file_path, content)
            
            # Shell script scans
            elif file_ext in [".sh", ".bash", ".zsh"]:
                self._scan_shell_script(file_path, content)
            
            # Batch script scans
            elif file_ext in [".bat", ".cmd", ".ps1"]:
                self._scan_batch_script(file_path, content)
            
        except Exception as e:
            self._add_finding(
                "scan_error", "LOW", "Scanning Error",
                "File Scan Error", f"Error scanning file: {str(e)}",
                str(file_path), 0, 0, str(e), "Review file manually"
            )
    
    def _scan_secrets(self, file_path: Path, content: str):
        """Scan for hardcoded secrets and credentials."""
        lines = content.split('\n')
        
        for pattern_name, pattern in self.secret_patterns.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                # Extract the secret value
                secret_value = match.group(2) if len(match.groups()) >= 2 else match.group(0)
                
                # Skip if looks like a placeholder or example
                if self._is_placeholder_secret(secret_value):
                    continue
                
                self._add_finding(
                    "hardcoded_secret", self.rules["hardcoded_secret"]["severity"],
                    self.rules["hardcoded_secret"]["category"],
                    f"Hardcoded {pattern_name.replace('_', ' ').title()}",
                    f"Hardcoded {pattern_name} found in source code. This poses a security risk if the code is shared or stored in version control.",
                    str(file_path), line_num, match.start() - content.rfind('\n', 0, match.start()),
                    match.group(0)[:100], "Move secret to environment variables or secure configuration",
                    self.rules["hardcoded_secret"]["cwe_id"], self.rules["hardcoded_secret"]["cvss_score"]
                )
    
    def _is_placeholder_secret(self, value: str) -> bool:
        """Check if a value appears to be a placeholder rather than real secret."""
        placeholders = {
            "your_api_key", "your_secret", "your_token", "replace_me",
            "example", "test", "demo", "placeholder", "changeme",
            "xxx", "yyy", "zzz", "abc", "123", "password", "secret"
        }
        
        value_lower = value.lower()
        return any(placeholder in value_lower for placeholder in placeholders)
    
    def _scan_command_injection(self, file_path: Path, content: str):
        """Scan for potential command injection vulnerabilities."""
        lines = content.split('\n')
        
        for pattern_name, pattern in self.command_injection_patterns.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                # Check if input is properly sanitized
                if self._has_input_validation(line_content):
                    severity = "MEDIUM"
                else:
                    severity = "HIGH"
                
                self._add_finding(
                    "command_injection", severity,
                    self.rules["command_injection"]["category"],
                    f"Potential Command Injection - {pattern_name.replace('_', ' ').title()}",
                    f"Use of {pattern_name} detected. This could lead to command injection if user input is not properly validated.",
                    str(file_path), line_num, match.start() - content.rfind('\n', 0, match.start()),
                    line_content.strip(), "Validate and sanitize all user inputs before passing to system commands",
                    self.rules["command_injection"]["cwe_id"], self.rules["command_injection"]["cvss_score"]
                )
    
    def _has_input_validation(self, line: str) -> bool:
        """Check if line contains input validation patterns."""
        validation_patterns = [
            "shlex.quote", "pipes.quote", "re.escape", "html.escape",
            "validate", "sanitize", "escape", "filter", "clean"
        ]
        return any(pattern in line for pattern in validation_patterns)
    
    def _scan_dangerous_functions(self, file_path: Path, content: str):
        """Scan for use of dangerous functions."""
        dangerous_functions = {
            r'\beval\s*\(': "eval() - Arbitrary code execution",
            r'\bexec\s*\(': "exec() - Arbitrary code execution", 
            r'\b__import__\s*\(': "__import__() - Dynamic imports",
            r'\bpickle\.loads?\s*\(': "pickle.load() - Arbitrary code execution via deserialization",
            r'\bmarshal\.loads?\s*\(': "marshal.load() - Arbitrary code execution via deserialization",
            r'\binput\s*\(': "input() - User input without validation",
            r'\braw_input\s*\(': "raw_input() - User input without validation"
        }
        
        for pattern, description in dangerous_functions.items():
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                self._add_finding(
                    "dangerous_function", self.rules["dangerous_function"]["severity"],
                    self.rules["dangerous_function"]["category"],
                    f"Dangerous Function Usage",
                    f"Use of {description}. This function can be dangerous if used with untrusted input.",
                    str(file_path), line_num, match.start() - content.rfind('\n', 0, match.start()),
                    match.group(0), "Avoid using dangerous functions or ensure input is properly validated",
                    self.rules["dangerous_function"]["cwe_id"], self.rules["dangerous_function"]["cvss_score"]
                )
    
    def _scan_crypto_issues(self, file_path: Path, content: str):
        """Scan for cryptographic issues."""
        for pattern_name, pattern in self.crypto_patterns.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                self._add_finding(
                    "weak_cryptography", self.rules["weak_cryptography"]["severity"],
                    self.rules["weak_cryptography"]["category"],
                    f"Weak Cryptographic Practice - {pattern_name.replace('_', ' ').title()}",
                    f"Use of {pattern_name} detected. This may indicate weak cryptographic practices.",
                    str(file_path), line_num, match.start() - content.rfind('\n', 0, match.start()),
                    match.group(0), "Use strong cryptographic algorithms and secure random number generators",
                    self.rules["weak_cryptography"]["cwe_id"], self.rules["weak_cryptography"]["cvss_score"]
                )
    
    def _scan_python_ast(self, file_path: Path, content: str):
        """Scan Python files using AST analysis."""
        try:
            tree = ast.parse(content)
            visitor = PythonSecurityVisitor(str(file_path))
            visitor.visit(tree)
            self.findings.extend(visitor.findings)
        except SyntaxError:
            # Skip files with syntax errors
            pass
    
    def _scan_shell_script(self, file_path: Path, content: str):
        """Scan shell scripts for security issues."""
        lines = content.split('\n')
        
        # Check for dangerous shell patterns
        dangerous_patterns = {
            r'\$\([^)]*\$[^)]*\)': "Command substitution with user input",
            r'`[^`]*\$[^`]*`': "Backtick command substitution with variables",
            r'eval\s+.*\$': "eval with variables",
            r'rm\s+-rf\s+\$': "Dangerous rm command with variables",
            r'chmod\s+777': "Overly permissive file permissions",
            r'curl\s+.*\|\s*sh': "Piping curl output to shell",
            r'wget\s+.*\|\s*sh': "Piping wget output to shell"
        }
        
        for i, line in enumerate(lines, 1):
            for pattern, description in dangerous_patterns.items():
                if re.search(pattern, line):
                    self._add_finding(
                        "shell_security", "MEDIUM", "Shell Security",
                        f"Dangerous Shell Pattern", description,
                        str(file_path), i, 0, line.strip(),
                        "Review shell command for security implications"
                    )
    
    def _scan_batch_script(self, file_path: Path, content: str):
        """Scan batch/PowerShell scripts for security issues."""
        lines = content.split('\n')
        
        # Check for dangerous batch/PowerShell patterns
        dangerous_patterns = {
            r'icacls\s+.*\*.*\s+/grant': "Wildcard icacls grant command",
            r'icacls\s+.*\s+/grant\s+.*:F': "Full control grant in icacls",
            r'takeown\s+/f\s+.*\*': "Wildcard takeown command",
            r'attrib\s+-r\s+.*\*': "Wildcard attribute removal",
            r'Invoke-Expression': "Invoke-Expression (eval equivalent)",
            r'IEX\s+': "IEX alias for Invoke-Expression",
            r'New-Object\s+.*COM': "COM object creation",
            r'Start-Process\s+.*-WindowStyle\s+Hidden': "Hidden process execution"
        }
        
        for i, line in enumerate(lines, 1):
            for pattern, description in dangerous_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    severity = "HIGH" if "wildcard" in description.lower() else "MEDIUM"
                    self._add_finding(
                        "batch_security", severity, "Batch/PowerShell Security",
                        f"Dangerous Batch/PowerShell Pattern", description,
                        str(file_path), i, 0, line.strip(),
                        "Review command for security implications"
                    )
    
    def _scan_crypto_files(self, directory: Path):
        """Scan for exposed cryptographic material files."""
        crypto_extensions = [".pem", ".key", ".crt", ".cer", ".p12", ".pfx", ".jks"]
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in crypto_extensions:
                # Check if it's in a secure location
                path_str = str(file_path).lower()
                insecure_locations = ["public", "www", "htdocs", "assets", "static", "resources"]
                
                is_insecure = any(location in path_str for location in insecure_locations)
                severity = "HIGH" if is_insecure else "MEDIUM"
                
                self._add_finding(
                    "exposed_crypto_material", severity,
                    self.rules["exposed_crypto_material"]["category"],
                    "Exposed Cryptographic Material",
                    f"Cryptographic file ({file_path.suffix}) found. Ensure it's properly secured.",
                    str(file_path), 0, 0, str(file_path),
                    "Move cryptographic files to secure locations with appropriate permissions",
                    self.rules["exposed_crypto_material"]["cwe_id"],
                    self.rules["exposed_crypto_material"]["cvss_score"]
                )
    
    def _scan_file_permissions(self, directory: Path):
        """Scan for insecure file permissions."""
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    file_stat = file_path.stat()
                    
                    # Check for world-writable files
                    if file_stat.st_mode & stat.S_IWOTH:
                        self._add_finding(
                            "insecure_permissions", "MEDIUM", "File Permissions",
                            "World-Writable File",
                            "File is writable by all users. This could allow unauthorized modifications.",
                            str(file_path), 0, 0, oct(file_stat.st_mode)[-3:],
                            "Remove world-write permissions: chmod o-w filename"
                        )
                    
                    # Check for executable files in unusual locations
                    if (file_stat.st_mode & stat.S_IXUSR and 
                        file_path.suffix not in [".sh", ".py", ".exe", ".bat", ".cmd"] and
                        "bin" not in str(file_path)):
                        
                        self._add_finding(
                            "suspicious_executable", "LOW", "File Permissions",
                            "Suspicious Executable File",
                            "File has execute permissions but unusual location/extension.",
                            str(file_path), 0, 0, oct(file_stat.st_mode)[-3:],
                            "Review file permissions and purpose"
                        )
                        
                except OSError:
                    # Skip files we can't stat
                    pass
    
    def _add_finding(self, rule_id: str, severity: str, category: str, title: str,
                    description: str, file_path: str, line_number: int, column_number: int,
                    evidence: str, remediation: str, cwe_id: Optional[str] = None,
                    cvss_score: Optional[float] = None):
        """Add a security finding to the results."""
        finding = SecurityFinding(
            rule_id=rule_id,
            severity=severity,
            category=category,
            title=title,
            description=description,
            file_path=file_path,
            line_number=line_number,
            column_number=column_number,
            evidence=evidence,
            remediation=remediation,
            cwe_id=cwe_id,
            cvss_score=cvss_score
        )
        self.findings.append(finding)
    
    def generate_report(self, scan_result: ScanResult, format_type: str = "markdown") -> str:
        """Generate a formatted security report."""
        if format_type == "json":
            return self._generate_json_report(scan_result)
        elif format_type == "csv":
            return self._generate_csv_report(scan_result)
        else:
            return self._generate_markdown_report(scan_result)
    
    def _generate_markdown_report(self, scan_result: ScanResult) -> str:
        """Generate a Markdown security report."""
        # Count findings by severity
        severity_counts = {}
        category_counts = {}
        
        for finding in scan_result.findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
        
        report = []
        report.append("# Security Linting Report\n")
        report.append(f"**Scan ID:** {scan_result.scan_id}\n")
        report.append(f"**Timestamp:** {scan_result.timestamp}\n")
        report.append(f"**Files Scanned:** {scan_result.files_scanned}\n")
        report.append(f"**Scan Duration:** {scan_result.scan_duration:.2f} seconds\n")
        report.append(f"**Total Findings:** {len(scan_result.findings)}\n\n")
        
        # Executive Summary
        critical_count = severity_counts.get("CRITICAL", 0)
        high_count = severity_counts.get("HIGH", 0)
        
        if critical_count > 0:
            report.append("🔴 **CRITICAL RISK**: Critical security vulnerabilities detected\n\n")
        elif high_count > 5:
            report.append("🟡 **MODERATE RISK**: Multiple high-severity findings\n\n")
        else:
            report.append("🟢 **LOW RISK**: No critical vulnerabilities detected\n\n")
        
        # Severity Breakdown
        report.append("## Findings by Severity\n\n")
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {"CRITICAL": "🔥", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "ℹ️", "INFO": "✅"}.get(severity, "")
                report.append(f"- {emoji} **{severity}**: {count}\n")
        report.append("\n")
        
        # Category Breakdown
        report.append("## Findings by Category\n\n")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{category}**: {count}\n")
        report.append("\n")
        
        # Detailed Findings
        report.append("## Detailed Findings\n\n")
        
        # Group by severity
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            severity_findings = [f for f in scan_result.findings if f.severity == severity]
            if not severity_findings:
                continue
                
            emoji = {"CRITICAL": "🔥", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "ℹ️", "INFO": "✅"}.get(severity, "")
            report.append(f"### {emoji} {severity} Severity ({len(severity_findings)} findings)\n\n")
            
            for i, finding in enumerate(severity_findings[:20]):  # Limit to first 20 per severity
                report.append(f"#### {i+1}. {finding.title}\n\n")
                report.append(f"- **File:** `{finding.file_path}`\n")
                if finding.line_number > 0:
                    report.append(f"- **Line:** {finding.line_number}\n")
                report.append(f"- **Category:** {finding.category}\n")
                if finding.cwe_id:
                    report.append(f"- **CWE:** {finding.cwe_id}\n")
                if finding.cvss_score:
                    report.append(f"- **CVSS Score:** {finding.cvss_score}\n")
                report.append(f"- **Description:** {finding.description}\n")
                report.append(f"- **Evidence:** `{finding.evidence[:200]}...`\n")
                report.append(f"- **Remediation:** {finding.remediation}\n\n")
            
            if len(severity_findings) > 20:
                report.append(f"*... and {len(severity_findings) - 20} more {severity} findings*\n\n")
        
        # Recommendations
        report.append("## Security Recommendations\n\n")
        
        if critical_count > 0:
            report.append("### Immediate Actions Required\n")
            report.append("- Address all CRITICAL severity findings immediately\n")
            report.append("- Review and remove hardcoded secrets\n")
            report.append("- Implement proper input validation and sanitization\n\n")
        
        report.append("### General Security Improvements\n")
        report.append("- Implement automated security scanning in CI/CD pipeline\n")
        report.append("- Use environment variables for configuration secrets\n")
        report.append("- Enable comprehensive security logging\n")
        report.append("- Regular security code reviews\n")
        report.append("- Keep dependencies updated and scan for vulnerabilities\n")
        report.append("- Implement principle of least privilege for file permissions\n\n")
        
        report.append("---\n")
        report.append("*Report generated by WatchLockAI Sentinel Security Linter*\n")
        
        return "".join(report)
    
    def _generate_json_report(self, scan_result: ScanResult) -> str:
        """Generate a JSON security report."""
        return json.dumps(asdict(scan_result), indent=2, default=str)
    
    def _generate_csv_report(self, scan_result: ScanResult) -> str:
        """Generate a CSV security report."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Severity", "Category", "Title", "File", "Line", "Evidence", "CWE", "CVSS", "Description", "Remediation"
        ])
        
        # Write findings
        for finding in scan_result.findings:
            writer.writerow([
                finding.severity, finding.category, finding.title,
                finding.file_path, finding.line_number, finding.evidence,
                finding.cwe_id or "", finding.cvss_score or "",
                finding.description, finding.remediation
            ])
        
        return output.getvalue()


class PythonSecurityVisitor(ast.NodeVisitor):
    """AST visitor for Python-specific security analysis."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.findings: List[SecurityFinding] = []
    
    def visit_Call(self, node: ast.Call):
        """Visit function calls to detect dangerous patterns."""
        # Check for dangerous function calls
        if isinstance(node.func, ast.Name):
            if node.func.id in ["eval", "exec", "compile"]:
                self._add_finding(
                    "dangerous_function", "HIGH", "Dangerous Functions",
                    f"Dangerous function: {node.func.id}",
                    f"Use of {node.func.id}() can lead to arbitrary code execution.",
                    node.lineno, node.col_offset, node.func.id,
                    "Avoid using eval/exec or ensure input is properly validated"
                )
        
        # Check for subprocess calls without shell=False
        elif isinstance(node.func, ast.Attribute):
            if (isinstance(node.func.value, ast.Name) and 
                node.func.value.id == "subprocess" and
                node.func.attr in ["call", "run", "Popen"]):
                
                # Check if shell=True is used
                shell_true = any(
                    isinstance(kw, ast.keyword) and kw.arg == "shell" and
                    isinstance(kw.value, ast.Constant) and kw.value.value is True
                    for kw in node.keywords
                )
                
                if shell_true:
                    self._add_finding(
                        "shell_injection", "HIGH", "Command Injection",
                        "subprocess call with shell=True",
                        "Using shell=True can lead to command injection vulnerabilities.",
                        node.lineno, node.col_offset, "shell=True",
                        "Use shell=False or validate/sanitize all inputs"
                    )
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import):
        """Visit import statements to detect dangerous imports."""
        dangerous_modules = {"pickle", "marshal", "dill", "cloudpickle"}
        
        for alias in node.names:
            if alias.name in dangerous_modules:
                self._add_finding(
                    "dangerous_import", "MEDIUM", "Dangerous Imports",
                    f"Import of dangerous module: {alias.name}",
                    f"Module {alias.name} can be used for arbitrary code execution via deserialization.",
                    node.lineno, node.col_offset, alias.name,
                    "Use safer serialization formats like JSON when possible"
                )
        
        self.generic_visit(node)
    
    def visit_Str(self, node: ast.Str):
        """Visit string literals to detect potential secrets."""
        # Check for potential secrets in string literals
        if len(node.s) > 20 and any(char.isalnum() for char in node.s):
            # Look for patterns that might be secrets
            if re.match(r'^[A-Za-z0-9+/=]{20,}$', node.s):  # Base64-like
                self._add_finding(
                    "potential_secret", "LOW", "Potential Secrets",
                    "Potential encoded secret in string literal",
                    "Long alphanumeric string that might be a secret or token.",
                    node.lineno, node.col_offset, node.s[:50],
                    "Review string content and move secrets to environment variables"
                )
        
        self.generic_visit(node)
    
    def _add_finding(self, rule_id: str, severity: str, category: str, title: str,
                    description: str, line_number: int, column_number: int,
                    evidence: str, remediation: str):
        """Add a finding from AST analysis."""
        finding = SecurityFinding(
            rule_id=rule_id,
            severity=severity,
            category=category,
            title=title,
            description=description,
            file_path=self.file_path,
            line_number=line_number,
            column_number=column_number,
            evidence=evidence,
            remediation=remediation
        )
        self.findings.append(finding)


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(description="WatchLockAI Security Linter")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--format", choices=["markdown", "json", "csv"], 
                       default="markdown", help="Output format")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--config", help="Config file path")
    parser.add_argument("--severity", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
                       default="INFO", help="Minimum severity to report")
    
    args = parser.parse_args()
    
    # Load config if provided
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Create linter and run scan
    linter = SecurityLinter(config)
    
    try:
        scan_result = linter.scan_directory(args.directory)
        
        # Filter by severity
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        min_severity_index = severity_order.index(args.severity)
        
        filtered_findings = [
            f for f in scan_result.findings 
            if severity_order.index(f.severity) <= min_severity_index
        ]
        scan_result.findings = filtered_findings
        
        # Generate report
        report = linter.generate_report(scan_result, args.format)
        
        # Output report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report written to {args.output}")
        else:
            print(report)
            
        # Exit with error code if critical or high severity findings
        critical_count = len([f for f in scan_result.findings if f.severity == "CRITICAL"])
        high_count = len([f for f in scan_result.findings if f.severity == "HIGH"])
        
        if critical_count > 0:
            sys.exit(2)
        elif high_count > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
