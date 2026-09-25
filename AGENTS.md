AGENTS.md -- Agent Operating Guide for WatchLockAI Sentinel

Purpose

- Define how this AI agent operates in this repository to deliver safe, precise, and high‑impact work.
- Align with the Codex CLI harness behavior while embracing depth, ambition, and end‑to‑end execution.

Repository Profile (quick map)

- Python 3.10+; modular EDR with async event bus.
- Key dirs: `app_core/` (bus, config, schemas, logging), `collectors/`, `detection/`, `response/`, `service/`, `console/`, `ui/`, `docs/`.
- Entrypoints: `app.py` (interactive + utilities), `service/service_wrapper.py` (Windows service), `console/web_api.py` (FastAPI server).
- Tests: `tests/` (E2E and component), rich docs in `docs/` and `docs/context/`.

Operating Mode: Depth‑First by Default

- Bias toward thoroughness and intensity: analyze broadly, then execute deeply.
- Produce multi‑artifact outputs (design notes, plans, code, tests, docs, telemetry).
- Where value is clear, propose ambitious refactors/improvements with migration notes.
- Maintain safety and platform guards while pursuing comprehensive solutions.

Scope & Priorities

- Maximize value and resilience over minimal surface change when appropriate.
- Respect style and contracts; prefer coherent, system‑level improvements to band‑aids.
- When editing existing code, be surgical; when building capabilities, be ambitious.

Planning & Execution

- Use the plan tool for multi‑step or complex work; keep it live and updated.
- Plans may include: design, backend, API, UI, tests, perf, docs, rollout.
- One step in progress at a time; mark completed as you move.
- For large efforts, structure work into sprints: Research -> Implementation -> Validation -> Hardening.

Proof‑of‑Work & Deliverables

- Always leave artifacts:
  - Design/decision docs under `docs/context/` (deep dives, ADRs, runbooks).
  - Tests: unit/integration/E2E aligned with the change.
  - Scripts or fixtures for repro/microbench when performance matters.
  - Validation notes and next steps.

Patches & File Editing

- Apply changes via the patch tool only; avoid raw writes.
- Prefer cohesive diffs--even if larger--when they improve clarity and integrity.
- Keep names and public contracts stable, or document breaking changes + migrations.
- Update docs alongside code; link files in `docs/context/index.json` when relevant.

Reading & Searching

- Prefer ripgrep: `rg -n -S --hidden --glob !**/.git/** PATTERN`.
- Read files in <=250‑line chunks to avoid truncation.
- On Windows, `Get-Content -TotalCount/-Tail` for targeted reads.

Response Style (chat)

- For architecture/design/tasks: deliver structured, in‑depth responses with clear sections.
- For quick updates: stay concise and operational.
- Always reference files with clickable paths and a start line (e.g., `console/web_api.py:1`).

Validation, Benchmarking, and Quality Gates

- Validate locally and specifically near changes; expand to broader tests as confidence grows.
- Propose and (when allowed) run:
  - Ruff (`ruff check .`), Pyright (`pyright`).
  - Tests (`pytest -q` or focused paths).
  - Microbench or perf probes (under `repro/microbench` where applicable).
- Define exit criteria (acceptance tests, metrics deltas) for significant changes.

Security, Privacy, and Safety

- Treat host and repo as sensitive; no data exfiltration; avoid network unless approved.
- Admin/API features are OFF by default; enable explicitly via env vars.
- Destructive actions remain gated by:
  - `responses.allow_destructive_actions` config.
  - Operational mode rules (observe/alert/contain/quarantine/offline).
  - Explicit user consent flows.

Platform Guards & Cross‑Platform

- Guard Windows‑only code (`sys.platform.startswith('win')` / `platform.system() == 'Windows'`).
- Ensure graceful degradation on non‑Windows (no crashes, clear logs/warnings).
- Service/tray/registry imports must be platform‑guarded.

Web/API Conventions

- Bind to `127.0.0.1` by default; document any changes.
- Gate sensitive/admin routes behind env flags and (optional) admin auth.
- Keep error shape consistent; reuse central exception handlers in `console/web_api.py`.

Knowledge/RAG

- SQLite FTS is the baseline; enable embeddings lazily if available.
- Avoid heavy model downloads unless explicitly approved; keep local‑only viable.

Operational Mode & Actions

- Persist mode via `config/operational_mode.json` atomically.
- Keep enforcement strict; do not weaken gating without explicit approval.

Documentation

- Add new context under `docs/context/` (deep dives, design notes, quickstarts, runbooks).
- Update `docs/context/index.json` when adding enduring references.

Approvals & Sandbox

- Approvals are on‑request. Ask before:
  - Network access or installing packages.
  - Long/slow runs (heavy tests, full builds, packaging).
  - Destructive operations (file deletions, resets).

Startup Checklist (Auto‑read)

- Preload files from `docs/context/agent_autoload.json` (small, high‑signal set).
- If missing context is detected, proactively propose additions to the autoload list.

Quality Checklist (before handoff)

- Change is correct, coherent, and validated (tests/linters/perf if applicable).
- Platform guards and safe defaults preserved.
- Docs updated (and linked) for any behavior/usage change.
- Clear follow‑ups and risks called out.

Escalations

- Ask clarifying questions when ambiguity exists.
- If a request conflicts with safety or architecture constraints, explain the trade‑offs and propose alternatives.
