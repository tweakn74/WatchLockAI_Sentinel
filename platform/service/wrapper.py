"""Windows service wrapper for WatchLockAI Sentinel using pywin32."""

from __future__ import annotations

import asyncio
import os
import sys
import threading
import time
from pathlib import Path

from loguru import logger

# Import our main application components
from core.bus import initialize_event_bus, shutdown_event_bus
from core.config import load_config
from core.logging import setup_logging
from detection.knowledge.loader import KnowledgeLoader

# Platform check: Windows service operations only available on Windows
IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    try:
        import servicemanager
        import win32event
        import win32service
        import win32serviceutil

        WINDOWS_SERVICE_AVAILABLE = True
    except ImportError:
        logger.warning("Windows service APIs not available (pywin32 not installed)")
        WINDOWS_SERVICE_AVAILABLE = False
else:
    logger.info("Windows service APIs not available on non-Windows platforms")
    WINDOWS_SERVICE_AVAILABLE = False

try:
    from console.web_api import SentinelWebAPI

    WEB_API_AVAILABLE = True
except ImportError:
    logger.warning("Web API not available (FastAPI dependencies not installed)")
    WEB_API_AVAILABLE = False


class SentinelService:
    """Core Sentinel service logic (service-independent)."""

    def __init__(self, config_path: str | None = None) -> None:
        """Initialize Sentinel service.

        Args:
            config_path: Path to configuration file.
        """
        self.config_path = config_path
        self.config = None
        self.event_bus = None
        self.knowledge_loader = None

        # Component managers
        self.collectors = {}
        self.rules_engine = None
        self.alert_manager = None
        self.actions_manager = None

        # Web API
        self.web_api = None

        # Runtime state
        self.running = False
        self.startup_time = None

        # Config reload infrastructure
        self._reload_lock = threading.Lock()
        self._reload_timer = None  # type: ignore[assignment]
        self._last_reload_at = 0.0

    async def initialize(self) -> None:
        """Initialize all Sentinel components."""
        try:
            logger.info("Initializing WatchLockAI Sentinel...")

            # Load configuration
            self.config = load_config(self.config_path)
            logger.info("Configuration loaded")

            # Setup logging
            log_handlers = setup_logging(
                log_level="INFO",
                log_dir="logs",
                enable_console=False,  # Disable console for service
                enable_file=True,
                enable_jsonl_events=True,
                enable_jsonl_alerts=True,
            )
            logger.info(f"Logging configured: {list(log_handlers.keys())}")

            # Initialize event bus
            self.event_bus = await initialize_event_bus()
            logger.info("Event bus initialized")

            # Wire MITRE ATT&CK engine (import-safe, default-OFF)
            try:
                from detection.attack_matrix import wire as wire_attack_matrix
                from response.playbooks import Playbooks
            except Exception:  # import-safe
                wire_attack_matrix = None
                Playbooks = None

            def _mode_provider():
                # return current operational mode string (e.g., "observe","alert","contain","quarantine","offline")
                return getattr(self, "operational_mode", "observe")

            if wire_attack_matrix and os.getenv("MITRE_MATRIX_ENABLED", "0") == "1":
                responder = (
                    Playbooks(self.event_bus, _mode_provider)
                    if (Playbooks and os.getenv("MITRE_REACTIVE_ENABLED", "0") == "1")
                    else None
                )
                profile = os.getenv("MITRE_PROFILE", "baseline")
                wire_attack_matrix(
                    self.event_bus, responder, rules=None, profile=profile
                )
                logger.info(f"MITRE ATT&CK engine wired with profile: {profile}")

            # Initialize knowledge loader and build index
            self.knowledge_loader = KnowledgeLoader()
            stats = self.knowledge_loader.rebuild_index()
            logger.info(f"Knowledge index built: {stats}")

            # Import and initialize components
            await self._initialize_collectors()
            await self._initialize_detection_engine()
            await self._initialize_response_managers()
            await self._initialize_web_api()

            self.startup_time = time.time()
            logger.info("Sentinel service initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize Sentinel service: {e}")
            raise

    async def _initialize_collectors(self) -> None:
        """Initialize all monitoring collectors."""
        from platform.collectors.filesystem import FileSystemMonitor
        from platform.collectors.health import HealthMonitor
        from platform.collectors.network import NetworkMonitor
        from platform.collectors.process import ProcessMonitor
        from platform.collectors.registry import RegistryMonitor

        # File system monitor
        if self.config.monitoring.file_system.enabled:
            self.collectors["fs"] = FileSystemMonitor(
                self.config.monitoring.file_system,
                self.event_bus,
            )
            await self.collectors["fs"].start()
            logger.info("File system monitor started")

        # Process monitor
        if self.config.monitoring.processes.enabled:
            self.collectors["proc"] = ProcessMonitor(
                self.config.monitoring.processes,
                self.event_bus,
            )
            await self.collectors["proc"].start()
            logger.info("Process monitor started")

        # Registry monitor
        if self.config.monitoring.registry.enabled:
            self.collectors["reg"] = RegistryMonitor(
                self.config.monitoring.registry,
                self.event_bus,
            )
            await self.collectors["reg"].start()
            logger.info("Registry monitor started")

        # Network monitor
        if self.config.monitoring.network.enabled:
            self.collectors["net"] = NetworkMonitor(
                self.config.monitoring.network,
                self.event_bus,
            )
            await self.collectors["net"].start()
            logger.info("Network monitor started")

        # Health monitor
        if self.config.health.enabled:
            self.collectors["health"] = HealthMonitor(
                self.config.health,
                self.event_bus,
            )
            await self.collectors["health"].start()
            logger.info("Health monitor started")

    async def _initialize_detection_engine(self) -> None:
        """Initialize detection rules engine."""
        from detection.rules_engine import RulesEngine

        # Get process monitor for ancestry lookups
        process_monitor = self.collectors.get("proc")

        self.rules_engine = RulesEngine(
            self.event_bus,
            self.knowledge_loader,
            process_monitor,
        )
        await self.rules_engine.start()
        logger.info("Rules engine started")

    async def _initialize_response_managers(self) -> None:
        """Initialize response and alerting managers."""
        from response.actions import ResponseActionsManager
        from response.alerts import AlertManager

        # Actions manager
        self.actions_manager = ResponseActionsManager(
            self.config.responses, self.config.operational
        )
        logger.info("Actions manager initialized")

        # Alert manager
        self.alert_manager = AlertManager(self.config.alerts, self.event_bus)
        await self.alert_manager.start()
        logger.info("Alert manager started")

    async def _initialize_web_api(self) -> None:
        """Initialize web API interface."""
        if not WEB_API_AVAILABLE:
            logger.warning("Web API disabled: dependencies not available")
            return

        try:
            # Initialize web API with local-only binding
            self.web_api = SentinelWebAPI(
                sentinel_service=self, host="127.0.0.1", port=8080
            )
            await self.web_api.start()
            logger.info(f"Web API started: {self.web_api.get_base_url()}")
        except Exception as e:
            logger.error(f"Failed to start web API: {e}")
            self.web_api = None

    async def start(self) -> None:
        """Start the Sentinel service."""
        if self.running:
            logger.warning("Sentinel service already running")
            return

        await self.initialize()
        self.running = True
        logger.info("WatchLockAI Sentinel service started")

    async def stop(self) -> None:
        """Stop the Sentinel service."""
        if not self.running:
            return

        logger.info("Stopping WatchLockAI Sentinel service...")
        self.running = False

        try:
            # Stop web API
            if self.web_api:
                await self.web_api.stop()
                logger.info("Web API stopped")

            # Stop response managers
            if self.alert_manager:
                await self.alert_manager.stop()
                logger.info("Alert manager stopped")

            # Stop detection engine
            if self.rules_engine:
                await self.rules_engine.stop()
                logger.info("Rules engine stopped")

            # Stop collectors
            for name, collector in self.collectors.items():
                await collector.stop()
                logger.info(f"{name} monitor stopped")

            # Shutdown event bus
            await shutdown_event_bus()
            logger.info("Event bus stopped")

            logger.info("WatchLockAI Sentinel service stopped")

        except Exception as e:
            logger.error(f"Error stopping Sentinel service: {e}")

    async def run_forever(self) -> None:
        """Run service until stopped."""
        await self.start()

        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Service run loop cancelled")
        finally:
            await self.stop()

    def get_status(self) -> dict:
        """Get service status information."""
        uptime = time.time() - self.startup_time if self.startup_time else 0

        return {
            "running": self.running,
            "uptime_seconds": uptime,
            "collectors": {
                name: collector.get_stats()
                for name, collector in self.collectors.items()
            },
            "rules_engine": self.rules_engine.get_stats() if self.rules_engine else {},
            "event_bus": self.event_bus.get_stats() if self.event_bus else {},
        }

    @property
    def uptime_seconds(self) -> float:
        """Get service uptime in seconds."""
        return time.time() - self.startup_time if self.startup_time else 0

    def trigger_config_reload(self, debounce_ms: int = 750) -> None:
        """Schedule a non-blocking, debounced config reload."""
        with self._reload_lock:
            try:
                if self._reload_timer is not None:
                    self._reload_timer.cancel()
            except Exception:
                pass
            delay_s = max(0, int(debounce_ms) / 1000.0)
            self._reload_timer = threading.Timer(delay_s, self._do_config_reload)
            self._reload_timer.daemon = True
            self._reload_timer.start()

    def _do_config_reload(self) -> None:
        """Perform the config reload safely and idempotently."""
        now = time.time()
        with self._reload_lock:
            self._last_reload_at = now
        # Call any existing config load function if present; otherwise no-op.
        reload_fn = getattr(self, "reload_config", None) or getattr(
            self, "load_config", None
        )
        if callable(reload_fn):
            try:
                reload_fn()  # type: ignore[misc]
            except Exception:
                # Swallow errors to keep this non-fatal; logging handled by existing logger if present.
                pass


if WINDOWS_SERVICE_AVAILABLE:

    class WatchLockAISentinelService(win32serviceutil.ServiceFramework):
        """Windows service wrapper for WatchLockAI Sentinel."""

        _svc_name_ = "WatchLockAISentinel"
        _svc_display_name_ = "WatchLockAI Sentinel"
        _svc_description_ = "Host security monitoring with RAG-backed detection"

        def __init__(self, args) -> None:
            """Initialize Windows service."""
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.sentinel_service = None
            self.service_thread = None

        def SvcStop(self) -> None:
            """Handle service stop request."""
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

            # Signal stop event
            win32event.SetEvent(self.hWaitStop)

            # Stop Sentinel service
            if self.sentinel_service:
                asyncio.run(self.sentinel_service.stop())

            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, ""),
            )

        def SvcDoRun(self) -> None:
            """Main service execution."""
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )

            try:
                # Initialize Sentinel service
                self.sentinel_service = SentinelService()

                # Run in asyncio event loop
                asyncio.run(self._run_service())

            except Exception as e:
                servicemanager.LogErrorMsg(f"Service error: {e}")

        async def _run_service(self) -> None:
            """Run Sentinel service in async context."""
            try:
                # Start Sentinel
                await self.sentinel_service.start()

                # Wait for stop signal
                while True:
                    # Check if stop was requested
                    if (
                        win32event.WaitForSingleObject(self.hWaitStop, 1000)
                        == win32event.WAIT_OBJECT_0
                    ):
                        break

                    # Keep event loop alive
                    await asyncio.sleep(0.1)

            finally:
                if self.sentinel_service:
                    await self.sentinel_service.stop()


def install_service() -> bool:
    """Install the Windows service."""
    if not IS_WINDOWS:
        print("Error: Windows service installation not available on this platform")
        return False

    if not WINDOWS_SERVICE_AVAILABLE:
        print("Error: Windows service APIs not available")
        return False

    try:
        # Ensure we have the service script
        service_script = Path(__file__).absolute()

        win32serviceutil.InstallService(
            serviceClassString=f"{service_script.stem}.WatchLockAISentinelService",
            serviceName="WatchLockAISentinel",
            displayName="WatchLockAI Sentinel",
            description="Host security monitoring with RAG-backed detection",
            startType=win32service.SERVICE_AUTO_START,
        )

        print("WatchLockAI Sentinel service installed successfully")
        return True

    except Exception as e:
        print(f"Failed to install service: {e}")
        return False


def uninstall_service() -> bool:
    """Uninstall the Windows service."""
    if not IS_WINDOWS:
        print("Error: Windows service uninstallation not available on this platform")
        return False

    if not WINDOWS_SERVICE_AVAILABLE:
        print("Error: Windows service APIs not available")
        return False

    try:
        win32serviceutil.RemoveService("WatchLockAISentinel")
        print("WatchLockAI Sentinel service uninstalled successfully")
        return True

    except Exception as e:
        print(f"Failed to uninstall service: {e}")
        return False


def start_service() -> bool:
    """Start the Windows service."""
    if not IS_WINDOWS:
        print("Error: Windows service start not available on this platform")
        return False

    if not WINDOWS_SERVICE_AVAILABLE:
        print("Error: Windows service APIs not available")
        return False

    try:
        win32serviceutil.StartService("WatchLockAISentinel")
        print("WatchLockAI Sentinel service started")
        return True

    except Exception as e:
        print(f"Failed to start service: {e}")
        return False


def stop_service() -> bool:
    """Stop the Windows service."""
    if not IS_WINDOWS:
        print("Error: Windows service stop not available on this platform")
        return False

    if not WINDOWS_SERVICE_AVAILABLE:
        print("Error: Windows service APIs not available")
        return False

    try:
        win32serviceutil.StopService("WatchLockAISentinel")
        print("WatchLockAI Sentinel service stopped")
        return True

    except Exception as e:
        print(f"Failed to stop service: {e}")
        return False


def run_interactive() -> bool:
    """Run Sentinel interactively (non-service mode)."""
    print("Starting WatchLockAI Sentinel in interactive mode...")

    try:
        # Create service instance
        sentinel = SentinelService()

        # Run until KeyboardInterrupt
        asyncio.run(sentinel.run_forever())

    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error running Sentinel: {e}")
        return False

    return True


def main() -> int:
    """Main entry point for service control."""
    if len(sys.argv) == 1:
        # No arguments - try to run as service
        if WINDOWS_SERVICE_AVAILABLE:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(WatchLockAISentinelService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            print(
                "Windows service APIs not available. Use --interactive to run directly."
            )
            return 1

    elif len(sys.argv) == 2:
        command = sys.argv[1].lower()

        if command == "install":
            success = install_service()
            return 0 if success else 1

        elif command == "uninstall":
            success = uninstall_service()
            return 0 if success else 1

        elif command == "start":
            success = start_service()
            return 0 if success else 1

        elif command == "stop":
            success = stop_service()
            return 0 if success else 1

        elif command == "--interactive":
            success = run_interactive()
            return 0 if success else 1

        elif command == "--debug":
            # Debug mode - interactive with debug logging
            os.environ["SENTINEL_LOG_LEVEL"] = "DEBUG"
            success = run_interactive()
            return 0 if success else 1

        else:
            print("Unknown command. Usage:")
            print("  service_wrapper.py install    - Install Windows service")
            print("  service_wrapper.py uninstall  - Uninstall Windows service")
            print("  service_wrapper.py start      - Start Windows service")
            print("  service_wrapper.py stop       - Stop Windows service")
            print("  service_wrapper.py --interactive - Run interactively")
            print("  service_wrapper.py --debug    - Run with debug logging")
            return 1

    else:
        print("Too many arguments")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
