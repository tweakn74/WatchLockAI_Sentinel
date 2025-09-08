# Coding Standards

## Ruff Configuration and Rules

### Active Ruff Rules
The project uses ruff with the following rule configuration:

```toml
# pyproject.toml (expected configuration)
[tool.ruff]
target-version = "py38"
line-length = 100

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings  
    "F",    # Pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
]
ignore = [
    "E501",  # Line too long (handled by formatter)
    "B008",  # Do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py

[tool.ruff.lint.isort]
known-first-party = ["app_core", "collectors", "detection", "response", "service", "console"]
```

### Code Style Expectations

#### Import Organization
```python
# Standard library imports
import asyncio
import json
import platform
from pathlib import Path
from typing import Dict, List, Optional, Union

# Third-party imports
import pydantic
from loguru import logger

# Local imports
from app_core.bus import EventBus
from app_core.schemas import SentinelEvent
from collectors.fs_monitor import FileSystemMonitor
```

#### Line Length and Formatting
- **Maximum line length**: 100 characters
- **String quotes**: Prefer double quotes `"string"` over single quotes
- **Trailing commas**: Use in multi-line constructs
- **Function definitions**: Break long signatures across multiple lines

```python
# Good: Multi-line function signature
def process_detection_alert(
    alert: DetectionAlert,
    severity_threshold: float,
    enable_notifications: bool = True,
) -> ActionResponse:
    pass

# Good: Multi-line dictionary
config_mapping = {
    "file_system": fs_config,
    "processes": proc_config,
    "registry": reg_config,  # Trailing comma
}
```

## Pyright Strict Profile Expectations

### Type Checking Configuration
```json
// pyrightconfig.json (expected)
{
    "typeCheckingMode": "strict",
    "pythonVersion": "3.8",
    "pythonPlatform": "All",
    "reportMissingImports": "error",
    "reportMissingTypeStubs": "warning",
    "reportUnknownParameterType": "error",
    "reportUnknownMemberType": "warning",
    "reportUnnecessaryIsInstance": "warning",
    "exclude": [
        "**/node_modules",
        "**/__pycache__",
        "**/.*"
    ]
}
```

### Type Annotation Requirements

#### Function Signatures
```python
# Required: All public functions must have type annotations
def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of byte data."""
    pass

# Required: Async functions
async def process_event(event: SentinelEvent) -> None:
    """Process incoming sentinel event."""
    pass

# Required: Class methods
class EventProcessor:
    def __init__(self, bus: EventBus) -> None:
        self._bus = bus
    
    def get_statistics(self) -> Dict[str, int]:
        return {"processed": 0}
```

#### Complex Type Annotations
```python
from typing import Dict, List, Optional, Union, Protocol, TypedDict

# Use Union for multiple types
ConfigValue = Union[str, int, bool, List[str]]

# Use Optional for nullable values
def get_config_value(key: str) -> Optional[ConfigValue]:
    pass

# Use Protocol for structural typing
class EventSubscriber(Protocol):
    async def __call__(self, event: SentinelEvent) -> None:
        ...

# Use TypedDict for structured dictionaries (see section below)
class DetectionMetadata(TypedDict):
    rule_id: str
    confidence: float
    matched_patterns: List[str]
```

## Typing Conventions

### TypedDict vs Pydantic Models

#### Use TypedDict for:
- Internal data structures
- Configuration dictionaries  
- Simple data containers without validation
- Performance-critical code paths

```python
from typing import TypedDict, List

class ProcessInfo(TypedDict):
    pid: int
    name: str
    cmdline: List[str]
    cpu_percent: float
    memory_mb: int

# Usage
def get_process_info(pid: int) -> ProcessInfo:
    return {
        "pid": pid,
        "name": "example.exe",
        "cmdline": ["/usr/bin/python", "app.py"],
        "cpu_percent": 1.5,
        "memory_mb": 128,
    }
```

#### Use Pydantic Models for:
- Event schemas and API models
- Configuration classes with validation
- Data that needs serialization/deserialization
- External interface boundaries

```python
from pydantic import BaseModel, validator
from typing import List

class FileEvent(BaseModel):
    path: str
    event_type: str
    timestamp: float
    size: Optional[int] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed = ['created', 'modified', 'deleted', 'moved']
        if v not in allowed:
            raise ValueError(f'event_type must be one of {allowed}')
        return v
    
    class Config:
        # Immutable events
        allow_mutation = False
```

### Platform Guards and Type Safety

#### Windows-Only Module Pattern
```python
import platform
from typing import Optional, TYPE_CHECKING

# Use TYPE_CHECKING for import-only dependencies
if TYPE_CHECKING:
    import winreg
else:
    winreg = None

IS_WINDOWS = platform.system() == "Windows"

# Proper platform guard with types
def read_registry_key(key_path: str) -> Optional[str]:
    """Read Windows registry key with proper platform guards."""
    if not IS_WINDOWS or winreg is None:
        logger.warning("Registry access not available on this platform")
        return None
    
    try:
        # Import winreg dynamically to avoid import errors on Linux
        import winreg  # noqa: F401
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "")
            return str(value)
    except (ImportError, OSError, FileNotFoundError):
        logger.exception(f"Failed to read registry key: {key_path}")
        return None
```

#### Type Stubs for Platform Modules
```python
# File: stubs/winreg.pyi (type stubs for development)
from typing import Any, Optional, Tuple

HKEY_LOCAL_MACHINE: int
HKEY_CURRENT_USER: int

def OpenKey(key: int, sub_key: str) -> Any: ...
def QueryValueEx(key: Any, value_name: str) -> Tuple[Any, int]: ...
```

### Error Handling Patterns

#### Structured Error Types
```python
from typing import Union
from enum import Enum

class ErrorCode(Enum):
    PLATFORM_NOT_SUPPORTED = "platform_not_supported"
    CONFIGURATION_INVALID = "configuration_invalid"
    DEPENDENCY_MISSING = "dependency_missing"
    RESOURCE_UNAVAILABLE = "resource_unavailable"

class SentinelError(Exception):
    """Base exception for all Sentinel errors."""
    def __init__(self, code: ErrorCode, message: str, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

# Usage
def initialize_registry_monitor() -> Union[RegistryMonitor, SentinelError]:
    if not IS_WINDOWS:
        return SentinelError(
            ErrorCode.PLATFORM_NOT_SUPPORTED,
            "Registry monitoring requires Windows platform",
            {"current_platform": platform.system()}
        )
    # ... implementation
```

## Network Restrictions in Tests

### No Network Calls in Tests
```python
# BAD: Real network calls in tests
def test_threat_intelligence_lookup():
    result = requests.get("https://api.threat-intel.com/lookup")
    assert result.status_code == 200

# GOOD: Mock network calls
import pytest
from unittest.mock import patch, Mock

@patch('requests.get')
def test_threat_intelligence_lookup(mock_get):
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"threat_level": "low"}
    mock_get.return_value = mock_response
    
    # Test the actual logic
    result = lookup_threat_intelligence("example.com")
    assert result["threat_level"] == "low"
    
    # Verify network call was made with correct parameters
    mock_get.assert_called_once_with(
        "https://api.threat-intel.com/lookup",
        params={"domain": "example.com"}
    )
```

### Test Data Management
```python
# Use fixtures for test data
@pytest.fixture
def sample_file_events():
    """Provide sample file events for testing."""
    return [
        FileEvent(
            path="/tmp/test.txt",
            event_type="created",
            timestamp=1000.0,
            size=1024
        ),
        FileEvent(
            path="/tmp/test.txt", 
            event_type="modified",
            timestamp=1001.0,
            size=2048
        ),
    ]

# Deterministic test data
def test_file_processing(sample_file_events):
    processor = FileProcessor()
    results = [processor.process(event) for event in sample_file_events]
    
    # Assertions based on deterministic data
    assert len(results) == 2
    assert results[0].action == "monitor"
    assert results[1].action == "analyze"
```

## Documentation Standards

### Docstring Format
```python
def process_detection_alert(
    alert: DetectionAlert,
    threshold: float,
    notify: bool = True
) -> ActionResponse:
    """Process a detection alert and determine response actions.
    
    This function evaluates the alert against configured thresholds
    and triggers appropriate response actions based on severity.
    
    Args:
        alert: The detection alert to process
        threshold: Minimum severity threshold for action (0.0-1.0)
        notify: Whether to send notifications (default: True)
    
    Returns:
        ActionResponse containing the actions taken and their results
        
    Raises:
        SentinelError: If alert processing fails or invalid threshold
        
    Example:
        >>> alert = DetectionAlert(rule_id="R001", severity="high")
        >>> response = process_detection_alert(alert, 0.7)
        >>> print(response.actions_taken)
        ['isolate_process', 'send_notification']
    """
    pass
```

### Code Comments
```python
# Good: Explain why, not what
def calculate_file_entropy(file_path: Path) -> float:
    """Calculate Shannon entropy to detect encrypted/packed files."""
    
    # Read in chunks to handle large files without memory issues
    chunk_size = 8192
    byte_counts = [0] * 256
    total_bytes = 0
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            for byte in chunk:
                byte_counts[byte] += 1
                total_bytes += 1
    
    # Shannon entropy calculation: H = -Σ(p * log2(p))
    # Higher entropy (closer to 8.0) suggests encryption/compression
    entropy = 0.0
    for count in byte_counts:
        if count > 0:
            probability = count / total_bytes
            entropy -= probability * math.log2(probability)
    
    return entropy
```

## Performance Guidelines

### Async/Await Best Practices
```python
# Good: Proper async context management
async def process_events_batch(events: List[SentinelEvent]) -> List[ActionResponse]:
    """Process multiple events concurrently."""
    tasks = [process_single_event(event) for event in events]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Good: Use async context managers
async def monitor_file_system(paths: List[str]) -> None:
    """Monitor file system changes asynchronously."""
    async with FileSystemWatcher(paths) as watcher:
        async for event in watcher.events():
            await process_file_event(event)
```

### Memory Management
```python
# Good: Use generators for large data sets
def read_log_entries(log_file: Path) -> Iterator[LogEntry]:
    """Read log entries one at a time to avoid memory issues."""
    with open(log_file, 'r') as f:
        for line in f:
            if entry := parse_log_line(line):
                yield entry

# Good: Limit collection sizes
class EventBuffer:
    def __init__(self, max_size: int = 1000):
        self._events: Deque[SentinelEvent] = deque(maxlen=max_size)
    
    def add_event(self, event: SentinelEvent) -> None:
        # Automatically drops oldest events when full
        self._events.append(event)
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-02T20:31:09+00:00  
**Author**: MiniMax Agent