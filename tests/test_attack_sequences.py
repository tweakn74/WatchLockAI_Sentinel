import os, unittest
from importlib.util import find_spec

def _skip(msg): return unittest.skip(msg)

HAS_BUS   = bool(find_spec("app_core")) and bool(find_spec("app_core.bus"))
HAS_ATTACK= bool(find_spec("detection")) and bool(find_spec("detection.attack_matrix"))

@unittest.skipUnless(HAS_BUS and HAS_ATTACK, "core modules missing")
class TestAttackSequences(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault("MITRE_MATRIX_ENABLED","1")
        os.environ.setdefault("MITRE_RULES_PATH","DOCS/mitre/rules/rc3_baseline.yaml")

        from app_core.bus import EventBus
        from detection import attack_matrix as am
        self.bus = EventBus()
        self.alerts = []

        # Subscribe to AlertEvent if available
        try:
            from app_core.schemas import AlertEvent
            self.bus.subscribe(AlertEvent, lambda evt: self.alerts.append(evt))
        except Exception:
            # Fallback: capture any object with rule_id attribute via generic callback
            def _catch(evt):
                if hasattr(evt, "rule_id") or hasattr(evt, "id"):
                    self.alerts.append(evt)
            try:
                self.bus.subscribe(object, _catch)
            except Exception:
                pass

        am.wire(self.bus)

    def _mk(self, name, **kwargs):
        cls = type(name, (), {})
        obj = cls()
        for k,v in kwargs.items(): setattr(obj,k,v)
        return obj

    def test_bruteforce_sequence(self):
        # 5 fails then success within window
        for _ in range(5):
            self.bus.publish(self._mk("AuthEvent", username="alice", src_ip="1.2.3.4", success=False))
        self.bus.publish(self._mk("AuthEvent", username="alice", src_ip="1.2.3.4", success=True))
        s = str(self.alerts)
        self.assertTrue(("ATTK-BRUTE-SEQUENCE" in s) or any(getattr(a,"rule_id", "")=="ATTK-BRUTE-SEQUENCE" for a in self.alerts))

    def test_phish_sequence(self):
        self.bus.publish(self._mk("EmailEvent", recipient="bob", has_attachment=True, file_type="docm"))
        self.bus.publish(self._mk("ProcEvent", user="bob", parent_process="winword.exe", child_process="powershell.exe"))
        s = str(self.alerts)
        self.assertTrue(("ATTK-PHISH-SEQUENCE" in s) or any(getattr(a,"rule_id", "")=="ATTK-PHISH-SEQUENCE" for a in self.alerts))

    def test_ransom_sequence(self):
        for i in range(120):
            self.bus.publish(self._mk("FileEvent", op="create", process="evil.exe", path=f"/tmp/f{i}.txt"))
        self.bus.publish(self._mk("NetworkEvent", process="evil.exe", bytes_out=60_000_000, dst_asn_rare=True))
        s = str(self.alerts)
        self.assertTrue(("ATTK-RANSOM-SEQUENCE-CHAIN" in s) or any(getattr(a,"rule_id", "")=="ATTK-RANSOM-SEQUENCE-CHAIN" for a in self.alerts))

if __name__ == "__main__":
    unittest.main()