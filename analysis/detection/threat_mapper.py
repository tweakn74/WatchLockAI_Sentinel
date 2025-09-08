#!/usr/bin/env python3
"""
Threat Mapping Generator v4.0 - ATT&CK-style threat analysis
Part of Credits Overdrive v4.0 (Proof-Oriented, Fail-Closed)

Maps features/endpoints to lightweight ATT&CK-style threat matrix with:
- Threat vectors mapped to application features
- Mitigations and defensive measures
- Test artifacts and verification references
- Risk assessments and recommendations
"""

import json
import os
import re
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ThreatVector:
    """Represents a potential threat vector"""
    id: str
    name: str
    description: str
    tactics: List[str]  # ATT&CK-style tactics
    techniques: List[str]  # Specific attack techniques
    affected_endpoints: List[str]
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    likelihood: str  # 'unlikely', 'possible', 'likely', 'certain'

@dataclass
class Mitigation:
    """Represents a security mitigation"""
    id: str
    name: str
    description: str
    mitigation_type: str  # 'preventive', 'detective', 'corrective'
    implementation_status: str  # 'implemented', 'partial', 'planned', 'missing'
    effectiveness: str  # 'low', 'medium', 'high'
    coverage: List[str]  # Which threat vectors this mitigates

@dataclass
class TestArtifact:
    """Represents test artifacts that verify security"""
    id: str
    name: str
    artifact_type: str  # 'test', 'scenario', 'verification', 'monitoring'
    file_path: str
    description: str
    coverage: List[str]  # Which threats this tests

class ThreatMapper:
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.routing_atlas = self._load_routing_atlas()
        self.threat_vectors = []
        self.mitigations = []
        self.test_artifacts = []
        
        # Load existing security artifacts
        self._discover_security_artifacts()
        
        # Define threat vector templates
        self._initialize_threat_vectors()
        
        # Define mitigations
        self._initialize_mitigations()

    def _load_routing_atlas(self) -> Dict[str, Any]:
        """Load routing atlas for endpoint analysis"""
        atlas_path = os.path.join(self.repo_root, "DOCS", "report", "routing_atlas.json")
        try:
            with open(atlas_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  routing_atlas.json not found, using empty atlas")
            return {"route_groups": {}}

    def _discover_security_artifacts(self) -> None:
        """Discover existing security test artifacts"""
        print("🔍 Discovering security artifacts...")
        
        # Security test files
        test_patterns = [
            (r'test.*auth.*\.py$', 'authentication_test'),
            (r'test.*rbac.*\.py$', 'authorization_test'),
            (r'test.*security.*\.py$', 'security_test'),
            (r'test.*quarantine.*\.py$', 'quarantine_test'),
            (r'test.*anomaly.*\.py$', 'anomaly_test'),
            (r'test.*attack.*\.py$', 'attack_simulation'),
            (r'test.*fuzz.*\.py$', 'fuzzing_test'),
            (r'test.*unicode.*\.py$', 'encoding_test'),
        ]
        
        for root, dirs, files in os.walk(self.repo_root):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_root)
                
                for pattern, artifact_type in test_patterns:
                    if re.search(pattern, file, re.IGNORECASE):
                        artifact = TestArtifact(
                            id=f"test_{len(self.test_artifacts)}",
                            name=file.replace('.py', '').replace('test_', ''),
                            artifact_type=artifact_type,
                            file_path=rel_path,
                            description=f"Security test: {file}",
                            coverage=[]  # Will be populated during mapping
                        )
                        self.test_artifacts.append(artifact)
        
        # Security documentation
        security_docs = [
            "DOCS/security/sec_lint_report.md",
            "DOCS/security/security_posture_rc1.md",
            "DOCS/security/threat_model.md",
        ]
        
        for doc_path in security_docs:
            full_path = os.path.join(self.repo_root, doc_path)
            if os.path.exists(full_path):
                artifact = TestArtifact(
                    id=f"doc_{len(self.test_artifacts)}",
                    name=os.path.basename(doc_path).replace('.md', ''),
                    artifact_type='documentation',
                    file_path=doc_path,
                    description=f"Security documentation: {os.path.basename(doc_path)}",
                    coverage=[]
                )
                self.test_artifacts.append(artifact)
        
        print(f"   📊 Found {len(self.test_artifacts)} security artifacts")

    def _initialize_threat_vectors(self) -> None:
        """Initialize threat vector definitions"""
        # Extract endpoints from routing atlas
        endpoints = self._extract_endpoints()
        
        # Define threat vectors based on common attack patterns
        threat_definitions = [
            {
                "id": "T001",
                "name": "Authentication Bypass",
                "description": "Attempts to bypass authentication mechanisms to gain unauthorized access",
                "tactics": ["Initial Access", "Privilege Escalation"],
                "techniques": ["Credential Stuffing", "Session Hijacking", "Token Manipulation"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['auth', 'login', 'token'])],
                "risk_level": "high",
                "likelihood": "possible"
            },
            {
                "id": "T002", 
                "name": "Authorization Escalation",
                "description": "Attempts to escalate privileges or access resources beyond authorized scope",
                "tactics": ["Privilege Escalation", "Defense Evasion"],
                "techniques": ["RBAC Bypass", "Admin Impersonation", "Role Confusion"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['admin', 'config', 'manage'])],
                "risk_level": "high",
                "likelihood": "possible"
            },
            {
                "id": "T003",
                "name": "Input Validation Bypass",
                "description": "Exploitation of insufficient input validation to inject malicious data",
                "tactics": ["Execution", "Persistence"],
                "techniques": ["SQL Injection", "Command Injection", "Path Traversal", "XSS"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['api', 'upload', 'search', 'query'])],
                "risk_level": "high", 
                "likelihood": "likely"
            },
            {
                "id": "T004",
                "name": "File System Manipulation",
                "description": "Unauthorized access or modification of file system resources",
                "tactics": ["Impact", "Exfiltration"],
                "techniques": ["Directory Traversal", "File Upload Abuse", "Symlink Attack"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['upload', 'file', 'backup', 'restore'])],
                "risk_level": "medium",
                "likelihood": "possible"
            },
            {
                "id": "T005",
                "name": "Information Disclosure",
                "description": "Unauthorized access to sensitive information through various vectors",
                "tactics": ["Collection", "Exfiltration"],
                "techniques": ["Error Message Exploitation", "Debug Info Leakage", "Timing Attacks"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['status', 'health', 'metrics', 'debug'])],
                "risk_level": "medium",
                "likelihood": "likely"
            },
            {
                "id": "T006",
                "name": "Denial of Service",
                "description": "Attempts to disrupt service availability through resource exhaustion",
                "tactics": ["Impact"],
                "techniques": ["Resource Exhaustion", "Algorithmic Complexity", "Memory Exhaustion"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['api', 'upload', 'process'])],
                "risk_level": "medium",
                "likelihood": "possible"
            },
            {
                "id": "T007",
                "name": "Configuration Manipulation",
                "description": "Unauthorized modification of application or system configuration",
                "tactics": ["Persistence", "Defense Evasion"],
                "techniques": ["Config Injection", "Feature Flag Abuse", "Setting Tampering"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['config', 'setting', 'reload'])],
                "risk_level": "high",
                "likelihood": "unlikely"
            },
            {
                "id": "T008",
                "name": "Data Exfiltration",
                "description": "Unauthorized extraction of sensitive data from the system",
                "tactics": ["Exfiltration"],
                "techniques": ["API Abuse", "Bulk Download", "Telemetry Exploitation"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['export', 'download', 'telemetry', 'data'])],
                "risk_level": "high",
                "likelihood": "possible"
            },
            {
                "id": "T009",
                "name": "Quarantine Bypass",
                "description": "Attempts to bypass quarantine mechanisms and access restricted resources",
                "tactics": ["Defense Evasion", "Impact"],
                "techniques": ["Path Manipulation", "Symlink Abuse", "Container Escape"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['quarantine', 'restore', 'file'])],
                "risk_level": "critical",
                "likelihood": "unlikely"
            },
            {
                "id": "T010",
                "name": "Anomaly Detection Evasion",
                "description": "Attempts to evade anomaly detection systems and security monitoring",
                "tactics": ["Defense Evasion"],
                "techniques": ["Behavior Mimicry", "Gradual Escalation", "Detection Poisoning"],
                "affected_endpoints": [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['anomaly', 'metrics', 'train'])],
                "risk_level": "medium",
                "likelihood": "unlikely"
            }
        ]
        
        # Convert to ThreatVector objects
        for threat_def in threat_definitions:
            vector = ThreatVector(**threat_def)
            self.threat_vectors.append(vector)

    def _initialize_mitigations(self) -> None:
        """Initialize mitigation definitions"""
        mitigation_definitions = [
            {
                "id": "M001",
                "name": "Authentication Framework",
                "description": "Robust authentication system with token validation and session management",
                "mitigation_type": "preventive",
                "implementation_status": "implemented",
                "effectiveness": "high",
                "coverage": ["T001", "T002"]
            },
            {
                "id": "M002",
                "name": "Role-Based Access Control (RBAC)",
                "description": "Fine-grained permission system with role separation and privilege checks",
                "mitigation_type": "preventive", 
                "implementation_status": "implemented",
                "effectiveness": "high",
                "coverage": ["T002", "T007"]
            },
            {
                "id": "M003",
                "name": "Input Validation Framework",
                "description": "Comprehensive input sanitization and validation at API boundaries",
                "mitigation_type": "preventive",
                "implementation_status": "partial",
                "effectiveness": "medium",
                "coverage": ["T003", "T004"]
            },
            {
                "id": "M004",
                "name": "Quarantine System",
                "description": "Isolated environment for file operations and potentially dangerous activities", 
                "mitigation_type": "preventive",
                "implementation_status": "implemented",
                "effectiveness": "high",
                "coverage": ["T004", "T009"]
            },
            {
                "id": "M005",
                "name": "Rate Limiting",
                "description": "Request rate limiting to prevent abuse and resource exhaustion",
                "mitigation_type": "preventive",
                "implementation_status": "partial",
                "effectiveness": "medium", 
                "coverage": ["T006", "T008"]
            },
            {
                "id": "M006",
                "name": "Error Handling",
                "description": "Secure error handling that prevents information disclosure",
                "mitigation_type": "preventive",
                "implementation_status": "implemented",
                "effectiveness": "medium",
                "coverage": ["T005"]
            },
            {
                "id": "M007",
                "name": "Anomaly Detection",
                "description": "Machine learning-based anomaly detection for unusual behavior patterns",
                "mitigation_type": "detective",
                "implementation_status": "implemented",
                "effectiveness": "medium",
                "coverage": ["T001", "T002", "T006", "T008"]
            },
            {
                "id": "M008",
                "name": "Security Monitoring",
                "description": "Comprehensive logging and monitoring of security events",
                "mitigation_type": "detective",
                "implementation_status": "implemented", 
                "effectiveness": "medium",
                "coverage": ["T001", "T002", "T005", "T007", "T008", "T009"]
            },
            {
                "id": "M009",
                "name": "Configuration Protection",
                "description": "Protected configuration management with change auditing",
                "mitigation_type": "preventive",
                "implementation_status": "implemented",
                "effectiveness": "high",
                "coverage": ["T007"]
            },
            {
                "id": "M010",
                "name": "Security Testing Suite",
                "description": "Comprehensive security testing including fuzzing and attack simulation",
                "mitigation_type": "preventive",
                "implementation_status": "implemented",
                "effectiveness": "high",
                "coverage": ["T001", "T002", "T003", "T004", "T005", "T006", "T007", "T008", "T009", "T010"]
            }
        ]
        
        # Convert to Mitigation objects
        for mitigation_def in mitigation_definitions:
            mitigation = Mitigation(**mitigation_def)
            self.mitigations.append(mitigation)

    def _extract_endpoints(self) -> List[str]:
        """Extract all endpoints from routing atlas"""
        endpoints = []
        for group_path, routes in self.routing_atlas.get("route_groups", {}).items():
            for route in routes:
                method = route.get("method", "GET")
                path = route.get("path", "/")
                endpoints.append(f"{method} {path}")
        return endpoints

    def generate_threat_map(self) -> None:
        """Generate comprehensive threat mapping"""
        print("🗺️  Generating threat mapping...")
        
        # Map test artifacts to threat coverage
        self._map_test_coverage()
        
        # Generate threat matrix
        self._generate_threat_matrix()
        
        print("✅ Threat mapping complete")

    def _map_test_coverage(self) -> None:
        """Map test artifacts to threat vector coverage"""
        # Define mappings between test artifacts and threats
        coverage_mappings = {
            'auth': ['T001', 'T002'],
            'rbac': ['T002'],
            'security': ['T001', 'T002', 'T003', 'T005'],
            'quarantine': ['T004', 'T009'],
            'anomaly': ['T007', 'T010'],
            'attack': ['T001', 'T002', 'T003', 'T006'],
            'fuzz': ['T003', 'T004', 'T006'],
            'unicode': ['T003', 'T005'],
        }
        
        # Update test artifact coverage
        for artifact in self.test_artifacts:
            for keyword, threats in coverage_mappings.items():
                if keyword in artifact.name.lower():
                    artifact.coverage.extend(threats)
                    # Remove duplicates
                    artifact.coverage = list(set(artifact.coverage))

    def _generate_threat_matrix(self) -> None:
        """Generate the main threat mapping document"""
        print("📄 Generating threat matrix document...")
        
        # Calculate coverage statistics
        coverage_stats = self._calculate_coverage_stats()
        
        report_content = f"""# Threat-Informed Security Mapping v4.0

**Generated:** 2025-09-07  
**Framework:** Credits Overdrive v4.0 Threat Mapper  
**Repository:** WatchLockAI Sentinel

## Executive Summary

This document maps application features and endpoints to potential threat vectors using a lightweight ATT&CK-style framework. Each threat is analyzed with corresponding mitigations, test coverage, and risk assessments.

### Risk Profile

| Risk Level | Threat Count | Coverage | Status |
|------------|--------------|----------|--------|
| **Critical** | {coverage_stats['critical']['count']} | {coverage_stats['critical']['coverage']:.1f}% | {'✅ Covered' if coverage_stats['critical']['coverage'] >= 80 else '⚠️ Needs Attention'} |
| **High** | {coverage_stats['high']['count']} | {coverage_stats['high']['coverage']:.1f}% | {'✅ Covered' if coverage_stats['high']['coverage'] >= 80 else '⚠️ Needs Attention'} |
| **Medium** | {coverage_stats['medium']['count']} | {coverage_stats['medium']['coverage']:.1f}% | {'✅ Covered' if coverage_stats['medium']['coverage'] >= 70 else '⚠️ Needs Attention'} |
| **Low** | {coverage_stats['low']['count']} | {coverage_stats['low']['coverage']:.1f}% | ✅ Acceptable |

### Mitigation Effectiveness

| Type | Count | Avg Effectiveness | Implementation |
|------|-------|-------------------|----------------|
| **Preventive** | {len([m for m in self.mitigations if m.mitigation_type == 'preventive'])} | {self._avg_effectiveness('preventive')} | {self._implementation_summary('preventive')} |
| **Detective** | {len([m for m in self.mitigations if m.mitigation_type == 'detective'])} | {self._avg_effectiveness('detective')} | {self._implementation_summary('detective')} |
| **Corrective** | {len([m for m in self.mitigations if m.mitigation_type == 'corrective'])} | {self._avg_effectiveness('corrective')} | {self._implementation_summary('corrective')} |

## Threat Vector Analysis

"""
        
        # Group threats by risk level
        for risk_level in ['critical', 'high', 'medium', 'low']:
            threats = [t for t in self.threat_vectors if t.risk_level == risk_level]
            if threats:
                report_content += f"### {risk_level.title()} Risk Threats\n\n"
                
                for threat in threats:
                    mitigations = [m for m in self.mitigations if threat.id in m.coverage]
                    tests = [t for t in self.test_artifacts if threat.id in t.coverage]
                    
                    report_content += f"""#### {threat.id}: {threat.name}

**Description:** {threat.description}

**Attack Surface:**
- **Tactics:** {', '.join(threat.tactics)}
- **Techniques:** {', '.join(threat.techniques)}
- **Likelihood:** {threat.likelihood.title()}
- **Affected Endpoints:** {len(threat.affected_endpoints)} endpoints

**Mitigations:**
"""
                    for mitigation in mitigations:
                        status_icon = {
                            'implemented': '✅',
                            'partial': '🔶',
                            'planned': '📋',
                            'missing': '❌'
                        }.get(mitigation.implementation_status, '❓')
                        
                        report_content += f"- {status_icon} **{mitigation.name}** ({mitigation.effectiveness} effectiveness)\n"
                    
                    if not mitigations:
                        report_content += "- ⚠️ No specific mitigations identified\n"
                    
                    report_content += f"""
**Test Coverage:**
"""
                    for test in tests:
                        report_content += f"- 🧪 `{test.file_path}` - {test.description}\n"
                    
                    if not tests:
                        report_content += "- ⚠️ No specific test coverage identified\n"
                    
                    report_content += "\n---\n\n"
        
        # Endpoint-specific analysis
        report_content += "## Endpoint Security Analysis\n\n"
        
        # Group endpoints by risk
        endpoint_risks = self._analyze_endpoint_risks()
        
        for risk_level in ['critical', 'high', 'medium']:
            endpoints = endpoint_risks.get(risk_level, [])
            if endpoints:
                report_content += f"### {risk_level.title()} Risk Endpoints\n\n"
                for endpoint, threats in endpoints[:10]:  # Top 10
                    report_content += f"- **{endpoint}** - Threats: {', '.join(threats)}\n"
                report_content += "\n"
        
        # Security test matrix
        report_content += "## Security Test Matrix\n\n"
        report_content += "| Test Artifact | Type | Coverage | Threats Tested |\n"
        report_content += "|---------------|------|----------|----------------|\n"
        
        for artifact in sorted(self.test_artifacts, key=lambda x: len(x.coverage), reverse=True):
            coverage_pct = (len(artifact.coverage) / len(self.threat_vectors)) * 100 if self.threat_vectors else 0
            threats_str = ', '.join(artifact.coverage[:5])  # First 5 threats
            if len(artifact.coverage) > 5:
                threats_str += f" (+{len(artifact.coverage) - 5} more)"
            
            report_content += f"| `{artifact.file_path}` | {artifact.artifact_type} | {coverage_pct:.1f}% | {threats_str} |\n"
        
        # Recommendations
        report_content += """
## Recommendations

### Immediate Actions (Critical/High Risk)
"""
        
        critical_high_threats = [t for t in self.threat_vectors if t.risk_level in ['critical', 'high']]
        uncovered_threats = []
        
        for threat in critical_high_threats:
            mitigations = [m for m in self.mitigations if threat.id in m.coverage and m.implementation_status == 'implemented']
            tests = [t for t in self.test_artifacts if threat.id in t.coverage]
            
            if not mitigations or not tests:
                uncovered_threats.append(threat)
        
        if uncovered_threats:
            for threat in uncovered_threats[:5]:  # Top 5
                report_content += f"1. **{threat.name} ({threat.id})** - {threat.likelihood} likelihood, needs immediate attention\n"
        else:
            report_content += "✅ All critical and high-risk threats have adequate coverage\n"
        
        report_content += """
### Medium-Term Improvements
1. **Enhance Input Validation** - Strengthen validation framework for better T003 coverage
2. **Improve Rate Limiting** - Implement comprehensive rate limiting across all endpoints
3. **Expand Security Testing** - Add more edge case and boundary testing
4. **Monitoring Enhancement** - Improve detection capabilities for evasion techniques

### Continuous Monitoring
- Regular threat model reviews (quarterly)
- Security test coverage analysis (monthly)
- Mitigation effectiveness assessment (bi-annually)
- Endpoint risk re-evaluation after major changes

## ATT&CK Mapping

| Threat ID | ATT&CK Tactics | Primary Techniques | Mitigation Strategy |
|-----------|----------------|-------------------|-------------------|
"""
        
        for threat in self.threat_vectors:
            primary_technique = threat.techniques[0] if threat.techniques else "N/A"
            mitigations = [m.name for m in self.mitigations if threat.id in m.coverage]
            mitigation_str = ', '.join(mitigations[:2])  # First 2 mitigations
            if len(mitigations) > 2:
                mitigation_str += f" (+{len(mitigations) - 2})"
            
            report_content += f"| {threat.id} | {', '.join(threat.tactics)} | {primary_technique} | {mitigation_str} |\n"
        
        report_content += """

---
*Generated by Credits Overdrive v4.0 - Threat Mapper*  
*Use tools/threat_mapper.py to regenerate this analysis*
"""
        
        # Save the report
        output_path = os.path.join(self.repo_root, "DOCS", "security", "threat_map.md")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Threat map: {output_path}")

    def _calculate_coverage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Calculate coverage statistics by risk level"""
        stats = {}
        
        for risk_level in ['critical', 'high', 'medium', 'low']:
            threats = [t for t in self.threat_vectors if t.risk_level == risk_level]
            covered_threats = []
            
            for threat in threats:
                mitigations = [m for m in self.mitigations if threat.id in m.coverage]
                tests = [t for t in self.test_artifacts if threat.id in t.coverage]
                
                # Consider covered if has both mitigations and tests
                if mitigations and tests:
                    covered_threats.append(threat)
            
            coverage_pct = (len(covered_threats) / len(threats)) * 100 if threats else 0
            
            stats[risk_level] = {
                'count': len(threats),
                'covered': len(covered_threats),
                'coverage': coverage_pct
            }
        
        return stats

    def _avg_effectiveness(self, mitigation_type: str) -> str:
        """Calculate average effectiveness for mitigation type"""
        mitigations = [m for m in self.mitigations if m.mitigation_type == mitigation_type]
        if not mitigations:
            return "N/A"
        
        effectiveness_values = {'low': 1, 'medium': 2, 'high': 3}
        total = sum(effectiveness_values.get(m.effectiveness, 2) for m in mitigations)
        avg = total / len(mitigations)
        
        if avg >= 2.5:
            return "High"
        elif avg >= 1.5:
            return "Medium"
        else:
            return "Low"

    def _implementation_summary(self, mitigation_type: str) -> str:
        """Get implementation summary for mitigation type"""
        mitigations = [m for m in self.mitigations if m.mitigation_type == mitigation_type]
        if not mitigations:
            return "N/A"
        
        implemented = len([m for m in mitigations if m.implementation_status == 'implemented'])
        total = len(mitigations)
        
        percentage = (implemented / total) * 100
        return f"{implemented}/{total} ({percentage:.0f}%)"

    def _analyze_endpoint_risks(self) -> Dict[str, List[Tuple[str, List[str]]]]:
        """Analyze risk levels for each endpoint"""
        endpoint_risks = {'critical': [], 'high': [], 'medium': [], 'low': []}
        
        # Get all endpoints
        endpoints = self._extract_endpoints()
        
        for endpoint in endpoints:
            # Find threats that affect this endpoint
            affecting_threats = []
            max_risk = 'low'
            
            for threat in self.threat_vectors:
                if endpoint in threat.affected_endpoints:
                    affecting_threats.append(threat.id)
                    
                    # Track highest risk level
                    if threat.risk_level == 'critical':
                        max_risk = 'critical'
                    elif threat.risk_level == 'high' and max_risk not in ['critical']:
                        max_risk = 'high'
                    elif threat.risk_level == 'medium' and max_risk not in ['critical', 'high']:
                        max_risk = 'medium'
            
            if affecting_threats:
                endpoint_risks[max_risk].append((endpoint, affecting_threats))
        
        return endpoint_risks


def main():
    """Main execution function"""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    print("🗺️  Starting Threat Mapping v4.0...")
    print(f"📁 Repository: {repo_root}")
    
    mapper = ThreatMapper(repo_root)
    mapper.generate_threat_map()
    
    print("\n🎉 P18 Complete: Threat Mapping Ready!")
    print("📋 Report generated:")
    print("   - DOCS/security/threat_map.md")


if __name__ == "__main__":
    main()
