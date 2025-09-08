# WatchLockAI Sentinel — Master Feature Backlog (v1)

## Priority A — Control & Core Detection
1. Policies CRUD + ETag (No UI)
   - Endpoints: GET/PUT `/api/policies` with `If-Match` ETag, 412 on conflict.
   - Store: `config/policies_store.py` (atomic, thread-safe).
   - Models: `Policies`, `PolicyRule` (Pydantic).
   - Tests: load/save/etag conflict; schema validation.
   - Gates: ruff=0, pyright=0 (touched), non-regression.

2. Operational Mode UI (thin)
   - `console/templates/policies.html` shows radio group for mode + rules table (read-only rules in this phase).
   - JS fetches mode via `/api/operational_mode`.
   - No business logic in UI. Non-regression gates apply.

3. ThreatIntel DB v1 (read-only)
   - Pack-in ATT&CK/Kill Chain/NIST-SANS bundles; simple full-text index.
   - Endpoint: `GET /api/ti/search?q=term&limit=50`.
   - Deterministic search; no external network.
   - Tests for result shape + pagination.

4. Behavioral Engine v1 (baseline + live score)
   - `detection/behavioral_engine.py` with sliding baseline per host/process metric, simple z-score or EWMA.
   - Event bus producer "behavioral.score".
   - Tests: deterministic scores on known sequences; seed/document fixed params.

## Priority B — Platform & Packaging
5. Platform Abstraction Layer (Windows stubs)
   - Centralize Windows-only ops behind `platforms/windows.py`; Linux stubs return No-Op.
   - Replace scattered guards with calls into this layer.
   - Tests: smoke on Linux; basic functional on Windows (guarded).

6. Windows Service Packaging
   - `tools/windows/build_installer.ps1` to produce MSI/exe; service install/uninstall commands.
   - Docs page: install/upgrade/rollback.
   - CI artifact publishing workflow (if CI in repo).

## Priority C — Reliability & Observability
7. Event Schema Hardening
   - Introduce TypedDict/Pydantic models for bus events; adapters at boundaries.
   - Back-compat maintained.
   - Tests: schema round-trip; invalid payload rejected.

8. Health/Readiness Probes
   - `/health` (liveness), `/ready` (readiness) endpoints.
   - Background-task lifecycle hooks integrated.
   - Tests: startup→ready, shutdown clean.

9. Audit Logging & Timeline
   - Structured JSON logs (action, subject, mode, decision, rule-id).
   - `DOCS/audit_fields.md` with field dictionary.
   - Tests: a few end-to-end assertions.

## Priority D — Advanced (stage after A/B/C)
10. Memory Archiver + Pointer Files
11. RBAC surface (admin vs named users; no "regular user" label)
12. Model Manager hook (no external downloads yet; interface only)

---
## Working Rules
- Every feature lands via a **Single-Target Contract** (like Operational Mode or Interop).
- Each contract must: (a) list touched files, (b) keep ruff/pyright at 0 for touched files, (c) hold test non-regression.
- UI stays thin; logic lives in core.
