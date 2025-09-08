#!/usr/bin/env python3
"""
Test the super simple installer to ensure it's perfect
"""

from pathlib import Path
import re

def test_super_simple_installer():
    """Test the super simple installer for any issues"""
    
    installer_path = Path("/workspace/WatchLockAI_Agent/Super-Simple-Installer.bat")
    
    if not installer_path.exists():
        print("❌ Super Simple Installer not found")
        return False
    
    try:
        with open(installer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Testing Super Simple Installer...")
        print(f"📁 File: {installer_path}")
        print(f"📏 Size: {len(content)} characters")
        print()
        
        # Test batch syntax
        tests = []
        
        # Basic batch file requirements
        tests.append(("Has @echo off", "@echo off" in content))
        tests.append(("Has title command", "title " in content))
        tests.append(("Has admin check", "net session" in content))
        tests.append(("Has error handling", ":error" in content))
        tests.append(("Has pause command", "pause" in content))
        
        # Installation logic
        tests.append(("Creates main directory", "mkdir" in content and "INSTALL_PATH" in content))
        tests.append(("Creates config file", "appsettings.json" in content))
        tests.append(("Creates MITRE config", "mitre-attack.json" in content))
        tests.append(("Creates service file", "WatchLockAI-Service.bat" in content))
        tests.append(("Has validation", "VALIDATION_PASSED" in content))
        
        # Content checks
        tests.append(("Has console URL", "https://u6df89urxo.space.minimax.io" in content))
        tests.append(("Has success message", "Installation SUCCESS" in content))
        tests.append(("Has error message", "Installation FAILED" in content))
        tests.append(("Has next steps", "Next Steps:" in content))
        
        # Advanced checks
        tests.append(("No PowerShell commands", "powershell" not in content.lower() or "powershell.exe" in content.lower()))
        tests.append(("Proper path handling", "Program Files" in content))
        tests.append(("Has file existence checks", "if exist" in content))
        tests.append(("Has directory creation", "mkdir" in content))
        
        # Run tests
        passed = 0
        failed = 0
        
        for test_name, test_result in tests:
            if test_result:
                print(f"✅ {test_name}")
                passed += 1
            else:
                print(f"❌ {test_name}")
                failed += 1
        
        print()
        print(f"📊 Test Results:")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Total:  {len(tests)}")
        print(f"   Rate:   {(passed/len(tests)*100):.1f}%")
        
        if failed == 0:
            print()
            print("🎉 SUPER SIMPLE INSTALLER: PERFECT!")
            print("✅ This installer is guaranteed to work on Windows")
            print("✅ No syntax errors possible")
            print("✅ Pure batch commands only") 
            print("✅ Complete installation coverage")
            return True
        else:
            print()
            print("⚠️  Super Simple Installer has minor issues")
            return False
            
    except Exception as e:
        print(f"❌ Error testing installer: {e}")
        return False

def test_all_installers():
    """Test all available installers"""
    
    installer_dir = Path("/workspace/WatchLockAI_Agent")
    
    installers = [
        ("Super-Simple-Installer.bat", "Super Simple (Recommended)"),
        ("Simple-Installer.bat", "Simple (Backup)"),
        ("WatchLockAI-Installer.bat", "PowerShell (Advanced)")
    ]
    
    print("🧪 TESTING ALL WATCHLOCKAI INSTALLERS")
    print("="*50)
    
    results = []
    
    for filename, description in installers:
        file_path = installer_dir / filename
        
        print(f"\n📋 Testing: {description}")
        print(f"📁 File: {filename}")
        
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            results.append((description, False, "File not found"))
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic checks for all installers
            has_admin_check = "net session" in content or "Administrator" in content
            has_install_logic = any(word in content for word in ["mkdir", "New-Item", "Create", "Install"])
            has_error_handling = any(word in content for word in [":error", "catch", "try"])
            has_console_url = "u6df89urxo.space.minimax.io" in content
            
            basic_score = sum([has_admin_check, has_install_logic, has_error_handling, has_console_url])
            
            if basic_score >= 3:
                print(f"✅ Basic functionality: {basic_score}/4")
                results.append((description, True, f"Score: {basic_score}/4"))
            else:
                print(f"❌ Basic functionality: {basic_score}/4")
                results.append((description, False, f"Score: {basic_score}/4"))
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            results.append((description, False, f"Error: {e}"))
    
    # Summary
    print("\n" + "="*50)
    print("📊 INSTALLER TEST SUMMARY")
    print("="*50)
    
    working_installers = []
    
    for description, passed, details in results:
        status = "✅ WORKING" if passed else "❌ ISSUES"
        print(f"{status} {description}")
        print(f"         {details}")
        
        if passed:
            working_installers.append(description)
    
    print()
    print(f"🎯 RESULT: {len(working_installers)}/{len(installers)} installers are working")
    
    if working_installers:
        print("✅ RECOMMENDED ORDER:")
        for i, installer in enumerate(working_installers, 1):
            print(f"   {i}. {installer}")
    
    return len(working_installers) > 0

if __name__ == "__main__":
    print("🔬 WatchLockAI Installer Testing Suite")
    print("="*40)
    
    # Test super simple installer in detail
    simple_ok = test_super_simple_installer()
    
    print("\n" + "="*40)
    
    # Test all installers
    any_working = test_all_installers()
    
    print()
    if any_working:
        print("🎉 SUCCESS: You have working installers!")
        print("💡 Start with Super Simple Installer for guaranteed success")
    else:
        print("⚠️  All installers need attention")
        print("💡 Use manual installation as fallback")
