# WatchLockAI Sentinel Feature Flags Matrix

**Generated:** 2025-09-06T22:43:50Z  
**Total Flags:** 53  
**Files Analyzed:** 117  

## Summary Statistics

### Flags by Category
- **feature:** 18 flags
- **storage:** 6 flags
- **logging:** 6 flags
- **configuration:** 8 flags
- **network:** 4 flags
- **performance:** 5 flags
- **auth:** 6 flags

### Security Classification
- **public:** 46 flags
- **sensitive:** 4 flags
- **secret:** 3 flags

### Most Used Flags
- **CONSOLE_AUTH_ENABLED** (auth): 16 usages in 8 files
- **CONFIG_HOT_RELOAD_ENABLED** (feature): 13 usages in 8 files
- **CONSOLE_AUTH_SESSION_KEY** (auth): 13 usages in 7 files
- **ADMIN_TOKEN** (auth): 13 usages in 6 files
- **ADMIN_AUTH_ENABLED** (auth): 11 usages in 5 files
- **STREAM_ENABLED** (feature): 10 usages in 5 files
- **HEALTH_ENDPOINT_ENABLED** (feature): 8 usages in 7 files
- **METRICS_DEBUG_ENABLED** (logging): 7 usages in 4 files
- **RATE_LIMIT_ENABLED** (performance): 7 usages in 5 files
- **CONSOLE_AUTH_USER_DB** (auth): 6 usages in 4 files

## Flag Details


### Auth Flags

#### ADMIN_AUTH_ENABLED 🟡

**Default:** `0`  
**Security:** sensitive  
**Used in:** 11 locations across 5 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, POST /api/auth/login  
**Security impact:** Authentication bypass risk; Privilege escalation potential  

#### ADMIN_TOKEN 🔴

**Default:** ⚠️ No default value  
**Security:** secret  
**Used in:** 13 locations across 6 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, POST /api/auth/login  
**Security impact:** Credential exposure risk; Unauthorized access potential; Should be encrypted/masked in logs  
**Failure modes:** No default value - runtime failure likely; Security degradation if misconfigured  

#### CONSOLE_AUTH_ENABLED 🟡

**Default:** `0`  
**Security:** sensitive  
**Used in:** 16 locations across 8 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, POST /api/auth/login  
**Security impact:** Authentication bypass risk; Privilege escalation potential  

#### CONSOLE_AUTH_SESSION_KEY 🔴

**Default:** ⚠️ No default value  
**Security:** secret  
**Used in:** 13 locations across 7 files  
**Influences routes:** GET /api/stream/health, GET /api/admin/config/schema, POST /api/admin/anomaly/train, POST /api/admin/export, POST /api/auth/logout  
**Security impact:** Credential exposure risk; Unauthorized access potential; Should be encrypted/masked in logs  
**Failure modes:** No default value - runtime failure likely; Security degradation if misconfigured  

#### CONSOLE_AUTH_USER_DB 🟡

**Default:** `data/auth/users.json`  
**Security:** sensitive  
**Used in:** 6 locations across 4 files  
**Influences routes:** POST /api/auth/logout, POST /api/auth/login, POST /api/admin/config/reload, GET /api/auth/me  
**Security impact:** Authentication bypass risk; Privilege escalation potential  

#### STREAM_REQUIRE_AUTH 🟡

**Default:** `0`  
**Security:** sensitive  
**Used in:** 5 locations across 3 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  
**Security impact:** Authentication bypass risk; Privilege escalation potential  


### Configuration Flags

#### CHAOS_MAX_LATENCY_MS 🟢

**Default:** `5000`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### CONFIG_HOT_RELOAD_DEBOUNCE_MS 🟢

**Default:** `750`  
**Security:** public  
**Used in:** 1 locations across 1 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### CONFIG_HOT_RELOAD_INTERVAL 🟢

**Default:** `3.0`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### PERF_SOAK_CLIENTS 🟢

**Default:** `16`  
**Security:** public  
**Used in:** 2 locations across 2 files  

#### PERF_SOAK_DURATION_S 🟢

**Default:** `600`  
**Security:** public  
**Used in:** 2 locations across 2 files  

#### RETENTION_DAYS 🟢

**Default:** `14`  
**Security:** public  
**Used in:** 2 locations across 2 files  
**Influences routes:** POST /api/admin/retention/run?dry=true&retention_days=30  

#### STREAM_HEALTH_INTERVAL_MS 🟢

**Default:** `1000`  
**Security:** public  
**Used in:** 4 locations across 3 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, POST /api/auth/login  

#### STREAM_TYPE 🟢

**Default:** `sse`  
**Security:** public  
**Used in:** 4 locations across 3 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, POST /api/auth/login  


### Feature Flags

#### ANOMALY_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 4 locations across 4 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### ANOMALY_SKLEARN_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 3 locations across 3 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### BACKUP_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 2 locations across 2 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### CHAOS_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 2 locations across 2 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### CONFIG_HOT_RELOAD_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 13 locations across 8 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, POST /api/admin/config/reload?debounce_ms=999999, GET /api/metrics/snapshot, GET /api/policies  

#### CONSOLE_UI_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 2 locations across 2 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### EXPORT_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 4 locations across 3 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### HEALTH_ENDPOINT_ENABLED 🟢

**Default:** `1`  
**Security:** public  
**Used in:** 8 locations across 7 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### MITRE_API_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 1 locations across 1 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### MITRE_MATRIX_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 5 locations across 5 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### MITRE_REACTIVE_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 2 locations across 2 files  

#### PERF_PROBE_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 1 locations across 1 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### PLUGINS_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 6 locations across 4 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### QUARANTINE_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 5 locations across 5 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### RETENTION_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 1 locations across 1 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### ROTATE_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 2 locations across 2 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### SERVICE_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 2 locations across 2 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### STREAM_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 10 locations across 5 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, POST /api/auth/login  


### Logging Flags

#### DEBUG 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### LOG_BACKUPS 🟢

**Default:** `5`  
**Security:** public  
**Used in:** 3 locations across 3 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### LOG_MAX_BYTES 🟢

**Default:** `1048576`  
**Security:** public  
**Used in:** 4 locations across 4 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### LOG_REDACT_SECRETS 🔴

**Default:** `1`  
**Security:** secret  
**Used in:** 6 locations across 6 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  
**Security impact:** Credential exposure risk; Unauthorized access potential; Should be encrypted/masked in logs  
**Failure modes:** Security degradation if misconfigured  

#### METRICS_DEBUG_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 7 locations across 4 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### SENTINEL_LOG_LEVEL 🟢

**Default:** ⚠️ No default value  
**Security:** public  
**Used in:** 1 locations across 1 files  
**Failure modes:** No default value - runtime failure likely  


### Network Flags

#### HOST 🟢

**Default:** `127.0.0.1`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### HOSTNAME 🟢

**Default:** `unknown`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### PERF_SOAK_BASE_URL 🟢

**Default:** `http://127.0.0.1:8080`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### PORT 🟢

**Default:** `8000`  
**Security:** public  
**Used in:** 1 locations across 1 files  


### Performance Flags

#### CHAOS_ERROR_RATE 🟢

**Default:** `0.1`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### RATE_LIMIT_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 7 locations across 5 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, POST /api/admin/config/reload?debounce_ms=999999, GET /api/metrics/snapshot, GET /api/policies  

#### TI_CACHE_ENABLED 🟢

**Default:** `0`  
**Security:** public  
**Used in:** 2 locations across 2 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### TI_CACHE_MAX 🟢

**Default:** `2048`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### TI_CACHE_TTL 🟢

**Default:** `300`  
**Security:** public  
**Used in:** 1 locations across 1 files  


### Storage Flags

#### BACKUP_DIR 🟢

**Default:** `data/backups`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### CONFIG_PATH 🟢

**Default:** `config.yaml`  
**Security:** public  
**Used in:** 1 locations across 1 files  

#### MITRE_PROFILE 🟢

**Default:** `baseline`  
**Security:** public  
**Used in:** 4 locations across 4 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  

#### MITRE_RULES_PATH 🟢

**Default:** ⚠️ No default value  
**Security:** public  
**Used in:** 2 locations across 2 files  
**Influences routes:** POST /api/actions/pause, GET /api/admin/config/schema, GET /api/metrics/snapshot, GET /api/policies, GET /api/anomaly/score  
**Failure modes:** No default value - runtime failure likely  

#### PLUGINS_DIR 🟢

**Default:** `plugins`  
**Security:** public  
**Used in:** 2 locations across 2 files  

#### QUARANTINE_DIR 🟢

**Default:** `data/quarantine`  
**Security:** public  
**Used in:** 2 locations across 2 files  

