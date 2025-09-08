#!/usr/bin/env python3
"""
WatchLockAI Sentinel Symbol Atlas Generator
P7: Deep Static Mapping & Docs Explosion

This tool performs comprehensive AST analysis of all Python files to generate:
- Symbol inventory (classes, functions, methods)
- Docstring status and quality assessment
- Cross-references ("who calls me", "I call who")
- Type hint analysis
- Import dependencies

Part of Credits Burner Mode v3.0 - stdlib only, no external dependencies.
"""
import ast
import os
import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class SymbolInfo:
    """Information about a code symbol (class, function, method)."""
    name: str
    type: str  # 'class', 'function', 'method', 'async_function', 'async_method'
    file_path: str
    line_number: int
    docstring: Optional[str]
    docstring_quality: str  # 'none', 'minimal', 'basic', 'good', 'excellent'
    args: List[str]
    return_annotation: Optional[str]
    decorators: List[str]
    is_public: bool
    is_async: bool
    calls_made: List[str]  # Functions/methods this symbol calls
    called_by: List[str]  # Who calls this symbol (populated in second pass)
    complexity_score: int  # Simple AST-based complexity
    parent_class: Optional[str]  # For methods


@dataclass
class ImportInfo:
    """Information about imports in a file."""
    module: str
    names: List[str]
    alias: Optional[str]
    is_from_import: bool
    line_number: int


@dataclass
class FileAnalysis:
    """Complete analysis of a Python file."""
    file_path: str
    file_hash: str
    symbols: List[SymbolInfo]
    imports: List[ImportInfo]
    total_lines: int
    docstring_coverage: float  # Percentage of public symbols with docstrings
    complexity_total: int
    ast_parse_success: bool
    parse_error: Optional[str]


class SymbolAtlasGenerator:
    """AST-based symbol analysis for WatchLockAI Sentinel codebase."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.file_analyses: Dict[str, FileAnalysis] = {}
        self.all_symbols: Dict[str, SymbolInfo] = {}  # Full symbol name -> info
        self.call_graph: Dict[str, Set[str]] = {}  # caller -> {callees}
        
    def analyze_codebase(self) -> Dict[str, Any]:
        """Perform complete codebase analysis."""
        print(f"Starting symbol atlas generation for: {self.root_path}")
        
        # Find all Python files
        python_files = list(self.root_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        print(f"Found {len(python_files)} Python files to analyze")
        
        # First pass: Analyze each file individually
        for py_file in python_files:
            try:
                analysis = self._analyze_file(py_file)
                self.file_analyses[str(py_file.relative_to(self.root_path))] = analysis
                
                # Build symbol registry
                for symbol in analysis.symbols:
                    full_name = f"{analysis.file_path}::{symbol.name}"
                    if symbol.parent_class:
                        full_name = f"{analysis.file_path}::{symbol.parent_class}.{symbol.name}"
                    self.all_symbols[full_name] = symbol
                    
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")
                
        # Second pass: Build call graph and cross-references
        self._build_call_graph()
        
        # Generate final atlas
        return self._generate_atlas()
        
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
        
    def _analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single Python file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            file_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Parse AST
            try:
                tree = ast.parse(content)
                parse_success = True
                parse_error = None
            except SyntaxError as e:
                return FileAnalysis(
                    file_path=str(file_path.relative_to(self.root_path)),
                    file_hash=file_hash,
                    symbols=[],
                    imports=[],
                    total_lines=len(content.split('\n')),
                    docstring_coverage=0.0,
                    complexity_total=0,
                    ast_parse_success=False,
                    parse_error=str(e)
                )
            
            # Extract symbols and imports
            visitor = SymbolVisitor(str(file_path.relative_to(self.root_path)))
            visitor.visit(tree)
            
            # Calculate docstring coverage
            public_symbols = [s for s in visitor.symbols if s.is_public]
            documented_symbols = [s for s in public_symbols if s.docstring]
            coverage = (len(documented_symbols) / len(public_symbols) * 100) if public_symbols else 0
            
            return FileAnalysis(
                file_path=str(file_path.relative_to(self.root_path)),
                file_hash=file_hash,
                symbols=visitor.symbols,
                imports=visitor.imports,
                total_lines=len(content.split('\n')),
                docstring_coverage=coverage,
                complexity_total=sum(s.complexity_score for s in visitor.symbols),
                ast_parse_success=True,
                parse_error=None
            )
            
        except Exception as e:
            return FileAnalysis(
                file_path=str(file_path.relative_to(self.root_path)),
                file_hash="",
                symbols=[],
                imports=[],
                total_lines=0,
                docstring_coverage=0.0,
                complexity_total=0,
                ast_parse_success=False,
                parse_error=str(e)
            )
    
    def _build_call_graph(self):
        """Build cross-reference call graph."""
        # For each symbol, determine what calls it
        for symbol_name, symbol_info in self.all_symbols.items():
            for called_func in symbol_info.calls_made:
                # Find matching symbols
                for potential_target, target_info in self.all_symbols.items():
                    if target_info.name == called_func:
                        target_info.called_by.append(symbol_name)
    
    def _generate_atlas(self) -> Dict[str, Any]:
        """Generate the final symbol atlas."""
        # Convert dataclasses to dictionaries for JSON serialization
        files_data = {}
        for file_path, analysis in self.file_analyses.items():
            files_data[file_path] = {
                'file_hash': analysis.file_hash,
                'total_lines': analysis.total_lines,
                'docstring_coverage': analysis.docstring_coverage,
                'complexity_total': analysis.complexity_total,
                'ast_parse_success': analysis.ast_parse_success,
                'parse_error': analysis.parse_error,
                'symbols': [asdict(symbol) for symbol in analysis.symbols],
                'imports': [asdict(import_info) for import_info in analysis.imports]
            }
        
        # Generate summary statistics
        total_symbols = len(self.all_symbols)
        public_symbols = len([s for s in self.all_symbols.values() if s.is_public])
        documented_symbols = len([s for s in self.all_symbols.values() if s.is_public and s.docstring])
        
        atlas = {
            'metadata': {
                'generator': 'WatchLockAI Symbol Atlas Generator',
                'version': '1.0.0',
                'timestamp': '2025-09-06T22:43:50Z',
                'total_files': len(self.file_analyses),
                'successful_parses': len([a for a in self.file_analyses.values() if a.ast_parse_success]),
                'total_symbols': total_symbols,
                'public_symbols': public_symbols,
                'documented_symbols': documented_symbols,
                'overall_docstring_coverage': (documented_symbols / public_symbols * 100) if public_symbols else 0
            },
            'files': files_data,
            'symbol_index': {name: asdict(info) for name, info in self.all_symbols.items()},
            'call_graph_summary': {
                'total_call_relationships': sum(len(symbol.calls_made) for symbol in self.all_symbols.values()),
                'most_called_functions': self._get_most_called_functions(),
                'most_complex_functions': self._get_most_complex_functions()
            }
        }
        
        return atlas
    
    def _get_most_called_functions(self) -> List[Dict[str, Any]]:
        """Get functions called most frequently."""
        call_counts = {}
        for symbol in self.all_symbols.values():
            call_count = len(symbol.called_by)
            if call_count > 0:
                call_counts[symbol.name] = {
                    'name': symbol.name,
                    'file_path': symbol.file_path,
                    'call_count': call_count
                }
        
        return sorted(call_counts.values(), key=lambda x: x['call_count'], reverse=True)[:10]
    
    def _get_most_complex_functions(self) -> List[Dict[str, Any]]:
        """Get most complex functions by AST analysis."""
        complex_functions = []
        for symbol in self.all_symbols.values():
            if symbol.complexity_score > 5:  # Threshold for "complex"
                complex_functions.append({
                    'name': symbol.name,
                    'file_path': symbol.file_path,
                    'complexity_score': symbol.complexity_score,
                    'type': symbol.type
                })
        
        return sorted(complex_functions, key=lambda x: x['complexity_score'], reverse=True)[:20]


class SymbolVisitor(ast.NodeVisitor):
    """AST visitor to extract symbol information."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.symbols: List[SymbolInfo] = []
        self.imports: List[ImportInfo] = []
        self.current_class = None
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Process class definitions."""
        docstring = self._extract_docstring(node)
        
        symbol = SymbolInfo(
            name=node.name,
            type='class',
            file_path=self.file_path,
            line_number=node.lineno,
            docstring=docstring,
            docstring_quality=self._assess_docstring_quality(docstring),
            args=[],
            return_annotation=None,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            is_public=not node.name.startswith('_'),
            is_async=False,
            calls_made=self._extract_calls(node),
            called_by=[],
            complexity_score=self._calculate_complexity(node),
            parent_class=None
        )
        
        self.symbols.append(symbol)
        
        # Process methods within the class
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Process function definitions."""
        self._process_function(node, 'function')
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Process async function definitions."""
        self._process_function(node, 'async_function')
    
    def _process_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], func_type: str):
        """Process function or method definition."""
        docstring = self._extract_docstring(node)
        
        # Determine if this is a method
        is_method = self.current_class is not None
        if is_method:
            symbol_type = 'async_method' if func_type.startswith('async') else 'method'
        else:
            symbol_type = func_type
        
        # Extract arguments
        args = []
        if node.args.args:
            args = [arg.arg for arg in node.args.args]
        
        # Extract return annotation
        return_annotation = None
        if node.returns:
            return_annotation = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        symbol = SymbolInfo(
            name=node.name,
            type=symbol_type,
            file_path=self.file_path,
            line_number=node.lineno,
            docstring=docstring,
            docstring_quality=self._assess_docstring_quality(docstring),
            args=args,
            return_annotation=return_annotation,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            is_public=not node.name.startswith('_'),
            is_async=func_type.startswith('async'),
            calls_made=self._extract_calls(node),
            called_by=[],
            complexity_score=self._calculate_complexity(node),
            parent_class=self.current_class
        )
        
        self.symbols.append(symbol)
        
        # Continue processing nested definitions
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import):
        """Process import statements."""
        for alias in node.names:
            import_info = ImportInfo(
                module=alias.name,
                names=[alias.name],
                alias=alias.asname,
                is_from_import=False,
                line_number=node.lineno
            )
            self.imports.append(import_info)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Process from...import statements."""
        if node.module:
            names = [alias.name for alias in node.names]
            import_info = ImportInfo(
                module=node.module,
                names=names,
                alias=None,
                is_from_import=True,
                line_number=node.lineno
            )
            self.imports.append(import_info)
    
    def _extract_docstring(self, node) -> Optional[str]:
        """Extract docstring from AST node."""
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return None
    
    def _assess_docstring_quality(self, docstring: Optional[str]) -> str:
        """Assess the quality of a docstring."""
        if not docstring:
            return 'none'
        
        # Simple heuristic-based assessment
        lines = docstring.strip().split('\n')
        
        if len(docstring) < 10:
            return 'minimal'
        elif len(lines) == 1:
            return 'basic'
        elif any(keyword in docstring.lower() for keyword in ['args:', 'returns:', 'raises:', 'parameters:']):
            return 'excellent'
        elif len(lines) > 2:
            return 'good'
        else:
            return 'basic'
    
    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}" if hasattr(decorator.value, 'id') else decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return 'unknown'
    
    def _extract_calls(self, node) -> List[str]:
        """Extract function calls from AST node."""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        
        # Remove duplicates and limit to reasonable number
        return list(set(calls))[:50]  # Prevent excessive data
    
    def _calculate_complexity(self, node) -> int:
        """Calculate simple complexity score based on AST structure."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity


def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."
    
    generator = SymbolAtlasGenerator(root_path)
    atlas = generator.analyze_codebase()
    
    # Output to DOCS/report/symbol_atlas.json
    output_path = Path(root_path) / "DOCS" / "report" / "symbol_atlas.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(atlas, f, indent=2, sort_keys=True)
    
    print(f"Symbol atlas generated: {output_path}")
    print(f"Total files analyzed: {atlas['metadata']['total_files']}")
    print(f"Total symbols found: {atlas['metadata']['total_symbols']}")
    print(f"Overall docstring coverage: {atlas['metadata']['overall_docstring_coverage']:.1f}%")


if __name__ == "__main__":
    main()
