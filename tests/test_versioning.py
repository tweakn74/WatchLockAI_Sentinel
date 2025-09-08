"""Tests for P5-001 versioning and changelog discipline."""

import os
import re
import unittest
from pathlib import Path


class TestVersioning(unittest.TestCase):
    """Test version parsing and changelog validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.version_file = self.repo_root / "VERSION"
        self.changelog_file = self.repo_root / "CHANGELOG.md"
    
    def test_version_file_exists(self):
        """Test that VERSION file exists and is readable."""
        self.assertTrue(self.version_file.exists(), "VERSION file must exist")
        self.assertTrue(self.version_file.is_file(), "VERSION must be a file")
    
    def test_version_semver_format(self):
        """Test that VERSION follows semantic versioning format."""
        with open(self.version_file, 'r') as f:
            version = f.read().strip()
        
        # Semver pattern: MAJOR.MINOR.PATCH with optional pre-release and build metadata
        semver_pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        
        self.assertRegex(version, semver_pattern, 
                        f"VERSION '{version}' must follow semantic versioning format")
        
        # Additional sanity checks
        parts = version.split('.')
        self.assertEqual(len(parts), 3, "VERSION must have exactly 3 parts (MAJOR.MINOR.PATCH)")
        
        # Check that all parts are numeric (for basic versions)
        if '-' not in version and '+' not in version:
            for part in parts:
                self.assertTrue(part.isdigit(), f"Version part '{part}' must be numeric")
    
    def test_version_is_valid_python_version(self):
        """Test that version can be parsed by Python packaging tools."""
        try:
            from packaging.version import Version
            with open(self.version_file, 'r') as f:
                version_str = f.read().strip()
            
            parsed_version = Version(version_str)
            self.assertIsInstance(parsed_version, Version)
            
        except ImportError:
            # packaging not available, skip this test
            self.skipTest("packaging module not available")
        except Exception as e:
            self.fail(f"Version '{version_str}' cannot be parsed: {e}")
    
    def test_changelog_file_exists(self):
        """Test that CHANGELOG.md exists and is readable."""
        self.assertTrue(self.changelog_file.exists(), "CHANGELOG.md file must exist")
        self.assertTrue(self.changelog_file.is_file(), "CHANGELOG.md must be a file")
    
    def test_changelog_has_version_entry(self):
        """Test that CHANGELOG.md has an entry for the current version."""
        with open(self.version_file, 'r') as f:
            current_version = f.read().strip()
        
        with open(self.changelog_file, 'r') as f:
            changelog_content = f.read()
        
        # Look for version entry in changelog
        version_pattern = rf'\[{re.escape(current_version)}\]'
        self.assertRegex(changelog_content, version_pattern,
                        f"CHANGELOG.md must contain entry for version {current_version}")
    
    def test_changelog_format_valid(self):
        """Test that CHANGELOG.md follows proper markdown format."""
        with open(self.changelog_file, 'r') as f:
            content = f.read()
        
        # Should start with # Changelog
        self.assertTrue(content.startswith('# Changelog'), 
                       "CHANGELOG.md should start with '# Changelog'")
        
        # Should have version headers with dates
        version_header_pattern = r'## \[\d+\.\d+\.\d+[^\]]*\] - \d{4}-\d{2}-\d{2}'
        matches = re.findall(version_header_pattern, content)
        self.assertGreater(len(matches), 0, 
                          "CHANGELOG.md should have at least one version entry with date")
        
        # Should have Added/Changed/Fixed sections (at least one)
        sections = ['### Added', '### Changed', '### Fixed', '### Security']
        has_section = any(section in content for section in sections)
        self.assertTrue(has_section, 
                       "CHANGELOG.md should have at least one standard section")
    
    def test_release_notes_exist(self):
        """Test that release notes exist for recent versions."""
        with open(self.version_file, 'r') as f:
            current_version = f.read().strip()
        
        # Check for release notes file
        major_minor = '.'.join(current_version.split('.')[:2])
        release_notes_file = self.repo_root / f"RELEASE_NOTES_v{major_minor}.md"
        
        self.assertTrue(release_notes_file.exists(), 
                       f"Release notes file should exist: RELEASE_NOTES_v{major_minor}.md")
    
    def test_version_consistency(self):
        """Test that version is consistent across files."""
        with open(self.version_file, 'r') as f:
            version_file_version = f.read().strip()
        
        # Check if version appears in changelog
        with open(self.changelog_file, 'r') as f:
            changelog_content = f.read()
        
        self.assertIn(f'[{version_file_version}]', changelog_content,
                     f"Version {version_file_version} should appear in CHANGELOG.md")
        
        # Check if setup.py or pyproject.toml has version (if they exist)
        setup_py = self.repo_root / "setup.py"
        if setup_py.exists():
            with open(setup_py, 'r') as f:
                setup_content = f.read()
            # Look for version in setup.py
            version_patterns = [
                rf'version\s*=\s*["\'{version_file_version}["\']',
                rf'__version__\s*=\s*["\'{version_file_version}["\']'
            ]
            has_version = any(re.search(pattern, setup_content) for pattern in version_patterns)
            self.assertTrue(has_version, f"setup.py should contain version {version_file_version}")
    
    def test_version_progression(self):
        """Test that version follows logical progression in changelog."""
        with open(self.changelog_file, 'r') as f:
            content = f.read()
        
        # Extract all version numbers from changelog
        version_pattern = r'\[(\d+\.\d+\.\d+[^\]]*)\]'
        versions = re.findall(version_pattern, content)
        
        if len(versions) > 1:
            try:
                from packaging.version import Version
                parsed_versions = [Version(v) for v in versions]
                
                # Check that versions are in descending order (newest first)
                for i in range(len(parsed_versions) - 1):
                    self.assertGreater(parsed_versions[i], parsed_versions[i + 1],
                                     f"Versions should be in descending order: {versions[i]} > {versions[i + 1]}")
            except ImportError:
                # Skip version ordering check if packaging not available
                pass


if __name__ == '__main__':
    unittest.main()
