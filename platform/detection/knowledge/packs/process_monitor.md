# Process Monitor -- Spec

Purpose: Track process starts/exits, parent/child linkage, and basic metadata.

Config:
- poll_interval_ms: int (default 1000)
- capture_hash: bool (default false)  # hashing exe is optional; skip if locked/slow

Behavior:
- On new PID observed -> ProcessEvent@v1(event_type='started').
- On missing prior PID -> ProcessEvent@v1(event_type='exited').
- Attempt exe path, cmdline, username. Hash exe if capture_hash true and file size < 64MB.
- Maintain in-memory pid->ppid map for ancestry checks.