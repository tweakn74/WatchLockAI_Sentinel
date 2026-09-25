#!/usr/bin/env python3
"""
Update documentation to clearly distinguish between default C: drive installation
and optional custom D: drive examples
"""

from pathlib import Path

def update_installation_docs():
    """Update all documentation to clarify drive installation options"""
    
    base_path = Path("/workspace/WatchLockAI_Agent")
    
    # Update QUICK_START.md
    quick_start_path = base_path / "QUICK_START.md"
    if quick_start_path.exists():
        with open(quick_start_path, 'r') as f:
            content = f.read()
        
        # Update the advanced options section
        content = content.replace(
            '### Custom Installation Path\n```powershell\nWatchLockAI-Installer.ps1 -InstallPath "D:\\Security\\WatchLockAI"\n```',
            '''### Custom Installation Path (Advanced)
**Default**: Installs to `C:\\Program Files\\WatchLockAI` (recommended)

**Custom Path Example**: Only if you need a different location
```powershell
# Example: Install to D: drive (only if D: drive exists and has space)
WatchLockAI-Installer.ps1 -InstallPath "D:\\Security\\WatchLockAI"

# Example: Install to different C: drive location
WatchLockAI-Installer.ps1 -InstallPath "C:\\MyApps\\WatchLockAI"
```
[WARN] **Important**: Make sure the target drive exists and has at least 2GB free space!'''
        )
        
        with open(quick_start_path, 'w') as f:
            f.write(content)
        
        print("[PASS] Updated QUICK_START.md")
    
    # Update INSTALLATION_GUIDE.md
    install_guide_path = base_path / "INSTALLATION_GUIDE.md"
    if install_guide_path.exists():
        with open(install_guide_path, 'r') as f:
            content = f.read()
        
        # Update custom installation section
        content = content.replace(
            'WatchLockAI-Installer.ps1 -InstallPath "D:\\\\Security\\\\WatchLockAI"',
            '''### Default Installation (Recommended)
The installer automatically uses `C:\\Program Files\\WatchLockAI` - no parameters needed!

### Custom Installation Path (Advanced)
Only use custom paths if you have specific requirements:
```powershell
# Install to D: drive (ensure D: drive exists!)
WatchLockAI-Installer.ps1 -InstallPath "D:\\Security\\WatchLockAI"

# Install to custom C: drive location
WatchLockAI-Installer.ps1 -InstallPath "C:\\CustomApps\\WatchLockAI"
```'''
        )
        
        with open(install_guide_path, 'w') as f:
            f.write(content)
        
        print("[PASS] Updated INSTALLATION_GUIDE.md")
    
    # Update README_INSTALLER.md
    readme_path = base_path / "README_INSTALLER.md"
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Update the custom installation section
        content = content.replace(
            '.\\\\WatchLockAI-Installer.ps1 -InstallPath "D:\\\\WatchLockAI"',
            '''# Default installation (recommended)
.\\WatchLockAI-Installer.ps1

# Custom path example (advanced users only)
.\\WatchLockAI-Installer.ps1 -InstallPath "D:\\Security\\WatchLockAI"'''
        )
        
        with open(readme_path, 'w') as f:
            f.write(content)
        
        print("[PASS] Updated README_INSTALLER.md")

def create_drive_compatibility_info():
    """Create a specific file explaining drive compatibility"""
    
    base_path = Path("/workspace/WatchLockAI_Agent")
    
    drive_info = """# WatchLockAI Drive Installation Guide

## [TARGET] **Simple Answer: It Installs to C: Drive by Default**

### Default Installation (99% of users)
- **Path**: `C:\\Program Files\\WatchLockAI\\`
- **Why C: Drive**: Windows standard location for applications
- **No Setup Required**: Just run the installer - it handles everything!

## [U+1F4BE] **Drive Compatibility Explained**

### What Happens by Default
1. Installer checks `C:\\Program Files\\` for space
2. Creates `C:\\Program Files\\WatchLockAI\\` directory
3. Installs all files to C: drive
4. **Result**: WatchLockAI runs from your C: drive [PASS]

### When Would You Use D: Drive?
Custom installation is **only needed if**:
- You have a very small C: drive (less than 2GB free)
- Your organization requires apps on a specific drive
- You have custom IT policies

### How to Check Your Setup
```powershell
# Check C: drive space (default location)
Get-PSDrive C | Select-Object Name, @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}}

# Check if D: drive exists
Get-PSDrive D -ErrorAction SilentlyContinue
```

## [U+1F527] **Installation Options**

### Option 1: Default (Recommended) - C: Drive
```batch
# Just run the installer - installs to C: drive automatically
WatchLockAI-Installer.bat
```

### Option 2: Custom Path (Advanced Users Only)
```powershell
# Only if you specifically need D: drive
WatchLockAI-Installer.ps1 -InstallPath "D:\\Security\\WatchLockAI"

# Or different C: drive location
WatchLockAI-Installer.ps1 -InstallPath "C:\\MyApps\\WatchLockAI"
```

## [WARN] **Important Notes**

### Why Default C: Drive is Best
- [PASS] **Always Available**: Every Windows system has C: drive
- [PASS] **Proper Permissions**: Program Files has correct security
- [PASS] **Windows Standard**: Expected location for services
- [PASS] **Automatic Updates**: Windows Update and antivirus expect C: drive

### D: Drive Considerations
- [U+2753] **May Not Exist**: Not all computers have D: drive
- [U+2753] **Different Types**: Could be CD/DVD, USB, or network drive
- [U+2753] **Permission Issues**: May not have proper service permissions
- [WARN] **Use Only If**: You specifically know you need it

## [TARGET] **Bottom Line**

**Just use the default installer!** It will install to `C:\\Program Files\\WatchLockAI\\` which works on every Windows computer.

The D: drive examples in documentation are for advanced scenarios only.

## [SEARCH] **Quick Check**

If you're unsure about your system:
```powershell
# Run this to see your drives
Get-PSDrive -PSProvider FileSystem
```

Most systems show:
- **C:** - Main Windows drive (use this!)
- **D:** - May or may not exist

**Recommendation**: Use the default C: drive installation unless you have a specific technical requirement for a different location.
"""
    
    drive_guide_path = base_path / "DRIVE_INSTALLATION_GUIDE.md"
    with open(drive_guide_path, 'w') as f:
        f.write(drive_info)
    
    print("[PASS] Created DRIVE_INSTALLATION_GUIDE.md")

if __name__ == "__main__":
    print("Clarifying installation drive documentation...")
    update_installation_docs()
    create_drive_compatibility_info()
    print("\n[PASS] Documentation updated to clarify C: vs D: drive installation!")
    print("\nKey points:")
    print("- DEFAULT: C: drive (C:\\Program Files\\WatchLockAI)")
    print("- CUSTOM: D: drive examples are for advanced users only")
    print("- RECOMMENDATION: Use default C: drive installation")
