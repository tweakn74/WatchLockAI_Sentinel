#!/usr/bin/env python3
"""
WatchLockAI Sentinel Feature Flags Matrix Generator
P7: Environment Variable Analysis & Documentation

This tool performs comprehensive analysis of environment variable usage to generate:
- Complete inventory of all environment flags
- Default values and where they're defined
- Route/endpoint dependencies and influences
- Security impact assessment
- Test coverage analysis
- File/line anchors for each flag

Part of Credits Burner Mode v3.0 - stdlib only, no external dependencies.
"""
import ast
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class FlagUsage:
    """Information about how a flag is used in a specific location."""
    file_path: str
    line_number: int
    usage_type: str  # 'getenv', 'environ_get', 'environ_direct', 'config_default'
    default_value: Optional[str]
    context: str  # Function/class where it's used
    code_snippet: str  # Relevant code line


@dataclass
class FlagInfo:
    """Complete information about an environment flag."""
    name: str
    usages: List[FlagUsage]
    default_values: Set[str]  # All default values found
    canonical_default: Optional[str]  # Most common/canonical default
    security_classification: str  # 'public', 'sensitive', 'secret', 'critical'
    security_impact: List[str]  # Security implications
    routes_influenced: List[str]  # API routes that depend on this flag
    failure_modes: List[str]  # What happens when flag is missing/wrong
    test_references: List[str]  # Test files that reference this flag
    documentation_status: str  # 'undocumented', 'partial', 'complete'
    category: str  # 'auth', 'logging', 'performance', 'feature', 'admin', 'security'


class FeatureFlagsAnalyzer:
    """AST-based environment variable analysis for WatchLockAI Sentinel."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.flags: Dict[str, FlagInfo] = {}
        self.source_files: List[Path] = []
        self.route_patterns: Dict[str, List[str]] = {}  # file -> routes
        
    def analyze_flags(self) -> Dict[str, Any]:
        """Perform complete flag analysis."""
        print(f"Starting feature flags analysis for: {self.root_path}")
        
        # Find all Python files
        python_files = list(self.root_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        self.source_files = python_files
        
        print(f"Found {len(python_files)} Python files to analyze")
        
        # First pass: Find all flag usages
        for py_file in python_files:
            try:
                self._analyze_file(py_file)
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")
                
        # Second pass: Analyze security, routes, and relationships
        self._analyze_security_impact()
        self._analyze_route_dependencies()
        self._find_test_coverage()
        self._categorize_flags()
        
        # Generate final matrix
        return self._generate_matrix()
        
    def _should_skip_file(self, path: Path) -> bool:
        """Determine if file should be skipped."""
        skip_patterns = [
            '__pycache__',
            '.git',
            'venv',
            '.venv',
            'node_modules',
            'dist',
            'build',
            '.pytest_cache'
        ]
        
        return any(pattern in str(path) for pattern in skip_patterns)
        
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file for environment variable usage."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return  # Skip files with syntax errors
                
            # Find environment variable usages
            visitor = EnvVarVisitor(str(file_path.relative_to(self.root_path)), content)
            visitor.visit(tree)
            
            # Process found flags
            for flag_name, usage in visitor.flag_usages.items():
                if flag_name not in self.flags:
                    self.flags[flag_name] = FlagInfo(
                        name=flag_name,
                        usages=[],
                        default_values=set(),
                        canonical_default=None,
                        security_classification='public',
                        security_impact=[],
                        routes_influenced=[],
                        failure_modes=[],
                        test_references=[],
                        documentation_status='undocumented',
                        category='unknown'
                    )
                
                self.flags[flag_name].usages.extend(usage)
                
                # Collect default values
                for use in usage:
                    if use.default_value:
                        self.flags[flag_name].default_values.add(use.default_value)
                        
            # Extract route patterns for later analysis
            self.route_patterns[str(file_path.relative_to(self.root_path))] = visitor.routes_found
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    def _analyze_security_impact(self):
        """Analyze security implications of each flag."""
        security_keywords = {
            'secret': ['TOKEN', 'KEY', 'PASSWORD', 'SECRET', 'PRIVATE'],
            'sensitive': ['SESSION', 'AUTH', 'ADMIN', 'USER', 'LOGIN'],
            'critical': ['SYSTEM', 'ROOT', 'CRITICAL', 'SECURITY'],
        }
        
        for flag_info in self.flags.values():
            flag_name = flag_info.name.upper()
            
            # Classify based on name patterns
            if any(keyword in flag_name for keyword in security_keywords['secret']):
                flag_info.security_classification = 'secret'
                flag_info.security_impact = [
                    'Credential exposure risk',
                    'Unauthorized access potential',
                    'Should be encrypted/masked in logs'
                ]
            elif any(keyword in flag_name for keyword in security_keywords['sensitive']):
                flag_info.security_classification = 'sensitive'
                flag_info.security_impact = [
                    'Authentication bypass risk',
                    'Privilege escalation potential'
                ]
            elif any(keyword in flag_name for keyword in security_keywords['critical']):
                flag_info.security_classification = 'critical'
                flag_info.security_impact = [
                    'System integrity risk',
                    'Security control bypass'
                ]
            
            # Add failure mode analysis
            if not flag_info.default_values:
                flag_info.failure_modes.append('No default value - runtime failure likely')
            if flag_info.security_classification in ['secret', 'critical']:
                flag_info.failure_modes.append('Security degradation if misconfigured')
                
    def _analyze_route_dependencies(self):
        """Analyze which API routes depend on each flag."""
        # This is a simplified analysis - in a real implementation,
        # we would need more sophisticated flow analysis
        for flag_info in self.flags.values():
            for usage in flag_info.usages:
                file_path = usage.file_path
                if file_path in self.route_patterns:
                    # If flag is used in a file with routes, assume dependency
                    flag_info.routes_influenced.extend(self.route_patterns[file_path])
                    
    def _find_test_coverage(self):
        """Find test files that reference each flag."""
        for flag_info in self.flags.values():
            for usage in flag_info.usages:
                if 'test' in usage.file_path.lower():
                    flag_info.test_references.append(usage.file_path)
                    
    def _categorize_flags(self):
        """Categorize flags by functionality."""
        categories = {
            'auth': ['AUTH', 'LOGIN', 'SESSION', 'TOKEN', 'RBAC'],
            'logging': ['LOG', 'DEBUG', 'VERBOSE', 'TRACE'],
            'performance': ['TIMEOUT', 'CACHE', 'POOL', 'LIMIT', 'RATE'],
            'feature': ['ENABLE', 'DISABLE', 'FEATURE', 'TOGGLE'],
            'admin': ['ADMIN', 'CONSOLE', 'MANAGEMENT'],
            'security': ['SECURITY', 'TLS', 'SSL', 'CIPHER', 'HASH'],
            'storage': ['PATH', 'DIR', 'FILE', 'STORAGE', 'DATA'],
            'network': ['HOST', 'PORT', 'URL', 'ENDPOINT', 'BIND']
        }
        
        for flag_info in self.flags.values():
            flag_name = flag_info.name.upper()
            
            # Find best category match
            best_category = 'configuration'
            max_matches = 0
            
            for category, keywords in categories.items():
                matches = sum(1 for keyword in keywords if keyword in flag_name)
                if matches > max_matches:
                    max_matches = matches
                    best_category = category
                    
            flag_info.category = best_category
            
            # Determine canonical default
            if flag_info.default_values:
                # Use most common default or first one found
                flag_info.canonical_default = list(flag_info.default_values)[0]
                
    def _generate_matrix(self) -> Dict[str, Any]:
        """Generate the final feature flags matrix."""
        # Convert to serializable format
        flags_data = {}
        for flag_name, flag_info in self.flags.items():
            flags_data[flag_name] = {
                'name': flag_info.name,
                'default_values': list(flag_info.default_values),
                'canonical_default': flag_info.canonical_default,
                'security_classification': flag_info.security_classification,
                'security_impact': flag_info.security_impact,
                'routes_influenced': list(set(flag_info.routes_influenced)),
                'failure_modes': flag_info.failure_modes,
                'test_references': list(set(flag_info.test_references)),
                'documentation_status': flag_info.documentation_status,
                'category': flag_info.category,
                'usage_count': len(flag_info.usages),
                'files_used_in': list(set([usage.file_path for usage in flag_info.usages])),
                'usages': [asdict(usage) for usage in flag_info.usages]
            }
        
        # Generate statistics
        total_flags = len(self.flags)
        by_category = {}
        by_security = {}
        
        for flag_info in self.flags.values():
            by_category[flag_info.category] = by_category.get(flag_info.category, 0) + 1
            by_security[flag_info.security_classification] = by_security.get(flag_info.security_classification, 0) + 1
        
        matrix = {
            'metadata': {
                'generator': 'WatchLockAI Feature Flags Matrix Generator',
                'version': '1.0.0',
                'timestamp': '2025-09-06T22:43:50Z',
                'total_flags': total_flags,
                'files_analyzed': len(self.source_files),
                'flags_with_defaults': len([f for f in self.flags.values() if f.default_values]),
                'flags_with_tests': len([f for f in self.flags.values() if f.test_references]),
            },
            'statistics': {
                'by_category': by_category,
                'by_security_classification': by_security,
                'most_used_flags': self._get_most_used_flags(),
                'flags_without_defaults': [name for name, info in self.flags.items() if not info.default_values],
                'security_sensitive_flags': [name for name, info in self.flags.items() if info.security_classification in ['secret', 'critical']]
            },
            'flags': flags_data
        }
        
        return matrix
        
    def _get_most_used_flags(self) -> List[Dict[str, Any]]:
        """Get flags used in the most locations."""
        usage_counts = []
        for flag_name, flag_info in self.flags.items():
            usage_counts.append({
                'name': flag_name,
                'usage_count': len(flag_info.usages),
                'files_count': len(set([usage.file_path for usage in flag_info.usages])),
                'category': flag_info.category
            })
        
        return sorted(usage_counts, key=lambda x: x['usage_count'], reverse=True)[:15]


class EnvVarVisitor(ast.NodeVisitor):
    """AST visitor to find environment variable usage."""
    
    def __init__(self, file_path: str, content: str):
        self.file_path = file_path
        self.content_lines = content.split('\n')
        self.flag_usages: Dict[str, List[FlagUsage]] = {}
        self.routes_found: List[str] = []
        self.current_context = 'module'
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track current function context."""
        old_context = self.current_context
        self.current_context = f"function:{node.name}"
        self.generic_visit(node)
        self.current_context = old_context
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Track current async function context."""
        old_context = self.current_context
        self.current_context = f"async_function:{node.name}"
        self.generic_visit(node)
        self.current_context = old_context
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Track current class context."""
        old_context = self.current_context
        self.current_context = f"class:{node.name}"
        self.generic_visit(node)
        self.current_context = old_context
        
    def visit_Call(self, node: ast.Call):
        """Process function calls that might access environment variables."""
        # os.getenv() calls
        if (isinstance(node.func, ast.Attribute) and 
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == 'os' and 
            node.func.attr == 'getenv'):
            
            if node.args and isinstance(node.args[0], ast.Constant):
                flag_name = node.args[0].value
                default_val = None
                
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    default_val = str(node.args[1].value)
                
                self._record_flag_usage(flag_name, node.lineno, 'getenv', default_val)
        
        # os.environ.get() calls
        elif (isinstance(node.func, ast.Attribute) and 
              isinstance(node.func.value, ast.Attribute) and
              isinstance(node.func.value.value, ast.Name) and
              node.func.value.value.id == 'os' and
              node.func.value.attr == 'environ' and
              node.func.attr == 'get'):
            
            if node.args and isinstance(node.args[0], ast.Constant):
                flag_name = node.args[0].value
                default_val = None
                
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    default_val = str(node.args[1].value)
                
                self._record_flag_usage(flag_name, node.lineno, 'environ_get', default_val)
        
        # Look for route definitions (FastAPI style)
        elif (isinstance(node.func, ast.Attribute) and 
              node.func.attr in ['get', 'post', 'put', 'delete', 'patch']):
            
            if node.args and isinstance(node.args[0], ast.Constant):
                route = node.args[0].value
                if isinstance(route, str) and route.startswith('/'):
                    self.routes_found.append(f"{node.func.attr.upper()} {route}")
        
        self.generic_visit(node)
        
    def visit_Subscript(self, node: ast.Subscript):
        """Process direct os.environ['VAR'] access."""
        if (isinstance(node.value, ast.Attribute) and 
            isinstance(node.value.value, ast.Name) and
            node.value.value.id == 'os' and 
            node.value.attr == 'environ' and
            isinstance(node.slice, ast.Constant)):
            
            flag_name = node.slice.value
            self._record_flag_usage(flag_name, node.lineno, 'environ_direct', None)
        
        self.generic_visit(node)
        
    def _record_flag_usage(self, flag_name: str, line_num: int, usage_type: str, default_val: Optional[str]):
        """Record a flag usage."""
        if flag_name not in self.flag_usages:
            self.flag_usages[flag_name] = []
        
        # Get code snippet
        code_snippet = ""
        if 1 <= line_num <= len(self.content_lines):
            code_snippet = self.content_lines[line_num - 1].strip()
        
        usage = FlagUsage(
            file_path=self.file_path,
            line_number=line_num,
            usage_type=usage_type,
            default_value=default_val,
            context=self.current_context,
            code_snippet=code_snippet
        )
        
        self.flag_usages[flag_name].append(usage)


def generate_markdown_report(matrix_data: Dict[str, Any], output_path: Path):
    """Generate human-readable markdown report from the matrix data."""
    md_content = f"""# WatchLockAI Sentinel Feature Flags Matrix

**Generated:** {matrix_data['metadata']['timestamp']}  
**Total Flags:** {matrix_data['metadata']['total_flags']}  
**Files Analyzed:** {matrix_data['metadata']['files_analyzed']}  

## Summary Statistics

### Flags by Category
{chr(10).join([f"- **{cat}:** {count} flags" for cat, count in matrix_data['statistics']['by_category'].items()])}

### Security Classification
{chr(10).join([f"- **{cls}:** {count} flags" for cls, count in matrix_data['statistics']['by_security_classification'].items()])}

### Most Used Flags
{chr(10).join([f"- **{flag['name']}** ({flag['category']}): {flag['usage_count']} usages in {flag['files_count']} files" for flag in matrix_data['statistics']['most_used_flags'][:10]])}

## Flag Details

"""

    # Group flags by category for organized display
    by_category = {}
    for flag_name, flag_data in matrix_data['flags'].items():
        category = flag_data['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((flag_name, flag_data))
    
    for category, flags in sorted(by_category.items()):
        md_content += f"\n### {category.title()} Flags\n\n"
        
        for flag_name, flag_data in sorted(flags):
            security_emoji = {
                'public': '🟢',
                'sensitive': '🟡', 
                'secret': '🔴',
                'critical': '🚨'
            }
            
            md_content += f"#### {flag_name} {security_emoji.get(flag_data['security_classification'], '⚪')}\n\n"
            
            if flag_data['canonical_default']:
                md_content += f"**Default:** `{flag_data['canonical_default']}`  \n"
            else:
                md_content += "**Default:** ⚠️ No default value  \n"
                
            md_content += f"**Security:** {flag_data['security_classification']}  \n"
            md_content += f"**Used in:** {flag_data['usage_count']} locations across {len(flag_data['files_used_in'])} files  \n"
            
            if flag_data['routes_influenced']:
                md_content += f"**Influences routes:** {', '.join(flag_data['routes_influenced'][:5])}  \n"
            
            if flag_data['security_impact']:
                md_content += f"**Security impact:** {'; '.join(flag_data['security_impact'])}  \n"
                
            if flag_data['failure_modes']:
                md_content += f"**Failure modes:** {'; '.join(flag_data['failure_modes'])}  \n"
            
            md_content += "\n"
    
    # Write markdown file
    with open(output_path, 'w') as f:
        f.write(md_content)


def main():
    """Main execution function."""
    import sys
    
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."
    
    analyzer = FeatureFlagsAnalyzer(root_path)
    matrix = analyzer.analyze_flags()
    
    # Output JSON matrix
    json_path = Path(root_path) / "DOCS" / "report" / "feature_flags_matrix.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, 'w') as f:
        json.dump(matrix, f, indent=2, sort_keys=True)
    
    # Output markdown report
    md_path = Path(root_path) / "DOCS" / "report" / "feature_flags.md"
    generate_markdown_report(matrix, md_path)
    
    print(f"Feature flags matrix generated:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print(f"Total flags analyzed: {matrix['metadata']['total_flags']}")
    print(f"Flags with defaults: {matrix['metadata']['flags_with_defaults']}")
    print(f"Security-sensitive flags: {len(matrix['statistics']['security_sensitive_flags'])}")


if __name__ == "__main__":
    main()
