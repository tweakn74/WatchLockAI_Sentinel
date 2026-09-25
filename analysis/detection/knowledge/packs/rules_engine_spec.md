# Rules & Policy -- Authoritative Definitions

Evaluation: Subscribe to event bus, maintain small rolling windows in-memory. 
Each alert must include `rationale` and `provenance` (this file + section heading).

## Rule: RansomwareBurstV1
provenance: rules_engine_spec.md#ransomwareburstv1
inputs: FileEvent@v1
config:
  burst_window_sec: 10
  min_suspicious_events: 120
  min_entropy: 7.2           # only if entropy present
  diverse_extensions: true   # >= 15 distinct new extensions in window
logic:
  - maintain a deque of FileEvent within window
  - count created/modified events; if >= min_suspicious_events AND
    (entropy criterion satisfied when available) AND
    (if diverse_extensions: count of distinct file extensions >= 15)
    => raise DetectionAlert@v1 with severity="high", tag="ransomware-io-burst"
rationale:
  "High-rate file churn with high-entropy writes across diverse extensions."

## Rule: NewAutostartPersistenceV1
provenance: rules_engine_spec.md#newautostartpersistencev1
inputs: RegistryEvent@v1
logic:
  - If hive/key matches any configured autostart key AND event_type in ['created','modified']
    => severity="medium", tag="persistence-autostart"
rationale:
  "Autostart location modified."

## Rule: SuspiciousParentChildV1
provenance: rules_engine_spec.md#suspiciousparentchildv1
inputs: ProcessEvent@v1 (+ ancestry map)
config:
  suspicious_parents: ["office", "winword", "excel", "powerpnt"]
  suspicious_children: ["cmd.exe","powershell.exe","wscript.exe","cscript.exe","mshta.exe","rundll32.exe"]
logic:
  - On process start: if parent exe basename contains any suspicious_parents AND child exe basename in suspicious_children
    => severity="high", tag="macro-spawn-shell"
rationale:
  "Office app spawned a scripting shell."

## Rule: RareEgressSpikeV1
provenance: rules_engine_spec.md#rareegressspikev1
inputs: NetworkEvent@v1
config:
  port_thresholds:
    high_risk: [4444, 4445, 8081, 8443]
  distinct_remote_ips_in_window: 50
  window_sec: 60
logic:
  - Maintain sliding window per pid; if distinct remote IPs >= threshold OR
    raddr_port in high_risk => severity="medium", tag="egress-anomaly"
rationale:
  "Unusual egress pattern for process."

## Rule: HealthDegradationComboV1
provenance: rules_engine_spec.md#healthdegradationcombov1
inputs: HealthMetric@v1 + FileEvent@v1
logic:
  - If cpu_pct > 95 and within 10s a file churn > 200 ops occurs
    => severity="low", tag="resource-burn-file-churn"
rationale:
  "CPU pinned coincident with file churn."