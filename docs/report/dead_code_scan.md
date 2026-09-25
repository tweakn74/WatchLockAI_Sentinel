# WatchLockAI Sentinel Dead Code Analysis Report

**Generated:** 2025-09-06T22:43:50Z  
**Files Analyzed:** 120  
**Total Dead Code Items:** 942  
**High Confidence Items:** 671  
**Potential Cleanup Lines:** 717  

## Summary Statistics

### Dead Code by Type
- **function:** 147 items
- **method:** 614 items
- **class:** 181 items

### Confidence Distribution
- **High Confidence:** 671 items
- **Medium Confidence:** 271 items
- **Low Confidence:** 0 items

## Most Problematic Files

- **console/web_api.py:** 69 issues (50 high confidence)
- **detection/behavioral_engine.py:** 30 issues (28 high confidence)
- **tools/dead_code_scan.py:** 27 issues (23 high confidence)
- **tools/routing_atlas_generator.py:** 27 issues (21 high confidence)
- **response/actions.py:** 27 issues (21 high confidence)
- **detection/rules_engine.py:** 25 issues (19 high confidence)
- **ui/tray_app.py:** 23 issues (18 high confidence)
- **console/auth.py:** 23 issues (18 high confidence)
- **tools/symbol_atlas_generator.py:** 23 issues (18 high confidence)
- **collectors/fs_monitor.py:** 21 issues (16 high confidence)

## Cleanup Recommendations

### High Priority - Safe to remove

**Count:** 671 items  
**Description:** These items have high confidence of being unused and can likely be removed safely.

**Sample Items:**
- `app.py:_setup_signal_handlers`
- `app.py:start`
- `app.py:_start_tray_ui`
- `app.py:stop`
- `app.py:run_forever`
- `temp_minimal_probes.py:subscribe`
- `temp_minimal_probes.py:publish`
- `service/service_wrapper.py:initialize`
- `service/service_wrapper.py:_initialize_collectors`
- `service/service_wrapper.py:_initialize_detection_engine`

### Medium Priority - Review and test

**Count:** 271 items  
**Description:** These items should be reviewed manually and tested before removal.

**Sample Items:**
- `generate_inventory.py:generate_inventory`
- `generate_p2_003_004_artifacts.py:sha256_of_file`
- `generate_p2_003_004_artifacts.py:generate_work_manifest`
- `generate_p2_003_004_artifacts.py:generate_repo_inventory`
- `app.py:signal_handler`
- `app.py:create_default_config`
- `app.py:validate_configuration`
- `app.py:rebuild_knowledge_index`
- `app.py:show_status`
- `temp_minimal_probes.py:MockEventBus`

## Detailed Analysis

### app.py

- **_setup_signal_handlers** (method) [U+1F534]
  - Line 46, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _setup_signal_handlers(self) -> None:...`

- **_start_tray_ui** (method) [U+1F534]
  - Line 78, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _start_tray_ui(self) -> None:...`

- **start** (method) [U+1F534]
  - Line 55, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 96, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **run_forever** (method) [U+1F534]
  - Line 120, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def run_forever(self) -> None:...`

- **signal_handler** (method) [U+1F7E1]
  - Line 48, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def signal_handler(signum: int, frame: Any) -> None:...`

- **create_default_config** (function) [U+1F7E1]
  - Line 168, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def create_default_config() -> None:...`

- **validate_configuration** (function) [U+1F7E1]
  - Line 182, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def validate_configuration(config_path: str) -> None:...`

- **rebuild_knowledge_index** (function) [U+1F7E1]
  - Line 205, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def rebuild_knowledge_index(packs_dir: str = "detection/knowledge/packs") -> Non...`

- **show_status** (function) [U+1F7E1]
  - Line 230, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def show_status() -> None:...`

### app_core/bus.py

- **_worker** (method) [U+1F534]
  - Line 95, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _worker(self) -> None:...`

- **_deliver_event** (method) [U+1F534]
  - Line 110, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _deliver_event(self, event: SentinelEvent) -> None:...`

- **start** (method) [U+1F534]
  - Line 72, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 82, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **subscribe** (method) [U+1F534]
  - Line 183, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def subscribe(...`

- **unsubscribe** (method) [U+1F534]
  - Line 223, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def unsubscribe(self, subscription: EventSubscription) -> None:...`

- **publish** (method) [U+1F534]
  - Line 239, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def publish(self, event: SentinelEvent) -> None:...`

- **publish_sync** (method) [U+1F534]
  - Line 253, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def publish_sync(self, event: SentinelEvent) -> None:...`

- **get_stats** (method) [U+1F534]
  - Line 269, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_stats(self) -> dict[str, Any]:...`

- **get_observability_metrics** (method) [U+1F534]
  - Line 286, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_observability_metrics(self) -> dict[str, int]:...`

### app_core/config.py

- **subscribe_on_change** (function) [U+1F534]
  - Line 306, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def subscribe_on_change(cb: Callable[[SentinelConfig], None]) -> None:...`

- **get_current_config** (function) [U+1F534]
  - Line 389, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def get_current_config() -> SentinelConfig | None:...`

- **get_config_version** (function) [U+1F534]
  - Line 398, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def get_config_version() -> int:...`

- **start_hot_reload** (function) [U+1F7E1]
  - Line 265, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def start_hot_reload(loop: asyncio.AbstractEventLoop | None = None) -> None:...`

- **stop_hot_reload** (function) [U+1F7E1]
  - Line 291, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def stop_hot_reload() -> None:...`

- **_watch_config** (function) [U+1F7E1]
  - Line 317, confidence: 0.60
  - Usages: 2
  - Reasons: Very few usages found, Private method/function (internal use)
  - Code: `async def _watch_config() -> None:...`

- **MonitoringConfig** (class) [U+1F7E1]
  - Line 82, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class MonitoringConfig(BaseModel):...`

- **RAGConfig** (class) [U+1F7E1]
  - Line 91, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class RAGConfig(BaseModel):...`

- **ServiceConfig** (class) [U+1F7E1]
  - Line 132, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class ServiceConfig(BaseModel):...`

- **PrivacyConfig** (class) [U+1F7E1]
  - Line 138, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class PrivacyConfig(BaseModel):...`

### app_core/logging_setup.py

- **log_event** (method) [U+1F534]
  - Line 31, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def log_event(self, event: SentinelEvent) -> None:...`

- **log_alert** (method) [U+1F534]
  - Line 48, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def log_alert(self, alert: DetectionAlert) -> None:...`

- **setup_windows_event_log** (function) [U+1F534]
  - Line 152, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def setup_windows_event_log() -> logging.Handler | None:...`

- **emit** (method) [U+1F534]
  - Line 173, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def emit(self, record: logging.LogRecord) -> None:...`

- **log_event** (function) [U+1F534]
  - Line 205, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def log_event(event: SentinelEvent, handlers: dict[str, Any]) -> None:...`

- **log_alert** (function) [U+1F534]
  - Line 220, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def log_alert(alert: DetectionAlert, handlers: dict[str, Any]) -> None:...`

- **get_log_stats** (function) [U+1F534]
  - Line 245, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def get_log_stats(log_dir: str = "logs") -> dict[str, Any]:...`

- **JSONLEventHandler** (class) [U+1F7E1]
  - Line 19, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class JSONLEventHandler:...`

- **JSONLAlertHandler** (class) [U+1F7E1]
  - Line 45, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class JSONLAlertHandler(JSONLEventHandler):...`

- **setup_logging** (function) [U+1F7E1]
  - Line 67, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def setup_logging(...`

### app_core/schemas.py

- **validate_entropy** (method) [U+1F534]
  - Line 101, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def validate_entropy(cls, v: float | None) -> float | None:...`

- **HealthAlert** (class) [U+1F534]
  - Line 181, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class HealthAlert(DetectionAlert):...`

### collectors/fs_monitor.py

- **_compile_exclude_patterns** (method) [U+1F534]
  - Line 114, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _compile_exclude_patterns(self) -> list[str]:...`

- **_should_exclude** (method) [U+1F534]
  - Line 122, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _should_exclude(self, file_path: str) -> bool:...`

- **_poll_loop** (method) [U+1F534]
  - Line 273, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _poll_loop(self) -> None:...`

- **_scan_directories** (method) [U+1F534]
  - Line 283, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _scan_directories(self) -> None:...`

- **_start_watchdog** (method) [U+1F534]
  - Line 379, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _start_watchdog(self) -> None:...`

- **_start_polling** (method) [U+1F534]
  - Line 401, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _start_polling(self) -> None:...`

- **create_file_event** (method) [U+1F534]
  - Line 138, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def create_file_event(...`

- **on_created** (method) [U+1F534]
  - Line 201, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def on_created(self, event: FileSystemEvent) -> None:...`

- **on_modified** (method) [U+1F534]
  - Line 209, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def on_modified(self, event: FileSystemEvent) -> None:...`

- **on_deleted** (method) [U+1F534]
  - Line 217, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def on_deleted(self, event: FileSystemEvent) -> None:...`

### collectors/health_monitor.py

- **_monitor_loop** (method) [U+1F534]
  - Line 104, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _monitor_loop(self) -> None:...`

- **_collect_health_metrics** (method) [U+1F534]
  - Line 128, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _collect_health_metrics(self) -> HealthMetric | None:...`

- **_check_thresholds** (method) [U+1F534]
  - Line 163, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _check_thresholds(self, metrics: HealthMetric) -> None:...`

- **_create_health_alert** (method) [U+1F534]
  - Line 212, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _create_health_alert(...`

- **start** (method) [U+1F534]
  - Line 74, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 90, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **get_current_metrics** (method) [U+1F534]
  - Line 249, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_current_metrics(self) -> HealthMetric | None:...`

- **get_stats** (method) [U+1F534]
  - Line 257, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_stats(self) -> dict[str, Any]:...`

- **get_system_info** (method) [U+1F534]
  - Line 283, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_system_info(self) -> dict[str, Any]:...`

- **get_cpu_temperature** (function) [U+1F7E1]
  - Line 26, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def get_cpu_temperature() -> float | None:...`

### collectors/net_monitor.py

- **_initialize_network_state** (method) [U+1F534]
  - Line 120, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _initialize_network_state(self) -> None:...`

- **_monitor_loop** (method) [U+1F534]
  - Line 145, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _monitor_loop(self) -> None:...`

- **_get_network_connections** (method) [U+1F534]
  - Line 159, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_network_connections(self) -> list[ConnectionInfo]:...`

- **_check_network_changes** (method) [U+1F534]
  - Line 216, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _check_network_changes(self) -> None:...`

- **_emit_network_event** (method) [U+1F534]
  - Line 262, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _emit_network_event(self, event_type: NetworkEventType, conn_state: Co...`

- **connection_key** (method) [U+1F534]
  - Line 61, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def connection_key(self) -> tuple[int | None, tuple[str, int], tuple[str, int], ...`

- **start** (method) [U+1F534]
  - Line 87, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 106, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **get_connection_stats** (method) [U+1F534]
  - Line 298, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_connection_stats(self) -> dict[str, Any]:...`

- **get_stats** (method) [U+1F534]
  - Line 318, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_stats(self) -> dict[str, Any]:...`

### collectors/proc_monitor.py

- **_initialize_process_state** (method) [U+1F534]
  - Line 110, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _initialize_process_state(self) -> None:...`

- **_monitor_loop** (method) [U+1F534]
  - Line 137, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _monitor_loop(self) -> None:...`

- **_check_process_changes** (method) [U+1F534]
  - Line 151, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _check_process_changes(self) -> None:...`

- **_handle_process_start** (method) [U+1F534]
  - Line 194, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _handle_process_start(self, proc: psutil.Process, info: dict[str, Any]...`

- **_handle_process_exit** (method) [U+1F534]
  - Line 238, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _handle_process_exit(self, pid: int) -> None:...`

- **start** (method) [U+1F534]
  - Line 77, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 96, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **get_process_ancestry** (method) [U+1F534]
  - Line 273, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_process_ancestry(self, pid: int, max_depth: int = 10) -> list[int]:...`

- **is_child_of** (method) [U+1F534]
  - Line 300, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def is_child_of(self, child_pid: int, parent_pid: int) -> bool:...`

- **get_stats** (method) [U+1F534]
  - Line 313, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_stats(self) -> dict[str, Any]:...`

### collectors/reg_monitor.py

- **_capture_state** (method) [U+1F534]
  - Line 163, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _capture_state(self) -> None:...`

- **_notification_loop** (method) [U+1F534]
  - Line 291, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _notification_loop(self) -> None:...`

- **_polling_loop** (method) [U+1F534]
  - Line 298, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _polling_loop(self) -> None:...`

- **_emit_registry_event** (method) [U+1F534]
  - Line 313, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _emit_registry_event(self, event_type: RegistryEventType, value_name: ...`

- **get_changes** (method) [U+1F534]
  - Line 185, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_changes(self) -> list[tuple[RegistryEventType, str]]:...`

- **start** (method) [U+1F534]
  - Line 263, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 282, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **start** (method) [U+1F534]
  - Line 363, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 393, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **get_stats** (method) [U+1F534]
  - Line 411, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_stats(self) -> dict[str, Any]:...`

### config/operational_mode.py

- **_invalidate_cache** (function) [U+1F534]
  - Line 185, confidence: 0.84
  - Usages: 1
  - Reasons: Only one usage found, Private method/function (internal use)
  - Code: `def _invalidate_cache() -> None:...`

- **_get_config_file_path** (function) [U+1F7E1]
  - Line 33, confidence: 0.60
  - Usages: 2
  - Reasons: Very few usages found, Private method/function (internal use)
  - Code: `def _get_config_file_path() -> Path:...`

- **_read_mode_from_file** (function) [U+1F7E1]
  - Line 44, confidence: 0.60
  - Usages: 2
  - Reasons: Very few usages found, Private method/function (internal use)
  - Code: `def _read_mode_from_file() -> OperationalMode:...`

- **_write_mode_to_file** (function) [U+1F7E1]
  - Line 75, confidence: 0.60
  - Usages: 2
  - Reasons: Very few usages found, Private method/function (internal use)
  - Code: `def _write_mode_to_file(mode: OperationalMode) -> None:...`

- **is_valid_mode** (function) [U+1F7E1]
  - Line 164, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def is_valid_mode(mode: str) -> bool:...`

- **get_valid_modes** (function) [U+1F7E1]
  - Line 176, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def get_valid_modes() -> list[OperationalMode]:...`

### console/anomaly.py

- **to_dict** (method) [U+1F534]
  - Line 43, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def to_dict(self) -> Dict[str, Any]:...`

- **from_dict** (method) [U+1F534]
  - Line 52, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def from_dict(self, data: Dict[str, Any]) -> None:...`

- **save_to_file** (method) [U+1F534]
  - Line 59, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def save_to_file(self) -> None:...`

- **load_from_file** (method) [U+1F534]
  - Line 69, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def load_from_file(self) -> None:...`

- **extract_features** (method) [U+1F534]
  - Line 99, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def extract_features(self, event_data: Optional[Dict[str, Any]] = None) -> Dict[...`

- **calculate_z_score** (method) [U+1F534]
  - Line 136, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def calculate_z_score(self, feature_name: str, value: float) -> float:...`

- **calculate_mad_score** (method) [U+1F534]
  - Line 147, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def calculate_mad_score(self, feature_name: str, value: float) -> float:...`

- **update_feature_stats** (method) [U+1F534]
  - Line 168, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def update_feature_stats(self, features: Dict[str, float]) -> None:...`

- **load_isolation_forest** (method) [U+1F534]
  - Line 336, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def load_isolation_forest(self) -> bool:...`

- **predict_with_isolation_forest** (method) [U+1F534]
  - Line 348, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def predict_with_isolation_forest(self, features: Dict[str, float]) -> Dict[str,...`

### console/api/operational_mode.py

- **get_operational_mode** (function) [U+1F534]
  - Line 21, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `async def get_operational_mode() -> OperationalModeResponse:...`

- **set_operational_mode** (function) [U+1F534]
  - Line 51, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `async def set_operational_mode(request: OperationalModeRequest) -> OperationalMo...`

### console/auth.py

- **_ensure_db_exists** (method) [U+1F534]
  - Line 34, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _ensure_db_exists(self):...`

- **_load_users** (method) [U+1F534]
  - Line 40, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _load_users(self) -> Dict[str, str]:...`

- **_save_users** (method) [U+1F534]
  - Line 48, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _save_users(self, users: Dict[str, str]):...`

- **_hash_password** (method) [U+1F534]
  - Line 53, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _hash_password(self, password: str) -> str:...`

- **_verify_password** (method) [U+1F534]
  - Line 62, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _verify_password(self, password: str, pw_hash: str) -> bool:...`

- **add_user** (method) [U+1F534]
  - Line 81, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def add_user(self, username: str, password: str) -> bool:...`

- **verify_user** (method) [U+1F534]
  - Line 91, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def verify_user(self, username: str, password: str) -> bool:...`

- **user_exists** (method) [U+1F534]
  - Line 99, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def user_exists(self, username: str) -> bool:...`

- **create_session_token** (method) [U+1F534]
  - Line 114, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def create_session_token(self, username: str) -> str:...`

- **verify_session_token** (method) [U+1F534]
  - Line 125, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def verify_session_token(self, token: str) -> Optional[str]:...`

### console/backup_restore.py

- **_calculate_file_hash** (method) [U+1F534]
  - Line 266, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _calculate_file_hash(self, file_path: Path) -> str:...`

- **list_backups** (method) [U+1F534]
  - Line 207, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def list_backups(self) -> Dict[str, Any]:...`

- **create_backup** (method) [U+1F7E1]
  - Line 45, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def create_backup(self, description: str = "") -> Dict[str, Any]:...`

- **restore_backup** (method) [U+1F7E1]
  - Line 116, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def restore_backup(self, backup_path: str, confirm: bool = False) -> Dict[str, A...`

- **get_backup_manager** (function) [U+1F7E1]
  - Line 286, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def get_backup_manager() -> BackupManager:...`

### console/chaos_probes.py

- **inject_latency** (method) [U+1F534]
  - Line 32, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def inject_latency(self, component: str, latency_ms: int) -> Dict[str, Any]:...`

- **inject_error** (method) [U+1F534]
  - Line 93, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def inject_error(self, component: str, error_type: str = "generic", error_rate: ...`

- **chaos_context** (method) [U+1F534]
  - Line 177, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def chaos_context(self, component: str, mode: str = "latency", **kwargs) -> "Cha...`

- **list_active_probes** (method) [U+1F534]
  - Line 190, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def list_active_probes(self) -> Dict[str, Any]:...`

- **stop_probe** (method) [U+1F534]
  - Line 213, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def stop_probe(self, injection_id: str) -> Dict[str, Any]:...`

- **stop_all_probes** (method) [U+1F534]
  - Line 250, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def stop_all_probes(self) -> Dict[str, Any]:...`

- **get_injection_history** (method) [U+1F534]
  - Line 280, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_injection_history(self, limit: int = 50) -> Dict[str, Any]:...`

- **get_statistics** (method) [U+1F534]
  - Line 308, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_statistics(self) -> Dict[str, Any]:...`

- **chaos_injection** (function) [U+1F7E1]
  - Line 423, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def chaos_injection(component: str, mode: str = "latency", **kwargs):...`

- **ChaosContext** (class) [U+1F7E1]
  - Line 351, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class ChaosContext:...`

### console/config_schema.py

- **_build_schema** (method) [U+1F534]
  - Line 23, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _build_schema(self) -> Dict[str, Any]:...`

- **_validate_value** (method) [U+1F534]
  - Line 232, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _validate_value(self, key: str, value: Any, schema_def: Dict[str, Any]) -> A...`

- **_check_required_dependencies** (method) [U+1F534]
  - Line 279, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _check_required_dependencies(self, key: str, value: Any, schema_def: Dict[st...`

- **validate_env_config** (method) [U+1F534]
  - Line 198, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def validate_env_config(self) -> Dict[str, Any]:...`

- **get_schema_dict** (method) [U+1F534]
  - Line 293, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_schema_dict(self) -> Dict[str, Any]:...`

- **get_config_summary** (method) [U+1F534]
  - Line 297, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_config_summary(self) -> Dict[str, Any]:...`

- **validate_current_config** (function) [U+1F534]
  - Line 331, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def validate_current_config() -> Dict[str, Any]:...`

- **get_schema_for_api** (function) [U+1F534]
  - Line 336, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def get_schema_for_api() -> Dict[str, Any]:...`

- **ConfigValidationError** (class) [U+1F7E1]
  - Line 12, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class ConfigValidationError(Exception):...`

- **get_config_schema** (function) [U+1F7E1]
  - Line 323, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def get_config_schema() -> ConfigSchema:...`

### console/console_ui.py

- **ensure_static_files** (function) [U+1F534]
  - Line 542, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def ensure_static_files() -> bool:...`

- **get_console_info** (function) [U+1F534]
  - Line 587, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def get_console_info() -> Dict[str, Any]:...`

- **get_dashboard_html** (function) [U+1F7E1]
  - Line 16, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def get_dashboard_html() -> str:...`

### console/log_config.py

- **_build_redaction_patterns** (method) [U+1F534]
  - Line 21, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _build_redaction_patterns(self):...`

- **_redact_text** (method) [U+1F534]
  - Line 84, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _redact_text(self, text: str) -> str:...`

- **filter** (method) [U+1F534]
  - Line 53, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def filter(self, record: logging.LogRecord) -> bool:...`

- **create_rotating_handler** (method) [U+1F534]
  - Line 123, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def create_rotating_handler(self, log_name: str,...`

- **setup_logger** (method) [U+1F534]
  - Line 161, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def setup_logger(self, logger_name: str,...`

- **get_log_status** (method) [U+1F534]
  - Line 192, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_log_status(self) -> Dict[str, Any]:...`

- **setup_application_logging** (function) [U+1F534]
  - Line 224, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def setup_application_logging():...`

- **SecretRedactionFilter** (class) [U+1F7E1]
  - Line 13, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class SecretRedactionFilter(logging.Filter):...`

- **RotatingLogConfig** (class) [U+1F7E1]
  - Line 96, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class RotatingLogConfig:...`

- **get_log_config** (function) [U+1F7E1]
  - Line 207, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def get_log_config() -> RotatingLogConfig:...`

### console/perf_probe.py

- **_make_request** (method) [U+1F534]
  - Line 40, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict:...`

- **generate_load_test_report** (method) [U+1F534]
  - Line 304, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_load_test_report(...`

- **run_stress_test** (function) [U+1F7E1]
  - Line 406, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def run_stress_test(...`

- **percentile** (method) [U+1F7E1]
  - Line 180, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def percentile(p):...`

- **run_basic_performance_check** (function) [U+1F7E1]
  - Line 389, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def run_basic_performance_check(base_url: str = "http://127.0.0.1:8080") -> Dict...`

- **get_performance_probe** (function) [U+1F7E1]
  - Line 430, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def get_performance_probe(base_url: str = "http://127.0.0.1:8080") -> Performanc...`

### console/plugin_sandbox.py

- **load_manifest** (method) [U+1F534]
  - Line 79, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def load_manifest(self) -> Dict[str, Any]:...`

- **verify_plugin_hash** (method) [U+1F534]
  - Line 104, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def verify_plugin_hash(self, plugin_name: str, plugin_config: Dict[str, Any]) ->...`

- **sandboxed_import** (method) [U+1F534]
  - Line 137, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def sandboxed_import(self, context: SandboxContext):...`

- **load_plugin** (method) [U+1F534]
  - Line 164, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def load_plugin(self, plugin_name: str, plugin_config: Dict[str, Any]) -> Option...`

- **load_all_plugins** (method) [U+1F534]
  - Line 219, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def load_all_plugins(self) -> Dict[str, Any]:...`

- **execute_plugin** (method) [U+1F534]
  - Line 241, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def execute_plugin(self, plugin_name: str, event: Dict[str, Any]) -> Optional[Di...`

- **unload_plugin** (method) [U+1F534]
  - Line 269, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def unload_plugin(self, plugin_name: str) -> bool:...`

- **restricted_import** (method) [U+1F7E1]
  - Line 143, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):...`

- **execute_plugin_hook** (function) [U+1F7E1]
  - Line 326, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def execute_plugin_hook(hook_name: str, event_data: Dict[str, Any]) -> List[Dict...`

### console/preflight_checks.py

- **check_python_environment** (method) [U+1F534]
  - Line 57, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_python_environment(self) -> PreflightResult:...`

- **check_required_modules** (method) [U+1F534]
  - Line 101, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_required_modules(self) -> PreflightResult:...`

- **check_file_permissions** (method) [U+1F534]
  - Line 157, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_file_permissions(self) -> PreflightResult:...`

- **check_network_connectivity** (method) [U+1F534]
  - Line 213, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_network_connectivity(self) -> PreflightResult:...`

- **check_system_resources** (method) [U+1F534]
  - Line 259, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_system_resources(self) -> PreflightResult:...`

- **check_configuration_integrity** (method) [U+1F534]
  - Line 333, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_configuration_integrity(self) -> PreflightResult:...`

- **check_security_settings** (method) [U+1F534]
  - Line 410, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_security_settings(self) -> PreflightResult:...`

- **run_all_checks** (method) [U+1F534]
  - Line 487, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def run_all_checks(self) -> PreflightSummary:...`

### console/quarantine.py

- **_load_mapping** (method) [U+1F534]
  - Line 122, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _load_mapping(self) -> None:...`

- **_save_mapping** (method) [U+1F534]
  - Line 132, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _save_mapping(self) -> None:...`

- **quarantine_file** (method) [U+1F7E1]
  - Line 142, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def quarantine_file(self, source_path: str) -> Dict[str, Any]:...`

- **restore_file** (method) [U+1F7E1]
  - Line 213, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def restore_file(self, sha256: str, target_path: Optional[str] = None) -> Dict[s...`

- **list_quarantined_files** (method) [U+1F7E1]
  - Line 289, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def list_quarantined_files(self) -> List[Dict[str, Any]]:...`

- **get_quarantine_status** (method) [U+1F7E1]
  - Line 306, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def get_quarantine_status(self) -> Dict[str, Any]:...`

- **quarantine_file** (function) [U+1F7E1]
  - Line 328, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def quarantine_file(source_path: str) -> Dict[str, Any]:...`

- **restore_file** (function) [U+1F7E1]
  - Line 334, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def restore_file(sha256: str, target_path: Optional[str] = None) -> Dict[str, An...`

- **list_quarantined_files** (function) [U+1F7E1]
  - Line 340, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def list_quarantined_files() -> List[Dict[str, Any]]:...`

- **get_quarantine_status** (function) [U+1F7E1]
  - Line 346, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def get_quarantine_status() -> Dict[str, Any]:...`

### console/rate_limit.py

- **allow** (method) [U+1F534]
  - Line 30, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def allow(self, cost: float = 1.0) -> bool:...`

- **rate_limit_dependency** (function) [U+1F534]
  - Line 44, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def rate_limit_dependency(route_key: str, max_calls: int, window_s: int):...`

- **TokenBucket** (class) [U+1F7E1]
  - Line 22, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class TokenBucket:...`

### console/retention.py

- **run_retention_job** (function) [U+1F7E1]
  - Line 218, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def run_retention_job(dry_run: bool = True, retention_days: Optional[int] = None...`

- **get_directory_stats** (function) [U+1F7E1]
  - Line 282, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def get_directory_stats() -> Dict:...`

### console/schemas.py

- **Config** (class) [U+1F534]
  - Line 25, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class Config:...`

- **Config** (class) [U+1F534]
  - Line 36, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class Config:...`

- **Config** (class) [U+1F534]
  - Line 49, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class Config:...`

- **OperationalModeRequest** (class) [U+1F7E1]
  - Line 17, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `class OperationalModeRequest(BaseModel):...`

- **OperationalModeResponse** (class) [U+1F7E1]
  - Line 30, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `class OperationalModeResponse(BaseModel):...`

- **OperationalModeUpdateResponse** (class) [U+1F7E1]
  - Line 41, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `class OperationalModeUpdateResponse(BaseModel):...`

### console/telemetry_export.py

- **collect_system_metrics** (method) [U+1F534]
  - Line 25, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def collect_system_metrics(self) -> Dict[str, Any]:...`

- **collect_application_metrics** (method) [U+1F534]
  - Line 71, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def collect_application_metrics(self) -> Dict[str, Any]:...`

- **collect_security_metrics** (method) [U+1F534]
  - Line 107, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def collect_security_metrics(self) -> Dict[str, Any]:...`

- **collect_plugin_metrics** (method) [U+1F534]
  - Line 138, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def collect_plugin_metrics(self) -> Dict[str, Any]:...`

- **collect_all_metrics** (method) [U+1F534]
  - Line 160, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def collect_all_metrics(self) -> Dict[str, Any]:...`

- **export_json** (method) [U+1F534]
  - Line 194, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def export_json(self, include_system: bool = True, include_security: bool = True...`

- **export_prometheus** (method) [U+1F534]
  - Line 215, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def export_prometheus(self) -> str:...`

- **export_csv** (method) [U+1F534]
  - Line 271, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def export_csv(self) -> str:...`

- **add_metric** (method) [U+1F7E1]
  - Line 225, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def add_metric(name: str, value: float, help_text: str, labels: Optional[Dict[st...`

- **export_telemetry** (function) [U+1F7E1]
  - Line 320, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def export_telemetry(format_type: str = "json", **kwargs) -> str:...`

### console/web_api.py

- **_setup_error_handlers** (method) [U+1F534]
  - Line 328, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _setup_error_handlers(self) -> None:...`

- **_setup_routes** (method) [U+1F534]
  - Line 359, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _setup_routes(self) -> None:...`

- **_get_composite_health_metrics** (method) [U+1F534]
  - Line 1579, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _get_composite_health_metrics(self) -> dict:...`

- **validation_exception_handler** (method) [U+1F534]
  - Line 332, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def validation_exception_handler(request: Request, exc: ValidationError) -...`

- **http_exception_handler** (method) [U+1F534]
  - Line 346, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def http_exception_handler(request: Request, exc: HTTPException) -> JSONRe...`

- **get_status** (method) [U+1F534]
  - Line 364, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def get_status() -> StatusResponse:...`

- **get_alerts** (method) [U+1F534]
  - Line 380, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def get_alerts() -> AlertSummary:...`

- **get_detections** (method) [U+1F534]
  - Line 412, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def get_detections(...`

- **pause_monitoring** (method) [U+1F534]
  - Line 442, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def pause_monitoring(duration_minutes: int = 5) -> ActionResponse:...`

- **resume_monitoring** (method) [U+1F534]
  - Line 455, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def resume_monitoring() -> ActionResponse:...`

### detection/attack_matrix.py

- **_basic_where_filter** (method) [U+1F534]
  - Line 237, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _basic_where_filter(self, where_clause: str, event_data: Dict[str, Any]) -> ...`

- **model_post_init** (method) [U+1F534]
  - Line 38, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def model_post_init(self, __context: Any) -> None:...`

- **increment** (method) [U+1F534]
  - Line 123, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def increment(self, key: str) -> int:...`

- **get_count** (method) [U+1F534]
  - Line 136, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_count(self, key: str) -> int:...`

- **handle_matches** (method) [U+1F534]
  - Line 250, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def handle_matches(self, matched_rules: List[Rule], event_data: Dict[str, Any]) ...`

- **process_event** (method) [U+1F7E1]
  - Line 181, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def process_event(self, event_type: str, event_data: Dict[str, Any]) -> List[Rul...`

- **get_loaded_rules** (method) [U+1F7E1]
  - Line 277, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def get_loaded_rules(self) -> List[Dict[str, Any]]:...`

- **get_loaded_rules** (function) [U+1F7E1]
  - Line 825, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def get_loaded_rules() -> List[Dict[str, Any]]:...`

- **wire** (function) [U+1F7E1]
  - Line 831, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def wire(bus, responder=None, rules=None, profile="baseline"):...`

- **AttackMatrixEngine** (class) [U+1F7E1]
  - Line 145, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class AttackMatrixEngine:...`

### detection/behavioral_engine.py

- **_get_event_type_string** (method) [U+1F534]
  - Line 112, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_event_type_string(self, event: BaseEvent) -> str:...`

- **_update_process_baseline** (method) [U+1F534]
  - Line 120, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _update_process_baseline(self, event: BaseEvent) -> None:...`

- **_update_network_baseline** (method) [U+1F534]
  - Line 142, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _update_network_baseline(self, event: BaseEvent) -> None:...`

- **_update_file_baseline** (method) [U+1F534]
  - Line 149, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _update_file_baseline(self, event: BaseEvent) -> None:...`

- **_update_resource_baseline** (method) [U+1F534]
  - Line 159, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _update_resource_baseline(self, event: BaseEvent) -> None:...`

- **_initialize_ml_models** (method) [U+1F534]
  - Line 285, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _initialize_ml_models(self) -> None:...`

- **_load_historical_baselines** (method) [U+1F534]
  - Line 314, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _load_historical_baselines(self) -> None:...`

- **_parse_event_data** (method) [U+1F534]
  - Line 350, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _parse_event_data(self, event_data: dict[str, Any]) -> BaseEvent | None:...`

- **_update_baselines_from_event** (method) [U+1F534]
  - Line 369, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _update_baselines_from_event(self, event: BaseEvent) -> None:...`

- **_get_entity_id** (method) [U+1F534]
  - Line 387, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_entity_id(self, event: BaseEvent) -> str:...`

### detection/knowledge/loader.py

- **_init_database** (method) [U+1F534]
  - Line 69, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _init_database(self) -> None:...`

- **_try_init_embeddings** (method) [U+1F534]
  - Line 128, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _try_init_embeddings(self) -> None:...`

- **_ensure_embeddings_loaded** (method) [U+1F534]
  - Line 150, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _ensure_embeddings_loaded(self) -> None:...`

- **_compute_file_hash** (method) [U+1F534]
  - Line 155, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _compute_file_hash(self, file_path: Path) -> str:...`

- **_parse_sentinel_directives** (method) [U+1F534]
  - Line 170, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _parse_sentinel_directives(self, content: str, filename: str) -> list[Sentin...`

- **_extract_sections** (method) [U+1F534]
  - Line 207, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_sections(self, content: str, filename: str) -> list[tuple[str, str,...`

- **_index_file** (method) [U+1F534]
  - Line 288, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _index_file(self, file_path: Path, conn: sqlite3.Connection, stats: dict[str...`

- **_query_embeddings** (method) [U+1F534]
  - Line 376, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _query_embeddings(self, query: str, limit: int) -> list[KnowledgeHit]:...`

- **_query_fts** (method) [U+1F534]
  - Line 432, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _query_fts(self, query: str, limit: int) -> list[KnowledgeHit]:...`

- **rebuild_index** (method) [U+1F534]
  - Line 249, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def rebuild_index(self) -> dict[str, Any]:...`

### detection/ml_scoring.py

- **_try_load_model** (method) [U+1F534]
  - Line 36, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _try_load_model(self, model_path: str) -> None:...`

- **_score_with_model** (method) [U+1F534]
  - Line 108, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _score_with_model(self, signal: dict[str, Any]) -> tuple[float, str]:...`

- **_extract_features** (method) [U+1F534]
  - Line 150, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_features(self, signal: dict[str, Any]) -> list[float]:...`

- **score_behavior** (method) [U+1F534]
  - Line 78, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def score_behavior(self, signal: dict[str, Any]) -> tuple[float, str] | None:...`

- **is_available** (method) [U+1F534]
  - Line 209, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def is_available(self) -> bool:...`

- **get_model_info** (method) [U+1F534]
  - Line 217, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_model_info(self) -> dict[str, Any]:...`

- **validate_signal** (method) [U+1F534]
  - Line 234, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def validate_signal(self, signal: dict[str, Any]) -> bool:...`

- **get_ml_scorer** (function) [U+1F7E1]
  - Line 281, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `def get_ml_scorer() -> MLScoringEngine:...`

- **MLScoringEngine** (class) [U+1F7E1]
  - Line 16, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class MLScoringEngine:...`

- **create_ml_scorer** (function) [U+1F7E1]
  - Line 259, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def create_ml_scorer(model_path: str | None = None) -> MLScoringEngine:...`

### detection/rule_dsl.py

- **_parse_where_clause** (method) [U+1F534]
  - Line 162, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _parse_where_clause(self, clause: str) -> List[Dict[str, Any]]:...`

- **_parse_condition** (method) [U+1F534]
  - Line 178, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _parse_condition(self, condition: str) -> Optional[Dict[str, Any]]:...`

- **_evaluate_condition** (method) [U+1F534]
  - Line 215, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _evaluate_condition(self, condition: Dict[str, Any], event_data: Dict[str, A...`

- **_get_field_value** (method) [U+1F534]
  - Line 240, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_field_value(self, data: Dict[str, Any], field: str) -> Any:...`

- **_initialize_rules** (method) [U+1F534]
  - Line 268, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _initialize_rules(self):...`

- **_extract_group_key** (method) [U+1F534]
  - Line 320, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_group_key(self, rule: Rule, event_data: Dict[str, Any]) -> Optional...`

- **_check_sequence_rule** (method) [U+1F534]
  - Line 431, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _check_sequence_rule(self, rule: SequenceRule, event_type: str, event_data: ...`

- **_evaluate_where_with_bindings** (method) [U+1F534]
  - Line 504, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _evaluate_where_with_bindings(self, where_clause: Dict[str, Any], event_data...`

- **_update_bindings** (method) [U+1F534]
  - Line 525, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _update_bindings(self, where_clause: Dict[str, Any], event_data: Dict[str, A...`

- **_check_count_condition** (method) [U+1F534]
  - Line 533, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _check_count_condition(self, actual_count: int, operator: str, expected_coun...`

### detection/rules_engine.py

- **_cleanup_old_events** (method) [U+1F534]
  - Line 52, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _cleanup_old_events(self) -> None:...`

- **_handle_file_event** (method) [U+1F534]
  - Line 500, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _handle_file_event(self, event: FileEvent) -> None:...`

- **_handle_process_event** (method) [U+1F534]
  - Line 522, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _handle_process_event(self, event: ProcessEvent) -> None:...`

- **_handle_registry_event** (method) [U+1F534]
  - Line 538, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _handle_registry_event(self, event: RegistryEvent) -> None:...`

- **_handle_network_event** (method) [U+1F534]
  - Line 554, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _handle_network_event(self, event: NetworkEvent) -> None:...`

- **_handle_health_metric** (method) [U+1F534]
  - Line 570, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _handle_health_metric(self, event: HealthMetric) -> None:...`

- **add_event** (method) [U+1F534]
  - Line 42, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def add_event(self, event: SentinelEvent) -> None:...`

- **get_events** (method) [U+1F534]
  - Line 60, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_events(self, event_type: type | None = None) -> list[SentinelEvent]:...`

- **count_events** (method) [U+1F534]
  - Line 76, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def count_events(self, event_type: type | None = None) -> int:...`

- **check_file_event** (method) [U+1F534]
  - Line 98, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_file_event(self, event: FileEvent) -> DetectionAlert | None:...`

### detection/threat_intel_db.py

- **_ti_cache_clear** (function) [U+1F534]
  - Line 41, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use)
  - Code: `def _ti_cache_clear() -> None:...`

- **_identify_framework** (method) [U+1F534]
  - Line 300, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _identify_framework(self, filename: str) -> str:...`

- **_extract_metadata** (method) [U+1F534]
  - Line 315, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_metadata(self, content: str, filename: str) -> dict[str, Any]:...`

- **_build_search_queries** (method) [U+1F534]
  - Line 342, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _build_search_queries(self, alert: DetectionAlert) -> list[str]:...`

- **_extract_techniques_from_intel** (method) [U+1F534]
  - Line 364, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_techniques_from_intel(self, intel_results: list[dict[str, Any]]) ->...`

- **_get_mitre_tactics** (method) [U+1F534]
  - Line 380, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_mitre_tactics(self) -> list[str]:...`

- **_get_kill_chain_phases** (method) [U+1F534]
  - Line 389, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_kill_chain_phases(self) -> list[str]:...`

- **_get_incident_response_phases** (method) [U+1F534]
  - Line 396, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_incident_response_phases(self) -> list[str]:...`

- **_get_mitre_techniques** (method) [U+1F534]
  - Line 403, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_mitre_techniques(self) -> list[str]:...`

- **_extract_tactics_from_results** (method) [U+1F534]
  - Line 412, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_tactics_from_results(self, results: list[dict[str, Any]]) -> list[s...`

### generate_inventory.py

- **generate_inventory** (function) [U+1F7E1]
  - Line 18, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def generate_inventory():...`

### generate_p2_003_004_artifacts.py

- **sha256_of_file** (function) [U+1F7E1]
  - Line 10, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def sha256_of_file(file_path):...`

- **generate_work_manifest** (function) [U+1F7E1]
  - Line 18, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def generate_work_manifest():...`

- **generate_repo_inventory** (function) [U+1F7E1]
  - Line 124, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def generate_repo_inventory():...`

### plugins/example_hello.py

- **initialize** (method) [U+1F534]
  - Line 30, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def initialize(self) -> bool:...`

- **execute** (method) [U+1F534]
  - Line 39, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def execute(self, event: Dict[str, Any]) -> Dict[str, Any]:...`

- **cleanup** (method) [U+1F534]
  - Line 58, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def cleanup(self) -> bool:...`

- **get_info** (method) [U+1F534]
  - Line 67, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_info(self) -> Dict[str, Any]:...`

- **create_plugin** (function) [U+1F534]
  - Line 87, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `def create_plugin(sandbox_context: Optional[Dict[str, Any]] = None):...`

- **HelloPlugin** (class) [U+1F7E1]
  - Line 16, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class HelloPlugin:...`

### response/actions.py

- **_auto_resume** (method) [U+1F534]
  - Line 242, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _auto_resume(self, duration: int) -> None:...`

- **_get_current_operational_mode** (method) [U+1F534]
  - Line 359, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_current_operational_mode(self) -> str:...`

- **_check_mode_enforcement** (method) [U+1F534]
  - Line 372, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _check_mode_enforcement(self, action_type: ActionType, action_description: s...`

- **to_dict** (method) [U+1F534]
  - Line 66, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def to_dict(self) -> dict[str, Any]:...`

- **terminate_process** (method) [U+1F534]
  - Line 87, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def terminate_process(pid: int, force: bool = False) -> ActionRecord:...`

- **pause_monitoring** (method) [U+1F534]
  - Line 190, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def pause_monitoring(self, duration_seconds: int) -> ActionRecord:...`

- **get_pause_remaining** (method) [U+1F534]
  - Line 270, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_pause_remaining(self) -> int | None:...`

- **resume_monitoring** (method) [U+1F534]
  - Line 282, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def resume_monitoring(self) -> ActionRecord:...`

- **quarantine_directory** (method) [U+1F534]
  - Line 316, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def quarantine_directory(path: str) -> ActionRecord:...`

- **terminate_process** (method) [U+1F534]
  - Line 431, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def terminate_process(self, pid: int, user_consent: bool = False, force: bool = ...`

### response/alerts.py

- **_handle_alert** (method) [U+1F534]
  - Line 268, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _handle_alert(self, alert: DetectionAlert) -> None:...`

- **send_notification** (method) [U+1F534]
  - Line 45, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def send_notification(self, alert: DetectionAlert) -> bool:...`

- **log_alert** (method) [U+1F534]
  - Line 96, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def log_alert(self, alert: DetectionAlert) -> bool:...`

- **get_recent_alerts** (method) [U+1F534]
  - Line 122, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_recent_alerts(self, count: int = 10) -> list[dict[str, Any]]:...`

- **add_alert** (method) [U+1F534]
  - Line 171, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def add_alert(self, alert: DetectionAlert) -> None:...`

- **get_alerts** (method) [U+1F534]
  - Line 180, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_alerts(self) -> list[DetectionAlert]:...`

- **get_recent_alerts** (method) [U+1F534]
  - Line 188, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_recent_alerts(self, count: int = 5) -> list[DetectionAlert]:...`

- **clear** (method) [U+1F534]
  - Line 199, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def clear(self) -> None:...`

- **start** (method) [U+1F534]
  - Line 237, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 255, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

### response/playbooks.py

- **_execute_response** (method) [U+1F534]
  - Line 61, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _execute_response(self, response: str, rule, ctx: Dict[str, Any]) -> N...`

- **Playbooks** (class) [U+1F7E1]
  - Line 13, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found
  - Code: `class Playbooks:...`

- **trigger** (method) [U+1F7E1]
  - Line 20, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `async def trigger(self, rule, ctx: Dict[str, Any]) -> None:...`

### scripts/generate_ga_signoff.py

- **_generate_signoff_content** (method) [U+1F534]
  - Line 375, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_signoff_content(self, components: Dict, assessment: Dict) -> str:...`

- **_format_performance_section** (method) [U+1F534]
  - Line 523, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _format_performance_section(self, perf_data: Dict) -> str:...`

- **_format_security_section** (method) [U+1F534]
  - Line 533, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _format_security_section(self, sec_data: Dict) -> str:...`

- **_format_sbom_section** (method) [U+1F534]
  - Line 544, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _format_sbom_section(self, sbom_data: Dict) -> str:...`

- **_format_packaging_section** (method) [U+1F534]
  - Line 553, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _format_packaging_section(self, pkg_data: Dict) -> str:...`

- **_format_windows_section** (method) [U+1F534]
  - Line 567, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _format_windows_section(self, win_data: Dict) -> str:...`

- **_format_verifier_section** (method) [U+1F534]
  - Line 578, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _format_verifier_section(self, verifier_data: Dict) -> str:...`

- **_format_risk_section** (method) [U+1F534]
  - Line 588, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _format_risk_section(self, blockers: List[str]) -> str:...`

- **_generate_recommendation_details** (method) [U+1F534]
  - Line 595, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_recommendation_details(self, assessment: Dict) -> str:...`

- **collect_performance_baseline** (method) [U+1F534]
  - Line 24, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def collect_performance_baseline(self) -> Dict:...`

### scripts/generate_sbom_clean.py

- **_extract_imports_from_file** (method) [U+1F534]
  - Line 60, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_imports_from_file(self, file_path: Path):...`

- **_classify_import** (method) [U+1F534]
  - Line 89, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _classify_import(self, import_name: str):...`

- **_generate_optional_license_analysis** (method) [U+1F534]
  - Line 308, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_optional_license_analysis(self, optional_deps):...`

- **scan_codebase** (method) [U+1F534]
  - Line 111, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def scan_codebase(self):...`

- **generate_sbom_manifest** (method) [U+1F534]
  - Line 145, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_sbom_manifest(self, output_path: Path):...`

- **generate_license_attestation** (method) [U+1F534]
  - Line 208, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_license_attestation(self, output_path: Path):...`

- **SBOMGenerator** (class) [U+1F7E1]
  - Line 52, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class SBOMGenerator:...`

### scripts/generate_security_posture.py

- **run_security_scan** (function) [U+1F7E1]
  - Line 15, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def run_security_scan(repo_root: Path):...`

- **analyze_findings** (function) [U+1F7E1]
  - Line 57, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def analyze_findings(findings_data):...`

- **calculate_security_score** (function) [U+1F7E1]
  - Line 119, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def calculate_security_score(severity_counts):...`

- **get_posture_level** (function) [U+1F7E1]
  - Line 142, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def get_posture_level(score):...`

- **generate_security_posture_report** (function) [U+1F7E1]
  - Line 162, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def generate_security_posture_report(analysis, output_path: Path):...`

- **generate_category_analysis** (function) [U+1F7E1]
  - Line 303, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def generate_category_analysis(category_breakdown, findings_by_category):...`

- **generate_recommendations** (function) [U+1F7E1]
  - Line 329, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def generate_recommendations(analysis):...`

- **generate_detailed_findings** (function) [U+1F7E1]
  - Line 352, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def generate_detailed_findings(findings_by_category):...`

### scripts/package_release.py

- **_create_manual_bundle** (method) [U+1F534]
  - Line 170, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _create_manual_bundle(self, bundle_path: Path) -> Tuple[bool, str]:...`

- **create_source_package** (method) [U+1F534]
  - Line 27, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def create_source_package(self) -> Tuple[bool, str]:...`

- **create_offline_bundle** (method) [U+1F534]
  - Line 115, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def create_offline_bundle(self) -> Tuple[bool, str]:...`

- **calculate_sha256** (method) [U+1F534]
  - Line 292, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def calculate_sha256(self, file_path: str) -> str:...`

- **generate_checksums** (method) [U+1F534]
  - Line 311, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_checksums(self, package_paths: List[str]) -> bool:...`

- **create_verification_evidence** (method) [U+1F534]
  - Line 345, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def create_verification_evidence(self, package_paths: List[str]) -> bool:...`

- **ReleasePackager** (class) [U+1F7E1]
  - Line 18, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class ReleasePackager:...`

### scripts/rc_soak_test.py

- **_monitor_system_resources** (method) [U+1F534]
  - Line 61, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _monitor_system_resources(self) -> None:...`

- **_run_load_test** (method) [U+1F534]
  - Line 74, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _run_load_test(self) -> Dict:...`

- **_calculate_percentiles** (method) [U+1F534]
  - Line 131, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _calculate_percentiles(self, data: List[float]) -> Dict[str, float]:...`

- **_assess_ga_readiness** (method) [U+1F534]
  - Line 281, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _assess_ga_readiness(self, rps: float, response_perf: Dict, cpu_perf: Dict, ...`

- **generate_baseline_report** (method) [U+1F534]
  - Line 152, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_baseline_report(self, output_path: str) -> bool:...`

- **RCSoakTest** (class) [U+1F7E1]
  - Line 31, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class RCSoakTest:...`

### scripts/rc_soak_test_mock.py

- **assess_ga_readiness** (method) [U+1F534]
  - Line 57, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def assess_ga_readiness(self) -> str:...`

- **generate_baseline_report** (method) [U+1F534]
  - Line 78, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_baseline_report(self, output_path: str) -> bool:...`

- **MockRCSoakTest** (class) [U+1F7E1]
  - Line 20, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class MockRCSoakTest:...`

### scripts/windows_install_dryrun.py

- **_simulate_commands** (method) [U+1F534]
  - Line 141, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _simulate_commands(self, script_path: Path) -> Dict:...`

- **_execute_with_whatif** (method) [U+1F534]
  - Line 202, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _execute_with_whatif(self, script_path: Path) -> Dict:...`

- **_validate_preparation** (method) [U+1F534]
  - Line 291, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _validate_preparation(self) -> Dict:...`

- **_validate_installation** (method) [U+1F534]
  - Line 303, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _validate_installation(self) -> Dict:...`

- **_validate_service_registration** (method) [U+1F534]
  - Line 322, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _validate_service_registration(self) -> Dict:...`

- **_validate_service_start** (method) [U+1F534]
  - Line 334, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _validate_service_start(self) -> Dict:...`

- **_validate_service_stop** (method) [U+1F534]
  - Line 353, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _validate_service_stop(self) -> Dict:...`

- **_validate_service_removal** (method) [U+1F534]
  - Line 365, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _validate_service_removal(self) -> Dict:...`

- **_validate_cleanup** (method) [U+1F534]
  - Line 384, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _validate_cleanup(self) -> Dict:...`

- **_generate_script_analysis_section** (method) [U+1F534]
  - Line 581, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_script_analysis_section(self, script_analyses: List[Dict]) -> str:...`

### service/service_wrapper.py

- **_initialize_collectors** (method) [U+1F534]
  - Line 137, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _initialize_collectors(self) -> None:...`

- **_initialize_detection_engine** (method) [U+1F534]
  - Line 190, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _initialize_detection_engine(self) -> None:...`

- **_initialize_response_managers** (method) [U+1F534]
  - Line 205, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _initialize_response_managers(self) -> None:...`

- **_initialize_web_api** (method) [U+1F534]
  - Line 219, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _initialize_web_api(self) -> None:...`

- **_do_config_reload** (method) [U+1F534]
  - Line 331, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _do_config_reload(self) -> None:...`

- **_run_service** (method) [U+1F534]
  - Line 396, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `async def _run_service(self) -> None:...`

- **initialize** (method) [U+1F534]
  - Line 77, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def initialize(self) -> None:...`

- **start** (method) [U+1F534]
  - Line 238, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 248, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **run_forever** (method) [U+1F534]
  - Line 286, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def run_forever(self) -> None:...`

### temp_minimal_probes.py

- **subscribe** (method) [U+1F534]
  - Line 14, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def subscribe(self, event_type, handler):...`

- **publish** (method) [U+1F534]
  - Line 19, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def publish(self, event_type, data):...`

- **MockEventBus** (class) [U+1F7E1]
  - Line 9, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class MockEventBus:...`

### tests/e2e/test_sentinel_e2e.py

- **_handle_file_event** (method) [U+1F534]
  - Line 67, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _handle_file_event(self, event: FileEvent) -> None:...`

- **_handle_health_metric** (method) [U+1F534]
  - Line 71, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _handle_health_metric(self, event: HealthMetric) -> None:...`

- **_handle_alert** (method) [U+1F534]
  - Line 75, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _handle_alert(self, event: DetectionAlert) -> None:...`

- **start** (method) [U+1F534]
  - Line 38, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self) -> None:...`

- **stop** (method) [U+1F534]
  - Line 61, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self) -> None:...`

- **get_stats** (method) [U+1F534]
  - Line 79, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_stats(self) -> dict[str, int]:...`

- **E2ETestCollector** (class) [U+1F7E1]
  - Line 23, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class E2ETestCollector:...`

### tests/test_anomaly.py

- **TestAnomalyState** (class) [U+1F534]
  - Line 29, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAnomalyState(unittest.TestCase):...`

- **TestAnomalyDetector** (class) [U+1F534]
  - Line 92, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAnomalyDetector(unittest.TestCase):...`

- **TestAnomalyFunctions** (class) [U+1F534]
  - Line 270, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAnomalyFunctions(unittest.TestCase):...`

- **TestAnomalyConfiguration** (class) [U+1F534]
  - Line 308, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAnomalyConfiguration(unittest.TestCase):...`

### tests/test_api_contract_check.py

- **TestAPIEndpoint** (class) [U+1F534]
  - Line 20, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAPIEndpoint(unittest.TestCase):...`

- **TestAPIContractAnalyzer** (class) [U+1F534]
  - Line 44, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAPIContractAnalyzer(unittest.TestCase):...`

- **TestAPIContractDiff** (class) [U+1F534]
  - Line 323, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAPIContractDiff(unittest.TestCase):...`

### tests/test_attack_matrix_smoke.py

- **subscribe** (method) [U+1F534]
  - Line 41, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def subscribe(self, event_type: str, handler):...`

- **publish** (method) [U+1F534]
  - Line 46, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def publish(self, event_type: str, data: Dict[str, Any]):...`

- **get_published_count** (method) [U+1F534]
  - Line 57, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_published_count(self, event_type: str) -> int:...`

- **check_dependencies** (function) [U+1F7E1]
  - Line 14, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_dependencies():...`

- **MinimalEventBus** (class) [U+1F7E1]
  - Line 34, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class MinimalEventBus:...`

- **TestAttackMatrixSmoke** (class) [U+1F7E1]
  - Line 61, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class TestAttackMatrixSmoke(unittest.TestCase):...`

### tests/test_attack_sequences.py

- **_skip** (function) [U+1F534]
  - Line 4, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use)
  - Code: `def _skip(msg): return unittest.skip(msg)...`

- **_mk** (method) [U+1F534]
  - Line 36, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _mk(self, name, **kwargs):...`

- **TestAttackSequences** (class) [U+1F534]
  - Line 10, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAttackSequences(unittest.TestCase):...`

- **_catch** (method) [U+1F7E1]
  - Line 26, confidence: 0.60
  - Usages: 2
  - Reasons: Very few usages found, Private method/function (internal use), Method may be unused in class
  - Code: `def _catch(evt):...`

### tests/test_auth.py

- **TestAuthSystemImportSafe** (class) [U+1F534]
  - Line 14, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAuthSystemImportSafe(unittest.TestCase):...`

- **TestAuthConfiguration** (class) [U+1F534]
  - Line 49, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAuthConfiguration(unittest.TestCase):...`

- **TestUserDatabase** (class) [U+1F534]
  - Line 105, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestUserDatabase(unittest.TestCase):...`

- **TestSessionManager** (class) [U+1F534]
  - Line 193, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestSessionManager(unittest.TestCase):...`

- **TestConsoleAuth** (class) [U+1F534]
  - Line 278, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestConsoleAuth(unittest.TestCase):...`

### tests/test_backup_restore.py

- **TestBackupRestore** (class) [U+1F534]
  - Line 21, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestBackupRestore(unittest.TestCase):...`

### tests/test_bus_metrics.py

- **TestEventBusObservability** (class) [U+1F7E1]
  - Line 11, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class TestEventBusObservability(unittest.TestCase):...`

### tests/test_chaos_probes.py

- **TestChaosProbes** (class) [U+1F534]
  - Line 19, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestChaosProbes(unittest.TestCase):...`

- **inject_chaos** (method) [U+1F7E1]
  - Line 317, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def inject_chaos(component_id):...`

### tests/test_config_migrate.py

- **TestConfigMigrator** (class) [U+1F534]
  - Line 18, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestConfigMigrator(unittest.TestCase):...`

### tests/test_config_reload.py

- **TestConfigHotReload** (class) [U+1F7E1]
  - Line 9, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class TestConfigHotReload(unittest.TestCase):...`

### tests/test_config_schema.py

- **TestConfigSchema** (class) [U+1F534]
  - Line 17, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestConfigSchema(unittest.TestCase):...`

### tests/test_console_ui.py

- **TestConsoleUI** (class) [U+1F534]
  - Line 22, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestConsoleUI(unittest.TestCase):...`

### tests/test_health_endpoint.py

- **TestHealthEndpoint** (class) [U+1F534]
  - Line 20, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestHealthEndpoint(unittest.TestCase):...`

### tests/test_integration_smoke.py

- **TestIntegrationSmoke** (class) [U+1F534]
  - Line 20, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestIntegrationSmoke:...`

- **mock_consumer** (method) [U+1F7E1]
  - Line 127, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def mock_consumer(event):...`

### tests/test_log_rotation.py

- **TestLogRotationImportSafe** (class) [U+1F534]
  - Line 13, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestLogRotationImportSafe(unittest.TestCase):...`

- **TestSecretRedactionFilter** (class) [U+1F534]
  - Line 57, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestSecretRedactionFilter(unittest.TestCase):...`

- **TestRotatingLogConfig** (class) [U+1F534]
  - Line 174, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestRotatingLogConfig(unittest.TestCase):...`

- **TestApplicationLoggingSetup** (class) [U+1F534]
  - Line 270, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestApplicationLoggingSetup(unittest.TestCase):...`

### tests/test_offline_installer.py

- **TestOfflineInstaller** (class) [U+1F534]
  - Line 12, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestOfflineInstaller(unittest.TestCase):...`

- **TestOfflineInstallerIntegration** (class) [U+1F534]
  - Line 249, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestOfflineInstallerIntegration(unittest.TestCase):...`

### tests/test_operational_mode.py

- **TestOperationalModeStorage** (class) [U+1F534]
  - Line 43, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestOperationalModeStorage(unittest.TestCase):...`

- **TestOperationalModeAPI** (class) [U+1F534]
  - Line 162, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestOperationalModeAPI(unittest.TestCase):...`

- **TestOperationalModeEnforcement** (class) [U+1F534]
  - Line 259, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestOperationalModeEnforcement:...`

- **setup_method** (method) [U+1F534]
  - Line 262, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def setup_method(self):...`

### tests/test_p2_endpoints.py

- **TestP2EndpointsImportSafe** (class) [U+1F534]
  - Line 12, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestP2EndpointsImportSafe(unittest.TestCase):...`

- **TestAuthEndpoints** (class) [U+1F534]
  - Line 34, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAuthEndpoints(unittest.TestCase):...`

- **TestAuthEndpointsDisabled** (class) [U+1F534]
  - Line 191, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestAuthEndpointsDisabled(unittest.TestCase):...`

- **TestStreamingEndpoints** (class) [U+1F534]
  - Line 233, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestStreamingEndpoints(unittest.TestCase):...`

- **TestP2IntegrationWithExistingFeatures** (class) [U+1F534]
  - Line 295, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestP2IntegrationWithExistingFeatures(unittest.TestCase):...`

### tests/test_perf_probe.py

- **TestPerformanceProbe** (class) [U+1F534]
  - Line 21, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestPerformanceProbe(unittest.TestCase):...`

- **TestPerformanceProbeIntegration** (class) [U+1F534]
  - Line 326, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestPerformanceProbeIntegration(unittest.TestCase):...`

- **side_effect** (method) [U+1F7E1]
  - Line 151, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def side_effect(*args, **kwargs):...`

### tests/test_plugin_sandbox.py

- **TestSandboxContext** (class) [U+1F534]
  - Line 22, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestSandboxContext(unittest.TestCase):...`

- **TestPluginLoader** (class) [U+1F534]
  - Line 70, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestPluginLoader(unittest.TestCase):...`

- **TestPluginHooks** (class) [U+1F534]
  - Line 248, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestPluginHooks(unittest.TestCase):...`

- **TestSandboxedImports** (class) [U+1F534]
  - Line 274, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestSandboxedImports(unittest.TestCase):...`

### tests/test_preflight_checks.py

- **TestPreflightResult** (class) [U+1F534]
  - Line 21, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestPreflightResult(unittest.TestCase):...`

- **TestPreflightChecker** (class) [U+1F534]
  - Line 52, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestPreflightChecker(unittest.TestCase):...`

- **TestPreflightFunctions** (class) [U+1F534]
  - Line 365, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestPreflightFunctions(unittest.TestCase):...`

- **find_spec_side_effect** (method) [U+1F7E1]
  - Line 108, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def find_spec_side_effect(module):...`

- **find_spec_side_effect** (method) [U+1F7E1]
  - Line 131, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def find_spec_side_effect(module):...`

### tests/test_quarantine.py

- **TestQuarantineUtilities** (class) [U+1F534]
  - Line 31, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestQuarantineUtilities(unittest.TestCase):...`

- **TestQuarantineManager** (class) [U+1F534]
  - Line 149, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestQuarantineManager(unittest.TestCase):...`

- **TestQuarantineFunctions** (class) [U+1F534]
  - Line 401, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestQuarantineFunctions(unittest.TestCase):...`

- **TestQuarantineConfiguration** (class) [U+1F534]
  - Line 467, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestQuarantineConfiguration(unittest.TestCase):...`

### tests/test_rate_limit.py

- **TestRateLimit** (class) [U+1F7E1]
  - Line 9, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class TestRateLimit(unittest.TestCase):...`

### tests/test_rbac.py

- **TestRBAC** (class) [U+1F7E1]
  - Line 9, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class TestRBAC(unittest.TestCase):...`

### tests/test_retention.py

- **TestRetention** (class) [U+1F534]
  - Line 28, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestRetention(unittest.TestCase):...`

- **create_test_files** (method) [U+1F534]
  - Line 51, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def create_test_files(self, directory: Path, count: int = 5, age_days: int = 30)...`

- **TestRetentionIntegration** (class) [U+1F534]
  - Line 309, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestRetentionIntegration(unittest.TestCase):...`

### tests/test_secret_rotation.py

- **TestSecretRotation** (class) [U+1F534]
  - Line 17, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestSecretRotation(unittest.TestCase):...`

### tests/test_self_check.py

- **TestSelfCheck** (class) [U+1F534]
  - Line 19, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestSelfCheck(unittest.TestCase):...`

- **mock_post** (method) [U+1F7E1]
  - Line 212, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found, Method may be unused in class
  - Code: `def mock_post(url, headers=None):...`

### tests/test_streaming.py

- **TestStreamingImportSafe** (class) [U+1F534]
  - Line 12, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestStreamingImportSafe(unittest.TestCase):...`

- **TestStreamingConfiguration** (class) [U+1F534]
  - Line 50, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestStreamingConfiguration(unittest.TestCase):...`

- **TestSSEEndpoint** (class) [U+1F534]
  - Line 92, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestSSEEndpoint(unittest.TestCase):...`

- **TestStreamingWithAuth** (class) [U+1F534]
  - Line 194, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestStreamingWithAuth(unittest.TestCase):...`

- **TestStreamingHealthMetrics** (class) [U+1F534]
  - Line 240, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestStreamingHealthMetrics(unittest.TestCase):...`

### tests/test_structured_logging.py

- **TestStructuredLogging** (class) [U+1F7E1]
  - Line 9, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class TestStructuredLogging(unittest.TestCase):...`

### tests/test_telemetry_export.py

- **TestTelemetryCollector** (class) [U+1F534]
  - Line 20, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestTelemetryCollector(unittest.TestCase):...`

- **TestTelemetryExporter** (class) [U+1F534]
  - Line 147, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestTelemetryExporter(unittest.TestCase):...`

- **TestExportFunctions** (class) [U+1F534]
  - Line 244, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestExportFunctions(unittest.TestCase):...`

### tests/test_versioning.py

- **TestVersioning** (class) [U+1F534]
  - Line 9, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestVersioning(unittest.TestCase):...`

### tests/test_windows_service.py

- **TestWindowsServiceImportSafe** (class) [U+1F534]
  - Line 12, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestWindowsServiceImportSafe(unittest.TestCase):...`

- **TestServiceScriptValidation** (class) [U+1F534]
  - Line 54, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestServiceScriptValidation(unittest.TestCase):...`

- **TestServiceRunnerDryRun** (class) [U+1F534]
  - Line 123, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestServiceRunnerDryRun(unittest.TestCase):...`

- **TestServiceInstallerDryRun** (class) [U+1F534]
  - Line 189, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestServiceInstallerDryRun(unittest.TestCase):...`

- **TestServiceUninstallerDryRun** (class) [U+1F534]
  - Line 243, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase
  - Code: `class TestServiceUninstallerDryRun(unittest.TestCase):...`

### tests/unit/test_alert_manager.py

- **temp_log_file** (function) [U+1F7E1]
  - Line 32, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def temp_log_file():...`

- **create_test_alert** (function) [U+1F7E1]
  - Line 58, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def create_test_alert(severity=AlertSeverity.MEDIUM, category=AlertCategory.GENE...`

### tests/unit/test_event_bus.py

- **handler_1** (function) [U+1F7E1]
  - Line 71, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def handler_1(event):...`

- **handler_2** (function) [U+1F7E1]
  - Line 74, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def handler_2(event):...`

- **file_handler** (function) [U+1F7E1]
  - Line 107, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def file_handler(event):...`

- **process_handler** (function) [U+1F7E1]
  - Line 110, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def process_handler(event):...`

- **path_filter** (function) [U+1F7E1]
  - Line 145, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def path_filter(event):...`

- **async_handler** (function) [U+1F7E1]
  - Line 176, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `async def async_handler(event):...`

- **good_handler** (function) [U+1F7E1]
  - Line 198, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def good_handler(event):...`

- **bad_handler** (function) [U+1F7E1]
  - Line 201, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def bad_handler(event):...`

### tests/unit/test_fs_monitor.py

- **_handle_event** (method) [U+1F534]
  - Line 78, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _handle_event(self, event):...`

- **start** (method) [U+1F534]
  - Line 67, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def start(self):...`

- **stop** (method) [U+1F534]
  - Line 74, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def stop(self):...`

- **get_events_by_type** (method) [U+1F534]
  - Line 81, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_events_by_type(self, event_type):...`

- **EventCollector** (class) [U+1F7E1]
  - Line 59, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class EventCollector:...`

### tests/unit/test_rules_engine.py

- **alert_handler** (function) [U+1F7E1]
  - Line 63, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def alert_handler(alert):...`

- **alert_handler** (function) [U+1F7E1]
  - Line 95, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def alert_handler(alert):...`

- **alert_handler** (function) [U+1F7E1]
  - Line 137, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def alert_handler(alert):...`

- **alert_handler** (function) [U+1F7E1]
  - Line 176, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def alert_handler(alert):...`

- **alert_handler** (function) [U+1F7E1]
  - Line 222, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def alert_handler(alert):...`

- **alert_handler** (function) [U+1F7E1]
  - Line 265, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def alert_handler(alert):...`

- **alert_handler** (function) [U+1F7E1]
  - Line 309, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def alert_handler(alert):...`

### tools/api_contract_check.py

- **_check_auth_required** (method) [U+1F534]
  - Line 139, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _check_auth_required(self, view_func: Any, path: str) -> bool:...`

- **_extract_feature_flag** (method) [U+1F534]
  - Line 169, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_feature_flag(self, view_func: Any, path: str) -> Optional[str]:...`

- **_analyze_response_fields** (method) [U+1F534]
  - Line 195, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_response_fields(self, view_func: Any) -> List[str]:...`

- **_dict_to_endpoint** (method) [U+1F534]
  - Line 356, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _dict_to_endpoint(self, ep_data: Dict[str, Any]) -> APIEndpoint:...`

- **_endpoints_differ** (method) [U+1F534]
  - Line 375, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _endpoints_differ(self, ep1: APIEndpoint, ep2: APIEndpoint) -> bool:...`

- **_analyze_endpoint_changes** (method) [U+1F534]
  - Line 391, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_endpoint_changes(self, old_ep: APIEndpoint, new_ep: APIEndpoint) ->...`

- **extract_fastapi_routes** (method) [U+1F534]
  - Line 58, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def extract_fastapi_routes(self) -> Dict[str, APIEndpoint]:...`

- **generate_contract** (method) [U+1F534]
  - Line 222, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_contract(self) -> Dict[str, Any]:...`

- **load_baseline_contract** (method) [U+1F534]
  - Line 254, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def load_baseline_contract(self, baseline_file: str) -> Dict[str, Any]:...`

- **save_contract** (method) [U+1F534]
  - Line 276, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def save_contract(self, contract: Dict[str, Any], output_file: str) -> bool:...`

### tools/composite_health_check.py

- **load_rc1_baseline** (function) [U+1F7E1]
  - Line 17, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def load_rc1_baseline() -> Dict[str, Any]:...`

- **check_file_integrity** (function) [U+1F7E1]
  - Line 51, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_file_integrity(baseline_hashes: Dict[str, str]) -> Dict[str, Any]:...`

- **check_flag_consistency** (function) [U+1F7E1]
  - Line 81, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_flag_consistency(baseline_flags: Dict[str, str]) -> Dict[str, Any]:...`

- **run_proof_consistency_check** (function) [U+1F7E1]
  - Line 97, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def run_proof_consistency_check(baseline_proofs: List[Dict[str, Any]]) -> Dict[s...`

### tools/config_migrate.py

- **_build_migration_rules** (method) [U+1F534]
  - Line 28, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _build_migration_rules(self) -> Dict[str, str]:...`

- **_update_config_file** (method) [U+1F534]
  - Line 254, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _update_config_file(self, migrations: List[Tuple[str, str, str]]):...`

- **scan_environment** (method) [U+1F534]
  - Line 54, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def scan_environment(self) -> Dict[str, str]:...`

- **scan_config_file** (method) [U+1F534]
  - Line 73, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def scan_config_file(self) -> Dict[str, str]:...`

- **detect_migrations_needed** (method) [U+1F534]
  - Line 105, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def detect_migrations_needed(self) -> List[Tuple[str, str, str]]:...`

- **apply_migrations** (method) [U+1F534]
  - Line 173, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def apply_migrations(self, dry_run: bool = False) -> Dict[str, any]:...`

- **list_current_config** (method) [U+1F534]
  - Line 280, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def list_current_config(self) -> Dict[str, any]:...`

- **create_backup** (method) [U+1F7E1]
  - Line 133, confidence: 0.70
  - Usages: 1
  - Reasons: Only one usage found, Method may be unused in class
  - Code: `def create_backup(self, source_type: str = "environment") -> Optional[str]:...`

### tools/dead_code_scan.py

- **_should_skip_file** (method) [U+1F534]
  - Line 77, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _should_skip_file(self, path: Path) -> bool:...`

- **_analyze_file_pass1** (method) [U+1F534]
  - Line 92, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_file_pass1(self, file_path: Path):...`

- **_analyze_file_pass2** (method) [U+1F534]
  - Line 121, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_file_pass2(self, file_path: Path):...`

- **_generate_report** (method) [U+1F534]
  - Line 148, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_report(self) -> Dict[str, Any]:...`

- **_get_most_problematic_files** (method) [U+1F534]
  - Line 204, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_most_problematic_files(self, by_file: Dict[str, List[DeadCodeItem]]) ->...`

- **_generate_cleanup_recommendations** (method) [U+1F534]
  - Line 221, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_cleanup_recommendations(self, by_confidence: Dict[str, List[DeadCo...`

- **_analyze_function** (method) [U+1F534]
  - Line 365, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_function(self, node):...`

- **_count_usages** (method) [U+1F534]
  - Line 399, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _count_usages(self, symbol_name: str) -> int:...`

- **_calculate_confidence** (method) [U+1F534]
  - Line 413, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _calculate_confidence(self, symbol_name: str, symbol_type: str, usage_count:...`

- **_get_dead_code_reasons** (method) [U+1F534]
  - Line 440, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_dead_code_reasons(self, symbol_name: str, symbol_type: str, usage_count...`

### tools/docstring_enricher.py

- **_should_skip_file** (method) [U+1F534]
  - Line 63, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _should_skip_file(self, path: Path) -> bool:...`

- **_process_file** (method) [U+1F534]
  - Line 80, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _process_file(self, file_path: Path):...`

- **_enhance_docstring** (method) [U+1F534]
  - Line 104, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _enhance_docstring(self, candidate: Dict[str, Any]) -> Optional[DocstringEnh...`

- **_generate_enhanced_docstring** (method) [U+1F534]
  - Line 133, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_enhanced_docstring(self, original: str, func_name: str,...`

- **_infer_common_exceptions** (method) [U+1F534]
  - Line 200, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _infer_common_exceptions(self, func_name: str, args: List[str]) -> List[str]...`

- **_determine_enhancement_type** (method) [U+1F534]
  - Line 244, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _determine_enhancement_type(self, original: str, enhanced: str) -> str:...`

- **_generate_report** (method) [U+1F534]
  - Line 253, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_report(self) -> Dict[str, Any]:...`

- **_process_function** (method) [U+1F534]
  - Line 338, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _process_function(self, node):...`

- **_extract_docstring** (method) [U+1F534]
  - Line 367, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_docstring(self, node) -> Optional[str]:...`

- **_get_return_annotation** (method) [U+1F534]
  - Line 375, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_return_annotation(self, node) -> Optional[str]:...`

### tools/feature_flags_analyzer.py

- **_should_skip_file** (method) [U+1F534]
  - Line 88, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _should_skip_file(self, path: Path) -> bool:...`

- **_analyze_file** (method) [U+1F534]
  - Line 103, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_file(self, file_path: Path):...`

- **_analyze_security_impact** (method) [U+1F534]
  - Line 148, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_security_impact(self):...`

- **_analyze_route_dependencies** (method) [U+1F534]
  - Line 186, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_route_dependencies(self):...`

- **_find_test_coverage** (method) [U+1F534]
  - Line 197, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _find_test_coverage(self):...`

- **_categorize_flags** (method) [U+1F534]
  - Line 204, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _categorize_flags(self):...`

- **_generate_matrix** (method) [U+1F534]
  - Line 237, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_matrix(self) -> Dict[str, Any]:...`

- **_get_most_used_flags** (method) [U+1F534]
  - Line 289, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_most_used_flags(self) -> List[Dict[str, Any]]:...`

- **_record_flag_usage** (method) [U+1F534]
  - Line 392, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _record_flag_usage(self, flag_name: str, line_num: int, usage_type: str, def...`

- **analyze_flags** (method) [U+1F534]
  - Line 61, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def analyze_flags(self) -> Dict[str, Any]:...`

### tools/migrate_prior_state.py

- **copy_if** (function) [U+1F7E1]
  - Line 9, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def copy_if(src: Path, dst: Path)->None:...`

### tools/perf_baseline.py

- **register_handler** (method) [U+1F534]
  - Line 31, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def register_handler(self, event_type: str, handler):...`

- **emit_async** (method) [U+1F534]
  - Line 37, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `async def emit_async(self, event_type: str, data: Any = None):...`

- **emit_sync** (method) [U+1F534]
  - Line 50, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def emit_sync(self, event_type: str, data: Any = None):...`

- **InlineEventBus** (class) [U+1F7E1]
  - Line 24, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class InlineEventBus:...`

- **measure_async_performance** (function) [U+1F7E1]
  - Line 79, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `async def measure_async_performance(event_bus, n_events: int = 1000) -> Dict[str...`

- **noop_handler** (function) [U+1F7E1]
  - Line 82, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `async def noop_handler(data):...`

- **measure_sync_performance** (function) [U+1F7E1]
  - Line 118, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def measure_sync_performance(event_bus, n_events: int = 1000) -> Dict[str, Any]:...`

- **noop_handler** (function) [U+1F7E1]
  - Line 121, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def noop_handler(data):...`

- **run_performance_baseline** (function) [U+1F7E1]
  - Line 156, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `async def run_performance_baseline(n_events: int = 1000) -> Dict[str, Any]:...`

### tools/repair_and_validate.py

- **ensure** (function) [U+1F7E1]
  - Line 74, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def ensure(p: Path, content: str, bdir: Path, needle: str|None)->str:...`

### tools/rotate_secrets.py

- **rotate_console_auth_session_key** (method) [U+1F534]
  - Line 29, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def rotate_console_auth_session_key(self) -> Dict[str, Any]:...`

- **rotate_admin_token** (method) [U+1F534]
  - Line 84, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def rotate_admin_token(self) -> Dict[str, Any]:...`

- **generate_salt** (method) [U+1F534]
  - Line 133, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_salt(self, name: str, length: int = 16) -> Dict[str, Any]:...`

- **preview_rotation_plan** (method) [U+1F534]
  - Line 191, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def preview_rotation_plan(self) -> Dict[str, Any]:...`

- **execute_rotation** (method) [U+1F534]
  - Line 241, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def execute_rotation(self, secret_types: Optional[List[str]] = None) -> Dict[str...`

- **get_rotation_history** (method) [U+1F534]
  - Line 292, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def get_rotation_history(self) -> Dict[str, Any]:...`

### tools/routing_atlas_generator.py

- **_should_skip_file** (method) [U+1F534]
  - Line 107, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _should_skip_file(self, path: Path) -> bool:...`

- **_analyze_file** (method) [U+1F534]
  - Line 122, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_file(self, file_path: Path):...`

- **_analyze_route_dependencies** (method) [U+1F534]
  - Line 143, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_route_dependencies(self):...`

- **_analyze_gating_flags** (method) [U+1F534]
  - Line 173, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_gating_flags(self):...`

- **_generate_atlas** (method) [U+1F534]
  - Line 188, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_atlas(self) -> Dict[str, Any]:...`

- **_get_route_prefix** (method) [U+1F534]
  - Line 243, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_route_prefix(self, path: str) -> str:...`

- **_get_most_complex_routes** (method) [U+1F534]
  - Line 253, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_most_complex_routes(self) -> List[Dict[str, Any]]:...`

- **_analyze_dependency_graph** (method) [U+1F534]
  - Line 272, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_dependency_graph(self) -> Dict[str, Any]:...`

- **_generate_security_matrix** (method) [U+1F534]
  - Line 291, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_security_matrix(self) -> Dict[str, Any]:...`

- **_extract_route_info** (method) [U+1F534]
  - Line 352, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_route_info(self, node) -> Optional[RouteInfo]:...`

### tools/sec_lint.py

- **_load_security_rules** (method) [U+1F534]
  - Line 26, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _load_security_rules(self) -> List[Dict[str, Any]]:...`

- **_is_false_positive** (method) [U+1F534]
  - Line 307, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _is_false_positive(self, rule_id: str, line: str, file_path: str) -> bool:...`

- **_generate_json_report** (method) [U+1F534]
  - Line 400, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_json_report(self, findings: List[Dict[str, Any]]) -> str:...`

- **_generate_text_report** (method) [U+1F534]
  - Line 432, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_text_report(self, findings: List[Dict[str, Any]]) -> str:...`

- **_generate_sarif_report** (method) [U+1F534]
  - Line 473, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_sarif_report(self, findings: List[Dict[str, Any]]) -> str:...`

- **scan_file** (method) [U+1F534]
  - Line 242, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:...`

- **scan_directory** (method) [U+1F534]
  - Line 343, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def scan_directory(self, directory: Path, recursive: bool = True) -> List[Dict[s...`

- **generate_report** (method) [U+1F534]
  - Line 381, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def generate_report(self, findings: List[Dict[str, Any]], format: str = "json") ...`

- **check_current_tree** (method) [U+1F534]
  - Line 527, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_current_tree(self) -> Tuple[List[Dict[str, Any]], int]:...`

- **SecurityLinter** (class) [U+1F7E1]
  - Line 18, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `class SecurityLinter:...`

### tools/self_check.py

- **log** (method) [U+1F534]
  - Line 33, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def log(self, message: str, level: str = "INFO"):...`

- **check_python_environment** (method) [U+1F534]
  - Line 44, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_python_environment(self) -> Dict[str, Any]:...`

- **check_file_system** (method) [U+1F534]
  - Line 99, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_file_system(self) -> Dict[str, Any]:...`

- **check_web_api_import** (method) [U+1F534]
  - Line 161, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_web_api_import(self) -> Dict[str, Any]:...`

- **check_health_endpoint** (method) [U+1F534]
  - Line 214, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_health_endpoint(self) -> Dict[str, Any]:...`

- **check_admin_authentication** (method) [U+1F534]
  - Line 270, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_admin_authentication(self) -> Dict[str, Any]:...`

- **check_configuration_validation** (method) [U+1F534]
  - Line 332, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def check_configuration_validation(self) -> Dict[str, Any]:...`

- **run_all_checks** (method) [U+1F534]
  - Line 381, confidence: 0.90
  - Usages: 0
  - Reasons: No usages found in codebase, Method may be unused in class
  - Code: `def run_all_checks(self) -> Tuple[bool, Dict[str, Any]]:...`

### tools/symbol_atlas_generator.py

- **_should_skip_file** (method) [U+1F534]
  - Line 110, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _should_skip_file(self, path: Path) -> bool:...`

- **_analyze_file** (method) [U+1F534]
  - Line 125, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _analyze_file(self, file_path: Path) -> FileAnalysis:...`

- **_build_call_graph** (method) [U+1F534]
  - Line 183, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _build_call_graph(self):...`

- **_generate_atlas** (method) [U+1F534]
  - Line 193, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _generate_atlas(self) -> Dict[str, Any]:...`

- **_get_most_called_functions** (method) [U+1F534]
  - Line 237, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_most_called_functions(self) -> List[Dict[str, Any]]:...`

- **_get_most_complex_functions** (method) [U+1F534]
  - Line 251, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_most_complex_functions(self) -> List[Dict[str, Any]]:...`

- **_process_function** (method) [U+1F534]
  - Line 313, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _process_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], ...`

- **_extract_docstring** (method) [U+1F534]
  - Line 382, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _extract_docstring(self, node) -> Optional[str]:...`

- **_assess_docstring_quality** (method) [U+1F534]
  - Line 390, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _assess_docstring_quality(self, docstring: Optional[str]) -> str:...`

- **_get_decorator_name** (method) [U+1F534]
  - Line 409, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _get_decorator_name(self, decorator) -> str:...`

### tools/verify_minimax_claims.py

- **find_spec_ok** (function) [U+1F7E1]
  - Line 32, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def find_spec_ok(mod: str) -> bool:...`

- **load_json** (function) [U+1F7E1]
  - Line 35, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def load_json(path: str) -> dict:...`

- **check_artifacts** (function) [U+1F7E1]
  - Line 39, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_artifacts() -> List[str]:...`

- **check_manifest_hashes** (function) [U+1F7E1]
  - Line 42, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_manifest_hashes(manifest: dict) -> List[str]:...`

- **run_py_compile** (function) [U+1F7E1]
  - Line 54, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def run_py_compile(files: List[str]) -> List[str]:...`

- **check_no_new_runtime_deps** (function) [U+1F7E1]
  - Line 68, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_no_new_runtime_deps(changed: List[str]) -> List[str]:...`

- **check_public_invariants** (function) [U+1F7E1]
  - Line 100, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_public_invariants() -> List[str]:...`

- **check_routes_on_off** (function) [U+1F7E1]
  - Line 129, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_routes_on_off() -> List[str]:...`

- **check_anomaly_routes** (function) [U+1F7E1]
  - Line 176, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_anomaly_routes() -> List[str]:...`

- **check_quarantine_routes** (function) [U+1F7E1]
  - Line 248, confidence: 0.50
  - Usages: 2
  - Reasons: Very few usages found
  - Code: `def check_quarantine_routes() -> List[str]:...`

### ui/tray_app.py

- **_create_alert_menu_items** (method) [U+1F534]
  - Line 180, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _create_alert_menu_items(self) -> list[pystray.MenuItem]:...`

- **_pause_monitoring** (method) [U+1F534]
  - Line 225, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _pause_monitoring(self, duration_seconds: int) -> None:...`

- **_resume_monitoring** (method) [U+1F534]
  - Line 247, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _resume_monitoring(self) -> None:...`

- **_open_console** (method) [U+1F534]
  - Line 265, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _open_console(self) -> None:...`

- **_open_policies** (method) [U+1F534]
  - Line 275, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _open_policies(self) -> None:...`

- **_open_logs** (method) [U+1F534]
  - Line 285, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _open_logs(self) -> None:...`

- **_test_notification** (method) [U+1F534]
  - Line 303, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _test_notification(self) -> None:...`

- **_open_settings** (method) [U+1F534]
  - Line 326, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _open_settings(self) -> None:...`

- **_show_about** (method) [U+1F534]
  - Line 331, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _show_about(self) -> None:...`

- **_show_alert_details** (method) [U+1F534]
  - Line 336, confidence: 1.00
  - Usages: 0
  - Reasons: No usages found in codebase, Private method/function (internal use), Method may be unused in class
  - Code: `def _show_alert_details(self, alert_id: str) -> None:...`


## Analysis Notes

### Confidence Levels
- **High ([U+1F534])**: Very likely dead code, safe to remove after testing
- **Medium ([U+1F7E1])**: Potentially dead code, requires manual review
- **Low ([U+1F7E2])**: Uncertain, may have dynamic usage or be framework code

### Limitations
This analysis uses static analysis and may miss:
- Dynamic imports and attribute access
- Reflection-based usage
- Framework callbacks and hooks
- Plugin system integrations
- External library dependencies

### Recommendations
1. **Start with high-confidence items** for initial cleanup
2. **Test thoroughly** before removing any code
3. **Review git history** to understand code purpose
4. **Consider deprecation** before removal for public APIs
