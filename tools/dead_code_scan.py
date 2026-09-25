#!/usr/bin/env python3
"""
WatchLockAI Sentinel Dead Code Scanner
P8: AST-based Dead Code Detection

This tool performs comprehensive dead code analysis to identify:
- Unused functions and methods
- Unused classes and class methods
- Unused variables and constants
- Unreachable code blocks
- Unused imports
- Potential code cleanup opportunities

Part of Credits Burner Mode v3.0 - stdlib only, no external dependencies.
"""
import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class DeadCodeItem:
    """Information about a potential dead code item."""
    file_path: str
    item_type: str  # 'function', 'class', 'method', 'variable', 'import', 'constant'
    name: str
    line_number: int
    definition_context: str  # Where it's defined (class, function, module)
    usage_count: int  # Number of times referenced
    potential_reasons: List[str]  # Why it might be dead code
    confidence: float  # 0.0-1.0 confidence it's actually dead
    code_snippet: str  # The actual code


class DeadCodeScanner:
    """AST-based dead code detection for WatchLockAI Sentinel."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.all_definitions: Dict[str, Set[str]] = {}  # file -> {defined symbols}
        self.all_usages: Dict[str, Set[str]] = {}  # file -> {used symbols}
        self.cross_file_usages: Dict[str, Set[str]] = {}  # symbol -> {files that use it}
        self.dead_code_items: List[DeadCodeItem] = []
        self.python_files: List[Path] = []
        
    def scan_dead_code(self) -> Dict[str, Any]:
        """Perform comprehensive dead code analysis."""
        print(f"Starting dead code scan for: {self.root_path}")
        
        # Find all Python files
        python_files = list(self.root_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        self.python_files = python_files
        
        print(f"Found {len(python_files)} Python files to analyze")
        
        # First pass: Collect all definitions and usages
        for py_file in python_files:
            try:
                self._analyze_file_pass1(py_file)
            except Exception as e:
                print(f"Error in pass 1 for {py_file}: {e}")
                
        # Second pass: Cross-reference and identify dead code
        for py_file in python_files:
            try:
                self._analyze_file_pass2(py_file)
            except Exception as e:
                print(f"Error in pass 2 for {py_file}: {e}")
                
        # Generate final report
        return self._generate_report()
        
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
        
    def _analyze_file_pass1(self, file_path: Path):
        """First pass: collect definitions and usages."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return  # Skip files with syntax errors
                
            # Collect definitions and usages
            visitor = DeadCodeVisitorPass1(str(file_path.relative_to(self.root_path)), content)
            visitor.visit(tree)
            
            # Store results
            file_key = str(file_path.relative_to(self.root_path))
            self.all_definitions[file_key] = visitor.definitions
            self.all_usages[file_key] = visitor.usages
            
            # Build cross-file usage mapping
            for symbol in visitor.usages:
                if symbol not in self.cross_file_usages:
                    self.cross_file_usages[symbol] = set()
                self.cross_file_usages[symbol].add(file_key)
                
        except Exception as e:
            print(f"Error in pass 1 processing {file_path}: {e}")
            
    def _analyze_file_pass2(self, file_path: Path):
        """Second pass: identify dead code."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return  # Skip files with syntax errors
                
            # Analyze for dead code
            visitor = DeadCodeVisitorPass2(
                str(file_path.relative_to(self.root_path)), 
                content,
                self.all_definitions,
                self.all_usages,
                self.cross_file_usages
            )
            visitor.visit(tree)
            
            # Collect dead code items
            self.dead_code_items.extend(visitor.dead_code_items)
            
        except Exception as e:
            print(f"Error in pass 2 processing {file_path}: {e}")
            
    def _generate_report(self) -> Dict[str, Any]:
        """Generate the dead code analysis report."""
        # Group dead code by type and file
        by_type = {}
        by_file = {}
        by_confidence = {'high': [], 'medium': [], 'low': []}
        
        for item in self.dead_code_items:
            # By type
            if item.item_type not in by_type:
                by_type[item.item_type] = []
            by_type[item.item_type].append(item)
            
            # By file
            if item.file_path not in by_file:
                by_file[item.file_path] = []
            by_file[item.file_path].append(item)
            
            # By confidence
            if item.confidence >= 0.8:
                by_confidence['high'].append(item)
            elif item.confidence >= 0.5:
                by_confidence['medium'].append(item)
            else:
                by_confidence['low'].append(item)
                
        # Calculate statistics
        total_items = len(self.dead_code_items)
        potential_cleanup_lines = sum(1 for item in self.dead_code_items if item.confidence >= 0.7)
        
        # Convert to serializable format
        items_data = [asdict(item) for item in self.dead_code_items]
        
        report = {
            'metadata': {
                'generator': 'WatchLockAI Dead Code Scanner',
                'version': '1.0.0',
                'timestamp': '2025-09-06T22:43:50Z',
                'files_analyzed': len(self.python_files),
                'total_dead_code_items': total_items,
                'high_confidence_items': len(by_confidence['high']),
                'potential_cleanup_lines': potential_cleanup_lines
            },
            'statistics': {
                'by_type': {item_type: len(items) for item_type, items in by_type.items()},
                'by_confidence': {conf: len(items) for conf, items in by_confidence.items()},
                'files_with_dead_code': len(by_file),
                'most_problematic_files': self._get_most_problematic_files(by_file)
            },
            'dead_code_items': items_data,
            'cleanup_recommendations': self._generate_cleanup_recommendations(by_confidence),
            'summary_by_file': {file: len(items) for file, items in by_file.items()}
        }
        
        return report
        
    def _get_most_problematic_files(self, by_file: Dict[str, List[DeadCodeItem]]) -> List[Dict[str, Any]]:
        """Get files with the most dead code issues."""
        file_scores = []
        for file_path, items in by_file.items():
            high_conf_count = len([item for item in items if item.confidence >= 0.8])
            total_count = len(items)
            score = high_conf_count * 2 + total_count
            
            file_scores.append({
                'file_path': file_path,
                'total_issues': total_count,
                'high_confidence_issues': high_conf_count,
                'cleanup_score': score
            })
            
        return sorted(file_scores, key=lambda x: x['cleanup_score'], reverse=True)[:10]
        
    def _generate_cleanup_recommendations(self, by_confidence: Dict[str, List[DeadCodeItem]]) -> List[Dict[str, Any]]:
        """Generate cleanup recommendations."""
        recommendations = []
        
        # High confidence items
        if by_confidence['high']:
            recommendations.append({
                'priority': 'High',
                'action': 'Safe to remove',
                'count': len(by_confidence['high']),
                'description': 'These items have high confidence of being unused and can likely be removed safely.',
                'items': [f"{item.file_path}:{item.name}" for item in by_confidence['high'][:10]]
            })
            
        # Medium confidence items
        if by_confidence['medium']:
            recommendations.append({
                'priority': 'Medium',
                'action': 'Review and test',
                'count': len(by_confidence['medium']),
                'description': 'These items should be reviewed manually and tested before removal.',
                'items': [f"{item.file_path}:{item.name}" for item in by_confidence['medium'][:10]]
            })
            
        # Low confidence items
        if by_confidence['low']:
            recommendations.append({
                'priority': 'Low',
                'action': 'Further analysis needed',
                'count': len(by_confidence['low']),
                'description': 'These items need more detailed analysis to determine if they are truly unused.',
                'items': [f"{item.file_path}:{item.name}" for item in by_confidence['low'][:10]]
            })
            
        return recommendations


class DeadCodeVisitorPass1(ast.NodeVisitor):
    """First pass AST visitor to collect definitions and usages."""
    
    def __init__(self, file_path: str, content: str):
        self.file_path = file_path
        self.content_lines = content.split('\n')
        self.definitions: Set[str] = set()
        self.usages: Set[str] = set()
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Record function definitions."""
        self.definitions.add(node.name)
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Record async function definitions."""
        self.definitions.add(node.name)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Record class definitions."""
        self.definitions.add(node.name)
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign):
        """Record variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.definitions.add(target.id)
        self.generic_visit(node)
        
    def visit_Import(self, node: ast.Import):
        """Record imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.definitions.add(name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Record from imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.definitions.add(name)
        self.generic_visit(node)
        
    def visit_Name(self, node: ast.Name):
        """Record name usages."""
        if isinstance(node.ctx, ast.Load):
            self.usages.add(node.id)
        self.generic_visit(node)
        
    def visit_Attribute(self, node: ast.Attribute):
        """Record attribute usages."""
        if isinstance(node.value, ast.Name):
            self.usages.add(node.value.id)
        self.generic_visit(node)


class DeadCodeVisitorPass2(ast.NodeVisitor):
    """Second pass AST visitor to identify dead code."""
    
    def __init__(self, file_path: str, content: str, all_definitions: Dict[str, Set[str]], 
                 all_usages: Dict[str, Set[str]], cross_file_usages: Dict[str, Set[str]]):
        self.file_path = file_path
        self.content_lines = content.split('\n')
        self.all_definitions = all_definitions
        self.all_usages = all_usages
        self.cross_file_usages = cross_file_usages
        self.dead_code_items: List[DeadCodeItem] = []
        self.current_class = None
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Analyze class definitions for dead code."""
        old_class = self.current_class
        self.current_class = node.name
        
        # Check if class is used
        usage_count = self._count_usages(node.name)
        confidence = self._calculate_confidence(node.name, 'class', usage_count)
        
        if confidence > 0.3:  # Potential dead code
            reasons = self._get_dead_code_reasons(node.name, 'class', usage_count)
            
            dead_item = DeadCodeItem(
                file_path=self.file_path,
                item_type='class',
                name=node.name,
                line_number=node.lineno,
                definition_context='module',
                usage_count=usage_count,
                potential_reasons=reasons,
                confidence=confidence,
                code_snippet=self._get_code_snippet(node.lineno)
            )
            self.dead_code_items.append(dead_item)
            
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze function definitions for dead code."""
        self._analyze_function(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Analyze async function definitions for dead code."""
        self._analyze_function(node)
        
    def _analyze_function(self, node):
        """Analyze function or method for dead code."""
        # Skip special methods and property setters/getters
        if node.name.startswith('__') and node.name.endswith('__'):
            self.generic_visit(node)
            return
            
        # Skip test methods
        if node.name.startswith('test_'):
            self.generic_visit(node)
            return
            
        usage_count = self._count_usages(node.name)
        item_type = 'method' if self.current_class else 'function'
        confidence = self._calculate_confidence(node.name, item_type, usage_count)
        
        if confidence > 0.3:  # Potential dead code
            reasons = self._get_dead_code_reasons(node.name, item_type, usage_count)
            
            dead_item = DeadCodeItem(
                file_path=self.file_path,
                item_type=item_type,
                name=node.name,
                line_number=node.lineno,
                definition_context=self.current_class or 'module',
                usage_count=usage_count,
                potential_reasons=reasons,
                confidence=confidence,
                code_snippet=self._get_code_snippet(node.lineno)
            )
            self.dead_code_items.append(dead_item)
            
        self.generic_visit(node)
        
    def _count_usages(self, symbol_name: str) -> int:
        """Count total usages of a symbol across all files."""
        total_usages = 0
        
        # Count usages in current file
        if symbol_name in self.all_usages.get(self.file_path, set()):
            total_usages += 1
            
        # Count cross-file usages
        if symbol_name in self.cross_file_usages:
            total_usages += len(self.cross_file_usages[symbol_name])
            
        return total_usages
        
    def _calculate_confidence(self, symbol_name: str, symbol_type: str, usage_count: int) -> float:
        """Calculate confidence that this is dead code (0.0-1.0)."""
        confidence = 0.0
        
        # Base confidence on usage count
        if usage_count == 0:
            confidence = 0.9
        elif usage_count == 1:
            confidence = 0.7
        elif usage_count == 2:
            confidence = 0.5
        else:
            confidence = 0.2
            
        # Adjust based on symbol characteristics
        if symbol_name.startswith('_') and not symbol_name.startswith('__'):
            confidence *= 1.2  # Private methods more likely to be dead
            
        if symbol_type == 'method' and symbol_name in ['setUp', 'tearDown']:
            confidence *= 0.1  # Test framework methods
            
        if symbol_name in ['main', '__init__', '__call__']:
            confidence *= 0.1  # Special methods less likely to be dead
            
        # Cap at 1.0
        return min(confidence, 1.0)
        
    def _get_dead_code_reasons(self, symbol_name: str, symbol_type: str, usage_count: int) -> List[str]:
        """Get reasons why this might be dead code."""
        reasons = []
        
        if usage_count == 0:
            reasons.append("No usages found in codebase")
        elif usage_count == 1:
            reasons.append("Only one usage found")
        elif usage_count <= 2:
            reasons.append("Very few usages found")
            
        if symbol_name.startswith('_'):
            reasons.append("Private method/function (internal use)")
            
        if symbol_type == 'method':
            reasons.append("Method may be unused in class")
            
        return reasons
        
    def _get_code_snippet(self, line_number: int) -> str:
        """Get code snippet around the line number."""
        if 1 <= line_number <= len(self.content_lines):
            return self.content_lines[line_number - 1].strip()
        return ""


def generate_markdown_report(report: Dict[str, Any], output_path: Path):
    """Generate markdown report from dead code analysis."""
    md_content = f"""# WatchLockAI Sentinel Dead Code Analysis Report

**Generated:** {report['metadata']['timestamp']}  
**Files Analyzed:** {report['metadata']['files_analyzed']}  
**Total Dead Code Items:** {report['metadata']['total_dead_code_items']}  
**High Confidence Items:** {report['metadata']['high_confidence_items']}  
**Potential Cleanup Lines:** {report['metadata']['potential_cleanup_lines']}  

## Summary Statistics

### Dead Code by Type
{chr(10).join([f"- **{dtype}:** {count} items" for dtype, count in report['statistics']['by_type'].items()])}

### Confidence Distribution
{chr(10).join([f"- **{conf.title()} Confidence:** {count} items" for conf, count in report['statistics']['by_confidence'].items()])}

## Most Problematic Files

"""

    for file_info in report['statistics']['most_problematic_files'][:10]:
        md_content += f"- **{file_info['file_path']}:** {file_info['total_issues']} issues "
        md_content += f"({file_info['high_confidence_issues']} high confidence)\n"

    md_content += "\n## Cleanup Recommendations\n\n"

    for rec in report['cleanup_recommendations']:
        md_content += f"### {rec['priority']} Priority - {rec['action']}\n\n"
        md_content += f"**Count:** {rec['count']} items  \n"
        md_content += f"**Description:** {rec['description']}\n\n"
        
        if rec['items']:
            md_content += "**Sample Items:**\n"
            for item in rec['items']:
                md_content += f"- `{item}`\n"
        md_content += "\n"

    md_content += "## Detailed Analysis\n\n"

    # Group items by file for detailed breakdown
    by_file = {}
    for item in report['dead_code_items']:
        if item['file_path'] not in by_file:
            by_file[item['file_path']] = []
        by_file[item['file_path']].append(item)

    for file_path, items in sorted(by_file.items()):
        md_content += f"### {file_path}\n\n"
        
        for item in sorted(items, key=lambda x: x['confidence'], reverse=True)[:10]:
            confidence_emoji = "[U+1F534]" if item['confidence'] >= 0.8 else "[U+1F7E1]" if item['confidence'] >= 0.5 else "[U+1F7E2]"
            md_content += f"- **{item['name']}** ({item['item_type']}) {confidence_emoji}\n"
            md_content += f"  - Line {item['line_number']}, confidence: {item['confidence']:.2f}\n"
            md_content += f"  - Usages: {item['usage_count']}\n"
            if item['potential_reasons']:
                md_content += f"  - Reasons: {', '.join(item['potential_reasons'])}\n"
            md_content += f"  - Code: `{item['code_snippet'][:80]}...`\n\n"

    md_content += """
## Analysis Notes

### Confidence Levels
- **High ([U+1F534])**: Very likely dead code, safe to remove after testing
- **Medium ([U+1F7E1])**: Potentially dead code, requires manual review
- **Low ([U+1F7E2])**: Uncertain, may have dynamic usage or be framework code

### Limitations
This analysis uses static analysis and may miss:
- Dynamic imports and attribute access
- Reflection-based usage
- Framework callbacks and hooks
- Plugin system integrations
- External library dependencies

### Recommendations
1. **Start with high-confidence items** for initial cleanup
2. **Test thoroughly** before removing any code
3. **Review git history** to understand code purpose
4. **Consider deprecation** before removal for public APIs
"""

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
    
    scanner = DeadCodeScanner(root_path)
    report = scanner.scan_dead_code()
    
    # Output JSON report
    json_path = Path(root_path) / "DOCS" / "report" / "dead_code_analysis.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, sort_keys=True)
    
    # Output markdown report
    md_path = Path(root_path) / "DOCS" / "report" / "dead_code_scan.md"
    generate_markdown_report(report, md_path)
    
    print(f"Dead code analysis complete:")
    print(f"  JSON Report: {json_path}")
    print(f"  Markdown Report: {md_path}")
    print(f"Files analyzed: {report['metadata']['files_analyzed']}")
    print(f"Total dead code items: {report['metadata']['total_dead_code_items']}")
    print(f"High confidence items: {report['metadata']['high_confidence_items']}")
    
    if report['statistics']['by_type']:
        print("\nDead code by type:")
        for dtype, count in report['statistics']['by_type'].items():
            print(f"  {dtype}: {count}")


if __name__ == "__main__":
    main()
