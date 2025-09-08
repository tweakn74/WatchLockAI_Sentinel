# System Assumptions and Invariants

This document captures explicit assumptions discovered during the workspace analysis. These assumptions are critical for understanding system behavior and maintaining consistency during development.

## Configuration Assumptions

### File System Assumptions
- **Config Directory Exists**: The `config/` directory is assumed to be writable for operational mode persistence
- **YAML Parsing**: `config.yaml` is assumed to be valid YAML with proper structure matching Pydantic models
- **Path Resolution**: File paths in configuration support both Windows (`C:\`) and Unix (`/`) formats
- **Environment Variables**: SENTINEL_* environment variables follow double-underscore `__` convention for nested keys

### Operational Mode Assumptions
- **Atomic Persistence**: Operational mode changes are atomic via temporary file + rename pattern
- **Thread Safety**: Multiple threads may read operational mode concurrently, but writes are serialized
- **Cache Consistency**: In-memory operational mode cache is invalidated on writes
- **Default Fallback**: System defaults to "observe" mode if configuration is invalid or missing

## Event System Assumptions

### Event Bus Invariants
- **Single Event Bus**: Only one EventBus instance exists per application lifecycle
- **Weak References**: Event subscribers are held as weak references to prevent memory leaks
- **Async Delivery**: All event delivery is asynchronous and non-blocking to publishers
- **Event Ordering**: Events are processed in FIFO order but delivery to subscribers may be concurrent
- **Error Isolation**: Subscriber errors do not affect other subscribers or the publisher

### Event Schema Invariants
- **Immutable Events**: Events are immutable after creation (Pydantic model validation)
- **Timestamp Consistency**: All events use UTC timezone with ISO-8601 format
- **Host Identity**: Events always include host_id from `socket.gethostname()`
- **Schema Version**: All events include sentinel_version for compatibility tracking

### Event Lifecycle Assumptions
- **Event History**: Event bus maintains circular buffer of recent events (default: 1000)
- **Subscription Cleanup**: Inactive subscribers are automatically cleaned up via weak references
- **Event Delivery**: Best-effort delivery, no guarantees for failed subscribers

## Platform Compatibility Assumptions

### Windows-Specific Assumptions
- **Registry Access**: Registry monitoring assumes appropriate Windows permissions
- **Service Installation**: Windows service installation requires administrator privileges  
- **pywin32 Availability**: Windows service functionality requires pywin32 package
- **Path Separators**: Windows paths use backslash separators in configuration

### Cross-Platform Assumptions
- **psutil Compatibility**: Process and network monitoring assumes psutil works consistently across platforms
- **File System Events**: watchdog library abstracts platform differences for file monitoring
- **Path Handling**: pathlib.Path handles platform-specific path operations
- **Socket API**: Network monitoring assumes consistent socket API across platforms

### Linux Behavior Assumptions
- **Graceful Degradation**: Windows-only features become no-ops without errors
- **Container Support**: System works in containerized environments without Windows-specific dependencies
- **Permission Model**: Unix permissions sufficient for file and process monitoring

## Security Model Assumptions

### Threat Detection Assumptions
- **Rules Engine**: Detection rules are loaded from files and cached in memory
- **Behavioral Baseline**: Behavioral detection assumes ability to establish baseline system behavior
- **Threat Intelligence**: TI database is pre-populated with known indicators and techniques
- **Event Correlation**: Multiple events may be correlated to identify attack patterns

### Response Action Assumptions
- **Authorization Model**: Destructive actions require explicit authorization via configuration
- **Process Termination**: System has sufficient privileges to terminate malicious processes
- **Quarantine Operations**: File quarantine assumes writable quarantine directory
- **User Consent**: Some actions may require user consent via UI confirmation

## Data Persistence Assumptions

### File System Assumptions
- **Log Directory**: `logs/` directory is writable for JSONL event and alert logging
- **Index Directory**: RAG knowledge index directory is writable for search index files
- **Atomic Operations**: File writes use atomic operations (temp file + rename) for consistency
- **File Locking**: Operating system provides appropriate file locking for concurrent access

### Data Format Assumptions
- **JSON Serialization**: All persistent data can be serialized to/from JSON
- **JSONL Streaming**: Log files use JSONL format for streaming and line-by-line processing
- **Configuration Schema**: Configuration follows stable schema with backward compatibility

## Network and API Assumptions

### Web API Assumptions
- **Local Binding**: Web API binds to localhost (127.0.0.1) for security by default
- **Single Instance**: Only one web API server instance runs per application
- **Request/Response**: All API operations are request/response (no WebSocket or SSE)
- **JSON Content**: API requests and responses use JSON content-type

### Network Monitoring Assumptions
- **Socket Access**: System has permissions to enumerate network connections
- **Process Association**: Network connections can be associated with process IDs
- **Connection States**: TCP/UDP connection states are consistently reported by OS

## Resource Management Assumptions

### Memory Management Assumptions
- **Bounded Buffers**: Event history and other buffers have configurable size limits
- **Weak References**: Automatic cleanup of unused subscribers prevents memory leaks
- **Python GC**: Python garbage collection handles event object lifecycle appropriately

### Performance Assumptions
- **Polling Intervals**: System can sustain configured polling intervals without performance degradation
- **Event Volume**: Event bus can handle expected volume of events without backpressure
- **Search Performance**: RAG knowledge search completes within reasonable time bounds
- **Concurrent Operations**: Multiple monitoring collectors can run concurrently without interference

## Startup and Shutdown Assumptions

### Initialization Order Assumptions
- **Configuration First**: Configuration must be loaded before other components
- **Event Bus Early**: Event bus must start before any event publishers or subscribers
- **Collectors After Bus**: Monitoring collectors start after event bus is ready
- **Web API Last**: Web API starts after all internal components are initialized

### Graceful Shutdown Assumptions
- **Signal Handling**: System handles SIGINT/SIGTERM signals for graceful shutdown
- **Component Cleanup**: All components support async shutdown with resource cleanup
- **Event Draining**: Event bus allows in-flight events to complete before shutdown
- **File Closure**: All log files and databases are properly closed on shutdown

## Development and Testing Assumptions

### Code Quality Assumptions
- **Type Safety**: All modules use Python type annotations for static analysis
- **Linting Compliance**: Code passes ruff linting without errors
- **Import Safety**: No circular imports or missing import guards
- **Error Handling**: All external operations include appropriate error handling

### Testing Assumptions
- **Mock Availability**: External dependencies can be mocked for unit testing
- **Test Isolation**: Tests do not interfere with each other or system state
- **Platform Coverage**: Tests run consistently on both Windows and Linux
- **Integration Testing**: E2E tests can exercise full system without external dependencies

## Deployment Assumptions

### Environment Assumptions
- **Python Version**: System requires Python 3.8+ with asyncio support
- **Dependency Availability**: All required packages are installable via pip/conda
- **File Permissions**: Application has read/write access to working directory
- **Port Availability**: Web API can bind to configured port (default: 8080)

### Security Assumptions
- **Local Access**: Web console accessed only from localhost for security
- **Configuration Security**: Configuration files stored with appropriate permissions
- **Log Security**: Event logs do not contain sensitive credential information
- **Process Isolation**: System runs with appropriate user privileges (not root/administrator unless required)

## External Dependency Assumptions

### Library Stability Assumptions
- **FastAPI**: REST API framework provides stable async request handling
- **Pydantic**: Data validation library maintains backward compatibility for models
- **psutil**: System monitoring library works consistently across target platforms  
- **watchdog**: File monitoring library handles platform-specific filesystem events

### Optional Dependency Assumptions
- **pywin32**: Windows service functionality gracefully degrades if not available
- **ML Libraries**: Machine learning features are optional and can be disabled
- **Threat Intel Sources**: External threat intelligence sources are optional enhancements
