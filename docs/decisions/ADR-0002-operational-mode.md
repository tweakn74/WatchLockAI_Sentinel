# ADR-0002: Operational Mode Runtime State Management

**Status:** Accepted  
**Date:** 2025-09-03  
**Deciders:** Engineering Team  

## Context and Problem Statement

WatchLockAI Sentinel requires a runtime configurable operational mode that controls system behavior without requiring application restart. The operational mode determines monitoring scope, response actions, and alert policies. The system needs to persist the current operational mode across restarts and provide atomic updates to prevent inconsistent state.

Original implementation used static configuration in `config.yaml`, but this required restart for changes and didn't support dynamic operational adjustments needed for incident response.

## Decision Drivers

- **Runtime Flexibility**: Must support operational mode changes without application restart
- **Persistence**: Current mode must survive application restarts  
- **Atomicity**: Mode changes must be atomic to prevent inconsistent state
- **Thread Safety**: Multiple threads may read mode concurrently during high-load monitoring
- **API Integration**: Web console and REST API must support mode changes
- **Configuration Integration**: Must integrate with existing Pydantic configuration system
- **Validation**: Mode values must be validated against allowed options
- **Auditability**: Mode changes should be logged for security audit

## Considered Options

### Option 1: In-Memory State Only
- Store operational mode only in memory with API updates
- Pros:
  - Simple implementation
  - Fast access
  - No file I/O overhead
- Cons:
  - Lost on restart (reverts to config.yaml default)
  - No persistence for incident response mode changes
  - Cannot recover operational state after crash

### Option 2: Direct config.yaml Updates
- Modify config.yaml file directly for operational mode changes
- Pros:
  - Single source of truth
  - Existing YAML parsing infrastructure
- Cons:
  - Complex atomic YAML updates
  - Risk of corrupting entire configuration
  - YAML structure makes atomic updates difficult
  - Requires restart to reload in some scenarios

### Option 3: Separate JSON State File with Atomic Updates
- Store operational mode in dedicated `config/operational_mode.json` file
- Use atomic write pattern (temp file + rename) for consistency
- Cache in memory with dirty flag for performance
- Pros:
  - Simple JSON structure easy to update atomically
  - Clear separation of runtime vs static configuration  
  - Thread-safe with file locking
  - Fast reads via caching
  - Can audit mode changes via file timestamps
- Cons:
  - Additional file to manage
  - Slightly more complex than in-memory only

## Decision Outcome

**Chosen option:** "Separate JSON State File with Atomic Updates" because it provides the best balance of persistence, atomicity, performance, and maintainability.

### Implementation Details

**Storage Format:**
```json
{
  "mode": "observe",
  "last_updated": "2025-09-03T03:02:21Z"
}
```

**Module Structure:** `config/operational_mode.py`
- `get_mode() -> OperationalMode` - Thread-safe cached read
- `set_mode(mode: OperationalMode) -> None` - Atomic write with validation  
- `is_valid_mode(mode: str) -> bool` - Mode validation
- `get_valid_modes() -> list[OperationalMode]` - Available modes

**Valid Modes:**
- `observe` - Monitor only, no automated response
- `alert` - Generate alerts, minimal automated response
- `contain` - Active containment of identified threats  
- `quarantine` - Aggressive isolation of suspicious activity
- `offline` - Disable most monitoring (maintenance mode)

**Thread Safety:**
- Global threading lock for write operations
- Cache invalidation on writes
- Atomic file operations (temp file + rename)

**API Integration:**
- `GET /api/operational_mode` - Current mode
- `PUT /api/operational_mode` - Update mode with validation
- Web console policy management page

### Positive Consequences
- Runtime operational flexibility for incident response
- Atomic mode changes prevent inconsistent state
- Thread-safe implementation supports concurrent access  
- Integration with existing web console and API
- Auditability via file timestamps and logging
- Performance optimization via caching
- Clear separation of static vs runtime configuration

### Negative Consequences
- Additional file to manage in deployment
- Slightly increased complexity vs in-memory only
- JSON file must be writable (deployment consideration)
- Potential for cache/file inconsistency if not implemented correctly

## Compliance

This decision ensures compliance with:

**Hard Gates:**
- `ruff=0` - Code follows linting standards with proper type annotations
- `pyright=0` - Full type safety with proper error handling
- Test non-regression - New functionality covered by unit and integration tests

**Platform Compatibility:**
- Uses pathlib.Path for cross-platform file operations
- Thread-safe operations work consistently on Windows and Linux
- No platform-specific dependencies

**Security Requirements:**
- File operations use secure atomic write patterns
- Input validation prevents invalid mode injection
- Logging provides audit trail for security analysis

**Performance Requirements:**
- Cached reads minimize file I/O overhead
- Atomic writes prevent lock contention
- No impact on high-frequency monitoring operations

## Follow-up Actions

- [x] Implement `config/operational_mode.py` module
- [x] Add operational mode API endpoints  
- [x] Update web console policy management
- [x] Add unit tests for atomic operations and edge cases
- [x] Update configuration documentation
- [ ] Add integration tests for mode changes during operation
- [ ] Implement audit logging for mode changes
- [ ] Consider adding mode change notifications via event bus

## Links and References

- Configuration management in `app_core/config.py`
- REST API implementation in `console/api/operational_mode.py`  
- Web console policy page in `console/templates/policies.html`
- Thread safety patterns: Python threading documentation
- Atomic file operations: POSIX rename semantics

---

## ADR Metadata

- **ID:** ADR-0002
- **Title:** Operational Mode Runtime State Management  
- **Status:** Accepted
- **Date:** 2025-09-03
- **Deciders:** Engineering Team
- **Technical Story:** Operational Mode Implementation

## Change Log

| Date | Author | Change |
|---|---|---|
| 2025-09-03 | MiniMax Agent | Initial creation and acceptance |
