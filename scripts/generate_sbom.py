#!/usr/bin/env python3
"""
Software Bill of Materials (SBOM) Generator

Generates SBOM manifest for WatchLockAI Sentinel project.
Temporary minimal implementation to fix syntax errors in P44.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Set, List


class SBOMGenerator:
    """Generates Software Bill of Materials for the project."""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.imports_found = {}
        
    def scan_imports(self) -> None:
        """Scan Python files for import statements."""
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                imports = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        imports.append(line)
                        
                if imports:
                    self.imports_found[str(py_file.relative_to(self.project_root))] = imports
                    
            except Exception:
                continue  # Skip files that can't be read
                
    def generate_manifest(self, output_path: Path) -> bool:
        """Generate SBOM manifest file."""
        try:
            self.scan_imports()
            
            manifest = {
                "metadata": {
                    "name": "WatchLockAI-Sentinel",
                    "version": "6.1.0", 
                    "description": "WatchLockAI Sentinel Security Framework",
                    "license": "MIT"
                },
                "dependencies": {
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "total_files": len(self.imports_found),
                    "total_imports": sum(len(imports) for imports in self.imports_found.values())
                },
                "file_manifest": self.imports_found
            }
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, sort_keys=True)
                
            print(f"✅ SBOM manifest generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate SBOM manifest: {e}")
            return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path(__file__).parent.parent
        
    output_path = project_root / "dist" / "sbom_manifest.json"
    
    generator = SBOMGenerator(project_root)
    success = generator.generate_manifest(output_path)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
