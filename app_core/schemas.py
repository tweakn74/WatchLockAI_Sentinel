"""Sentinel Event Schemas - Pydantic v2 models implementing schemas.md specifications."""

from __future__ import annotations

import socket
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventType(str, Enum):
    """File system event types."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class ProcessEventType(str, Enum):
    """Process event types."""
    STARTED = "started"
    EXITED = "exited"


class RegistryEventType(str, Enum):
    """Registry event types."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"


class RegistryHive(str, Enum):
    """Windows registry hives."""
    HKCU = "HKCU"
    HKLM = "HKLM"
    HKU = "HKU"
    HKCR = "HKCR"


class NetworkEventType(str, Enum):
    """Network event types."""
    CONNECTION = "connection"
    LISTEN = "listen"
    CLOSE = "close"


class NetworkProtocol(str, Enum):
    """Network protocols."""
    TCP = "TCP"
    UDP = "UDP"
    OTHER = "OTHER"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AlertCategory(str, Enum):
    """Alert categories."""
    RANSOMWARE = "ransomware"
    PERSISTENCE = "persistence"
    PROCESS = "process"
    NETWORK = "network"
    HEALTH = "health"
    GENERAL = "general"


class BaseEvent(BaseModel):
    """Base event with common fields per schemas.md."""

    host_id: str = Field(default_factory=lambda: socket.gethostname())
    sentinel_version: str = Field(default="1.0.0")
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
    )


class FileEvent(BaseEvent):
    """FileEvent@v1 implementing schemas.md specification."""

    event_type: EventType
    path: str
    old_path: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None
    entropy: float | None = Field(None, ge=0.0, le=8.0)
    proc_pid: int | None = None
    proc_name: str | None = None

    @field_validator("entropy")
    @classmethod
    def validate_entropy(cls, v: float | None) -> float | None:
        """Validate entropy is within Shannon entropy bounds."""
        if v is not None and (v < 0.0 or v > 8.0):
            msg = "Entropy must be between 0.0 and 8.0"
            raise ValueError(msg)
        return v


class ProcessEvent(BaseEvent):
    """ProcessEvent@v1 implementing schemas.md specification."""

    event_type: ProcessEventType
    pid: int
    ppid: int | None = None
    exe: str | None = None
    cmdline: str | None = None
    username: str | None = None
    hash_sha256: str | None = None
    start_ts: str | None = None
    end_ts: str | None = None


class RegistryEvent(BaseEvent):
    """RegistryEvent@v1 implementing schemas.md specification."""

    event_type: RegistryEventType
    hive: RegistryHive
    key_path: str
    value_name: str | None = None
    value_type: str | None = None
    data_preview: str | None = Field(None, max_length=200)
    proc_pid: int | None = None
    proc_name: str | None = None


class NetworkEvent(BaseEvent):
    """NetworkEvent@v1 implementing schemas.md specification."""

    event_type: NetworkEventType
    pid: int | None = None
    proc_name: str | None = None
    laddr_ip: str | None = None
    laddr_port: int | None = Field(None, ge=0, le=65535)
    raddr_ip: str | None = None
    raddr_port: int | None = Field(None, ge=0, le=65535)
    proto: NetworkProtocol
    status: str | None = None


class HealthMetric(BaseEvent):
    """HealthMetric@v1 implementing schemas.md specification."""

    cpu_pct: float = Field(ge=0.0, le=100.0)
    ram_pct: float = Field(ge=0.0, le=100.0)
    disk_pct_free: float = Field(ge=0.0, le=100.0)
    temp_c: float | None = None


class ProvenanceInfo(BaseModel):
    """Rule provenance information per Knowledge Pack requirements."""

    file: str
    section: str
    lines: str | None = None


class DetectionAlert(BaseEvent):
    """DetectionAlert@v1 implementing alerts.md specification."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: AlertSeverity
    category: AlertCategory
    tag: str
    entities: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    rationale: str
    provenance: ProvenanceInfo
    suggested_actions: list[str] = Field(default_factory=list)


class HealthAlert(DetectionAlert):
    """Health-specific alert subclass."""

    category: AlertCategory = Field(default=AlertCategory.HEALTH)


# Event type union for bus routing
SentinelEvent = FileEvent | ProcessEvent | RegistryEvent | NetworkEvent | HealthMetric | DetectionAlert
