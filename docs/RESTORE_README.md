# Full Harvest v7.1 - Restoration Guide

This document provides comprehensive instructions for verifying and restoring the Full Harvest v7.1 packages. The harvest includes both source-only and complete repository archives with deterministic builds and comprehensive verification.

## [PKG] Package Overview

**Full Harvest v7.1** contains two main archive types:

- **`source_only_v7_1.zip`** - Complete source code without distribution artifacts (467 files, ~17MB)
- **`everything_v7_1.zip`** - Complete repository including all distribution files (470 files, ~20MB)

All packages are built deterministically with `SOURCE_DATE_EPOCH=1700000000` for reproducible builds.

## [SEARCH] Package Contents

### Distribution Directory Structure
```
dist/
├── source_only_v7_1.zip           # Source-only package
├── everything_v7_1.zip            # Complete repository package
├── FULL_HARVEST_MANIFEST.json     # Complete file manifest with hashes
├── SHA256SUMS                      # SHA256 checksums for verification
└── *.parts.json                    # Part indexes (if archives are split)
```

### Verification Files
```
DOCS/report/
├── harvest_filelist.txt            # Complete file tree listing
├── merkle_root.txt                 # Merkle tree root hash
└── verification_evidence.md        # Build verification logs
```

## [START] Quick Start

### Option 1: PowerShell (Windows/Cross-platform)

```powershell
# Restore both packages with verification
.\scripts\restore_full_harvest.ps1

# Restore only source package
.\scripts\restore_full_harvest.ps1 -SourceOnly

# Restore to custom directory
.\scripts\restore_full_harvest.ps1 -TargetDir "MyRestore"

# Skip verification (not recommended)
.\scripts\restore_full_harvest.ps1 -Verify:$false
```

### Option 2: Bash (Linux/macOS/WSL)

```bash
# Restore both packages with verification
bash scripts/restore_full_harvest.sh

# Restore only source package
bash scripts/restore_full_harvest.sh --source-only

# Restore to custom directory
bash scripts/restore_full_harvest.sh --target MyRestore

# Skip verification (not recommended)
bash scripts/restore_full_harvest.sh --no-verify
```

## [PLAN] Detailed Instructions

### Step 1: Pre-restoration Verification

Before extraction, verify package integrity:

```bash
# Navigate to the distribution directory
cd dist/

# Verify all checksums
sha256sum -c SHA256SUMS
# OR on macOS:
shasum -a 256 -c SHA256SUMS
```

Expected output:
```
source_only_v7_1.zip: OK
everything_v7_1.zip: OK
FULL_HARVEST_MANIFEST.json: OK
```

### Step 2: Manual Archive Inspection

Inspect archive contents without extraction:

```bash
# List source-only archive contents
unzip -l source_only_v7_1.zip | head -20

# List everything archive contents  
unzip -l everything_v7_1.zip | head -20

# Check file counts
unzip -l source_only_v7_1.zip | tail -1
unzip -l everything_v7_1.zip | tail -1
```

### Step 3: Restoration

Choose your restoration method:

#### Automated Restoration (Recommended)

**PowerShell:**
```powershell
# Full restoration with verification
.\scripts\restore_full_harvest.ps1

# Custom options
.\scripts\restore_full_harvest.ps1 -TargetDir "WatchLockAI_v7_1" -DistDir "./dist"
```

**Bash:**
```bash
# Full restoration with verification
bash scripts/restore_full_harvest.sh

# Custom options
bash scripts/restore_full_harvest.sh --target "WatchLockAI_v7_1" --dist "./dist"
```

#### Manual Restoration

```bash
# Create restoration directories
mkdir -p WatchLockAI_Sentinel_Restored_source_only
mkdir -p WatchLockAI_Sentinel_Restored_everything

# Extract source-only package
unzip -q source_only_v7_1.zip -d WatchLockAI_Sentinel_Restored_source_only/

# Extract everything package
unzip -q everything_v7_1.zip -d WatchLockAI_Sentinel_Restored_everything/

# Verify extraction
find WatchLockAI_Sentinel_Restored_source_only -type f | wc -l  # Should be 467
find WatchLockAI_Sentinel_Restored_everything -type f | wc -l   # Should be 470
```

## [U+1F527] Advanced Features

### Handling Split Archives

For archives exceeding 1GB (automatically split):

1. **Automatic Reassembly**: Both scripts automatically detect and reassemble split archives
2. **Manual Reassembly**: 
   ```bash
   # Check for parts index
   ls *.parts.json
   
   # Manual reassembly example (if everything_v7_1.zip was split)
   cat everything_v7_1.zip.part* > everything_v7_1.zip
   ```

### Verification Levels

1. **Full Verification** (default):
   - SHA256SUMS verification
   - Part integrity checking (if applicable)
   - File count validation

2. **Quick Verification**:
   ```bash
   # Skip SHA256 verification (faster but less secure)
   bash scripts/restore_full_harvest.sh --no-verify
   ```

3. **Manual Deep Verification**:
   ```bash
   # Compare against manifest
   python3 -c "
   import json
   with open('FULL_HARVEST_MANIFEST.json') as f:
       manifest = json.load(f)
   print(f'Source files: {manifest[\"source_package\"][\"files_count\"]}')
   print(f'Everything files: {manifest[\"everything_package\"][\"files_count\"]}')
   print(f'Build timestamp: {manifest[\"build_timestamp\"]}')
   "
   ```

## [TARGET] Expected Results

### Successful Restoration Output

**PowerShell:**
```
[U+1F527] Full Harvest v7.1 Restoration Script
=============================================
[SEARCH] Verifying SHA256SUMS...
  [PASS] source_only_v7_1.zip
  [PASS] everything_v7_1.zip
  [PASS] FULL_HARVEST_MANIFEST.json
[PASS] SHA256 verification passed!
[PKG] Extracting source-only package...
  [PASS] Extracted 467 files (XX,XXX,XXX bytes)
[PKG] Extracting everything package...
  [PASS] Extracted 470 files (XX,XXX,XXX bytes)

=============================================
[PASS] RESTORATION COMPLETE
   Files restored: 937
   Total bytes: XX,XXX,XXX
   Target directories created
     - WatchLockAI_Sentinel_Restored_source_only
     - WatchLockAI_Sentinel_Restored_everything
[U+1F7E2] OK - Full Harvest v7.1 restoration successful!
=============================================
```

### Directory Structure After Restoration

```
WatchLockAI_Sentinel_Restored_source_only/
├── DOCS/
├── tools/
├── tests/
├── app_core/
├── console/
├── detection/
├── collectors/
├── plugins/
├── service/
├── ui/
└── ... (467 total files)

WatchLockAI_Sentinel_Restored_everything/
├── (same as above, plus)
├── dist/
│   ├── source_only_v7_1.zip
│   ├── everything_v7_1.zip
│   └── ... (470 total files)
```

## [TOOL] Troubleshooting

### Common Issues

#### 1. **Permission Denied Errors**
```bash
# Linux/macOS: Add execute permissions
chmod +x scripts/restore_full_harvest.sh

# Alternative: Run with bash directly
bash scripts/restore_full_harvest.sh
```

#### 2. **SHA256 Verification Failures**
```bash
# Check file integrity
ls -la dist/
sha256sum dist/source_only_v7_1.zip dist/everything_v7_1.zip

# Compare with expected checksums
cat dist/SHA256SUMS
```

#### 3. **Extraction Failures**
```bash
# Check available disk space
df -h .

# Test archive integrity
unzip -t source_only_v7_1.zip
unzip -t everything_v7_1.zip
```

#### 4. **Missing Utilities**
```bash
# Install required utilities (Ubuntu/Debian)
sudo apt install unzip sha256sum

# Install required utilities (macOS)
brew install coreutils
```

### Recovery Procedures

#### Complete Re-download
If verification consistently fails:
1. Re-download all harvest files
2. Verify network integrity
3. Check storage device health

#### Partial Recovery
If only one archive fails:
```bash
# Restore only the working archive
bash scripts/restore_full_harvest.sh --source-only
# OR
bash scripts/restore_full_harvest.sh --everything
```

## [LOCK] Security Considerations

### Verification Best Practices

1. **Always verify SHA256SUMS** before extraction
2. **Check file counts** against manifest
3. **Verify restoration environment** is clean
4. **Use official restoration scripts** when possible

### Trust Chain

```
Deterministic Build -> SHA256SUMS -> Merkle Root -> Verification Evidence
SOURCE_DATE_EPOCH=1700000000 -> Reproducible Packages -> Verified Restoration
```

## [U+1F4DA] Integration with VS Code

After successful restoration:

1. **Open in VS Code**:
   ```bash
   code WatchLockAI_Sentinel_Restored_source_only/
   ```

2. **Verify Python Environment**:
   ```bash
   cd WatchLockAI_Sentinel_Restored_source_only/
   python -m py_compile $(find . -name "*.py")
   ```

3. **Check Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

## [PASS] Verification Checklist

- [ ] SHA256SUMS verification passed
- [ ] Source package extracted (467 files expected)
- [ ] Everything package extracted (470 files expected) 
- [ ] No extraction errors reported
- [ ] Directory structure matches expected layout
- [ ] Python files compile without syntax errors
- [ ] All restoration scripts executed successfully

## [U+1F4DE] Support Information

**Restoration Script Issues**: Check script help output with `--help` or `-h`
**Verification Problems**: Examine `DOCS/report/verification_evidence.md`
**Build Information**: Review `FULL_HARVEST_MANIFEST.json`

---

*Full Harvest v7.1 - Deterministic, Self-Verifying, VS Code Ready*  
*Generated: 2025-09-08T02:43:XX UTC (SOURCE_DATE_EPOCH=1700000000)*