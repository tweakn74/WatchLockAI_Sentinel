# Health Monitor — Spec

Purpose: Report host health and generate HealthAlert@v1 when thresholds crossed.

Config:
- cpu_warn: int (default 90)
- ram_warn: int (default 90)
- disk_warn_pct_free: int (default 5)
- temp_warn_c: Optional[float]

Behavior:
- Sample every 5s. Emit HealthMetric@v1.
- If metric exceeds warn threshold, emit DetectionAlert@v1 with category='health'.