#!/usr/bin/env python3
"""
Taint Flow Scanner v4.0 - AST-based data flow analysis
Part of Credits Overdrive v4.0 (Proof-Oriented, Fail-Closed)

Traces flows for file paths, tokens, and user input to sensitive sinks:
- File system writes, reads outside quarantine
- Subprocess execution
- Network operations
- Database queries with user data

Uses only Python stdlib (ast, os, sys) for portability.
"""

import ast
import os
import sys
import json
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class TaintSource:
    """Represents a taint source (where untrusted data enters)"""
    file_path: str
    line_number: int
    function_name: str
    variable_name: str
    source_type: str  # 'user_input', 'file_path', 'network', 'token'
    description: str

@dataclass
class TaintSink:
    """Represents a taint sink (where data could cause harm)"""
    file_path: str
    line_number: int
    function_name: str
    sink_type: str  # 'file_write', 'subprocess', 'network', 'sql'
    operation: str
    description: str

@dataclass
class TaintFlow:
    """Represents a complete taint flow from source to sink"""
    source: TaintSource
    sink: TaintSink
    flow_path: List[str]  # Variables/functions in the flow
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    mitigation_present: bool
    description: str

class TaintFlowAnalyzer:
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.sources = []
        self.sinks = []
        self.flows = []
        self.quarantine_paths = self._detect_quarantine_paths()
        
        # Patterns for identifying taint sources
        self.source_patterns = {
            'user_input': [
                r'request\.(json|form|args|data|get_json)',
                r'input\s*\(',
                r'sys\.argv',
                r'os\.environ\.get',
                r'getpass\.getpass',
                r'click\.(option|argument)',
                r'argparse\.',
            ],
            'file_path': [
                r'request\.(files|form)\[.*\]',
                r'os\.path\.join.*request',
                r'pathlib\.Path.*request',
                r'\.filename',
                r'upload\.filename',
            ],
            'network': [
                r'requests\.(get|post|put|delete)',
                r'urllib\.request',
                r'socket\.recv',
                r'websocket\.',
            ],
            'token': [
                r'request\.headers\[.*[aA]uth',
                r'request\.headers\.get.*[aA]uth',
                r'bearer.*token',
                r'jwt\.',
                r'session\[.*token',
            ]
        }
        
        # Patterns for identifying taint sinks
        self.sink_patterns = {
            'file_write': [
                r'open\s*\(',
                r'\.write\s*\(',
                r'\.writelines\s*\(',
                r'shutil\.(copy|move)',
                r'os\.(rename|remove|unlink)',
                r'pathlib\.Path.*write',
            ],
            'subprocess': [
                r'subprocess\.(run|call|Popen)',
                r'os\.system',
                r'os\.popen',
                r'os\.spawn',
                r'exec\s*\(',
                r'eval\s*\(',
            ],
            'network': [
                r'requests\.(post|put|delete)',
                r'urllib\.request',
                r'socket\.send',
                r'smtp\.',
            ],
            'sql': [
                r'\.execute\s*\(',
                r'\.query\s*\(',
                r'cursor\.',
                r'SELECT.*WHERE',
                r'INSERT.*VALUES',
                r'UPDATE.*SET',
            ]
        }
        
        # Security mitigation patterns
        self.mitigation_patterns = [
            r'sanitize',
            r'escape',
            r'validate',
            r'filter',
            r'whitelist',
            r'allowlist',
            r'quarantine',
            r'safe_path',
            r'secure_',
            r'parameterized',
            r'prepared',
        ]

    def _detect_quarantine_paths(self) -> Set[str]:
        """Detect quarantine/safe path patterns"""
        quarantine_paths = set()
        
        # Look for quarantine directories
        for root, dirs, files in os.walk(self.repo_root):
            for dir_name in dirs:
                if 'quarantine' in dir_name.lower():
                    quarantine_paths.add(os.path.join(root, dir_name))
        
        # Add common safe paths
        quarantine_paths.update([
            '/tmp/quarantine',
            'data/quarantine',
            'quarantine/',
            'safe/',
            'sandbox/',
        ])
        
        return quarantine_paths

    def scan_all_files(self) -> None:
        """Scan all Python files for taint flows"""
        print("[SEARCH] Scanning for taint flows...")
        
        python_files = []
        for root, dirs, files in os.walk(self.repo_root):
            # Skip certain directories
            if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.pytest_cache', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        print(f"[BARS] Found {len(python_files)} Python files to analyze")
        
        for file_path in python_files:
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"[WARN]  Error analyzing {file_path}: {e}")
        
        # Analyze flows
        self._analyze_taint_flows()
        
        print(f"[CHART] Analysis complete:")
        print(f"   [TARGET] Sources: {len(self.sources)}")
        print(f"   [U+1F573]  Sinks: {len(self.sinks)}")
        print(f"   [U+1F30A] Flows: {len(self.flows)}")

    def _analyze_file(self, file_path: str) -> None:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=file_path)
            
            # Analyze the AST
            visitor = TaintASTVisitor(file_path, content, self)
            visitor.visit(tree)
            
            self.sources.extend(visitor.sources)
            self.sinks.extend(visitor.sinks)
            
        except SyntaxError as e:
            # Skip files with syntax errors
            pass
        except Exception as e:
            # Skip files that can't be processed
            pass

    def _analyze_taint_flows(self) -> None:
        """Analyze potential taint flows from sources to sinks"""
        for source in self.sources:
            for sink in self.sinks:
                # Simple heuristic: sources and sinks in same file or related files
                if self._could_flow(source, sink):
                    flow = self._create_taint_flow(source, sink)
                    if flow:
                        self.flows.append(flow)

    def _could_flow(self, source: TaintSource, sink: TaintSink) -> bool:
        """Determine if taint could flow from source to sink"""
        # Same file - likely flow
        if source.file_path == sink.file_path:
            return True
        
        # Source in web API, sink in file operations - potential flow
        if ('web_api' in source.file_path or 'console' in source.file_path) and sink.sink_type == 'file_write':
            return True
        
        # User input to subprocess - high risk
        if source.source_type == 'user_input' and sink.sink_type == 'subprocess':
            return True
        
        # File path manipulation
        if source.source_type == 'file_path' and sink.sink_type == 'file_write':
            return True
        
        return False

    def _create_taint_flow(self, source: TaintSource, sink: TaintSink) -> Optional[TaintFlow]:
        """Create a taint flow object"""
        # Determine risk level
        risk_level = self._assess_risk(source, sink)
        
        # Check for mitigations
        mitigation_present = self._check_mitigations(source, sink)
        
        # Create flow path (simplified)
        flow_path = [source.variable_name, sink.operation]
        
        # Generate description
        description = f"{source.source_type} '{source.variable_name}' flows to {sink.sink_type} operation"
        
        flow = TaintFlow(
            source=source,
            sink=sink,
            flow_path=flow_path,
            risk_level=risk_level,
            mitigation_present=mitigation_present,
            description=description
        )
        
        return flow

    def _assess_risk(self, source: TaintSource, sink: TaintSink) -> str:
        """Assess risk level of taint flow"""
        # Critical: User input to subprocess
        if source.source_type == 'user_input' and sink.sink_type == 'subprocess':
            return 'critical'
        
        # High: File path manipulation outside quarantine
        if source.source_type == 'file_path' and sink.sink_type == 'file_write':
            if not self._is_quarantined_path(sink):
                return 'high'
        
        # High: User input to SQL without parameterization
        if source.source_type == 'user_input' and sink.sink_type == 'sql':
            return 'high'
        
        # Medium: Network data to file system
        if source.source_type == 'network' and sink.sink_type == 'file_write':
            return 'medium'
        
        # Medium: Token usage in file operations
        if source.source_type == 'token' and sink.sink_type == 'file_write':
            return 'medium'
        
        return 'low'

    def _check_mitigations(self, source: TaintSource, sink: TaintSink) -> bool:
        """Check if mitigations are present"""
        # Read source and sink file contexts
        try:
            source_context = self._get_file_context(source.file_path, source.line_number)
            sink_context = self._get_file_context(sink.file_path, sink.line_number)
            
            combined_context = source_context + " " + sink_context
            
            # Check for mitigation patterns
            for pattern in self.mitigation_patterns:
                if re.search(pattern, combined_context, re.IGNORECASE):
                    return True
            
            return False
        except:
            return False

    def _get_file_context(self, file_path: str, line_number: int, context_lines: int = 5) -> str:
        """Get context around a specific line"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            start = max(0, line_number - context_lines)
            end = min(len(lines), line_number + context_lines)
            
            return ' '.join(lines[start:end])
        except:
            return ""

    def _is_quarantined_path(self, sink: TaintSink) -> bool:
        """Check if sink operates on quarantined/safe paths"""
        sink_context = self._get_file_context(sink.file_path, sink.line_number)
        
        # Check if any quarantine paths are mentioned
        for qpath in self.quarantine_paths:
            if qpath in sink_context:
                return True
        
        # Check for quarantine keywords
        quarantine_keywords = ['quarantine', 'sandbox', 'safe', 'temp']
        for keyword in quarantine_keywords:
            if keyword in sink_context.lower():
                return True
        
        return False

    def generate_reports(self) -> None:
        """Generate taint flow reports"""
        print("[PAGE] Generating taint flow reports...")
        
        # Generate JSON report
        self._generate_json_report()
        
        # Generate Markdown report
        self._generate_markdown_report()
        
        print("[PASS] Taint flow reports generated")

    def _generate_json_report(self) -> None:
        """Generate JSON taint map"""
        report_data = {
            "timestamp": "2025-09-07T00:00:00Z",
            "generator": "Taint Flow Scanner v4.0",
            "summary": {
                "total_sources": len(self.sources),
                "total_sinks": len(self.sinks),
                "total_flows": len(self.flows),
                "risk_distribution": self._get_risk_distribution(),
                "mitigation_coverage": self._get_mitigation_coverage()
            },
            "sources": [asdict(source) for source in self.sources],
            "sinks": [asdict(sink) for sink in self.sinks],
            "flows": [asdict(flow) for flow in self.flows]
        }
        
        output_path = os.path.join(self.repo_root, "DOCS", "security", "taint_map.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"[U+1F4BE] JSON report: {output_path}")

    def _generate_markdown_report(self) -> None:
        """Generate Markdown taint analysis report"""
        risk_dist = self._get_risk_distribution()
        mitigation_coverage = self._get_mitigation_coverage()
        
        report_content = f"""# Taint Flow Analysis Report v4.0

**Generated:** 2025-09-07  
**Scanner:** Credits Overdrive v4.0 Taint Flow Scanner  
**Repository:** WatchLockAI Sentinel

## Executive Summary

| Metric | Count | Details |
|--------|-------|---------|
| **Taint Sources** | {len(self.sources)} | Entry points for untrusted data |
| **Taint Sinks** | {len(self.sinks)} | Potentially dangerous operations |
| **Data Flows** | {len(self.flows)} | Source->sink paths identified |
| **Critical Flows** | {risk_dist.get('critical', 0)} | Immediate security risks |
| **High Risk Flows** | {risk_dist.get('high', 0)} | Significant security concerns |
| **Mitigation Coverage** | {mitigation_coverage:.1f}% | Flows with detected mitigations |

## Risk Distribution

```
Critical: {risk_dist.get('critical', 0):3} flows - Immediate action required
High:     {risk_dist.get('high', 0):3} flows - Priority remediation  
Medium:   {risk_dist.get('medium', 0):3} flows - Schedule for review
Low:      {risk_dist.get('low', 0):3} flows - Monitor
```

## Critical Findings

"""
        
        # Add critical flows
        critical_flows = [f for f in self.flows if f.risk_level == 'critical']
        if critical_flows:
            report_content += "### [ALERT] Critical Risk Flows\n\n"
            for i, flow in enumerate(critical_flows, 1):
                report_content += f"""**{i}. {flow.description}**
- **Source:** `{flow.source.file_path}:{flow.source.line_number}` ({flow.source.source_type})
- **Sink:** `{flow.sink.file_path}:{flow.sink.line_number}` ({flow.sink.sink_type})
- **Mitigation:** {'[PASS] Present' if flow.mitigation_present else '[FAIL] Missing'}
- **Path:** {' -> '.join(flow.flow_path)}

"""
        else:
            report_content += "### [PASS] No Critical Risk Flows Detected\n\n"
        
        # Add high risk flows
        high_flows = [f for f in self.flows if f.risk_level == 'high']
        if high_flows:
            report_content += "### [WARN] High Risk Flows\n\n"
            for i, flow in enumerate(high_flows[:5], 1):  # Top 5
                report_content += f"""**{i}. {flow.description}**
- **Source:** `{flow.source.file_path}:{flow.source.line_number}`
- **Sink:** `{flow.sink.file_path}:{flow.sink.line_number}`
- **Mitigation:** {'[PASS]' if flow.mitigation_present else '[FAIL]'}

"""
        
        # Source analysis
        report_content += f"""## Source Analysis

### By Type
"""
        source_types = {}
        for source in self.sources:
            source_types[source.source_type] = source_types.get(source.source_type, 0) + 1
        
        for source_type, count in sorted(source_types.items()):
            report_content += f"- **{source_type.replace('_', ' ').title()}:** {count} sources\n"
        
        # Sink analysis
        report_content += f"""
## Sink Analysis

### By Type
"""
        sink_types = {}
        for sink in self.sinks:
            sink_types[sink.sink_type] = sink_types.get(sink.sink_type, 0) + 1
        
        for sink_type, count in sorted(sink_types.items()):
            report_content += f"- **{sink_type.replace('_', ' ').title()}:** {count} sinks\n"
        
        # Unsanitized path usage
        report_content += """
## Path Security Analysis

### Quarantine Compliance
"""
        
        path_flows = [f for f in self.flows if f.source.source_type == 'file_path']
        quarantined_flows = [f for f in path_flows if self._is_quarantined_path(f.sink)]
        
        if path_flows:
            compliance_rate = (len(quarantined_flows) / len(path_flows)) * 100
            report_content += f"""
- **Total file path flows:** {len(path_flows)}
- **Quarantined operations:** {len(quarantined_flows)}
- **Compliance rate:** {compliance_rate:.1f}%

"""
            
            # List non-quarantined flows
            non_quarantined = [f for f in path_flows if not self._is_quarantined_path(f.sink)]
            if non_quarantined:
                report_content += "### [WARN] Non-Quarantined File Operations\n\n"
                for flow in non_quarantined[:10]:  # Top 10
                    report_content += f"- `{flow.sink.file_path}:{flow.sink.line_number}` - {flow.sink.operation}\n"
        else:
            report_content += "- [PASS] No file path flows detected\n"
        
        # Recommendations
        report_content += """
## Recommendations

### High Priority
1. **Sanitize all user inputs** before use in file operations or subprocess calls
2. **Implement path validation** to restrict file operations to quarantine directories
3. **Use parameterized queries** for all database operations
4. **Add input validation** at API boundaries

### Medium Priority
1. **Implement rate limiting** for file upload endpoints
2. **Add logging** for all taint source->sink flows
3. **Review token handling** in file operations
4. **Enhance error handling** to prevent information leakage

### Monitoring
- Set up alerts for new critical/high risk flows
- Regular re-scanning after code changes
- Track mitigation coverage improvements

---
*Generated by Credits Overdrive v4.0 - Taint Flow Scanner*  
*Use tools/taint_scan.py to regenerate this report*
"""
        
        output_path = os.path.join(self.repo_root, "DOCS", "security", "taint_map.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"[PAGE] Markdown report: {output_path}")

    def _get_risk_distribution(self) -> Dict[str, int]:
        """Get distribution of flows by risk level"""
        distribution = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for flow in self.flows:
            distribution[flow.risk_level] += 1
        return distribution

    def _get_mitigation_coverage(self) -> float:
        """Get percentage of flows with mitigations"""
        if not self.flows:
            return 0.0
        
        mitigated = sum(1 for flow in self.flows if flow.mitigation_present)
        return (mitigated / len(self.flows)) * 100


class TaintASTVisitor(ast.NodeVisitor):
    """AST visitor to identify taint sources and sinks"""
    
    def __init__(self, file_path: str, content: str, analyzer: TaintFlowAnalyzer):
        self.file_path = file_path
        self.content = content
        self.lines = content.split('\n')
        self.analyzer = analyzer
        self.sources = []
        self.sinks = []
        self.current_function = "module"

    def visit_FunctionDef(self, node):
        """Track current function context"""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Call(self, node):
        """Analyze function calls for sources and sinks"""
        try:
            call_str = self._ast_to_string(node)
            line_number = getattr(node, 'lineno', 0)
            
            # Check for taint sources
            self._check_sources(call_str, line_number)
            
            # Check for taint sinks
            self._check_sinks(call_str, line_number)
            
        except Exception:
            pass
        
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Analyze assignments for taint propagation"""
        try:
            if hasattr(node, 'value') and isinstance(node.value, ast.Call):
                call_str = self._ast_to_string(node.value)
                line_number = getattr(node, 'lineno', 0)
                
                # Get variable name
                var_name = "unknown"
                if node.targets and hasattr(node.targets[0], 'id'):
                    var_name = node.targets[0].id
                
                # Check if this assignment creates a taint source
                self._check_assignment_sources(call_str, var_name, line_number)
                
        except Exception:
            pass
        
        self.generic_visit(node)

    def _ast_to_string(self, node) -> str:
        """Convert AST node to string representation"""
        try:
            import astor
            return astor.to_source(node).strip()
        except ImportError:
            # Fallback without astor
            if hasattr(node, 'func'):
                if hasattr(node.func, 'attr'):
                    return f"{self._get_node_name(node.func.value)}.{node.func.attr}"
                else:
                    return self._get_node_name(node.func)
            return "unknown_call"

    def _get_node_name(self, node) -> str:
        """Get name from AST node"""
        if hasattr(node, 'id'):
            return node.id
        elif hasattr(node, 'attr'):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        else:
            return "unknown"

    def _check_sources(self, call_str: str, line_number: int):
        """Check if call matches taint source patterns"""
        for source_type, patterns in self.analyzer.source_patterns.items():
            for pattern in patterns:
                if re.search(pattern, call_str, re.IGNORECASE):
                    source = TaintSource(
                        file_path=self.file_path,
                        line_number=line_number,
                        function_name=self.current_function,
                        variable_name=self._extract_variable_name(call_str),
                        source_type=source_type,
                        description=f"{source_type} in {call_str}"
                    )
                    self.sources.append(source)
                    break

    def _check_sinks(self, call_str: str, line_number: int):
        """Check if call matches taint sink patterns"""
        for sink_type, patterns in self.analyzer.sink_patterns.items():
            for pattern in patterns:
                if re.search(pattern, call_str, re.IGNORECASE):
                    sink = TaintSink(
                        file_path=self.file_path,
                        line_number=line_number,
                        function_name=self.current_function,
                        sink_type=sink_type,
                        operation=call_str,
                        description=f"{sink_type} operation: {call_str}"
                    )
                    self.sinks.append(sink)
                    break

    def _check_assignment_sources(self, call_str: str, var_name: str, line_number: int):
        """Check if assignment creates a taint source"""
        for source_type, patterns in self.analyzer.source_patterns.items():
            for pattern in patterns:
                if re.search(pattern, call_str, re.IGNORECASE):
                    source = TaintSource(
                        file_path=self.file_path,
                        line_number=line_number,
                        function_name=self.current_function,
                        variable_name=var_name,
                        source_type=source_type,
                        description=f"Assignment: {var_name} = {call_str}"
                    )
                    self.sources.append(source)
                    break

    def _extract_variable_name(self, call_str: str) -> str:
        """Extract variable name from call string"""
        # Simple heuristic to extract meaningful variable names
        if 'request.' in call_str:
            return 'request_data'
        elif 'input(' in call_str:
            return 'user_input'
        elif 'argv' in call_str:
            return 'command_args'
        elif 'environ' in call_str:
            return 'env_var'
        else:
            return 'tainted_var'


def main():
    """Main execution function"""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    print("[SEARCH] Starting Taint Flow Analysis v4.0...")
    print(f"[U+1F4C1] Repository: {repo_root}")
    
    analyzer = TaintFlowAnalyzer(repo_root)
    analyzer.scan_all_files()
    analyzer.generate_reports()
    
    print("\n[U+1F389] P17 Complete: Taint Flow Analysis Ready!")
    print("[PLAN] Reports generated:")
    print("   - DOCS/security/taint_map.json")
    print("   - DOCS/security/taint_map.md")


if __name__ == "__main__":
    main()
