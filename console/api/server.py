"""FastAPI web interface for WatchLockAI Sentinel.

Provides local HTTP API and web console for monitoring and management.
"""

from __future__ import annotations

import asyncio
import os
import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel, ValidationError


# Feature flags
RATE_LIMIT_ENABLED = False  # Rate limiting (disabled by default for non-regression)
HEALTH_ENDPOINT_ENABLED = os.getenv("HEALTH_ENDPOINT_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
METRICS_DEBUG_ENABLED = os.getenv("METRICS_DEBUG_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
CONFIG_HOT_RELOAD_ENABLED = os.getenv(
    "CONFIG_HOT_RELOAD_ENABLED", "0"
).strip().lower() in {"1", "true", "yes", "on"}  # default OFF
CONFIG_HOT_RELOAD_DEBOUNCE_MS = int(os.getenv("CONFIG_HOT_RELOAD_DEBOUNCE_MS", "750"))

# MITRE ATT&CK flags (default OFF)
MITRE_API_ENABLED = os.getenv("MITRE_API_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# RBAC for admin routes (P1-005)
ADMIN_AUTH_ENABLED = os.getenv("ADMIN_AUTH_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}  # default OFF
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

# P2-001: Anomaly detection flags
ANOMALY_ENABLED = os.getenv("ANOMALY_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}  # default OFF
ANOMALY_SKLEARN_ENABLED = os.getenv("ANOMALY_SKLEARN_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}  # default OFF

# P2-002: Quarantine flags
QUARANTINE_ENABLED = os.getenv("QUARANTINE_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}  # default OFF

# P2-003: Console authentication flags (default OFF)
CONSOLE_AUTH_ENABLED = os.getenv("CONSOLE_AUTH_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
CONSOLE_AUTH_RATE_LIMIT = 10  # login attempts per minute

# P2-004: Streaming/SSE flags (default OFF)
STREAM_ENABLED = os.getenv("STREAM_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
STREAM_TYPE = os.getenv("STREAM_TYPE", "sse").lower()  # only 'sse' implemented
STREAM_HEALTH_INTERVAL_MS = int(os.getenv("STREAM_HEALTH_INTERVAL_MS", "1000"))
STREAM_REQUIRE_AUTH = os.getenv("STREAM_REQUIRE_AUTH", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# P3-002: Log rotation & redaction flags (default ON for safe defaults)
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "1048576"))  # 1MB default
LOG_BACKUPS = int(os.getenv("LOG_BACKUPS", "5"))  # 5 backup files default
LOG_REDACT_SECRETS = os.getenv("LOG_REDACT_SECRETS", "1").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}  # default ON

# P3-003: Service packaging flag (default OFF)
SERVICE_ENABLED = os.getenv("SERVICE_ENABLED", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}  # default OFF

try:
    # Optional import; safe if module missing
    from . import rate_limit as rl  # type: ignore
except Exception:
    rl = None  # type: ignore

# P2-001: Import-safe anomaly detection
try:
    from . import anomaly as anomaly_mod  # type: ignore
except Exception:
    anomaly_mod = None  # type: ignore

# P2-002: Import-safe quarantine system
try:
    from . import quarantine as quarantine_mod  # type: ignore
except Exception:
    quarantine_mod = None  # type: ignore

# P2-003: Import-safe auth system
try:
    from . import auth as auth_mod  # type: ignore
except Exception:
    auth_mod = None  # type: ignore

# P3-001: Import-safe config schema system
try:
    from . import config_schema as config_schema_mod  # type: ignore
except Exception:
    config_schema_mod = None  # type: ignore

# Simple in-memory rate limiter
_rate_limiter: dict[str, list[float]] = {}


def rate_limited(
    key_fn: Callable[[Any], str], max_calls: int, per_seconds: int
) -> Callable:
    """Rate limiting decorator (only active when RATE_LIMIT_ENABLED=True).

    Args:
        key_fn: Function to generate rate limit key from request
        max_calls: Maximum calls allowed
        per_seconds: Time window in seconds

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            if not RATE_LIMIT_ENABLED:
                return await func(*args, **kwargs)

            # Extract key from request
            key = key_fn(args[0] if args else None)  # Assume first arg is request
            current_time = time.time()

            # Initialize or clean old entries
            if key not in _rate_limiter:
                _rate_limiter[key] = []

            # Remove expired entries
            _rate_limiter[key] = [
                t for t in _rate_limiter[key] if current_time - t < per_seconds
            ]

            # Check rate limit
            if len(_rate_limiter[key]) >= max_calls:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            # Record this request
            _rate_limiter[key].append(current_time)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def admin_auth_dependency():
    """RBAC dependency for admin routes - supports X-Admin-Token header OR session auth when enabled."""

    def _dep(request):
        if not ADMIN_AUTH_ENABLED:
            return  # No auth required when disabled

        # First, try session-based authentication (if enabled)
        if CONSOLE_AUTH_ENABLED and auth_mod:
            try:
                session_user = auth_mod.get_session_user(request)
                if session_user:
                    return  # Valid session found, allow access
            except Exception:
                pass  # Fall through to token auth

        # Fall back to token-based authentication
        if not ADMIN_TOKEN:
            raise HTTPException(status_code=500, detail="Admin token not configured")

        token = getattr(request, "headers", {}).get("x-admin-token") or getattr(
            request, "headers", {}
        ).get("X-Admin-Token")
        if not token or token != ADMIN_TOKEN:
            raise HTTPException(status_code=403, detail="Admin authentication required")

    return _dep


def log_structured_metrics(route: str, counters: dict, uptime_s: int) -> None:
    """Emit structured log for metrics endpoint calls (P1-006)."""
    try:
        # Try to use existing logger first
        try:
            from loguru import logger  # type: ignore

            logger.info(
                "metrics_access",
                extra={
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "route": route,
                    "counters": counters,
                    "uptime_s": uptime_s,
                },
            )
        except ImportError:
            # Fall back to stdlib logging
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "route": route,
                "counters": counters,
                "uptime_s": uptime_s,
            }
            logging.getLogger("sentinel.metrics").info(json.dumps(log_data))
    except Exception:
        # Swallow logging errors to keep API stable
        pass


class StatusResponse(BaseModel):
    """Service status response model."""

    running: bool
    uptime_seconds: float
    collectors: dict[str, Any]
    rules_engine: dict[str, Any]
    event_bus: dict[str, Any]
    timestamp: str


class AlertSummary(BaseModel):
    """Alert summary response model."""

    total_alerts: int
    critical_alerts: int
    warning_alerts: int
    info_alerts: int
    recent_alerts: list[dict[str, Any]]


class DetectionResponse(BaseModel):
    """Detection events response model."""

    total_detections: int
    detections: list[dict[str, Any]]
    filters: dict[str, Any]


class ActionResponse(BaseModel):
    """Action execution response model."""

    success: bool
    message: str


class ThreatIntelResponse(BaseModel):
    """Threat intelligence search response model."""

    success: bool
    query: str
    total_results: int
    results: list[dict[str, Any]]
    frameworks_searched: list[str]
    timestamp: str


class PolicyResponse(BaseModel):
    """Operational policies response model."""

    success: bool
    operational_mode: str
    allow_destructive_actions: bool
    timestamp: str


class PolicyUpdateResponse(BaseModel):
    """Policy update response model."""

    success: bool
    message: str
    operational_mode: str
    timestamp: str


class EventBusMetricsResponse(BaseModel):
    """Event bus observability metrics response model."""

    event_bus: dict[str, int]


class CompositeHealthResponse(BaseModel):
    """Composite health response combining stats + observability + flag state."""

    service: dict[str, Any]
    event_bus: dict[str, Any]
    flags: dict[str, str]
    version: str


class MITRERule(BaseModel):
    """MITRE ATT&CK rule information."""

    id: str
    name: str
    tactic: str
    technique: str
    event: str
    threshold: int
    window_s: int
    severity: str
    response: str
    stage: Optional[str] = None
    group_by: Optional[str] = None
    where: Optional[str] = None


class MITRECoverageResponse(BaseModel):
    """MITRE ATT&CK coverage response."""

    enabled: bool
    profile: str
    rules_count: int
    by_tactic: Dict[str, int]
    rules: list[MITRERule]


class SentinelWebAPI:
    """FastAPI web interface for Sentinel service."""

    def __init__(
        self, sentinel_service: Any, host: str = "127.0.0.1", port: int = 8080
    ) -> None:
        """Initialize web API.

        Args:
            sentinel_service: Reference to SentinelService instance.
            host: Host to bind to (default: localhost only).
            port: Port to bind to.
        """
        self.sentinel_service = sentinel_service
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="WatchLockAI Sentinel API",
            description="Local web interface for endpoint security monitoring",
            version="0.2.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
        )
        self.server: uvicorn.Server | None = None
        self.server_task: asyncio.Task | None = None

        # Setup templates and static files
        console_dir = Path(__file__).parent
        self.templates = Jinja2Templates(directory=console_dir / "templates")

        # Setup static files if directory exists
        static_dir = console_dir / "static"
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

        # Include operational mode API routes
        try:
            from console.api.operational_mode import router as operational_mode_router

            self.app.include_router(operational_mode_router)
        except ImportError as e:
            logger.warning(f"Failed to load operational mode API routes: {e}")

        self._setup_error_handlers()
        self._setup_routes()

    def _setup_error_handlers(self) -> None:
        """Setup centralized error handlers for consistent API responses."""

        @self.app.exception_handler(ValidationError)
        async def validation_exception_handler(
            request: Request, exc: ValidationError
        ) -> JSONResponse:
            """Handle Pydantic validation errors with structured 422 responses."""
            logger.warning(f"Validation error on {request.url}: {exc}")
            return JSONResponse(
                status_code=422,
                content={"error": {"code": "VALIDATION_ERROR", "detail": str(exc)}},
            )

        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(
            request: Request, exc: HTTPException
        ) -> JSONResponse:
            """Handle HTTP exceptions with structured error envelope."""
            logger.warning(
                f"HTTP error {exc.status_code} on {request.url}: {exc.detail}"
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": {"code": "HTTP_ERROR", "detail": exc.detail}},
            )

    def _setup_routes(self) -> None:
        """Setup API routes and web console endpoints."""

        # API Endpoints
        @self.app.get("/api/status", response_model=StatusResponse)
        async def get_status() -> StatusResponse:
            """Get service status."""
            if not self.sentinel_service:
                raise HTTPException(status_code=503, detail="Service not available")

            status = self.sentinel_service.get_status()
            return StatusResponse(
                running=status["running"],
                uptime_seconds=status["uptime_seconds"],
                collectors=status["collectors"],
                rules_engine=status["rules_engine"],
                event_bus=status["event_bus"],
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        @self.app.get("/api/alerts", response_model=AlertSummary)
        async def get_alerts() -> AlertSummary:
            """Get alerts summary."""
            if not self.sentinel_service or not self.sentinel_service.alert_manager:
                raise HTTPException(
                    status_code=503, detail="Alert manager not available"
                )

            # Get recent alerts from alert manager
            try:
                recent_alerts = self.sentinel_service.alert_manager.get_recent_alerts(
                    limit=50
                )

                # Count by severity
                critical_count = sum(
                    1 for a in recent_alerts if a.get("severity") == "critical"
                )
                warning_count = sum(
                    1 for a in recent_alerts if a.get("severity") == "warning"
                )
                info_count = sum(
                    1 for a in recent_alerts if a.get("severity") == "info"
                )

                return AlertSummary(
                    total_alerts=len(recent_alerts),
                    critical_alerts=critical_count,
                    warning_alerts=warning_count,
                    info_alerts=info_count,
                    recent_alerts=recent_alerts[:10],  # Latest 10 for summary
                )
            except Exception as e:
                logger.error(f"Error getting alerts: {e}")
                return AlertSummary(
                    total_alerts=0,
                    critical_alerts=0,
                    warning_alerts=0,
                    info_alerts=0,
                    recent_alerts=[],
                )

        @self.app.get("/api/detections", response_model=DetectionResponse)
        async def get_detections(
            limit: int = 100,
            severity: str | None = None,
            tag: str | None = None,
        ) -> DetectionResponse:
            """Get detection events with optional filtering."""
            if not self.sentinel_service or not self.sentinel_service.rules_engine:
                raise HTTPException(
                    status_code=503, detail="Rules engine not available"
                )

            try:
                # Get detections from rules engine
                detections = self.sentinel_service.rules_engine.get_recent_detections(
                    limit=limit,
                    filters={"severity": severity, "tag": tag}
                    if severity or tag
                    else None,
                )

                return DetectionResponse(
                    total_detections=len(detections),
                    detections=detections,
                    filters={"severity": severity, "tag": tag},
                )
            except Exception as e:
                logger.error(f"Error getting detections: {e}")
                return DetectionResponse(
                    total_detections=0,
                    detections=[],
                    filters={},
                )

        @self.app.post("/api/actions/pause", response_model=ActionResponse)
        async def pause_monitoring(duration_minutes: int = 5) -> ActionResponse:
            """Pause monitoring for specified duration."""
            if not self.sentinel_service or not self.sentinel_service.actions_manager:
                raise HTTPException(
                    status_code=503, detail="Actions manager not available"
                )

            try:
                result = self.sentinel_service.actions_manager.pause_monitoring(
                    duration_minutes * 60
                )
                return ActionResponse(success=True, message=result.message)
            except Exception as e:
                logger.error(f"Error pausing monitoring: {e}")
                raise HTTPException(status_code=500, detail=str(e)) from e

        @self.app.post("/api/actions/resume", response_model=ActionResponse)
        async def resume_monitoring() -> ActionResponse:
            """Resume monitoring if paused."""
            if not self.sentinel_service or not self.sentinel_service.actions_manager:
                raise HTTPException(
                    status_code=503, detail="Actions manager not available"
                )

            try:
                result = self.sentinel_service.actions_manager.resume_monitoring()
                return ActionResponse(success=True, message=result.message)
            except Exception as e:
                logger.error(f"Error resuming monitoring: {e}")
                raise HTTPException(status_code=500, detail=str(e)) from e

        @self.app.get("/api/ti/search", response_model=ThreatIntelResponse)
        async def search_threat_intelligence(
            query: str, limit: int = 10
        ) -> ThreatIntelResponse:
            """Search threat intelligence knowledge base."""
            if not query or len(query.strip()) < 2:
                raise HTTPException(
                    status_code=400, detail="Query must be at least 2 characters"
                )

            if limit < 1 or limit > 50:
                raise HTTPException(
                    status_code=400, detail="Limit must be between 1 and 50"
                )

            try:
                # Import here to avoid circular imports
                from platform.detection.threat_intel_db import get_threat_intel_db

                threat_intel_db = get_threat_intel_db()
                results = threat_intel_db.search(query.strip(), k=limit)

                return ThreatIntelResponse(
                    success=True,
                    query=query,
                    total_results=len(results),
                    results=results,
                    frameworks_searched=[
                        "MITRE_ATT&CK",
                        "Cyber_Kill_Chain",
                        "Threat_Hunting",
                        "Incident_Response",
                    ],
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

            except Exception as e:
                logger.error(f"Error searching threat intelligence: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Search failed: {str(e)}"
                ) from e

        @self.app.get("/api/policies", response_model=PolicyResponse)
        async def get_policies() -> PolicyResponse:
            """Get current operational policies."""
            try:
                # Get current configuration
                if not self.sentinel_service or not hasattr(
                    self.sentinel_service, "config"
                ):
                    raise HTTPException(
                        status_code=503, detail="Service configuration not available"
                    )

                config = self.sentinel_service.config

                return PolicyResponse(
                    success=True,
                    operational_mode=config.operational.mode,
                    allow_destructive_actions=config.responses.allow_destructive_actions,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

            except Exception as e:
                logger.error(f"Error getting policies: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to get policies: {str(e)}"
                ) from e

        @self.app.post("/api/policies", response_model=PolicyUpdateResponse)
        async def set_policies(policies_data: dict[str, Any]) -> PolicyUpdateResponse:
            """Update operational policies."""
            try:
                if not self.sentinel_service or not hasattr(
                    self.sentinel_service, "config"
                ):
                    raise HTTPException(
                        status_code=503, detail="Service configuration not available"
                    )

                # Validate operational mode
                new_mode = policies_data.get("operational_mode")
                if new_mode not in ["monitor", "proactive"]:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid operational mode. Must be 'monitor' or 'proactive'",
                    )

                # Update configuration
                config = self.sentinel_service.config
                config.operational.mode = new_mode

                # Save configuration to file (simplified - in production would use proper config persistence)
                from pathlib import Path

                import yaml

                config_path = Path("config.yaml")
                if config_path.exists():
                    # Read current config
                    with open(config_path, encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    # Update operational mode
                    if "operational" not in config_data:
                        config_data["operational"] = {}
                    config_data["operational"]["mode"] = new_mode

                    # Write back to file
                    with open(config_path, "w", encoding="utf-8") as f:
                        yaml.dump(config_data, f, default_flow_style=False)

                # Update actions manager if available
                if (
                    hasattr(self.sentinel_service, "actions_manager")
                    and self.sentinel_service.actions_manager
                ):
                    self.sentinel_service.actions_manager.operational_config.mode = (
                        new_mode
                    )

                logger.info(f"Operational mode updated to: {new_mode}")

                return PolicyUpdateResponse(
                    success=True,
                    message=f"Operational mode updated to '{new_mode}'",
                    operational_mode=new_mode,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

            except HTTPException:
                raise  # Re-raise HTTP exceptions
            except Exception as e:
                logger.error(f"Error updating policies: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to update policies: {str(e)}"
                ) from e

        # Web Console Pages
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request) -> HTMLResponse:
            """Main dashboard page."""
            return self.templates.TemplateResponse(
                "dashboard.html", {"request": request}
            )

        @self.app.get("/detections", response_class=HTMLResponse)
        async def detections_page(request: Request) -> HTMLResponse:
            """Detections page."""
            return self.templates.TemplateResponse(
                "detections.html", {"request": request}
            )

        @self.app.get("/assets", response_class=HTMLResponse)
        async def assets_page(request: Request) -> HTMLResponse:
            """Asset monitoring page."""
            return self.templates.TemplateResponse("assets.html", {"request": request})

        @self.app.get("/accounts", response_class=HTMLResponse)
        async def accounts_page(request: Request) -> HTMLResponse:
            """Account activity page."""
            return self.templates.TemplateResponse(
                "accounts.html", {"request": request}
            )

        @self.app.get("/processes", response_class=HTMLResponse)
        async def processes_page(request: Request) -> HTMLResponse:
            """Script and process monitoring page."""
            return self.templates.TemplateResponse(
                "processes.html", {"request": request}
            )

        @self.app.get("/policies", response_class=HTMLResponse)
        async def policies_page(request: Request) -> HTMLResponse:
            """Operational policies configuration page."""
            return self.templates.TemplateResponse(
                "policies.html", {"request": request}
            )

        # Debug metrics route (opt-in only)
        if METRICS_DEBUG_ENABLED:

            @self.app.get(
                "/api/metrics/event_bus", response_model=EventBusMetricsResponse
            )
            async def get_event_bus_metrics() -> EventBusMetricsResponse:
                """Get event bus observability metrics (debug only - requires METRICS_DEBUG_ENABLED=1)."""
                if not self.sentinel_service or not self.sentinel_service.event_bus:
                    raise HTTPException(
                        status_code=503, detail="Event bus not available"
                    )

                try:
                    metrics = (
                        self.sentinel_service.event_bus.get_observability_metrics()
                    )

                    # Structured logging (P1-006)
                    log_structured_metrics(
                        "/api/metrics/event_bus",
                        metrics,
                        int(getattr(self.sentinel_service, "uptime_seconds", 0)),
                    )

                    return EventBusMetricsResponse(event_bus=metrics)
                except Exception as e:
                    logger.error(f"Error getting event bus metrics: {e}")
                    raise HTTPException(status_code=500, detail="Failed to get metrics")

            @self.app.get("/api/metrics/snapshot")
            async def get_metrics_snapshot() -> dict:
                """Get timestamped rollup of all metrics (debug only - requires METRICS_DEBUG_ENABLED=1)."""
                svc = getattr(self, "sentinel_service", None)
                eb = getattr(svc, "event_bus", None) if svc else None

                # Gather all metrics
                event_bus_metrics = (
                    eb.get_observability_metrics()
                    if (eb and hasattr(eb, "get_observability_metrics"))
                    else {"delivery_success_count": 0, "delivery_failure_count": 0}
                )
                service_status = getattr(svc, "get_status", lambda: {})() if svc else {}
                uptime_s = int(getattr(svc, "uptime_seconds", 0)) if svc else 0

                snapshot = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "uptime_s": uptime_s,
                    "metrics": {
                        "event_bus": event_bus_metrics,
                        "service": service_status,
                    },
                }

                # Structured logging (P1-006)
                log_structured_metrics(
                    "/api/metrics/snapshot", event_bus_metrics, uptime_s
                )

                return snapshot

        # Composite health metrics endpoint (default ON, non-breaking)
        if HEALTH_ENDPOINT_ENABLED:
            deps = []
            try:
                if rl is not None:
                    from fastapi import Depends  # type: ignore

                    # 60 requests per minute for health checks
                    deps = [
                        Depends(
                            rl.rate_limit_dependency(
                                "metrics_health", max_calls=60, window_s=60
                            )
                        )
                    ]
            except Exception:
                deps = []

            @self.app.get(
                "/api/metrics/health",
                dependencies=deps,
                response_model=CompositeHealthResponse,
            )
            def metrics_health() -> CompositeHealthResponse:
                """Get composite health metrics combining stats + observability + flag state (requires HEALTH_ENDPOINT_ENABLED=1)."""
                svc = getattr(self, "sentinel_service", None)
                eb = getattr(svc, "event_bus", None) if svc else None

                # Service status
                service_status = getattr(svc, "get_status", lambda: {})() if svc else {}
                uptime_s = int(getattr(svc, "uptime_seconds", 0)) if svc else 0

                # Event bus metrics (merge stats + observability)
                event_bus_stats = getattr(eb, "get_stats", lambda: {})() if eb else {}
                event_bus_observability = (
                    getattr(eb, "get_observability_metrics", lambda: {})() if eb else {}
                )
                event_bus_combined = {**event_bus_stats, **event_bus_observability}

                # Feature flags state
                flags_state = {
                    "METRICS_DEBUG_ENABLED": os.getenv("METRICS_DEBUG_ENABLED", "0"),
                    "CONFIG_HOT_RELOAD_ENABLED": os.getenv(
                        "CONFIG_HOT_RELOAD_ENABLED", "0"
                    ),
                    "TI_CACHE_ENABLED": os.getenv("TI_CACHE_ENABLED", "0"),
                    "RATE_LIMIT_ENABLED": os.getenv("RATE_LIMIT_ENABLED", "0"),
                    "HEALTH_ENDPOINT_ENABLED": os.getenv(
                        "HEALTH_ENDPOINT_ENABLED", "0"
                    ),
                }

                # Version (RC tag if available, else "rc-1")
                version = "rc-1"  # Default as specified in requirements

                # Structured logging (P1-006)
                log_structured_metrics(
                    "/api/metrics/health", event_bus_combined, uptime_s
                )

                return CompositeHealthResponse(
                    service=service_status,
                    event_bus=event_bus_combined,
                    flags=flags_state,
                    version=version,
                )

        # MITRE ATT&CK coverage endpoint (default OFF)
        if MITRE_API_ENABLED:

            @self.app.get("/api/mitre/coverage", response_model=MITRECoverageResponse)
            def get_mitre_coverage() -> MITRECoverageResponse:
                """Get MITRE ATT&CK coverage information with profile and tactic breakdown."""
                try:
                    profile = os.getenv("MITRE_PROFILE", "baseline")
                    matrix_enabled = os.getenv("MITRE_MATRIX_ENABLED", "0") == "1"

                    # Try to get rules from loaded engine first, then load manually
                    rules_data = []
                    try:
                        from platform.detection.attack_matrix import get_loaded_rules

                        rules_data = get_loaded_rules()
                    except Exception:
                        # Fallback to manual loading
                        try:
                            from detection.attack_matrix import (
                                load_rules_from_path,
                                load_rules_by_profile,
                            )

                            # Load rules using profile system
                            rules_path = os.getenv("MITRE_RULES_PATH")
                            if rules_path:
                                rules = load_rules_from_path(rules_path, profile)
                            else:
                                # Try profile-specific YAML path first
                                profile_yaml_path = f"DOCS/mitre/rules/{profile}.yaml"
                                if Path(profile_yaml_path).exists():
                                    rules = load_rules_from_path(
                                        profile_yaml_path, profile
                                    )
                                else:
                                    # Use profile-based defaults
                                    rules = load_rules_by_profile(profile)

                            # Convert to dict format
                            for rule in rules:
                                rule_dict = {
                                    "id": rule.id,
                                    "name": rule.name,
                                    "tactic": rule.tactic,
                                    "technique": rule.technique,
                                    "event": rule.event,
                                    "threshold": rule.threshold,
                                    "window_s": rule.window_s,
                                    "severity": rule.severity,
                                    "response": rule.response,
                                }
                                # Add optional fields if present
                                if hasattr(rule, "stage"):
                                    rule_dict["stage"] = rule.stage
                                if hasattr(rule, "group_by"):
                                    rule_dict["group_by"] = rule.group_by
                                if hasattr(rule, "where"):
                                    rule_dict["where"] = rule.where
                                rules_data.append(rule_dict)

                        except ImportError:
                            # Fallback if detection module not available
                            rules_data = []

                    # Convert rules to response format and calculate tactic breakdown
                    rule_list = []
                    tactic_counts = {}

                    for rule_data in rules_data:
                        rule_dict = MITRERule(
                            id=rule_data.get("id", ""),
                            name=rule_data.get("name", ""),
                            tactic=rule_data.get("tactic", ""),
                            technique=rule_data.get("technique", ""),
                            event=rule_data.get("event", ""),
                            threshold=rule_data.get("threshold", 0),
                            window_s=rule_data.get("window_s", 0),
                            severity=rule_data.get("severity", ""),
                            response=rule_data.get("response", ""),
                            stage=rule_data.get("stage"),
                            group_by=rule_data.get("group_by"),
                            where=rule_data.get("where"),
                        )
                        rule_list.append(rule_dict)

                        # Count by tactic
                        tactic = rule_data.get("tactic", "Unknown")
                        tactic_counts[tactic] = tactic_counts.get(tactic, 0) + 1

                    return MITRECoverageResponse(
                        enabled=matrix_enabled,
                        profile=profile,
                        rules_count=len(rule_list),
                        by_tactic=tactic_counts,
                        rules=rule_list,
                    )

                except Exception as e:
                    logger.error(f"Error getting MITRE coverage: {e}")
                    # Return empty response on error
                    return MITRECoverageResponse(
                        enabled=False,
                        profile="baseline",
                        rules_count=0,
                        by_tactic={},
                        rules=[],
                    )

        # Config hot reload admin route (default OFF)
        if CONFIG_HOT_RELOAD_ENABLED:
            deps = []
            try:
                if rl is not None:
                    from fastapi import Depends  # type: ignore

                    # 5 requests per minute for admin reload
                    deps.append(
                        Depends(
                            rl.rate_limit_dependency(
                                "admin_config_reload", max_calls=5, window_s=60
                            )
                        )
                    )

                # Add RBAC dependency
                from fastapi import Depends  # type: ignore

                deps.append(Depends(admin_auth_dependency()))
            except Exception:
                # If FastAPI not available, create minimal deps list
                deps = []

            @self.app.post("/api/admin/config/reload", dependencies=deps)
            def admin_config_reload(debounce_ms: int | None = None) -> dict:
                """Trigger a non-blocking, debounced config reload (requires CONFIG_HOT_RELOAD_ENABLED=1)."""
                # Input validation (bounded integer via query param; defaults preserved)
                try:
                    dm = (
                        int(debounce_ms)
                        if debounce_ms is not None
                        else CONFIG_HOT_RELOAD_DEBOUNCE_MS
                    )
                except Exception:
                    dm = CONFIG_HOT_RELOAD_DEBOUNCE_MS
                if dm < 0:
                    dm = 0
                if dm > 60000:
                    dm = 60000  # hard upper bound for safety

                svc = getattr(self, "sentinel_service", None)
                trigger = getattr(svc, "trigger_config_reload", None)
                if callable(trigger):
                    try:
                        trigger(dm)
                    except Exception:
                        # swallow to keep API stable; true errors should be logged by service logger if present
                        pass
                return {"status": "reloading"}

        # P3-001: Configuration schema endpoint (always available when admin auth enabled)
        if ADMIN_AUTH_ENABLED:
            deps = []
            try:
                # Add RBAC dependency for admin routes
                from fastapi import Depends  # type: ignore

                deps.append(Depends(admin_auth_dependency()))
            except Exception:
                deps = []

            @self.app.get("/api/admin/config/schema", dependencies=deps)
            def admin_config_schema() -> dict:
                """Get configuration schema and current validation state (requires admin auth)."""
                if config_schema_mod is None:
                    return {
                        "error": "Configuration schema module not available",
                        "enabled": False,
                    }

                try:
                    result = config_schema_mod.get_schema_for_api()

                    # Structured logging
                    log_structured_metrics(
                        "/api/admin/config/schema",
                        {
                            "schema_version": result.get("summary", {}).get(
                                "schema_version", "unknown"
                            ),
                            "total_settings": result.get("summary", {}).get(
                                "total_settings", 0
                            ),
                        },
                        0,
                    )

                    return result
                except Exception as e:
                    return {"error": str(e), "enabled": True}

        # P2-001: Anomaly detection endpoints
        if ANOMALY_ENABLED and METRICS_DEBUG_ENABLED:
            # Debug-gated anomaly score endpoint
            deps = []
            try:
                if rl is not None:
                    from fastapi import Depends  # type: ignore

                    # 10 requests per minute for anomaly score
                    deps = [
                        Depends(
                            rl.rate_limit_dependency(
                                "anomaly_score", max_calls=10, window_s=60
                            )
                        )
                    ]
            except Exception:
                deps = []

            @self.app.get("/api/anomaly/score", dependencies=deps)
            def anomaly_score(window: int = 60) -> dict:
                """Get anomaly score for specified time window (requires ANOMALY_ENABLED=1 and METRICS_DEBUG_ENABLED=1)."""
                if anomaly_mod is None:
                    return {
                        "error": "Anomaly detection module not available",
                        "enabled": False,
                    }

                try:
                    # Bounded window parameter (1 minute to 24 hours)
                    window_minutes = max(1, min(window, 1440))
                    result = anomaly_mod.compute_anomaly_score(window_minutes)

                    # Add current observation to improve future scoring
                    anomaly_mod.add_observation()

                    # Structured logging
                    log_structured_metrics("/api/anomaly/score", result, 0)

                    return result
                except Exception as e:
                    return {"error": str(e), "enabled": True}

        if ANOMALY_ENABLED and ANOMALY_SKLEARN_ENABLED:
            # RBAC-gated anomaly training endpoint
            deps = []
            try:
                if rl is not None:
                    from fastapi import Depends  # type: ignore

                    # 2 requests per hour for training (resource intensive)
                    deps.append(
                        Depends(
                            rl.rate_limit_dependency(
                                "anomaly_train", max_calls=2, window_s=3600
                            )
                        )
                    )

                # Add RBAC dependency
                from fastapi import Depends  # type: ignore

                deps.append(Depends(admin_auth_dependency()))
            except Exception:
                deps = []

            @self.app.post("/api/admin/anomaly/train", dependencies=deps)
            def admin_anomaly_train() -> dict:
                """Train anomaly detection model (requires ANOMALY_ENABLED=1, ANOMALY_SKLEARN_ENABLED=1, and admin auth)."""
                if anomaly_mod is None:
                    return {
                        "error": "Anomaly detection module not available",
                        "enabled": False,
                    }

                try:
                    result = anomaly_mod.train_isolation_forest()

                    # Structured logging
                    log_structured_metrics("/api/admin/anomaly/train", result, 0)

                    return result
                except Exception as e:
                    return {"error": str(e), "enabled": True}

        # P2-002: Quarantine endpoints
        if QUARANTINE_ENABLED:
            # Quarantine file endpoint (RBAC + rate-limited)
            deps = []
            try:
                if rl is not None:
                    from fastapi import Depends  # type: ignore

                    # 10 quarantine operations per hour
                    deps.append(
                        Depends(
                            rl.rate_limit_dependency(
                                "quarantine_file", max_calls=10, window_s=3600
                            )
                        )
                    )

                # Add RBAC dependency
                from fastapi import Depends  # type: ignore

                deps.append(Depends(admin_auth_dependency()))
            except Exception:
                deps = []

            @self.app.post("/api/admin/quarantine", dependencies=deps)
            def admin_quarantine_file(path: str) -> dict:
                """Quarantine a file (requires QUARANTINE_ENABLED=1 and admin auth)."""
                if quarantine_mod is None:
                    return {
                        "error": "Quarantine module not available",
                        "enabled": False,
                    }

                try:
                    # Input validation
                    if not path or not isinstance(path, str):
                        return {"error": "Valid file path required", "enabled": True}

                    result = quarantine_mod.quarantine_file(path)

                    # Structured logging
                    log_structured_metrics(
                        "/api/admin/quarantine",
                        {"path": path, "result": result.get("status", "unknown")},
                        0,
                    )

                    return result
                except Exception as e:
                    return {"error": str(e), "enabled": True}

            # Restore file endpoint (RBAC + rate-limited)
            deps = []
            try:
                if rl is not None:
                    from fastapi import Depends  # type: ignore

                    # 10 restore operations per hour
                    deps.append(
                        Depends(
                            rl.rate_limit_dependency(
                                "quarantine_restore", max_calls=10, window_s=3600
                            )
                        )
                    )

                # Add RBAC dependency
                from fastapi import Depends  # type: ignore

                deps.append(Depends(admin_auth_dependency()))
            except Exception:
                deps = []

            @self.app.post("/api/admin/quarantine/restore", dependencies=deps)
            def admin_quarantine_restore(sha256: str, target_path: str = None) -> dict:
                """Restore a quarantined file (requires QUARANTINE_ENABLED=1 and admin auth)."""
                if quarantine_mod is None:
                    return {
                        "error": "Quarantine module not available",
                        "enabled": False,
                    }

                try:
                    # Input validation
                    if not sha256 or not isinstance(sha256, str):
                        return {"error": "Valid SHA256 hash required", "enabled": True}

                    # Validate SHA256 format (basic check)
                    if len(sha256) != 64 or not all(
                        c in "0123456789abcdefABCDEF" for c in sha256
                    ):
                        return {"error": "Invalid SHA256 format", "enabled": True}

                    result = quarantine_mod.restore_file(sha256.lower(), target_path)

                    # Structured logging
                    log_structured_metrics(
                        "/api/admin/quarantine/restore",
                        {"sha256": sha256, "result": result.get("status", "unknown")},
                        0,
                    )

                    return result
                except Exception as e:
                    return {"error": str(e), "enabled": True}

        # P2-003: Authentication endpoints (session-based)
        if CONSOLE_AUTH_ENABLED:
            # Define auth models
            class LoginRequest(BaseModel):
                username: str
                password: str

            class AuthResponse(BaseModel):
                status: str
                message: str = ""

            class UserInfoResponse(BaseModel):
                user: str

            # Login endpoint (rate limited)
            @rate_limited(
                lambda req: getattr(req, "client", {}).get("host", "unknown"),
                CONSOLE_AUTH_RATE_LIMIT,
                60,
            )  # 10 attempts per minute
            @self.app.post("/api/auth/login", response_model=AuthResponse)
            async def auth_login(
                login_data: LoginRequest, request: Request
            ) -> AuthResponse:
                """Authenticate user and create session (requires CONSOLE_AUTH_ENABLED=1)."""
                if auth_mod is None:
                    raise HTTPException(
                        status_code=503, detail="Auth module not available"
                    )

                try:
                    auth = auth_mod.get_auth()
                    if not auth.enabled:
                        raise HTTPException(
                            status_code=503, detail="Authentication not enabled"
                        )

                    # Validate credentials
                    if auth.authenticate_user(login_data.username, login_data.password):
                        # Create session token
                        session_token = auth.create_session(login_data.username)

                        # Create response with secure cookie
                        response = JSONResponse(
                            {"status": "ok", "message": "Authentication successful"}
                        )

                        cookie_config = auth.get_cookie_config()
                        response.set_cookie(
                            key=auth.cookie_name, value=session_token, **cookie_config
                        )

                        # Structured logging
                        log_structured_metrics(
                            "/api/auth/login",
                            {"username": login_data.username, "result": "success"},
                            0,
                        )

                        return response
                    else:
                        # Invalid credentials
                        log_structured_metrics(
                            "/api/auth/login",
                            {"username": login_data.username, "result": "failed"},
                            0,
                        )
                        raise HTTPException(
                            status_code=401, detail="Invalid credentials"
                        )

                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Login error: {e}")
                    raise HTTPException(status_code=500, detail="Authentication error")

            # Logout endpoint
            @self.app.post("/api/auth/logout", response_model=AuthResponse)
            async def auth_logout(request: Request) -> AuthResponse:
                """Clear session and logout user (requires CONSOLE_AUTH_ENABLED=1)."""
                if auth_mod is None:
                    raise HTTPException(
                        status_code=503, detail="Auth module not available"
                    )

                try:
                    auth = auth_mod.get_auth()
                    if not auth.enabled:
                        raise HTTPException(
                            status_code=503, detail="Authentication not enabled"
                        )

                    # Create response that clears the session cookie
                    response = JSONResponse(
                        {"status": "ok", "message": "Logout successful"}
                    )

                    # Clear session cookie
                    response.delete_cookie(key=auth.cookie_name)

                    # Structured logging
                    log_structured_metrics("/api/auth/logout", {"result": "success"}, 0)

                    return response

                except Exception as e:
                    logger.error(f"Logout error: {e}")
                    raise HTTPException(status_code=500, detail="Logout error")

            # Current user info endpoint
            @self.app.get("/api/auth/me", response_model=UserInfoResponse)
            async def auth_me(request: Request) -> UserInfoResponse:
                """Get current authenticated user info (requires CONSOLE_AUTH_ENABLED=1)."""
                if auth_mod is None:
                    raise HTTPException(
                        status_code=503, detail="Auth module not available"
                    )

                try:
                    auth = auth_mod.get_auth()
                    if not auth.enabled:
                        raise HTTPException(
                            status_code=503, detail="Authentication not enabled"
                        )

                    # Check session
                    username = auth_mod.get_session_user(request)
                    if not username:
                        raise HTTPException(status_code=401, detail="Not authenticated")

                    # Structured logging
                    log_structured_metrics(
                        "/api/auth/me", {"username": username, "result": "success"}, 0
                    )

                    return UserInfoResponse(user=username)

                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Auth me error: {e}")
                    raise HTTPException(status_code=500, detail="Authentication error")

        # P2-004: Server-Sent Events streaming endpoint
        if STREAM_ENABLED and STREAM_TYPE == "sse":
            # Connection rate limiter for SSE (per IP)
            _sse_connections: dict[str, int] = {}
            SSE_MAX_CONNECTIONS_PER_IP = 2

            @self.app.get("/api/stream/health")
            async def stream_health(request: Request):
                """Stream health metrics via Server-Sent Events (requires STREAM_ENABLED=1)."""

                # Get client IP for rate limiting
                client_ip = getattr(request, "client", {}).get("host", "unknown")

                # Check connection limit per IP
                current_connections = _sse_connections.get(client_ip, 0)
                if current_connections >= SSE_MAX_CONNECTIONS_PER_IP:
                    raise HTTPException(
                        status_code=429, detail="Too many concurrent connections"
                    )

                # Check authentication if required
                if STREAM_REQUIRE_AUTH and CONSOLE_AUTH_ENABLED and auth_mod:
                    username = auth_mod.get_session_user(request)
                    if not username:
                        raise HTTPException(
                            status_code=401,
                            detail="Authentication required for streaming",
                        )

                try:
                    # Import for streaming response
                    from fastapi.responses import StreamingResponse  # type: ignore
                    import asyncio
                    import json

                    async def event_generator():
                        # Increment connection count
                        _sse_connections[client_ip] = (
                            _sse_connections.get(client_ip, 0) + 1
                        )

                        try:
                            while True:
                                # Get current health metrics (reuse existing health endpoint logic)
                                try:
                                    health_data = (
                                        await self._get_composite_health_metrics()
                                    )

                                    # Format as SSE event
                                    event_data = {
                                        "timestamp": datetime.now(
                                            timezone.utc
                                        ).isoformat(),
                                        "event": "health_update",
                                        "data": health_data,
                                    }

                                    # SSE format: data: {json}\n\n
                                    sse_data = f"data: {json.dumps(event_data)}\n\n"
                                    yield sse_data.encode("utf-8")

                                except Exception as e:
                                    # Send error event
                                    error_event = {
                                        "timestamp": datetime.now(
                                            timezone.utc
                                        ).isoformat(),
                                        "event": "error",
                                        "data": {"error": str(e)},
                                    }
                                    error_sse = f"data: {json.dumps(error_event)}\n\n"
                                    yield error_sse.encode("utf-8")

                                # Wait for next interval
                                await asyncio.sleep(STREAM_HEALTH_INTERVAL_MS / 1000.0)

                        finally:
                            # Decrement connection count when done
                            if client_ip in _sse_connections:
                                _sse_connections[client_ip] = max(
                                    0, _sse_connections[client_ip] - 1
                                )
                                if _sse_connections[client_ip] == 0:
                                    del _sse_connections[client_ip]

                    # Return streaming response with proper headers
                    return StreamingResponse(
                        event_generator(),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "Access-Control-Allow-Origin": "*",  # CORS for browser clients
                            "Access-Control-Allow-Headers": "Cache-Control",
                        },
                    )

                except Exception as e:
                    logger.error(f"SSE streaming error: {e}")
                    raise HTTPException(status_code=500, detail="Streaming error")

        # Health check
        @self.app.get("/health")
        async def health_check() -> dict[str, str]:
            """Simple health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # P3-006: Telemetry export endpoint (default OFF)
        EXPORT_ENABLED = os.getenv("EXPORT_ENABLED", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if EXPORT_ENABLED:
            try:
                from console.telemetry_export import export_telemetry

                @self.app.get("/api/export/telemetry")
                async def telemetry_export(
                    format_type: str = "json",
                    include_system: bool = True,
                    include_security: bool = True,
                ) -> dict:
                    """Export telemetry data in various formats (requires EXPORT_ENABLED=1)."""
                    try:
                        if format_type not in ["json", "prometheus", "csv"]:
                            raise HTTPException(
                                status_code=400,
                                detail="Unsupported format. Use json, prometheus, or csv",
                            )

                        result = export_telemetry(
                            format_type=format_type,
                            include_system=include_system,
                            include_security=include_security,
                        )

                        # Set appropriate content type
                        if format_type == "prometheus":
                            from fastapi.responses import PlainTextResponse

                            return PlainTextResponse(result, media_type="text/plain")
                        elif format_type == "csv":
                            from fastapi.responses import PlainTextResponse

                            return PlainTextResponse(result, media_type="text/csv")
                        else:
                            return JSONResponse(json.loads(result))

                    except ValueError as e:
                        raise HTTPException(status_code=400, detail=str(e))
                    except Exception as e:
                        logger.error(f"Telemetry export error: {e}")
                        raise HTTPException(status_code=500, detail="Export failed")

            except ImportError:
                logger.warning("Telemetry export module not available")

        # P3-005: Plugin management endpoints (default OFF)
        PLUGINS_ENABLED = os.getenv("PLUGINS_ENABLED", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if PLUGINS_ENABLED and ADMIN_AUTH_ENABLED:
            try:
                from console.plugin_sandbox import (
                    get_plugin_loader,
                    execute_plugin_hook,
                )

                deps = []
                try:
                    # Add RBAC dependency for admin routes
                    from fastapi import Depends  # type: ignore

                    deps.append(Depends(admin_auth_dependency()))
                except Exception:
                    deps = []

                @self.app.get("/api/admin/plugins", dependencies=deps)
                async def plugins_list() -> dict:
                    """List all loaded plugins (requires PLUGINS_ENABLED=1 and admin auth)."""
                    try:
                        loader = get_plugin_loader()
                        plugins_info = {}

                        for name, plugin in loader.loaded_plugins.items():
                            if hasattr(plugin, "get_info"):
                                info = plugin.get_info()
                            else:
                                info = {"name": name, "status": "loaded"}
                            plugins_info[name] = info

                        return {
                            "enabled": True,
                            "loaded_count": len(plugins_info),
                            "plugins": plugins_info,
                        }

                    except Exception as e:
                        logger.error(f"Plugin list error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Failed to list plugins"
                        )

                @self.app.post("/api/admin/plugins/execute", dependencies=deps)
                async def plugins_execute(
                    hook_name: str, event_data: dict = None
                ) -> dict:
                    """Execute plugin hook (requires PLUGINS_ENABLED=1 and admin auth)."""
                    try:
                        if not hook_name:
                            raise HTTPException(
                                status_code=400, detail="Hook name required"
                            )

                        if event_data is None:
                            event_data = {}

                        results = execute_plugin_hook(hook_name, event_data)

                        return {
                            "hook": hook_name,
                            "results": results,
                            "executed_count": len(results),
                        }

                    except Exception as e:
                        logger.error(f"Plugin execution error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Plugin execution failed"
                        )

            except ImportError:
                logger.warning("Plugin sandbox module not available")

        # P3-004: Preflight checks endpoint (admin only)
        if ADMIN_AUTH_ENABLED:
            try:
                from console.preflight_checks import run_preflight_checks

                deps = []
                try:
                    # Add RBAC dependency for admin routes
                    from fastapi import Depends  # type: ignore

                    deps.append(Depends(admin_auth_dependency()))
                except Exception:
                    deps = []

                @self.app.get("/api/admin/preflight", dependencies=deps)
                async def preflight_checks() -> dict:
                    """Run preflight checks (requires admin auth)."""
                    try:
                        summary = run_preflight_checks(verbose=False)

                        # Convert to dict for JSON serialization
                        from dataclasses import asdict

                        return asdict(summary)

                    except Exception as e:
                        logger.error(f"Preflight checks error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Preflight checks failed"
                        )

            except ImportError:
                logger.warning("Preflight checks module not available")

        # P4-001: Backup & Restore endpoints (default OFF)
        BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if BACKUP_ENABLED and ADMIN_AUTH_ENABLED:
            try:
                from console.backup_restore import create_backup, restore_backup

                deps = []
                try:
                    from fastapi import Depends  # type: ignore

                    deps.append(Depends(admin_auth_dependency()))
                except Exception:
                    deps = []

                @self.app.post("/api/admin/backup", dependencies=deps)
                async def backup_create() -> dict:
                    """Create system backup (requires BACKUP_ENABLED=1 and admin auth)."""
                    try:
                        result = create_backup()
                        return result
                    except Exception as e:
                        logger.error(f"Backup creation error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Backup creation failed"
                        )

                @self.app.post("/api/admin/restore", dependencies=deps)
                async def backup_restore(
                    backup_path: str, confirm: bool = False
                ) -> dict:
                    """Restore from backup (requires BACKUP_ENABLED=1 and admin auth)."""
                    try:
                        result = restore_backup(backup_path, confirm)
                        return result
                    except Exception as e:
                        logger.error(f"Backup restore error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Backup restore failed"
                        )

            except ImportError:
                logger.warning("Backup/restore module not available")

        # P4-002: Secret Rotation endpoints (default OFF)
        ROTATE_ENABLED = os.getenv("ROTATE_ENABLED", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if ROTATE_ENABLED and ADMIN_AUTH_ENABLED:
            try:
                from tools.rotate_secrets import (
                    rotate_secrets_preview,
                    rotate_secrets_execute,
                )

                deps = []
                try:
                    from fastapi import Depends  # type: ignore

                    deps.append(Depends(admin_auth_dependency()))
                except Exception:
                    deps = []

                @self.app.post("/api/admin/rotate/preview", dependencies=deps)
                async def secrets_rotate_preview() -> dict:
                    """Preview secret rotation (requires ROTATE_ENABLED=1 and admin auth)."""
                    try:
                        result = rotate_secrets_preview()
                        return result
                    except Exception as e:
                        logger.error(f"Secret rotation preview error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Secret rotation preview failed"
                        )

                @self.app.post("/api/admin/rotate/execute", dependencies=deps)
                async def secrets_rotate_execute() -> dict:
                    """Execute secret rotation (requires ROTATE_ENABLED=1 and admin auth)."""
                    try:
                        result = rotate_secrets_execute()
                        return result
                    except Exception as e:
                        logger.error(f"Secret rotation execution error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Secret rotation failed"
                        )

            except ImportError:
                logger.warning("Secret rotation module not available")

        # P4-004: Chaos Engineering endpoints (default OFF)
        CHAOS_ENABLED = os.getenv("CHAOS_ENABLED", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if CHAOS_ENABLED and ADMIN_AUTH_ENABLED:
            try:
                from console.chaos_probes import get_chaos_manager

                deps = []
                try:
                    from fastapi import Depends  # type: ignore

                    deps.append(Depends(admin_auth_dependency()))
                except Exception:
                    deps = []

                @self.app.post("/api/admin/chaos/inject", dependencies=deps)
                async def chaos_inject_endpoint(mode: str, ms: int = None) -> dict:
                    """Inject chaos (requires CHAOS_ENABLED=1 and admin auth)."""
                    try:
                        manager = get_chaos_manager()
                        kwargs = {"ms": ms} if ms is not None else {}
                        result = manager.inject_chaos(mode, **kwargs)
                        return result
                    except Exception as e:
                        logger.error(f"Chaos injection error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Chaos injection failed"
                        )

                @self.app.get("/api/admin/chaos/status", dependencies=deps)
                async def chaos_status() -> dict:
                    """Get chaos probe status (requires CHAOS_ENABLED=1 and admin auth)."""
                    try:
                        manager = get_chaos_manager()
                        result = manager.get_probe_status()
                        return result
                    except Exception as e:
                        logger.error(f"Chaos status error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Chaos status check failed"
                        )

            except ImportError:
                logger.warning("Chaos probes module not available")

        # P5-002: Data Retention endpoints (default OFF)
        RETENTION_ENABLED = os.getenv("RETENTION_ENABLED", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if RETENTION_ENABLED and ADMIN_AUTH_ENABLED:
            try:
                from console.retention import run_retention_job, get_directory_stats

                deps = []
                try:
                    from fastapi import Depends, Query  # type: ignore

                    deps.append(Depends(admin_auth_dependency()))
                except Exception:
                    deps = []

                @self.app.post("/api/admin/retention/run", dependencies=deps)
                async def retention_run_endpoint(
                    dry: bool = Query(True, description="Dry run mode (default: true)"),
                    retention_days: Optional[int] = Query(
                        None, description="Override retention days"
                    ),
                ) -> dict:
                    """Run data retention job (requires RETENTION_ENABLED=1 and admin auth)."""
                    try:
                        result = run_retention_job(
                            dry_run=dry, retention_days=retention_days
                        )
                        log_structured_metrics(
                            "retention_run",
                            {
                                "dry_run": dry,
                                "retention_days": retention_days
                                or result.get("retention_days", 0),
                            },
                            int(time.time()),
                        )
                        return {"status": "ok", **result}
                    except Exception as e:
                        logger.error(f"Retention job error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Retention job failed"
                        )

                @self.app.get("/api/admin/retention/stats", dependencies=deps)
                async def retention_stats_endpoint() -> dict:
                    """Get retention directory statistics (requires RETENTION_ENABLED=1 and admin auth)."""
                    try:
                        stats = get_directory_stats()
                        return {"status": "ok", **stats}
                    except Exception as e:
                        logger.error(f"Retention stats error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Failed to get retention stats"
                        )

            except ImportError:
                logger.warning("Retention module not available")

        # P5-005: Performance Smoke & Concurrency Probe (default OFF)
        PERF_PROBE_ENABLED = os.getenv("PERF_PROBE_ENABLED", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if PERF_PROBE_ENABLED and ADMIN_AUTH_ENABLED:
            try:
                from console.perf_probe import (
                    get_performance_probe,
                    run_basic_performance_check,
                )

                deps = []
                try:
                    from fastapi import Depends, Query  # type: ignore

                    deps.append(Depends(admin_auth_dependency()))
                except Exception:
                    deps = []

                @self.app.post("/api/admin/perf/probe", dependencies=deps)
                async def perf_probe_endpoint(
                    clients: int = Query(
                        10, description="Number of concurrent clients", ge=1, le=50
                    ),
                    duration_s: float = Query(
                        5.0, description="Test duration in seconds", ge=0.1, le=60.0
                    ),
                    endpoint: str = Query(
                        "/api/metrics/health", description="Endpoint to test"
                    ),
                ) -> dict:
                    """Run performance probe test (requires PERF_PROBE_ENABLED=1 and admin auth)."""
                    try:
                        # Validate endpoint
                        if not endpoint.startswith("/"):
                            endpoint = "/" + endpoint

                        # Create probe and run test
                        probe = get_performance_probe(f"http://{self.host}:{self.port}")
                        result = probe.generate_load_test_report(
                            endpoint=endpoint,
                            clients=clients,
                            duration_seconds=duration_s,
                        )

                        # Log performance metrics
                        metrics = result.get("load_test", {}).get("metrics", {})
                        log_structured_metrics(
                            "perf_probe",
                            {
                                "endpoint": endpoint,
                                "clients": clients,
                                "duration_s": duration_s,
                                "rps": metrics.get("requests_per_second", 0),
                                "success_rate": metrics.get("success_rate", 0),
                            },
                            int(time.time()),
                        )

                        return {"status": "ok", **result}

                    except Exception as e:
                        logger.error(f"Performance probe error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Performance probe failed"
                        )

                @self.app.get("/api/admin/perf/quick", dependencies=deps)
                async def perf_quick_check() -> dict:
                    """Run quick performance check (requires PERF_PROBE_ENABLED=1 and admin auth)."""
                    try:
                        result = run_basic_performance_check(
                            f"http://{self.host}:{self.port}"
                        )
                        return {"status": "ok", **result}
                    except Exception as e:
                        logger.error(f"Quick performance check error: {e}")
                        raise HTTPException(
                            status_code=500, detail="Quick performance check failed"
                        )

            except ImportError:
                logger.warning("Performance probe module not available")

        # P4-006: Console UI setup (default OFF)
        CONSOLE_UI_ENABLED = os.getenv("CONSOLE_UI_ENABLED", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if CONSOLE_UI_ENABLED:
            try:
                from console.console_ui import setup_console_routes

                setup_console_routes(self.app)
            except ImportError:
                logger.warning("Console UI module not available")

    async def _get_composite_health_metrics(self) -> dict:
        """Get composite health metrics for streaming (helper for SSE)."""
        try:
            # Reuse existing health endpoint logic
            if not self.sentinel_service:
                return {"status": "error", "message": "Service not available"}

            # Get basic health info
            health_info = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "healthy",
                "uptime_seconds": int(
                    time.time()
                    - getattr(self.sentinel_service, "start_time", time.time())
                ),
                "service_status": "running",
            }

            # Add event bus metrics if available
            try:
                from core.bus import get_event_bus

                bus = get_event_bus()
                if hasattr(bus, "get_observability_metrics"):
                    bus_metrics = bus.get_observability_metrics()
                    health_info["event_bus"] = bus_metrics
            except Exception:
                health_info["event_bus"] = {"status": "unavailable"}

            # Add service component metrics if available
            if hasattr(self.sentinel_service, "get_health_status"):
                try:
                    service_health = self.sentinel_service.get_health_status()
                    health_info.update(service_health)
                except Exception:
                    pass

            return health_info

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def start(self) -> None:
        """Start the web API server."""
        if self.server_task:
            logger.warning("Web API server already running")
            return

        try:
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=False,  # Disable access logs to reduce noise
            )
            self.server = uvicorn.Server(config)

            # Run server in background task
            self.server_task = asyncio.create_task(self.server.serve())
            logger.info(f"Web API server started on http://{self.host}:{self.port}")

            # Start config hot reload (no-op if disabled)
            from core.config import start_hot_reload

            start_hot_reload()

        except Exception as e:
            logger.error(f"Failed to start web API server: {e}")
            raise

    async def stop(self) -> None:
        """Stop the web API server."""
        if not self.server_task:
            return

        try:
            if self.server:
                self.server.should_exit = True

            if self.server_task:
                self.server_task.cancel()
                try:
                    await self.server_task
                except asyncio.CancelledError:
                    pass
                self.server_task = None

            # Stop config hot reload
            from core.config import stop_hot_reload

            stop_hot_reload()

            logger.info("Web API server stopped")

        except Exception as e:
            logger.error(f"Error stopping web API server: {e}")

    def get_base_url(self) -> str:
        """Get base URL for the web interface."""
        return f"http://{self.host}:{self.port}"
