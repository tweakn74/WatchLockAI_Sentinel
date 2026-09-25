# WatchLockAI Sentinel Integration Blueprint
**Date:** 2026-03-22
**Author:** Biff (SOC Commander / Forensic Investigator)
**Target:** `C:\Users\craig\code_projects\WatchLockAI_Sentinel`

## Architecture Overview
WatchLockAI is a native Python SIEM/EDR platform built to run as a Windows Service (`WatchLockAISentinel`). It exposes a local FastAPI web server on `http://127.0.0.1:8080` (by default) that provides health checks, threat intelligence, metrics, and anomaly detection. 

We will integrate WatchLockAI into OpenClaw NOT by rewriting its Python code, but by creating a new `watchlockai` agent in `openclaw.json`. The OpenClaw gateway will start the Sentinel daemon (if it isn't running as a Windows service already) and the agent will read the JSON logs and interact with the FastAPI endpoints.

## Step 1: OpenClaw Configuration Patch
We must inject this new agent definition into `openclaw.json`. 

```json
{
  "id": "watchlockai",
  "name": "WatchLockAI",
  "workspace": "C:\\Users\\craig\\.openclaw\\agents\\watchlockai\\workspace",
  "model": {
    "primary": "anthropic/claude-opus-4-6",
    "fallbacks": ["anthropic/claude-sonnet-4-6"]
  },
  "allowedProviders": ["anthropic"],
  "identity": { "name": "WatchLockAI" },
  "compactionInstructions": "You are WatchLockAI, the Agentic SOC Sentinel. This is a context compaction summary. Preserve: (1) What Biff or Pulselet tasked you with. (2) The current threat status of the host machine (GREEN/YELLOW/RED). (3) Any detected anomalies, quarantined processes, or blocked IPs. (4) The status of the Sentinel Python daemon. You protect Craig's systems.",
  "thinkingDefault": "high",
  "tools": {
    "profile": "coding",
    "alsoAllow": ["web_search", "message", "nodes", "exec", "read", "write"]
  }
}
```

*Note: You requested `quaid.oralious@gmail.com` as the auth profile. Since Doc's `anthropic:default` profile is already configured with that email, WatchLockAI will share the `anthropic:default` token automatically by using the `anthropic` provider.*

## Step 2: The Sentinel Daemon Configuration
The WatchLockAI project requires a `.env` file or `config.yaml` to activate its core features, as they are "DEFAULT OFF" in the source code to prevent breaking changes.

Before starting the daemon, we must create `C:\Users\craig\code_projects\WatchLockAI_Sentinel\.env` with the following baseline config:
```env
WEB_API_HOST=127.0.0.1
WEB_API_PORT=8080
HEALTH_ENDPOINT_ENABLED=1
CONSOLE_UI_ENABLED=1
MITRE_API_ENABLED=1
EXPORT_ENABLED=1
LOG_LEVEL=INFO
```

## Step 3: Startup and Execution
The OpenClaw agent will use the `exec` tool to manage the Sentinel daemon.
**Startup Command:**
```powershell
cd C:\Users\craig\code_projects\WatchLockAI_Sentinel
python app.py --interactive
```
*Note: We run in `--interactive` mode because OpenClaw cannot easily manage background Windows Services without elevation. The `app.py` process will run in the background via the OpenClaw `exec` tool.*

## Step 4: The SOC Communication Loop
1. **Biff (Commander):** Sends an hourly health check request to `agent:watchlockai:main`: `"Pull the latest telemetry and MITRE alerts."`
2. **WatchLockAI (Sentinel):** Uses the `exec` tool to curl `http://127.0.0.1:8080/api/status` or reads `logs/audit.log`, then replies to Biff via `sessions_send`.
3. **Pulselet (Evolution):** Can ping WatchLockAI before executing automated code deployments to ensure the system is not under active attack or experiencing resource starvation.

## Execution Handoff
Pulselet is authorized to execute this integration. She should:
1. Dispatch Doc to patch the `openclaw.json` config with the new agent.
2. Create the `.env` file in the WatchLockAI directory.
3. Test the daemon startup using the `exec` tool.