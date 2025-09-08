# Actions — Spec

Default: Non-destructive. Destructive actions require `responses.allow_destructive_actions=true`.

Supported actions:
- terminate_process(pid): only if config enabled; log success/failure.
- pause_monitoring(seconds): always allowed.
- quarantine_directory(path): STUB ONLY — do not implement until explicitly specified.

UI requires explicit user click/consent before any destructive action. Log the consent event.