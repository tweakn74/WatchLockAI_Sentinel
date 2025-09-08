# Platform Guards and Cross-Platform Compatibility

## Platform Detection Strategy

WatchLockAI Sentinel uses `sys.platform.startswith('win')` as the primary platform detection mechanism throughout the codebase.

### Standard Guard Pattern
```python
import sys
IS_WINDOWS = sys.platform.startswith('win')

if IS_WINDOWS:
    # Windows-specific imports and logic
    import winreg
else:
    # Non-Windows fallback
    logger.info("Windows-only feature not available on this platform")
```

## Windows-Only Surfaces

### Registry Monitoring (`collectors/reg_monitor.py`)
- **Guard Status**: ✅ Fully Guarded
- **Windows Dependencies**: `winreg` module
- **Linux Behavior**: Module loads but all operations become no-ops
- **Guard Implementation**:
  ```python
  IS_WINDOWS = sys.platform.startswith('win')
  
  if IS_WINDOWS:
      try:
          import winreg
          _windows_available = True
      except ImportError:
          _windows_available = False
          winreg = None
  else:
      _windows_available = False
      winreg = None
  
  WINDOWS_AVAILABLE = _windows_available and IS_WINDOWS
  ```
- **Fallback Behavior**: Registry events never generated on Linux

### Windows Service Integration (`service/service_wrapper.py`)
- **Guard Status**: ✅ Fully Guarded  
- **Windows Dependencies**: `servicemanager`, `win32event`, `win32service`, `win32serviceutil`
- **Linux Behavior**: Service functions return error messages and `False`
- **Guard Implementation**:
  ```python
  IS_WINDOWS = sys.platform.startswith('win')
  
  if IS_WINDOWS:
      try:
          import servicemanager
          import win32event
          import win32service
          import win32serviceutil
          WINDOWS_SERVICE_AVAILABLE = True
      except ImportError:
          WINDOWS_SERVICE_AVAILABLE = False
  else:
      WINDOWS_SERVICE_AVAILABLE = False
  ```
- **Service Functions**: `install_service()`, `uninstall_service()`, `start_service()`, `stop_service()`
- **Fallback Behavior**: All service functions print error message and return `False`

### Process Termination (`response/actions.py`)
- **Guard Status**: ⚠️ Partially Guarded
- **Platform Differences**: Different timeouts and error handling for Windows vs Unix
- **Guard Implementation**:
  ```python
  IS_WINDOWS = sys.platform.startswith('win')
  
  # Platform-aware timeout logic
  timeout = 10 if IS_WINDOWS else 5  # Windows may need more time
  proc.wait(timeout=timeout)
  ```
- **Behavior**: Adapts timeouts and error messages based on platform

## Cross-Platform Monitoring Components

### File System Monitoring (`collectors/fs_monitor.py`)
- **Guard Status**: ✅ Cross-Platform
- **Dependencies**: `watchdog` library (cross-platform)
- **Platform Handling**: Uses `watchdog.observers.Observer` which handles platform differences internally
- **Path Handling**: Supports both Windows (`C:\Path\`) and Unix (`/path/`) path formats

### Process Monitoring (`collectors/proc_monitor.py`)
- **Guard Status**: ✅ Cross-Platform
- **Dependencies**: `psutil` library (cross-platform)
- **Platform Handling**: `psutil` abstracts platform differences for process enumeration and info

### Network Monitoring (`collectors/net_monitor.py`)
- **Guard Status**: ✅ Cross-Platform
- **Dependencies**: `psutil` library (cross-platform)
- **Platform Handling**: `psutil.net_connections()` works across platforms with consistent interface

### Health Monitoring (`collectors/health_monitor.py`)
- **Guard Status**: ✅ Cross-Platform
- **Dependencies**: `psutil` library (cross-platform)
- **Platform Handling**: CPU, memory, disk metrics work consistently across platforms

## Web Console and APIs (`console/`)
- **Guard Status**: ✅ Cross-Platform
- **Dependencies**: `FastAPI`, `uvicorn` (cross-platform)
- **Platform Handling**: All REST API endpoints work identically on Windows and Linux

## Linux CI Behavior

### Test Coverage on Linux
- **Unit Tests**: All unit tests pass on Linux (collectors return no-op results for Windows-only components)
- **Integration Tests**: Basic service startup/shutdown tests work with web API
- **E2E Tests**: Limited functionality on Linux (no registry monitoring, no Windows service)

### Expected Linux Behavior
1. **Application Startup**: ✅ Fully functional
2. **Web Console**: ✅ Fully functional at `http://localhost:8080`
3. **File/Process/Network Monitoring**: ✅ Fully functional
4. **Health Monitoring**: ✅ Fully functional
5. **Registry Monitoring**: ❌ No events generated (expected)
6. **Windows Service**: ❌ Installation/management functions fail (expected)
7. **Detection/Response**: ⚠️ Limited (depends on available events)

### Linux Startup Warnings (Expected)
```
INFO  Registry monitoring not available on non-Windows platforms
INFO  Windows service APIs not available on non-Windows platforms  
WARN  Windows service APIs not available (pywin32 not installed)
```

## Platform-Specific Configuration

### Windows Service Configuration (`config.yaml`)
```yaml
service:
  install_on_setup: true  # Only affects Windows
```

### Registry Monitoring Configuration (`config.yaml`) 
```yaml
monitoring:
  registry:
    enabled: true  # Safe on Linux (becomes no-op)
    watch_keys:
      - "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
      # Windows-specific registry keys
```

### Platform Environment Variables
- `SENTINEL_MONITORING__REGISTRY__ENABLED=false` - Explicitly disable registry monitoring
- `SENTINEL_SERVICE__INSTALL_ON_SETUP=false` - Skip service installation attempts

## Guard Enhancement Opportunities

### Potential Improvements
1. **Registry Module**: Could add more explicit Linux warning messages
2. **Service Functions**: Could provide more detailed error messages about missing dependencies
3. **Configuration Validation**: Could warn about Windows-specific config on Linux
4. **Documentation**: Could auto-generate platform compatibility matrices

### Missing Guards
- No identified critical missing guards
- Current implementation provides appropriate fallbacks for all Windows-specific functionality

## Testing Strategy

### Windows Testing
- Full functionality testing including Windows service and registry monitoring
- pywin32 dependency validation
- Service install/uninstall/start/stop operations

### Linux Testing  
- Core functionality testing (file/process/network monitoring)
- Web console and API testing
- Graceful degradation testing for Windows-only features
- No Windows-specific error conditions

### Cross-Platform Testing
- Configuration parsing and validation
- Event bus and detection engine functionality
- Response actions (with platform-appropriate timeouts)
- Web API consistency across platforms

## Deployment Considerations

### Windows Deployment
- Requires `pywin32` package for service functionality
- Registry monitoring requires appropriate Windows permissions
- Service installation requires administrator privileges

### Linux Deployment  
- Core functionality works without Windows-specific dependencies
- Monitoring limited to file/process/network (no registry)
- Runs as regular application (no service management)
- Docker-friendly (no Windows service dependencies)

### Hybrid Environments
- Configuration files are portable between platforms
- Event schemas are identical across platforms
- Web API provides consistent interface for management tools
