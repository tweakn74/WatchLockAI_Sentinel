Agent Context Autoload

Purpose
- Declare the minimal set of documentation this agent should read automatically at startup.

How it works
- The file `docs/context/agent_autoload.json` lists repo‑relative paths to preload.
- Keep this list small and high‑signal; link out to broader docs via `docs/context/index.json`.

Editing the list
- Add/remove paths under the `files` array.
- Prefer stable, human‑authored sources (guides, runbooks, standards, overview).

Current autoload files (see JSON for source of truth)
- `AGENTS.md`
- `docs/context/index.json`
- `docs/context/workspace_deep_dive.md`
- `docs/INDEX.md`
- `docs/workspace_overview.md`
- `docs/session_startup.md`
- `docs/coding_standards.md`
- `docs/testing_strategy.md`
- `docs/release_checklist.md`
- `docs/master_todo.md`
- `docs/master_todo.json`
- `docs/context/event_system_architecture.md`
- `docs/context/api_reference_complete.md`
- `docs/context/detection_engine_architecture.md`
- `docs/context/response_system_architecture.md`
- `docs/context/configuration_system_architecture.md`
- `docs/context/component_integration_patterns.md`
- `docs/context/development_workflow_patterns.md`

