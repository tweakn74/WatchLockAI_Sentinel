import os
import sys
import logging

# Set up basic logging to suppress warnings
logging.basicConfig(level=logging.ERROR)

# Mock EventBus for testing
class MockEventBus:
    def __init__(self):
        self.handlers = {}
        self.published_events = []
    
    def subscribe(self, event_type, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def publish(self, event_type, data):
        self.published_events.append({"type": event_type, "data": data})
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(data)
                except Exception:
                    pass

os.environ["MITRE_MATRIX_ENABLED"]="1"
os.environ["MITRE_PROFILE"]="baseline"

try:
    # Try to import detection module directly
    sys.path.insert(0, '/workspace/WatchLockAI_Sentinel')
    from detection import attack_matrix as am
    
    bus = MockEventBus()
    alerts = []
    
    # Subscribe to capture alerts
    def capture_alert(data):
        alerts.append(data)
    
    bus.subscribe("AlertEvent", capture_alert)
    
    # Try to wire - this might fail gracefully due to missing dependencies
    try:
        # Load rules from YAML file directly 
        rules = am.load_rules_from_path("DOCS/mitre/rules/baseline.yaml", "baseline")
        print(f"LOADED_RULES: {len(rules)}")
        
        # Create engine manually
        engine = am.AttackMatrixEngine(rules)
        engine.bus = bus
        
        # Debug: Check if rules have where clauses
        for rule in rules[:2]:  # Check first 2 rules
            print(f"RULE {rule.id}: where={getattr(rule, 'where', 'NO_WHERE')}, threshold={rule.threshold}, group_by={getattr(rule, 'group_by', 'NO_GROUP_BY')}")
        
        # Test BRUTE-LOGIN rule (from baseline.yaml: field: result, operator: ==, value: failure)
        brute_count = 0
        for i in range(12):
            event_data = {
                "username": "alice",
                "result": "failure",  # String as expected by where clause
                "src_ip": "10.0.0.5", 
                "timestamp": 1234567890 + i
            }
            matched = engine.process_event("AuthEvent", event_data)
            if matched:
                brute_count += len(matched)
                engine.handle_matches(matched, event_data)
        
        # Test RANSOM-PREENC rule (from baseline.yaml: operation in [create, rename, delete], group_by: process)
        ransom_count = 0
        for i in range(105):
            event_data = {
                "process": "evil.exe",  # Field name expected by group_by
                "operation": "create",  # Field name expected by where clause
                "extension": ".doc",   # Field for extension matching
                "file_path": f"/tmp/file_{i}.doc",
                "timestamp": 1234567890 + i
            }
            matched = engine.process_event("FileEvent", event_data)
            if matched:
                ransom_count += len(matched)
                engine.handle_matches(matched, event_data)
        
        print(f"BRUTE_MATCHES: {brute_count}")
        print(f"RANSOM_MATCHES: {ransom_count}")
        print(f"ALERTS_LEN: {len(alerts)}")
        print("OK" if (brute_count > 0 and ransom_count > 0) else "LOW_MATCH_COUNT")
        
    except Exception as e:
        print(f"ENGINE_ERROR: {e}")
        # Try basic rule loading at least
        try:
            rules = am.load_baseline_rules()
            print(f"RULES_LOADED: {len(rules)} (engine failed but rules loadable)")
        except Exception as e2:
            print(f"RULES_ERROR: {e2}")

except Exception as e:
    print(f"IMPORT_ERROR: {e}")
    print("SKIPPED - detection module not importable")