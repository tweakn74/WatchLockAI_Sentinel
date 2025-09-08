# Registry Monitor — Spec (Windows only)

Purpose: Watch common persistence keys.

Config:
- watch_keys: 
  - "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
  - "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
  - "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"
  - "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"
- method: 'notify'|'polling' (default 'notify')

Behavior:
- Prefer RegNotifyChangeKeyValue (pywin32). Fallback polling every 2s.
- Emit RegistryEvent@v1 with value_name, type, data_preview (truncate to 200 chars).
- Log access errors but continue.