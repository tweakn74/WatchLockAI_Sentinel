# Security Linting Report
**Scan ID:** 4256a6db
**Timestamp:** 2025-09-06 15:32:01 UTC
**Files Scanned:** 354
**Scan Duration:** 43.80 seconds
**Total Findings:** 591

[U+1F534] **CRITICAL RISK**: Critical security vulnerabilities detected

## Findings by Severity

- [FIRE] **CRITICAL**: 2
- [WARN] **HIGH**: 142
- [SYS] **MEDIUM**: 10
- ℹ **LOW**: 437

## Findings by Category

- **File Permissions**: 343
- **Code Injection**: 134
- **Potential Secrets**: 94
- **Dangerous Functions**: 11
- **Cryptography**: 5
- **Hardcoded Secrets**: 2
- **Dangerous Imports**: 2

## Detailed Findings

### [FIRE] CRITICAL Severity (2 findings)

#### 1. Hardcoded Token

- **File:** `DOCS/report/windows_service.md`
- **Line:** 45
- **Category:** Hardcoded Secrets
- **CWE:** CWE-798
- **CVSS Score:** 9.8
- **Description:** Hardcoded token found in source code. This poses a security risk if the code is shared or stored in version control.
- **Evidence:** `TOKEN=your_secure_admin_token_here...`
- **Remediation:** Move secret to environment variables or secure configuration

#### 2. Hardcoded Private Key

- **File:** `tests/test_quarantine_traversal.py`
- **Line:** 72
- **Category:** Hardcoded Secrets
- **CWE:** CWE-798
- **CVSS Score:** 9.8
- **Description:** Hardcoded private_key found in source code. This poses a security risk if the code is shared or stored in version control.
- **Evidence:** `-----BEGIN PRIVATE KEY-----...`
- **Remediation:** Move secret to environment variables or secure configuration

### [WARN] HIGH Severity (142 findings)

#### 1. Potential Command Injection - Dangerous Imports

- **File:** `temp_rc2_evidence.py`
- **Line:** 2
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 2. Potential Command Injection - Dangerous Imports

- **File:** `temp_synthetic_probes.py`
- **Line:** 1
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 3. Potential Command Injection - Dangerous Imports

- **File:** `service/service_wrapper.py`
- **Line:** 6
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 4. Potential Command Injection - Dangerous Imports

- **File:** `DOCS/report/api_contract.md`
- **Line:** 315
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 5. Potential Command Injection - Dangerous Imports

- **File:** `DOCS/report/api_contract.md`
- **Line:** 325
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 6. Potential Command Injection - Dangerous Imports

- **File:** `generate_inventory.py`
- **Line:** 3
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 7. Potential Command Injection - Dangerous Imports

- **File:** `scripts/generate_sbom.py`
- **Line:** 10
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 8. Potential Command Injection - Shell Command

- **File:** `scripts/windows_install_dryrun.py`
- **Line:** 215
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of shell_command detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `result = subprocess.run(...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 9. Potential Command Injection - Dangerous Imports

- **File:** `scripts/windows_install_dryrun.py`
- **Line:** 7
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 10. Potential Command Injection - Dangerous Imports

- **File:** `scripts/windows_install_dryrun.py`
- **Line:** 10
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import subprocess...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 11. Potential Command Injection - Shell Command

- **File:** `scripts/generate_security_posture.py`
- **Line:** 34
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of shell_command detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `result = subprocess.run(...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 12. Potential Command Injection - Dangerous Imports

- **File:** `scripts/generate_security_posture.py`
- **Line:** 9
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 13. Potential Command Injection - Dangerous Imports

- **File:** `scripts/generate_security_posture.py`
- **Line:** 10
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import subprocess...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 14. Potential Command Injection - Dangerous Imports

- **File:** `scripts/rc_soak_test_mock.py`
- **Line:** 9
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 15. Potential Command Injection - Shell Command

- **File:** `scripts/generate_ga_signoff.py`
- **Line:** 246
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of shell_command detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `result = subprocess.run(...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 16. Potential Command Injection - Dangerous Imports

- **File:** `scripts/generate_ga_signoff.py`
- **Line:** 9
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 17. Potential Command Injection - Dangerous Imports

- **File:** `scripts/generate_ga_signoff.py`
- **Line:** 10
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import subprocess...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 18. Potential Command Injection - Dangerous Imports

- **File:** `scripts/generate_sbom_clean.py`
- **Line:** 10
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 19. Potential Command Injection - Dangerous Imports

- **File:** `scripts/rc_soak_test.py`
- **Line:** 11
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of dangerous_imports detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `import os...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 20. Potential Command Injection - Shell Command

- **File:** `scripts/package_release.py`
- **Line:** 143
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of shell_command detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `result = subprocess.run(...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

*... and 122 more HIGH findings*

### [SYS] MEDIUM Severity (10 findings)

#### 1. Potential Command Injection - Sql Injection

- **File:** `final_validation.json`
- **Line:** 33
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of sql_injection detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `"out": "FFFFFFFFFFFFFFFF......FF.F.FFF.FF.FFFFFFFFFF.FFFFFFFFFFFFFFFFFFFFFFFFF.. [ 86%]\n...........                                                              [100%]\n==============================...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 2. Potential Command Injection - Sql Injection

- **File:** `DOCS/Compatibility_Report.json`
- **Line:** 8
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of sql_injection detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `"out": "FFFFFFFFFFFFF.....FFFF.FF.FFFF.FFF.FFFFFFFFFF.FFFFFFFFFFFFFFFFFFFFFFFFF. [ 85%]\n............                                                             [100%]\n==============================...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 3. Potential Command Injection - Sql Injection

- **File:** `DOCS/Build_Manifest.json`
- **Line:** 33
- **Category:** Code Injection
- **CWE:** CWE-78
- **CVSS Score:** 8.1
- **Description:** Use of sql_injection detected. This could lead to command injection if user input is not properly validated.
- **Evidence:** `"out": "FFFFFFFFFFFFFFFF......FF.F.FFF.FF.FFFFFFFFFF.FFFFFFFFFFFFFFFFFFFFFFFFF.. [ 86%]\n...........                                                              [100%]\n==============================...`
- **Remediation:** Validate and sanitize all user inputs before passing to system commands

#### 4. Weak Cryptographic Practice - Weak Hash

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 266
- **Category:** Cryptography
- **CWE:** CWE-327
- **CVSS Score:** 5.9
- **Description:** Use of weak_hash detected. This may indicate weak cryptographic practices.
- **Evidence:** `md5(...`
- **Remediation:** Use strong cryptographic algorithms and secure random number generators

#### 5. Weak Cryptographic Practice - Insecure Random

- **File:** `tests/test_fuzz_inputs.py`
- **Line:** 74
- **Category:** Cryptography
- **CWE:** CWE-327
- **CVSS Score:** 5.9
- **Description:** Use of insecure_random detected. This may indicate weak cryptographic practices.
- **Evidence:** `random.choice...`
- **Remediation:** Use strong cryptographic algorithms and secure random number generators

#### 6. Weak Cryptographic Practice - Insecure Random

- **File:** `tests/unit/test_fs_monitor.py`
- **Line:** 300
- **Category:** Cryptography
- **CWE:** CWE-327
- **CVSS Score:** 5.9
- **Description:** Use of insecure_random detected. This may indicate weak cryptographic practices.
- **Evidence:** `random.choice...`
- **Remediation:** Use strong cryptographic algorithms and secure random number generators

#### 7. Weak Cryptographic Practice - Insecure Random

- **File:** `console/chaos_probes.py`
- **Line:** 142
- **Category:** Cryptography
- **CWE:** CWE-327
- **CVSS Score:** 5.9
- **Description:** Use of insecure_random detected. This may indicate weak cryptographic practices.
- **Evidence:** `random.random...`
- **Remediation:** Use strong cryptographic algorithms and secure random number generators

#### 8. Import of dangerous module: pickle

- **File:** `console/anomaly.py`
- **Line:** 15
- **Category:** Dangerous Imports
- **Description:** Module pickle can be used for arbitrary code execution via deserialization.
- **Evidence:** `pickle...`
- **Remediation:** Use safer serialization formats like JSON when possible

#### 9. Import of dangerous module: pickle

- **File:** `detection/ml_scoring.py`
- **Line:** 9
- **Category:** Dangerous Imports
- **Description:** Module pickle can be used for arbitrary code execution via deserialization.
- **Evidence:** `pickle...`
- **Remediation:** Use safer serialization formats like JSON when possible

#### 10. Weak Cryptographic Practice - Weak Hash

- **File:** `tools/sec_lint.py`
- **Line:** 200
- **Category:** Cryptography
- **CWE:** CWE-327
- **CVSS Score:** 5.9
- **Description:** Use of weak_hash detected. This may indicate weak cryptographic practices.
- **Evidence:** `md5(...`
- **Remediation:** Use strong cryptographic algorithms and secure random number generators

### ℹ LOW Severity (437 findings)

#### 1. Potential encoded secret in string literal

- **File:** `app_core/config.py`
- **Line:** 94
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `detection/knowledge/index...`
- **Remediation:** Review string content and move secrets to environment variables

#### 2. Potential encoded secret in string literal

- **File:** `collectors/health_monitor.py`
- **Line:** 239
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `healthdegradationcombov1...`
- **Remediation:** Review string content and move secrets to environment variables

#### 3. Potential encoded secret in string literal

- **File:** `app.py`
- **Line:** 205
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `detection/knowledge/packs...`
- **Remediation:** Review string content and move secrets to environment variables

#### 4. Potential encoded secret in string literal

- **File:** `app.py`
- **Line:** 296
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `detection/knowledge/packs...`
- **Remediation:** Review string content and move secrets to environment variables

#### 5. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 59
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/config/reload...`
- **Remediation:** Review string content and move secrets to environment variables

#### 6. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 60
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/config/schema...`
- **Remediation:** Review string content and move secrets to environment variables

#### 7. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 61
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/anomaly/train...`
- **Remediation:** Review string content and move secrets to environment variables

#### 8. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 62
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/quarantine...`
- **Remediation:** Review string content and move secrets to environment variables

#### 9. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 63
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/quarantine/restore...`
- **Remediation:** Review string content and move secrets to environment variables

#### 10. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 65
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/plugins/execute...`
- **Remediation:** Review string content and move secrets to environment variables

#### 11. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 69
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/rotate/preview...`
- **Remediation:** Review string content and move secrets to environment variables

#### 12. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 70
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/rotate/execute...`
- **Remediation:** Review string content and move secrets to environment variables

#### 13. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 71
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/chaos/inject...`
- **Remediation:** Review string content and move secrets to environment variables

#### 14. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 72
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/chaos/status...`
- **Remediation:** Review string content and move secrets to environment variables

#### 15. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 73
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/retention/run...`
- **Remediation:** Review string content and move secrets to environment variables

#### 16. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 74
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/retention/stats...`
- **Remediation:** Review string content and move secrets to environment variables

#### 17. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 75
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/perf/probe...`
- **Remediation:** Review string content and move secrets to environment variables

#### 18. Potential encoded secret in string literal

- **File:** `tests/test_rbac_abuse.py`
- **Line:** 76
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/admin/perf/quick...`
- **Remediation:** Review string content and move secrets to environment variables

#### 19. Potential encoded secret in string literal

- **File:** `tests/test_api_contract_check.py`
- **Line:** 114
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/unknown/endpoint...`
- **Remediation:** Review string content and move secrets to environment variables

#### 20. Potential encoded secret in string literal

- **File:** `tests/test_structured_logging.py`
- **Line:** 26
- **Category:** Potential Secrets
- **Description:** Long alphanumeric string that might be a secret or token.
- **Evidence:** `/api/metrics/snapshot...`
- **Remediation:** Review string content and move secrets to environment variables

*... and 417 more LOW findings*

## Security Recommendations

### Immediate Actions Required
- Address all CRITICAL severity findings immediately
- Review and remove hardcoded secrets
- Implement proper input validation and sanitization

### General Security Improvements
- Implement automated security scanning in CI/CD pipeline
- Use environment variables for configuration secrets
- Enable comprehensive security logging
- Regular security code reviews
- Keep dependencies updated and scan for vulnerabilities
- Implement principle of least privilege for file permissions

---
*Report generated by WatchLockAI Sentinel Security Linter*
