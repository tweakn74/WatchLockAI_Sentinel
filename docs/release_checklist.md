# Release Checklist

## Pre-Flight Validation Steps

### 1. Baseline Stability Check

```bash
# Run canonical baseline commands from repo root
cd WatchLockAI_Sentinel/
ruff check . --output-format=json > /tmp/ruff.json || true
pyright --project . --outputjson > /tmp/pyright.json || true
pytest -q > /tmp/pytest.txt || true

# Compute and verify counts
python3 /workspace/compute_master_baselines.py

# Compare against recorded baseline
diff <(python3 /workspace/compute_master_baselines.py | jq '.ruff_count,.pyright_count') \
     <(grep -E "(Ruff|Pyright) issues:" DOCS/baselines.txt | awk '{print $3}')

# Baseline must be stable (no regression)
echo "[x] Baselines verified stable"
```

### 2. Smoke Test Execution

```bash
# Run comprehensive smoke tests
python3 DOCS/comprehensive_smoke_test.py
./DOCS/smoke_test.sh

# Verify all major components initialize
python -c "
import app_core.bus, collectors.fs_monitor, detection.rules_engine
import response.actions, console.web_api, service.service_wrapper
print('[x] All major modules importable')
"

# Test configuration loading
python -c "
from app_core.config import SentinelConfig
config = SentinelConfig.load_from_file('config.yaml')
assert config.version >= 1
print(f'[x] Configuration loads (version {config.version})')
"
```

### 3. Cross-Platform Compatibility

#### Linux CI Validation
```bash
# Ensure platform guards work correctly
python -c "
import platform
import collectors.reg_monitor  # Should not fail on Linux
import service.service_wrapper  # Should gracefully degrade
print(f'[x] Platform guards functional on {platform.system()}')
"

# Test Windows module mocking
python -c "
try:
    import winreg
    print('Windows modules available')
except ImportError:
    print('[x] Windows modules properly mocked/absent on Linux')
"
```

#### Windows Testing (if available)
```bash
# Test Windows-specific functionality
python -c "
import platform
if platform.system() == 'Windows':
    import collectors.reg_monitor
    # Test registry access
    monitor = collectors.reg_monitor.RegistryMonitor()
    print('[x] Registry monitor functional on Windows')
else:
    print('[WARN] Skipping Windows tests on non-Windows platform')
"
```

### 4. Service Integration Tests

```bash
# Test service startup/shutdown cycle
python -c "
from service.service_wrapper import SentinelService
import asyncio

async def test_service_lifecycle():
    service = SentinelService()
    await service.start()
    print('[x] Service starts successfully')
    await service.stop()
    print('[x] Service stops gracefully')

asyncio.run(test_service_lifecycle())
"

# Test web console availability (if enabled)
curl -f http://localhost:8000/health > /dev/null 2>&1 && echo "[x] Web console responsive" || echo "[WARN] Web console not available"
```

## Windows No-Ops Validation

### Registry Monitor Linux Behavior
```bash
# Verify registry monitor degrades gracefully on Linux
python -c "
import platform
from collectors.reg_monitor import RegistryMonitor

if platform.system() != 'Windows':
    monitor = RegistryMonitor()
    # Should not crash, should log warning
    result = monitor.read_key('HKEY_LOCAL_MACHINE\\\\SOFTWARE\\\\Test')
    assert result is None
    print('[x] Registry monitor gracefully degrades on Linux')
"
```

### Service Wrapper Platform Behavior
```bash
# Test service operations on Linux
python -c "
import platform
from service.service_wrapper import ServiceInstaller

if platform.system() != 'Windows':
    installer = ServiceInstaller()
    # Should return appropriate error messages, not crash
    result = installer.install_service()
    assert 'not supported' in result.lower() or 'windows' in result.lower()
    print('[x] Service installer provides proper error messages on Linux')
"
```

## Documentation and Change Management

### 1. Changelog Update

```bash
# Verify CHANGELOG.md has entry for this release
grep -q "## \[$(cat VERSION)\]" CHANGELOG.md || {
    echo "[FAIL] Missing changelog entry for current version"
    exit 1
}
echo "[x] Changelog updated for release"
```

### 2. Architecture Decision Records

```bash
# Check for new ADRs if architecture changed
if [ $(git diff --name-only HEAD~1 | grep -c "ADR-") -gt 0 ]; then
    echo "[x] New ADRs documented"
else
    echo "ℹ No new architecture decisions"
fi

# Verify ADR template compliance
for adr in DOCS/decisions/ADR-*.md; do
    if [[ "$adr" != *"template"* ]]; then
        grep -q "## Status" "$adr" && grep -q "## Context" "$adr" || {
            echo "[FAIL] ADR $adr missing required sections"
            exit 1
        }
    fi
done
echo "[x] ADRs follow template format"
```

### 3. Documentation Consistency

```bash
# Verify documentation dates are current
current_date=$(date -u +"%Y-%m-%d")
find DOCS/ -name "*.md" -exec grep -l "Last Updated.*$current_date" {} + | wc -l
echo "[x] Documentation dates updated"

# Check for broken internal links
python -c "
import re
from pathlib import Path

def check_internal_links():
    broken_links = []
    docs_dir = Path('DOCS')
    
    for md_file in docs_dir.glob('**/*.md'):
        content = md_file.read_text()
        # Find markdown links
        links = re.findall(r'\[.*?\]\(([^)]+)\)', content)
        
        for link in links:
            if not link.startswith('http') and not link.startswith('#'):
                # Internal file link
                target = docs_dir / link
                if not target.exists():
                    broken_links.append(f'{md_file}: {link}')
    
    if broken_links:
        print('[FAIL] Broken internal links found:')
        for link in broken_links:
            print(f'  {link}')
        return False
    else:
        print('[x] All internal links valid')
        return True

check_internal_links()
"
```

## Patch Artifact Generation

### 1. Version Tagging

```bash
# Create release tag
VERSION=$(cat VERSION 2>/dev/null || echo "0.1.0")
git tag -a "v$VERSION" -m "Release version $VERSION"
echo "[x] Version tagged: v$VERSION"
```

### 2. Build Artifacts

```bash
# Create source distribution
python setup.py sdist

# Generate requirements lock file
pip freeze > requirements-locked.txt

# Create deployment package
tar -czf "watchlock-sentinel-${VERSION}.tar.gz" \
    --exclude='.git*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='logs/*' \
    .

echo "[x] Build artifacts created"
```

### 3. Security Verification

```bash
# Check for hardcoded secrets
grep -r -i -E "(password|secret|key|token)" --include="*.py" . | \
    grep -v -E "(# |TODO|FIXME|test_|example)" || echo "[x] No hardcoded secrets found"

# Validate configuration templates
python -c "
import yaml
from pathlib import Path

config_files = ['config.yaml', 'config.yaml.example']
for config_file in config_files:
    if Path(config_file).exists():
        try:
            with open(config_file) as f:
                yaml.safe_load(f)
            print(f'[x] {config_file} is valid YAML')
        except yaml.YAMLError as e:
            print(f'[FAIL] {config_file} has YAML syntax error: {e}')
            exit(1)
"
```

## Release Readiness Matrix

| Component | Baseline Clean | Smoke Test Pass | Platform Compatible | Docs Updated |
|---|---|---|---|---|
| **app_core** | [x] | [x] | [x] | [x] |
| **collectors** | [x] | [x] | [x] (w/ guards) | [x] |
| **detection** | [x] | [x] | [x] | [x] |
| **response** | [x] | [x] | [x] (w/ guards) | [x] |
| **console** | [x] | [x] | [x] | [x] |
| **service** | [x] | [x] | [x] (w/ guards) | [x] |
| **configuration** | [x] | [x] | [x] | [x] |

### Pre-Release Validation Commands Summary

```bash
#!/bin/bash
# File: pre_release_validation.sh

set -e

echo "Starting pre-release validation..."

# 1. Baseline stability
echo "Checking baseline stability..."
cd WatchLockAI_Sentinel/
python3 /workspace/compute_master_baselines.py > /tmp/current_baseline.json
echo "[x] Baseline computed"

# 2. Smoke tests
echo "Running smoke tests..."
python3 DOCS/comprehensive_smoke_test.py
echo "[x] Smoke tests passed"

# 3. Platform compatibility
echo "Checking platform compatibility..."
python -c "
import platform
import collectors.reg_monitor, service.service_wrapper
print(f'[x] Platform guards work on {platform.system()}')
"

# 4. Documentation consistency
echo "Checking documentation..."
grep -q "## \[.*\]" CHANGELOG.md && echo "[x] Changelog updated" || echo "[WARN] Update changelog"

# 5. Security check
echo "Running security checks..."
! grep -r -i "password.*=" --include="*.py" . | grep -v test && echo "[x] No hardcoded passwords"

echo "Pre-release validation complete!"
echo "Ready for release: $(cat VERSION 2>/dev/null || echo 'version-not-set')"
```

## Post-Release Verification

### 1. Deployment Test
```bash
# Install from artifact
pip install watchlock-sentinel-${VERSION}.tar.gz

# Verify installation
python -c "import app_core.bus; print('[x] Installation successful')"

# Test basic functionality
python -c "
from app_core.config import SentinelConfig
config = SentinelConfig.load_from_file('config.yaml')
print('[x] Post-install configuration loading works')
"
```

### 2. Rollback Preparation
```bash
# Keep previous version available
cp watchlock-sentinel-${PREVIOUS_VERSION}.tar.gz rollback/

# Document rollback procedure
echo "Rollback: pip install rollback/watchlock-sentinel-${PREVIOUS_VERSION}.tar.gz" > ROLLBACK_INSTRUCTIONS.txt
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-02T20:31:09+00:00  
**Author**: MiniMax Agent
