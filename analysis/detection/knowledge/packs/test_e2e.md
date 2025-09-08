# E2E Test Scenario — Spec

Goal: Prove pipeline wiring without destructive actions.

Scenario:
1) Start app in non-service mode with default config (file_monitor on a temp directory).
2) Create 10 small files in temp dir over 2 seconds, then modify 5 of them.
3) Expect:
   - FileEvent@v1 count >= 15 in logs
   - No ransomware alert (threshold is 120 in 10s)
   - 1 health metric observed
4) Verify an alert of type 'health' can be forced by setting cpu_warn=0 in a test config.
Record results to `DOCS/Build_Manifest.json`.