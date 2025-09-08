#!/usr/bin/env python3
"""P6-003: Security Posture Report Generator

Runs enhanced security linting and generates comprehensive security posture report
for GA readiness assessment.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def run_security_scan(repo_root: Path):
    """Run the enhanced security linter on the codebase.
    
    Args:
        repo_root: Repository root directory
        
    Returns:
        tuple: (success, findings_data)
    """
    try:
        # Run sec_lint.py with JSON output
        cmd = [
            sys.executable, 
            str(repo_root / "tools" / "sec_lint.py"),
            "--path", str(repo_root),
            "--format", "json",
            "--recursive"
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=repo_root,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Parse JSON output
            try:
                findings = json.loads(result.stdout)
                return True, findings
            except json.JSONDecodeError:
                return False, {"error": "Invalid JSON output from sec_lint.py"}
        else:
            return False, {"error": f"sec_lint.py failed: {result.stderr}"}
            
    except subprocess.TimeoutExpired:
        return False, {"error": "Security scan timed out"}
    except Exception as e:
        return False, {"error": f"Security scan failed: {e}"}

def analyze_findings(findings_data):
    """Analyze security findings and categorize by severity and type.
    
    Args:
        findings_data: Raw findings from security scanner
        
    Returns:
        dict: Analysis summary
    """
    if "error" in findings_data:
        return {"error": findings_data["error"]}
    
    # Initialize counters
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "ERROR": 0}
    category_counts = {}
    total_files_scanned = 0
    files_with_issues = set()
    
    # Extract findings if nested in report structure
    findings = findings_data
    if isinstance(findings_data, dict) and "findings" in findings_data:
        findings = findings_data["findings"]
        total_files_scanned = findings_data.get("summary", {}).get("files_scanned", 0)
    
    # Process each finding
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        category = finding.get("category", "Unknown")
        file_path = finding.get("file", "")
        
        # Count by severity
        if severity in severity_counts:
            severity_counts[severity] += 1
        else:
            severity_counts[severity] = 1
        
        # Count by category
        category_counts[category] = category_counts.get(category, 0) + 1
        
        # Track files with issues
        if file_path:
            files_with_issues.add(file_path)
    
    # Calculate summary metrics
    total_findings = len(findings)
    files_with_issues_count = len(files_with_issues)
    
    # Determine overall security posture
    posture_score = calculate_security_score(severity_counts)
    posture_level = get_posture_level(posture_score)
    
    return {
        "total_findings": total_findings,
        "files_scanned": total_files_scanned,
        "files_with_issues": files_with_issues_count,
        "severity_breakdown": severity_counts,
        "category_breakdown": category_counts,
        "security_score": posture_score,
        "posture_level": posture_level,
        "findings": findings
    }

def calculate_security_score(severity_counts):
    """Calculate a security score based on finding severities.
    
    Args:
        severity_counts: Dict of severity -> count
        
    Returns:
        int: Security score (0-100, higher is better)
    """
    # Weighting for different severities
    weights = {"CRITICAL": -50, "HIGH": -20, "MEDIUM": -5, "LOW": -1, "ERROR": -2}
    
    # Start with perfect score
    score = 100
    
    # Deduct points for findings
    for severity, count in severity_counts.items():
        if severity in weights:
            score += weights[severity] * count
    
    # Ensure score stays in valid range
    return max(0, min(100, score))

def get_posture_level(score):
    """Get security posture level based on score.
    
    Args:
        score: Security score (0-100)
        
    Returns:
        str: Posture level description
    """
    if score >= 95:
        return "EXCELLENT"
    elif score >= 85:
        return "GOOD"
    elif score >= 70:
        return "FAIR"
    elif score >= 50:
        return "POOR"
    else:
        return "CRITICAL"

def generate_security_posture_report(analysis, output_path: Path):
    """Generate the security posture report.
    
    Args:
        analysis: Security analysis results
        output_path: Path to write the report
        
    Returns:
        bool: Success status
    """
    if "error" in analysis:
        error_content = f"""# WatchLockAI Sentinel Security Posture Report

**Version:** 0.9.0-rc1  
**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Status:** ERROR

## Scan Error

❌ **Security scan failed:** {analysis['error']}

Please resolve the scanning issue and run the security posture assessment again.

---
*Generated by WatchLockAI Sentinel Security Posture Generator (P6-003)*
"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(error_content)
            return True
        except Exception:
            return False
    
    # Generate full report
    posture_emoji = {
        "EXCELLENT": "🟢",
        "GOOD": "🟡", 
        "FAIR": "🟠",
        "POOR": "🔴",
        "CRITICAL": "💀"
    }
    
    status_emoji = posture_emoji.get(analysis["posture_level"], "❓")
    
    # GA readiness assessment
    severity_counts = analysis.get("severity_breakdown", analysis.get("severity_counts", {}))
    ga_ready = severity_counts.get("CRITICAL", 0) == 0 and severity_counts.get("HIGH", 0) == 0
    ga_status = "✅ GA READY" if ga_ready else "⚠️ REVIEW REQUIRED"
    
    # Create detailed findings breakdown
    findings_by_category = {}
    for finding in analysis["findings"]:
        category = finding.get("category", "Unknown")
        if category not in findings_by_category:
            findings_by_category[category] = []
        findings_by_category[category].append(finding)
    
    content = f"""# WatchLockAI Sentinel Security Posture Report

**Version:** 0.9.0-rc1  
**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Security Score:** {analysis['security_score']}/100  
**Posture Level:** {status_emoji} {analysis['posture_level']}  
**GA Readiness:** {ga_status}

## Executive Summary

WatchLockAI Sentinel v0.9.0-rc1 security posture assessment completed with **{analysis['total_findings']} security findings** across **{analysis['files_scanned']} files scanned**. Security score of **{analysis['security_score']}/100** indicates **{analysis['posture_level']}** security posture.

## Security Metrics

### Findings Breakdown
- **Critical:** {severity_counts.get('CRITICAL', 0)} findings
- **High:** {severity_counts.get('HIGH', 0)} findings  
- **Medium:** {severity_counts.get('MEDIUM', 0)} findings
- **Low:** {severity_counts.get('LOW', 0)} findings
- **Scan Errors:** {severity_counts.get('ERROR', 0)} files

### Coverage Statistics
- **Files Scanned:** {analysis['files_scanned']}
- **Files with Issues:** {analysis['files_with_issues']}
- **Clean Files:** {analysis['files_scanned'] - analysis['files_with_issues']}
- **Coverage Rate:** {((analysis['files_scanned'] - analysis['files_with_issues']) / max(analysis['files_scanned'], 1) * 100):.1f}%

## Security Categories Analysis

{generate_category_analysis(analysis['category_breakdown'], findings_by_category)}

## P6-003 Enhanced Security Checks Status

### ✅ Hardcoded Secrets Detection
- **Rules:** SEC001, SEC002, SEC017, SEC023
- **Coverage:** Passwords, API keys, AWS/GCP/Azure credentials, environment variables
- **Status:** {'✅ PASS' if severity_counts.get('CRITICAL', 0) == 0 else '❌ ISSUES FOUND'}

### ✅ Access Control & ACL Validation  
- **Rules:** SEC018, SEC024
- **Coverage:** Wildcard ACLs, excessive permissions
- **Status:** {'✅ PASS' if sum(1 for f in analysis['findings'] if f.get('rule_id') in ['SEC018', 'SEC024']) == 0 else '❌ ISSUES FOUND'}

### ✅ File System Security
- **Rules:** SEC005, SEC019
- **Coverage:** World-writable permissions, filesystem security
- **Status:** {'✅ PASS' if sum(1 for f in analysis['findings'] if f.get('rule_id') in ['SEC005', 'SEC019']) == 0 else '❌ ISSUES FOUND'}

### ✅ Cookie Security Flags
- **Rules:** SEC020, SEC021, SEC022
- **Coverage:** HttpOnly, Secure, SameSite attributes
- **Status:** {'✅ PASS' if sum(1 for f in analysis['findings'] if f.get('rule_id') in ['SEC020', 'SEC021', 'SEC022']) == 0 else '❌ ISSUES FOUND'}

## GA Readiness Assessment

### Security Gate Criteria
| Criterion | Target | Actual | Status |
|-----------|---------|---------|---------|
| Critical Issues | 0 | {severity_counts.get('CRITICAL', 0)} | {'✅' if severity_counts.get('CRITICAL', 0) == 0 else '❌'} |
| High Severity Issues | ≤ 2 | {severity_counts.get('HIGH', 0)} | {'✅' if severity_counts.get('HIGH', 0) <= 2 else '❌'} |
| Security Score | ≥ 85 | {analysis['security_score']} | {'✅' if analysis['security_score'] >= 85 else '❌'} |
| Clean File Rate | ≥ 90% | {((analysis['files_scanned'] - analysis['files_with_issues']) / max(analysis['files_scanned'], 1) * 100):.1f}% | {'✅' if ((analysis['files_scanned'] - analysis['files_with_issues']) / max(analysis['files_scanned'], 1) * 100) >= 90 else '❌'} |

### Recommendations

{generate_recommendations(analysis)}

## Detailed Findings

{generate_detailed_findings(findings_by_category) if analysis['total_findings'] > 0 else '✅ No security issues detected - All scanned files passed security validation.'}

---
*Generated by WatchLockAI Sentinel Security Posture Generator (P6-003)*
"""
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def generate_category_analysis(category_breakdown, findings_by_category):
    """Generate analysis by security category."""
    if not category_breakdown:
        return "✅ No security categories with findings detected."
    
    analysis = []
    for category, count in sorted(category_breakdown.items()):
        severity_summary = {}
        for finding in findings_by_category.get(category, []):
            sev = finding.get("severity", "UNKNOWN")
            severity_summary[sev] = severity_summary.get(sev, 0) + 1
        
        severity_text = ", ".join(f"{count} {sev}" for sev, count in severity_summary.items())
        
        # Risk assessment
        if any(finding.get("severity") in ["CRITICAL", "HIGH"] for finding in findings_by_category.get(category, [])):
            risk_level = "🔴 HIGH RISK"
        elif any(finding.get("severity") == "MEDIUM" for finding in findings_by_category.get(category, [])):
            risk_level = "🟡 MEDIUM RISK"
        else:
            risk_level = "🟢 LOW RISK"
        
        analysis.append(f"- **{category}:** {count} findings ({severity_text}) - {risk_level}")
    
    return "\\n".join(analysis)

def generate_recommendations(analysis):
    """Generate security recommendations based on analysis."""
    recommendations = []
    
    severity_counts = analysis.get("severity_breakdown", analysis.get("severity_counts", {}))
    
    if severity_counts.get('CRITICAL', 0) > 0:
        recommendations.append("🚨 **IMMEDIATE ACTION REQUIRED:** Resolve all CRITICAL security issues before GA release")
    
    if severity_counts.get('HIGH', 0) > 2:
        recommendations.append("⚠️ **HIGH PRIORITY:** Address HIGH severity findings to meet GA security criteria")
    
    if analysis['security_score'] < 85:
        recommendations.append(f"📈 **IMPROVE SCORE:** Current score ({analysis['security_score']}) below GA threshold (85)")
    
    if analysis['files_with_issues'] / max(analysis['files_scanned'], 1) > 0.1:
        recommendations.append("🧹 **CODE CLEANUP:** High percentage of files contain security issues")
    
    if not recommendations:
        recommendations.append("✅ **SECURITY POSTURE EXCELLENT:** All GA security criteria met")
    
    return "\\n".join(recommendations)

def generate_detailed_findings(findings_by_category):
    """Generate detailed findings section.""" 
    if not findings_by_category:
        return "No detailed findings to report."
    
    details = []
    for category, findings in sorted(findings_by_category.items()):
        details.append(f"### {category}")
        details.append("")
        
        for finding in findings[:5]:  # Limit to first 5 findings per category
            severity_emoji = {"CRITICAL": "💀", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🔵"}.get(finding.get("severity"), "❓")
            details.append(f"- {severity_emoji} **{finding.get('rule_id')}:** {finding.get('description')}")
            details.append(f"  - File: `{finding.get('file', 'Unknown')}`")
            details.append(f"  - Line: {finding.get('line', 'N/A')}")
            details.append("")
        
        if len(findings) > 5:
            details.append(f"*... and {len(findings) - 5} more findings in this category*")
            details.append("")
    
    return "\\n".join(details)

def main():
    """Main entry point for security posture report generation."""
    repo_root = Path(__file__).parent.parent.absolute()
    
    print("WatchLockAI Sentinel Security Posture Assessment")
    print(f"Repository: {repo_root}")
    print()
    
    # Run security scan
    print("Running enhanced security scan...")
    success, findings_data = run_security_scan(repo_root)
    
    if not success:
        print(f"❌ Security scan failed: {findings_data.get('error', 'Unknown error')}")
        return 1
    
    print("✅ Security scan completed")
    
    # Analyze findings
    print("Analyzing security findings...")
    analysis = analyze_findings(findings_data)
    
    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return 1
    
    print(f"✅ Analysis completed - {analysis['total_findings']} findings, score: {analysis['security_score']}/100")
    print(f"Debug - Severity breakdown: {analysis.get('severity_breakdown', 'Missing')}")
    
    # Generate report
    output_path = repo_root / "DOCS" / "security" / "security_posture_rc1.md"
    
    print("Generating security posture report...")
    success = generate_security_posture_report(analysis, output_path)
    
    if success:
        print(f"✅ P6-003 Security Posture Report completed successfully")
        print(f"📄 Security Posture: {output_path}")
        print(f"🎯 Security Score: {analysis['security_score']}/100 ({analysis['posture_level']})")
        return 0
    else:
        print(f"❌ P6-003 Security Posture Report failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
