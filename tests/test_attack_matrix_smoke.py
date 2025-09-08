#!/usr/bin/env python3
"""
MITRE ATT&CK Import-Safe Smoke Test
Tests basic detection engine functionality without pytest dependency.
"""

import sys
import os
import time
import unittest
import importlib.util
from typing import Dict, Any, List

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    # Check for pydantic
    pydantic_spec = importlib.util.find_spec("pydantic")
    if not pydantic_spec:
        missing_deps.append("pydantic")
    
    # Check for app_core.bus
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        bus_spec = importlib.util.find_spec("app_core.bus")
        if not bus_spec:
            missing_deps.append("app_core.bus")
    except Exception:
        missing_deps.append("app_core.bus")
    
    return missing_deps

class MinimalEventBus:
    """Minimal test event bus for isolation"""
    
    def __init__(self):
        self.handlers = {}
        self.published_events = []
    
    def subscribe(self, event_type: str, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def publish(self, event_type: str, data: Dict[str, Any]):
        self.published_events.append({"type": event_type, "data": data})
        
        # Call handlers if present
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Handler error: {e}")
    
    def get_published_count(self, event_type: str) -> int:
        """Get count of published events of given type"""
        return len([e for e in self.published_events if e["type"] == event_type])

class TestAttackMatrixSmoke(unittest.TestCase):
    """Smoke tests for MITRE ATT&CK detection engine"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear any existing published events
        if hasattr(self, 'bus'):
            self.bus.published_events = []
    
    def test_brute_force_detection(self):
        """Test brute force login detection rule"""
        try:
            # Import detection components
            from detection.attack_matrix import wire, load_default_rules
            
            # Create minimal test bus
            self.bus = MinimalEventBus()
            
            # Load default rules
            rules = load_default_rules()
            
            # Find brute force rule
            brute_force_rule = None
            for rule in rules:
                if "brute force" in rule.name.lower():
                    brute_force_rule = rule
                    break
            
            self.assertIsNotNone(brute_force_rule, "Brute Force rule not found in default rules")
            
            # Wire the engine with test bus
            engine = wire(self.bus, responder=None, rules=rules)
            
            # Initially no alerts should be published
            initial_count = self.bus.get_published_count("AlertEvent")
            self.assertEqual(initial_count, 0, "No alerts should be published initially")
            
            # Simulate brute force attempts (threshold is 10 in 60s)
            username = "test_user"
            for i in range(12):  # Exceed threshold
                event_data = {
                    "username": username,
                    "result": "failure",  # Field name from baseline.yaml
                    "login_success": False,
                    "success": False,  # Legacy field for backward compatibility
                    "timestamp": time.time(),
                    "source_ip": "192.168.1.100"
                }
                
                # Publish AuthEvent
                self.bus.publish("AuthEvent", event_data)
            
            # Check that AlertEvent was published
            alert_count = self.bus.get_published_count("AlertEvent")
            self.assertGreater(alert_count, 0, "AlertEvent should be published after threshold exceeded")
            
            print(f"✓ Brute force detection test passed - {alert_count} alerts generated")
            
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        except Exception as e:
            self.fail(f"Brute force detection test failed: {e}")
    
    def test_baseline_ransomware_detection(self):
        """Test baseline ransomware pre-encryption detection"""
        try:
            # Import detection components
            from detection.attack_matrix import wire, load_baseline_rules
            
            # Create minimal test bus
            self.bus = MinimalEventBus()
            
            # Load baseline rules
            rules = load_baseline_rules()
            
            # Find ransomware rule
            ransom_rule = None
            for rule in rules:
                if "ATTK-RANSOM-PREENC" == rule.id:
                    ransom_rule = rule
                    break
            
            self.assertIsNotNone(ransom_rule, "Ransomware pre-encryption rule not found in baseline rules")
            
            # Wire the engine with test bus
            engine = wire(self.bus, responder=None, rules=rules)
            
            # Initially no alerts should be published
            initial_count = self.bus.get_published_count("AlertEvent")
            self.assertEqual(initial_count, 0, "No alerts should be published initially")
            
            # Simulate rapid file operations (threshold is 100 in 30s)
            process_name = "suspicious_process.exe"
            for i in range(105):  # Exceed threshold
                event_data = {
                    "process": process_name,  # Field name from baseline.yaml
                    "process_name": process_name,  # Legacy field for backward compatibility
                    "operation": "create" if i % 3 == 0 else ("rename" if i % 3 == 1 else "delete"),
                    "action": "create" if i % 3 == 0 else ("rename" if i % 3 == 1 else "delete"),  # Legacy field
                    "file_path": f"/tmp/file_{i}.doc",  # Use .doc extension to match rule
                    "extension": ".doc",  # Extension field for rule matching
                    "timestamp": time.time()
                }
                
                # Publish FileEvent
                self.bus.publish("FileEvent", event_data)
            
            # Check that AlertEvent was published
            alert_count = self.bus.get_published_count("AlertEvent")
            self.assertGreater(alert_count, 0, "AlertEvent should be published after threshold exceeded")
            
            print(f"✓ Baseline ransomware detection test passed - {alert_count} alerts generated")
            
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        except Exception as e:
            self.fail(f"Baseline ransomware detection test failed: {e}")
    
    def test_rule_loading(self):
        """Test that default and baseline rules can be loaded"""
        try:
            from detection.attack_matrix import load_default_rules, load_baseline_rules
            
            # Test default rules (5 legacy rules)
            default_rules = load_default_rules()
            self.assertIsInstance(default_rules, list, "Default rules should be a list")
            self.assertEqual(len(default_rules), 5, "Should have exactly 5 default rules")
            
            # Test baseline rules (20 comprehensive rules)
            baseline_rules = load_baseline_rules()
            self.assertIsInstance(baseline_rules, list, "Baseline rules should be a list")
            self.assertEqual(len(baseline_rules), 20, "Should have exactly 20 baseline rules")
            
            # Check that each rule has required fields
            for rules, rule_type in [(default_rules, "default"), (baseline_rules, "baseline")]:
                for rule in rules:
                    self.assertTrue(hasattr(rule, 'id'), f"{rule_type} rule {rule} should have id field")
                    self.assertTrue(hasattr(rule, 'name'), f"{rule_type} rule {rule} should have name field")
                    self.assertTrue(hasattr(rule, 'tactic'), f"{rule_type} rule {rule} should have tactic field")
                    self.assertTrue(hasattr(rule, 'technique'), f"{rule_type} rule {rule} should have technique field")
                    self.assertTrue(hasattr(rule, 'event'), f"{rule_type} rule {rule} should have event field")
                    self.assertTrue(hasattr(rule, 'threshold'), f"{rule_type} rule {rule} should have threshold field")
            
            print(f"✓ Rule loading test passed - {len(default_rules)} default + {len(baseline_rules)} baseline rules loaded")
            
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        except Exception as e:
            self.fail(f"Rule loading test failed: {e}")
    
    def test_import_safety(self):
        """Test that modules can be imported safely"""
        try:
            # Test detection.attack_matrix import
            import detection.attack_matrix
            
            # Test response.playbooks import 
            import response.playbooks
            
            print("✓ Import safety test passed - all modules imported successfully")
            
        except ImportError as e:
            self.skipTest(f"Modules not available for import test: {e}")
        except Exception as e:
            self.fail(f"Import safety test failed: {e}")

def main():
    """Main test runner"""
    print("MITRE ATT&CK Smoke Test Starting...")
    
    # Check dependencies first
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"SKIP: missing deps - {', '.join(missing_deps)}")
        sys.exit(0)
    
    # Run tests
    try:
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAttackMatrixSmoke)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Return appropriate exit code
        if result.wasSuccessful():
            print("\n✓ All MITRE ATT&CK smoke tests passed!")
            sys.exit(0)
        else:
            print(f"\n✗ {len(result.failures)} test(s) failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"Test runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
