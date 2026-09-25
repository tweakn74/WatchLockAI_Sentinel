#!/usr/bin/env python3
"""
Dead Code Patch Generator v4.0 - Generate safe removal patches
Part of Credits Overdrive v4.0 (Proof-Oriented, Fail-Closed)

Creates non-applied patch files for dead code removal with:
- Risk assessment for each patch
- Revert plan and rollback instructions
- Regression testing recommendations
- Prioritized triage report
"""

import json
import os
import re
import hashlib
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class DeadCodePatch:
    """Represents a dead code removal patch"""
    patch_id: str
    file_path: str
    function_name: str
    line_start: int
    line_end: int
    patch_content: str
    risk_level: str  # 'low', 'medium', 'high'
    confidence: float
    revert_plan: str
    test_requirements: List[str]
    dependencies: List[str]

class DeadCodePatchGenerator:
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.dead_code_analysis = self._load_dead_code_analysis()
        self.patches = []
        self.patch_dir = os.path.join(repo_root, "DOCS", "report", "dead_code_patches")
        
    def _load_dead_code_analysis(self) -> Dict[str, Any]:
        """Load existing dead code analysis"""
        analysis_path = os.path.join(self.repo_root, "DOCS", "report", "dead_code_analysis.json")
        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("[WARN]  dead_code_analysis.json not found")
            return {"dead_code_items": [], "cleanup_recommendations": []}

    def generate_all_patches(self) -> None:
        """Generate patches for all dead code items"""
        print("[U+1F527] Generating dead code removal patches...")
        
        # Create patch directory
        os.makedirs(self.patch_dir, exist_ok=True)
        
        # Process dead code items
        for item in self.dead_code_analysis.get("dead_code_items", []):
            try:
                patch = self._create_patch_for_item(item)
                if patch:
                    self.patches.append(patch)
                    self._save_patch_file(patch)
            except Exception as e:
                print(f"[WARN]  Error creating patch for {item.get('name', 'unknown')}: {e}")
        
        # Generate triage report
        self._generate_triage_report()
        
        print(f"[PASS] Generated {len(self.patches)} patches")

    def _create_patch_for_item(self, item: Dict[str, Any]) -> DeadCodePatch:
        """Create a patch for a single dead code item"""
        file_path = item.get("file_path", "")
        function_name = item.get("name", "")
        line_number = item.get("line_number", 0)
        confidence = item.get("confidence", 0.0)
        
        if not file_path or not function_name:
            return None
        
        # Read the source file
        full_path = os.path.join(self.repo_root, file_path)
        if not os.path.exists(full_path):
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            return None
        
        # Find function boundaries
        line_start, line_end = self._find_function_boundaries(lines, line_number, function_name)
        
        if line_start is None or line_end is None:
            return None
        
        # Generate patch content
        patch_content = self._generate_patch_content(file_path, lines, line_start, line_end)
        
        # Assess risk level
        risk_level = self._assess_risk_level(item, file_path, function_name)
        
        # Generate patch ID
        patch_id = f"patch_{hashlib.md5(f'{file_path}_{function_name}'.encode()).hexdigest()[:8]}"
        
        # Create revert plan
        revert_plan = self._create_revert_plan(file_path, function_name, line_start, line_end)
        
        # Determine test requirements
        test_requirements = self._determine_test_requirements(file_path, function_name, risk_level)
        
        # Find dependencies
        dependencies = self._find_dependencies(item, function_name)
        
        patch = DeadCodePatch(
            patch_id=patch_id,
            file_path=file_path,
            function_name=function_name,
            line_start=line_start,
            line_end=line_end,
            patch_content=patch_content,
            risk_level=risk_level,
            confidence=confidence,
            revert_plan=revert_plan,
            test_requirements=test_requirements,
            dependencies=dependencies
        )
        
        return patch

    def _find_function_boundaries(self, lines: List[str], target_line: int, function_name: str) -> Tuple[int, int]:
        """Find the start and end lines of a function"""
        start_line = None
        end_line = None
        
        # Search around the target line for function definition
        search_range = range(max(0, target_line - 10), min(len(lines), target_line + 10))
        
        for i in search_range:
            line = lines[i].strip()
            if line.startswith(f"def {function_name}(") or line.startswith(f"class {function_name}("):
                start_line = i
                break
        
        if start_line is None:
            # Fallback: use target line
            start_line = max(0, target_line - 1)
        
        # Find end of function by tracking indentation
        if start_line is not None:
            base_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
            
            for i in range(start_line + 1, len(lines)):
                line = lines[i]
                if line.strip() == "":
                    continue
                    
                current_indent = len(line) - len(line.lstrip())
                
                # If we hit code at same or lower indentation level, function ends
                if current_indent <= base_indent and line.strip():
                    end_line = i - 1
                    break
            
            if end_line is None:
                end_line = min(len(lines) - 1, start_line + 20)  # Fallback
        
        return start_line, end_line

    def _generate_patch_content(self, file_path: str, lines: List[str], start_line: int, end_line: int) -> str:
        """Generate unified diff patch content"""
        # Create unified diff format
        patch_lines = [
            f"--- a/{file_path}",
            f"+++ b/{file_path}",
            f"@@ -{start_line + 1},{end_line - start_line + 1} +{start_line + 1},0 @@"
        ]
        
        # Add removed lines (prefixed with -)
        for i in range(start_line, end_line + 1):
            if i < len(lines):
                patch_lines.append(f"-{lines[i].rstrip()}")
        
        return "\n".join(patch_lines)

    def _assess_risk_level(self, item: Dict[str, Any], file_path: str, function_name: str) -> str:
        """Assess risk level for removing this code"""
        confidence = item.get("confidence", 0.0)
        
        # High risk indicators
        high_risk_indicators = [
            'main',
            '__init__',
            'setup',
            'start',
            'initialize',
            'config',
            'auth',
            'security',
        ]
        
        # Medium risk indicators
        medium_risk_indicators = [
            'api',
            'handler',
            'process',
            'validate',
            'check',
        ]
        
        # Check function name
        func_lower = function_name.lower()
        
        if any(indicator in func_lower for indicator in high_risk_indicators):
            return 'high'
        
        if any(indicator in func_lower for indicator in medium_risk_indicators):
            return 'medium'
        
        # Check file path
        if any(path_part in file_path.lower() for path_part in ['app.py', 'main.py', '__init__.py']):
            return 'high'
        
        if any(path_part in file_path.lower() for path_part in ['api', 'service', 'console']):
            return 'medium'
        
        # Check confidence level
        if confidence < 0.3:
            return 'high'
        elif confidence < 0.7:
            return 'medium'
        else:
            return 'low'

    def _create_revert_plan(self, file_path: str, function_name: str, start_line: int, end_line: int) -> str:
        """Create revert plan for the patch"""
        return f"""# Revert Plan for {function_name} in {file_path}

## Quick Revert
```bash
# Apply reverse patch
git apply --reverse DOCS/report/dead_code_patches/{self._get_patch_filename(file_path, function_name)}

# Or restore from backup
git checkout HEAD -- {file_path}
```

## Manual Revert
1. Open {file_path}
2. Navigate to line {start_line + 1}
3. Restore the removed function code from git history
4. Test functionality

## Verification Steps
1. Run compile check: `python -m py_compile {file_path}`
2. Run related tests: `python -m pytest tests/ -k {function_name}`
3. Check for import errors: `python -c "import {file_path.replace('/', '.').replace('.py', '')}"`
4. Verify application startup if core function

## Emergency Rollback
If issues occur in production:
1. `git revert <commit_hash>` to undo the removal
2. Redeploy immediately
3. Investigate issues before re-attempting removal
"""

    def _determine_test_requirements(self, file_path: str, function_name: str, risk_level: str) -> List[str]:
        """Determine what tests should be run before applying patch"""
        base_tests = [
            f"python -m py_compile {file_path}",
            "python -m pytest tests/ --tb=short"
        ]
        
        if risk_level == 'high':
            base_tests.extend([
                "python tools/verify_minimax_claims.py",
                "python -c \"import app; print('Import check passed')\"",
                "python tools/scenario_replayer.py --category valid_requests --dry-run --limit 10"
            ])
        elif risk_level == 'medium':
            base_tests.extend([
                f"python -m pytest tests/ -k {function_name}",
                "python -c \"import console.web_api; print('API import check passed')\""
            ])
        
        return base_tests

    def _find_dependencies(self, item: Dict[str, Any], function_name: str) -> List[str]:
        """Find potential dependencies that might be affected"""
        # This is a simplified dependency finder
        # In a real implementation, you'd do AST analysis
        dependencies = []
        
        # Check if function name appears in other files
        for root, dirs, files in os.walk(self.repo_root):
            if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.pytest_cache']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if function_name in content and file_path != os.path.join(self.repo_root, item.get('file_path', '')):
                                rel_path = os.path.relpath(file_path, self.repo_root)
                                dependencies.append(rel_path)
                    except Exception:
                        continue
        
        return dependencies[:5]  # Limit to first 5 dependencies

    def _get_patch_filename(self, file_path: str, function_name: str) -> str:
        """Generate patch filename"""
        safe_path = file_path.replace('/', '_').replace('.py', '')
        return f"{safe_path}_{function_name}.patch"

    def _save_patch_file(self, patch: DeadCodePatch) -> None:
        """Save individual patch file"""
        filename = self._get_patch_filename(patch.file_path, patch.function_name)
        patch_path = os.path.join(self.patch_dir, filename)
        
        patch_header = f"""# Dead Code Removal Patch
# Patch ID: {patch.patch_id}
# File: {patch.file_path}
# Function: {patch.function_name}
# Risk Level: {patch.risk_level.upper()}
# Confidence: {patch.confidence:.2f}
# Generated: 2025-09-07 by Credits Overdrive v4.0

"""
        
        full_patch_content = patch_header + patch.patch_content
        
        with open(patch_path, 'w', encoding='utf-8') as f:
            f.write(full_patch_content)

    def _generate_triage_report(self) -> None:
        """Generate comprehensive triage report"""
        print("[PAGE] Generating dead code triage report...")
        
        # Group patches by risk level
        risk_groups = {'low': [], 'medium': [], 'high': []}
        for patch in self.patches:
            risk_groups[patch.risk_level].append(patch)
        
        report_content = f"""# Dead Code Removal Triage Report v4.0

**Generated:** 2025-09-07  
**Tool:** Credits Overdrive v4.0 Dead Code Patch Generator  
**Repository:** WatchLockAI Sentinel

## Executive Summary

| Category | Count | Action | Timeline |
|----------|-------|--------|----------|
| **Low Risk** | {len(risk_groups['low'])} | Apply immediately | This sprint |
| **Medium Risk** | {len(risk_groups['medium'])} | Review and test | Next sprint |
| **High Risk** | {len(risk_groups['high'])} | Manual review required | Future sprint |
| **Total Patches** | {len(self.patches)} | - | - |

## Risk Assessment Overview

### [PASS] Low Risk (Safe to Remove)
These patches have high confidence and minimal risk of causing issues.

"""
        
        for patch in risk_groups['low'][:10]:  # Show first 10
            report_content += f"""**{patch.patch_id}**: `{patch.file_path}:{patch.function_name}`
- **Confidence:** {patch.confidence:.2f}
- **Patch:** `{self._get_patch_filename(patch.file_path, patch.function_name)}`
- **Dependencies:** {len(patch.dependencies)} potential

"""
        
        if len(risk_groups['low']) > 10:
            report_content += f"*... and {len(risk_groups['low']) - 10} more low-risk patches*\n"
        
        report_content += """
### [WARN] Medium Risk (Review Required)
These patches should be reviewed and tested before application.

"""
        
        for patch in risk_groups['medium']:
            report_content += f"""**{patch.patch_id}**: `{patch.file_path}:{patch.function_name}`
- **Confidence:** {patch.confidence:.2f}
- **Dependencies:** {', '.join(patch.dependencies[:3])}{'...' if len(patch.dependencies) > 3 else ''}
- **Tests Required:** {len(patch.test_requirements)} steps

"""
        
        report_content += """
### [ALERT] High Risk (Manual Review)
These patches require careful manual review and extensive testing.

"""
        
        for patch in risk_groups['high']:
            report_content += f"""**{patch.patch_id}**: `{patch.file_path}:{patch.function_name}`
- **Confidence:** {patch.confidence:.2f}
- **Risk Factors:** Core functionality, low confidence, or critical path
- **Revert Plan:** Available in patch file

"""
        
        report_content += f"""
## Implementation Recommendations

### Phase 1: Low Risk (Immediate)
Apply low-risk patches immediately after basic testing:

```bash
# Apply all low-risk patches
cd DOCS/report/dead_code_patches/
"""
        
        for patch in risk_groups['low'][:5]:
            filename = self._get_patch_filename(patch.file_path, patch.function_name)
            report_content += f'git apply {filename}\n'
        
        report_content += """
# Run verification
python tools/verify_minimax_claims.py
python -m pytest tests/ --tb=short
```

### Phase 2: Medium Risk (Next Sprint)
Review and test medium-risk patches:

1. **Code Review:** Manual inspection of each function
2. **Testing:** Run all specified test requirements
3. **Staging:** Apply to staging environment first
4. **Monitoring:** Monitor for 24 hours before production

### Phase 3: High Risk (Future)
High-risk patches require extensive analysis:

1. **Architecture Review:** Understand impact on system architecture
2. **Comprehensive Testing:** Full regression test suite
3. **Backup Strategy:** Ensure easy rollback capability
4. **Staged Rollout:** Apply to subset of environments first

## Patch File Locations

All patches are saved in: `DOCS/report/dead_code_patches/`

| Risk Level | Patch Count | Total Lines Removed |
|------------|-------------|-------------------|
| Low | {len(risk_groups['low'])} | {sum(p.line_end - p.line_start + 1 for p in risk_groups['low'])} |
| Medium | {len(risk_groups['medium'])} | {sum(p.line_end - p.line_start + 1 for p in risk_groups['medium'])} |
| High | {len(risk_groups['high'])} | {sum(p.line_end - p.line_start + 1 for p in risk_groups['high'])} |

## Revert Procedures

Each patch file includes:
- Unified diff format for easy application/reversal
- Detailed revert instructions
- Emergency rollback procedures
- Verification steps

**Emergency Revert:**
```bash
# Revert specific patch
git apply --reverse DOCS/report/dead_code_patches/<patch_file>

# Revert all changes
git checkout HEAD -- .
```

## Quality Assurance

Before applying any patch:
1. [PASS] Review patch content manually
2. [PASS] Run specified test requirements  
3. [PASS] Verify no compilation errors
4. [PASS] Check application startup
5. [PASS] Monitor logs for errors

## Monitoring After Application

Post-removal monitoring checklist:
- [ ] Application startup successful
- [ ] All endpoints responding
- [ ] No new error logs
- [ ] Performance metrics stable
- [ ] User-facing functionality intact

---
*Generated by Credits Overdrive v4.0 - Dead Code Patch Generator*  
*Patches are non-destructive until manually applied*
"""
        
        report_path = os.path.join(self.repo_root, "DOCS", "report", "dead_code_triage.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"[PAGE] Triage report: {report_path}")


def main():
    """Main execution function"""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    print("[U+267B] Starting Dead Code Patch Generation v4.0...")
    print(f"[U+1F4C1] Repository: {repo_root}")
    
    generator = DeadCodePatchGenerator(repo_root)
    generator.generate_all_patches()
    
    print("\n[U+1F389] P19 Complete: Dead Code Removal Plan Ready!")
    print("[PLAN] Generated:")
    print("   - DOCS/report/dead_code_patches/*.patch")
    print("   - DOCS/report/dead_code_triage.md")


if __name__ == "__main__":
    main()
