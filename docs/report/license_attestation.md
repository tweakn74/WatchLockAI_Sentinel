# WatchLockAI Sentinel License Attestation

**Version:** 0.9.0-rc1  
**Date:** 2025-09-05 18:08:59 UTC  
**Scope:** Release Candidate Dependencies  

## Executive Summary

WatchLockAI Sentinel v0.9.0-rc1 maintains a **zero external runtime dependency** architecture, relying exclusively on Python Standard Library modules for core functionality. All optional dependencies are import-gated and provide graceful degradation when unavailable.

## Runtime Dependencies (Required)

### Standard Library Only
- **Count:** 48 modules
- **License:** Python Software Foundation License (compatible with commercial use)
- **Stability:** Guaranteed by Python version compatibility
- **Security:** Maintained by Python Security Response Team

#### Runtime Modules Used
- `argparse`\n- `ast`\n- `asyncio`\n- `contextlib`\n- `dataclasses`\n- `enum`\n- `hmac`\n- `importlib`\n- `json`\n- `logging`\n- `math`\n- `os`\n- `random`\n- `secrets`\n- `statistics`\n- `threading`\n- `unittest`\n- `urllib`\n- `winreg`\n- `zipfile`\n...

*Complete list: 48 stdlib modules (see SBOM manifest)*

## Development/Optional Dependencies (Gated)

### Import Gating Strategy
All optional dependencies are wrapped in try/except blocks to ensure graceful degradation:

```python
try:
    import fastapi
except ImportError:
    fastapi = None  # Feature disabled, no error
```

### Optional Modules Detected
- `PIL` - Optional (feature degrades gracefully if unavailable)\n- `app` - Optional (feature degrades gracefully if unavailable)\n- `fastapi` - Optional (feature degrades gracefully if unavailable)\n- `loguru` - Optional (feature degrades gracefully if unavailable)\n- `numpy` - Optional (feature degrades gracefully if unavailable)\n- `packaging` - Optional (feature degrades gracefully if unavailable)\n- `plyer` - Optional (feature degrades gracefully if unavailable)\n- `pydantic` - Optional (feature degrades gracefully if unavailable)\n- `pydantic_settings` - Optional (feature degrades gracefully if unavailable)\n- `pystray` - Optional (feature degrades gracefully if unavailable)\n- `pytest` - Optional (feature degrades gracefully if unavailable)\n- `requests` - Optional (feature degrades gracefully if unavailable)\n- `schemas` - Optional (feature degrades gracefully if unavailable)\n- `sentence_transformers` - Optional (feature degrades gracefully if unavailable)\n- `servicemanager` - Optional (feature degrades gracefully if unavailable)\n- `sklearn` - Optional (feature degrades gracefully if unavailable)\n- `uvicorn` - Optional (feature degrades gracefully if unavailable)\n- `watchdog` - Optional (feature degrades gracefully if unavailable)\n- `win32event` - Optional (feature degrades gracefully if unavailable)\n- `win32evtlog` - Optional (feature degrades gracefully if unavailable)\n- `win32evtlogutil` - Optional (feature degrades gracefully if unavailable)\n- `win32service` - Optional (feature degrades gracefully if unavailable)\n- `win32serviceutil` - Optional (feature degrades gracefully if unavailable)\n- `yaml` - Optional (feature degrades gracefully if unavailable)

## Local Project Modules

### Internal Components
- **Count:** 9 local modules
- **License:** Project license (same as main codebase)
- **Scope:** Internal business logic, no external dependencies

- `app_core` - Internal module\n- `collectors` - Internal module\n- `config` - Internal module\n- `console` - Internal module\n- `detection` - Internal module\n- `response` - Internal module\n- `service` - Internal module\n- `tools` - Internal module\n- `ui` - Internal module

## License Compliance Analysis

### Runtime Compliance [PASS]
- **Zero GPL Dependencies:** Confirmed
- **Zero AGPL Dependencies:** Confirmed  
- **Zero Copyleft Issues:** Runtime uses only PSF-licensed stdlib
- **Commercial Use:** Fully compatible

### Optional Dependencies License Review
[WARN] `PIL` - License TBD - Review required\n[WARN] `app` - License TBD - Review required\n[PASS] `fastapi` - MIT License - Compatible\n[WARN] `loguru` - License TBD - Review required\n[PASS] `numpy` - BSD License - Compatible\n[WARN] `packaging` - License TBD - Review required\n[WARN] `plyer` - License TBD - Review required\n[WARN] `pydantic` - License TBD - Review required\n[WARN] `pydantic_settings` - License TBD - Review required\n[WARN] `pystray` - License TBD - Review required\n[WARN] `pytest` - License TBD - Review required\n[PASS] `requests` - Apache 2.0 - Compatible\n[WARN] `schemas` - License TBD - Review required\n[WARN] `sentence_transformers` - License TBD - Review required\n[WARN] `servicemanager` - License TBD - Review required\n[PASS] `sklearn` - BSD License - Compatible\n[PASS] `uvicorn` - BSD License - Compatible\n[WARN] `watchdog` - License TBD - Review required\n[WARN] `win32event` - License TBD - Review required\n[WARN] `win32evtlog` - License TBD - Review required\n[WARN] `win32evtlogutil` - License TBD - Review required\n[WARN] `win32service` - License TBD - Review required\n[WARN] `win32serviceutil` - License TBD - Review required\n[WARN] `yaml` - License TBD - Review required

## Recommendations for GA

1. **[PASS] APPROVED:** Runtime dependency model (stdlib only)
2. **[PASS] APPROVED:** Import gating implementation
3. **[WARN] REVIEW:** Optional dependency licenses before production use
4. **[PASS] APPROVED:** Zero supply chain risk for core functionality

---
*Generated by WatchLockAI Sentinel SBOM Generator (P6-002)*
