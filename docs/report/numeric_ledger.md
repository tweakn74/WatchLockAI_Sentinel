# Numeric Sanity Ledger

**Generated:** 2025-09-07T18:49:50.218376Z  
**Tool:** `tools/numeric_ledger.py`  
**Scope:** Credits Ragnarok v6.0 - P31 Numeric Sanity Audit

## Executive Summary

Ground truth metric recomputation from filesystem and code analysis. **Status:** ✅ All metrics within acceptable bounds.

## Claimed vs Computed Metrics

| Metric | Claimed | Computed | Delta | Status |
|--------|---------|----------|-------|--------|
| **Routes** | N/A | 12 | N/A | ➖ N/A |
| **Schemas** | N/A | 48 | N/A | ➖ N/A |
| **Scenarios** | N/A | 5000 | N/A | ➖ N/A |
| **Schema Samples** | N/A | 0 | N/A | ➖ N/A |
| **Adrs** | N/A | 0 | N/A | ➖ N/A |
| **Sdk Files** | N/A | 0 | N/A | ➖ N/A |
| **Tool Files** | N/A | 27 | N/A | ➖ N/A |
| **Test Files** | N/A | 46 | N/A | ➖ N/A |

## Route Details

**Total Unique Routes:** 12

| Method | Path | File | Detection |
|--------|------|------|----------|
| `GET` | `/api/admin/config/schema` | console/web_api.py | python_ast |
| `GET` | `/api/anomaly/score` | console/web_api.py | python_ast |
| `GET` | `/api/metrics/health` | console/web_api.py | python_ast |
| `GET` | `/api/mitre/coverage` | console/web_api.py | python_ast |
| `PATCH` | `console.anomaly.ANOMALY_SKLEARN_ENABLED` | tests/test_anomaly.py | python_ast |
| `PATCH` | `console.quarantine.QUARANTINE_ENABLED` | tests/test_quarantine.py | python_ast |
| `PATCH` | `os.name` | tests/test_quarantine.py | python_ast |
| `PATCH` | `subprocess.run` | tests/test_quarantine.py | python_ast |
| `POST` | `/api/admin/anomaly/train` | console/web_api.py | python_ast |
| `POST` | `/api/admin/config/reload` | console/web_api.py | python_ast |
| `POST` | `/api/admin/quarantine` | console/web_api.py | python_ast |
| `POST` | `/api/admin/quarantine/restore` | console/web_api.py | python_ast |

## Computation Details

- **Workspace:** `/workspace/WatchLockAI_Sentinel`
- **Computed At:** 2025-09-07T18:49:50.215014Z
- **Method:** Direct filesystem and code analysis
- **Tool Version:** numeric_ledger.py v1.0
