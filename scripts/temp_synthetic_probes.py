import os
os.environ["MITRE_MATRIX_ENABLED"]="1"
os.environ["MITRE_PROFILE"]="baseline"

try:
    from app_core.bus import EventBus
    from detection import attack_matrix as am
    from datetime import datetime

    bus=EventBus()
    alerts=[]
    
    # Try to subscribe to AlertEvent if available
    try:
        from app_core.schemas import AlertEvent
        bus.subscribe(AlertEvent, lambda e: alerts.append(e))
    except Exception: 
        # Fallback for any alert-like object
        def capture_alert(e):
            if hasattr(e, 'rule_id') or hasattr(e, 'id') or 'alert' in str(type(e)).lower():
                alerts.append(e)
        bus.subscribe(object, capture_alert)
    
    # Wire the engine
    am.wire(bus)
    
    # Test BRUTE-LOGIN: 10 failed logins for same user
    for i in range(10):
        e=type("AuthEvent",(),{})()
        e.username="alice"
        e.src_ip="10.0.0.5"
        e.result="failure"  # Based on baseline.yaml where clause
        e.success=False
        bus.publish(e)
    
    # Test RANSOM-PREENC: 120 file operations by same process 
    for i in range(120):
        f=type("FileEvent",(),{})()
        f.operation="create"
        f.op="create"  # Alternative field name
        f.process="suspicious.exe"
        f.path=f"/d/file_{i}.doc"
        f.extension=".doc"
        bus.publish(f)
    
    print("ALERTS_LEN", len(alerts))
    print("OK" if len(alerts)>=2 else "LOW_ALERT_COUNT")
    
    # Debug info
    for alert in alerts:
        if hasattr(alert, 'rule_id'):
            print(f"ALERT: {alert.rule_id}")
        elif hasattr(alert, 'id'):
            print(f"ALERT: {alert.id}")
        else:
            print(f"ALERT: {type(alert)}")

except Exception as e:
    print(f"PROBE_ERROR: {e}")
    import traceback
    traceback.print_exc()