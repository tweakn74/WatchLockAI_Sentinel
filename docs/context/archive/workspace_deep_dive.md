WatchLockAI Sentinel – Deep‑Dive Workspace Report

Overview

- Purpose: Python-based endpoint detection and response (EDR) focused on Windows with cross‑platform support.
- Architecture: Modular, event-driven system centered on an async event bus; collectors publish events, detection generates alerts, response components act, and an optional web console provides local management.
- Entrypoints: `app.py` (interactive + CLI utilities), `service/service_wrapper.py` (Windows service), `console/web_api.py` (FastAPI server, started from service).

Tech Stack

- Language: Python 3.10+
- Core libs: `pydantic v2`, `loguru`, `PyYAML`, `tenacity`, `click`.
- Monitoring: `psutil`, `watchdog`.
- UI: `pystray` + `Pillow` for tray (Windows), optional.
- Web/API: `FastAPI` + `uvicorn` (local-only by default).
- Windows service: `pywin32` (optional; guarded by platform checks).
- RAG/Knowledge: SQLite FTS; optional `sentence-transformers` embeddings with lazy init.
- Tooling: `ruff`, `pyright`, `pytest`, `pytest-asyncio`.

Entrypoints & Modes

- Interactive CLI: `app.py` supports run loop, `--no-ui`, `--debug`, `--config`, plus utilities `--create-config`, `--validate-config`, `--rebuild-index`, `--status`.
- Windows service: `service/service_wrapper.py` installs/starts/stops service; in service mode starts core + optional Web API (127.0.0.1:8080).
- Web console: `console/web_api.py` creates a FastAPI app; admin features are gated by env flags and (optional) admin auth.

Core Architecture

- Event Bus: `app_core/bus.py` implements an async pub/sub bus with a worker task, weakref subscriptions, recent history, and observability counters.
- Config: `app_core/config.py` defines `SentinelConfig` and nested configs; YAML load with Pydantic validation; optional hot‑reload watcher; persistent operational mode in `config/operational_mode.json`.
- Schemas: `app_core/schemas.py` provides Pydantic v2 models for events and alerts, including enums and validation (entropy bounds, port ranges, etc.).
- Collectors: `collectors/*` publish `FileEvent`, `ProcessEvent`, `RegistryEvent`, `NetworkEvent`, and `HealthMetric` based on config toggles.
- Detection: `detection/rules_engine.py` (rolling windows + ransomware burst rule), optional DSL/sequence support via `detection/rule_dsl.py`, behavioral and intel helpers, and a RAG loader.
- RAG/Knowledge: `detection/knowledge/loader.py` builds/queries a local index from knowledge packs (`detection/knowledge/packs`) using SQLite FTS or optional embeddings.
- Response: `response/alerts.py` (toast + JSONL + tray buffer) and `response/actions.py` (mode‑aware actions with user‑consent gating; destructive actions guarded).
- UI Tray: `ui/tray_app.py` (pystray icon, status, recent alerts, pause/resume controls) run on a background thread.
- Web API: `console/web_api.py` mounts templates/static; exposes status/alerts; optional admin endpoints (retention, backup/restore, rotation, chaos, perf) via env flags and optional auth.

Execution Flow

- Startup: `SentinelService.initialize()` loads config, sets up logging, starts event bus, (optionally wires MITRE ATT&CK), rebuilds knowledge index, and starts collectors, rules engine, response managers, and Web API (127.0.0.1:8080).
- Run loop: `SentinelApplication.run_forever()` updates tray status, monitors pause/resume state via `ResponseActionsManager`.
- Shutdown: orderly stop of Web API, alerts, rules engine, collectors, and event bus.

Configuration

- File: `config.yaml` (root) with nested sections for monitoring, health, operational, rag, alerts, responses, service, privacy.
- Hot reload: disabled by default; enable with `CONFIG_HOT_RELOAD_ENABLED=1` (debounced watcher).
- Operational Mode: stored atomically in `config/operational_mode.json`; API to get/set via `console/api/operational_mode.py`.
- Defaults: conservative (e.g., destructive actions off, many admin endpoints gated off by env flags).

Web Console API (local‑only default)

- Status: `/api/status` (service + bus + rules/collectors status).
- Alerts: `/api/alerts` summary (recent + counts).
- Operational Mode: GET/PUT `/api/operational_mode` with strict schema (`console/schemas.py`).
- Admin (feature‑flagged + optional auth): secret rotation, backups, retention, chaos probes, perf probes, streaming/SSE, anomaly/quarantine, plugins. Flags like `ADMIN_AUTH_ENABLED`, `ANOMALY_ENABLED`, `QUARANTINE_ENABLED`, `STREAM_ENABLED`, `CONSOLE_UI_ENABLED` gate availability.

Knowledge/RAG

- Index: SQLite DB at `detection/knowledge/index/knowledge.db` with FTS tables and optional embeddings table.
- Mode: FTS by default; embeddings mode activates lazily if `sentence-transformers` import succeeds (model `all-MiniLM-L6-v2`).
- Capabilities: Rebuild index, query with provenance (filename/section/lines), parse structured “sentinel:directive” blocks from packs into a directives table.

Response & Modes

- Modes: `observe`, `alert`, `contain`, `quarantine`, `offline` (validated, persisted atomically).
- Enforcement: Destructive actions (e.g., terminate process) are blocked or logged based on mode; additional user consent gating and `allow_destructive_actions` config apply.
- Alerts: Toast notifications (if `plyer` present) and JSONL logging (`logs/alerts.jsonl`).

Data & Logging

- Logs dir: `logs/` with `sentinel.log`, `events.jsonl`, `alerts.jsonl`, optional `debug.log`.
- Windows Event Log: optional integration for high‑severity alerts in `app_core/logging_setup.py` (guarded by platform imports).
- Data: knowledge DB as above; quarantine audit at `data/quarantine/`.

Plugins

- Loader/Sandbox: `console/plugin_sandbox.py` loads `plugins/manifest.json`, verifies SHA‑256, and enforces a restricted import surface based on permissions (filesystem/network/system_calls).
- Example: `plugins/example_hello.py` with factory `create_plugin()` and metadata.

Tests

- E2E: `tests/e2e/test_sentinel_e2e.py` exercises fs + health collectors, rules engine, and alert pipeline (non‑destructive expectations). Writes `DOCS/E2E_Test_Results.json` in test run.
- Broader tests: Console, retention, backup, perf, plugin sandbox, etc. Platform specifics are often mocked/guarded.

How To Run (local dev)

- Create venv and install: `pip install -r requirements.txt` (Windows users also need `pywin32`, tray deps, etc.).
- Interactive: `python app.py` (use `--no-ui` on systems without tray deps; `--debug` for verbose).
- Rebuild knowledge: `python app.py --rebuild-index` (or `python -m detection.knowledge.loader --rebuild-index`).
- Web API (via service): Start service wrapper or include in interactive run by leaving FastAPI deps installed.

Notable Flags & Defaults (selected)

- Web API: `HEALTH_ENDPOINT_ENABLED`, `STREAM_ENABLED/STREAM_TYPE`, `ADMIN_AUTH_ENABLED` (+`ADMIN_TOKEN`), `ANOMALY_*`, `QUARANTINE_ENABLED`, `MITRE_*`.
- Logging: `LOG_MAX_BYTES`, `LOG_BACKUPS`, `LOG_REDACT_SECRETS` (default ON), console/file/JSONL toggles from `setup_logging()`.
- Config reload: `CONFIG_HOT_RELOAD_ENABLED` (default OFF).

Observations & Potential Gaps

- Service wrapper duplication: `service/service_wrapper.py` appears to contain duplicated blocks; worth a cleanup pass for maintainability.
- Feature flags default to OFF: many admin endpoints are inert until env flags (and optionally admin auth) are enabled.
- Embeddings model is optional: defaults to FTS; ensure `sentence-transformers` availability only when desired (size/startup cost).
- Windows‑only paths and behavior: tray, service, and registry monitoring gracefully degrade on non‑Windows; verify expectations per platform.
- Case sensitivity: Some docs/tests reference `DOCS/…` while repo uses `docs/…`; Windows is case‑insensitive, Linux is not—watch paths in CI.

Key Files

- Entrypoint: `app.py`
- Service: `service/service_wrapper.py`
- Web API: `console/web_api.py`
- Event Bus: `app_core/bus.py`
- Config: `app_core/config.py`, `config/operational_mode.py`
- Schemas: `app_core/schemas.py`
- Collectors: `collectors/*.py`
- Detection: `detection/rules_engine.py`, `detection/rule_dsl.py`
- Knowledge: `detection/knowledge/loader.py`, `detection/knowledge/packs/_index.yaml`
- Response: `response/alerts.py`, `response/actions.py`, `response/playbooks.py`
- Tray UI: `ui/tray_app.py`

Quick Next Steps

- Run interactive smoke: `python app.py --no-ui --debug` (verify logs/alerts JSONL created).
- Hit API (if enabled): `GET http://127.0.0.1:8080/api/status` and `/api/operational_mode`.
- Rebuild knowledge index and confirm `detection/knowledge/index/knowledge.db` entries.
- If targeting Windows service, install `pywin32` and try `python service/service_wrapper.py --interactive` first, then `install`.

