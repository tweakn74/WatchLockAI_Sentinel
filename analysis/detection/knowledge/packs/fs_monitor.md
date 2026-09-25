# File System Monitor -- Spec

Purpose: Observe user-configured directories for create/modify/delete/rename. 
Prefer OS notifications via watchdog; fallback to polling.

Config shape (document in app_core/config.py):
- paths: list[str]
- exclude_globs: list[str]
- method: 'watchdog'|'polling'
- compute_entropy: bool (default false)
- compute_hash_small_files: bool (default false)
- small_file_threshold_bytes: int (default 1_048_576)
- burst_window_sec: int (default 10) for rules

Behavior:
- On each event, emit FileEvent@v1.
- Entropy: if enabled and file size <= small_file_threshold, compute Shannon byte-entropy.
- Hash: if enabled and file size <= small_file_threshold, compute SHA-256.
- Apply exclude_globs before any heavy work.
- Include best-effort proc attribution on Windows by mapping open handles or recent proc I/O (best-effort; may be None).

Performance:
- Debounce rapid rename pairs (rename emits 'renamed' with old_path).
- Backpressure-safe: queue -> app_core.bus (async).