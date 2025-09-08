# Alerts — Spec

Outputs:
- JSONL at `logs/alerts.jsonl`
- Windows toast notifications (if enabled in config)
- Tray UI list of last 10 alerts

Each DetectionAlert@v1 includes:
- id (uuid4)
- ts
- severity: 'low'|'medium'|'high'
- category: 'ransomware'|'persistence'|'process'|'network'|'health'|'general'
- tag: short slug
- entities: dict (e.g., path, pid, key_path)
- confidence: float (0..1)  # default 0.8 unless ML score provided
- rationale: str
- provenance:
    file: "rules_engine_spec.md"
    section: "RansomwareBurstV1"
    lines: Optional[str]  # if available
- suggested_actions: list[str]  # human-readable, non-destructive by default