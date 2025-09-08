"""Response Actions system implementing actions.md specifications."""

from __future__ import annotations

import asyncio
import sys
import time
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

import psutil
from loguru import logger

if TYPE_CHECKING:
    from app_core.config import OperationalConfig, ResponsesConfig

# Platform check: Some operations have platform-specific behaviors
IS_WINDOWS = sys.platform.startswith('win')


class ActionResult(str, Enum):
    """Action execution results."""
    SUCCESS = "success"
    FAILED = "failed"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    ALREADY_DONE = "already_done"


class ActionType(str, Enum):
    """Types of response actions."""
    TERMINATE_PROCESS = "terminate_process"
    PAUSE_MONITORING = "pause_monitoring"
    QUARANTINE_DIRECTORY = "quarantine_directory"  # STUB ONLY


class ActionRecord:
    """Record of executed action with metadata."""

    def __init__(
        self,
        action_type: ActionType,
        parameters: dict[str, Any],
        result: ActionResult,
        message: str,
        user_consent: bool = False,
    ) -> None:
        """Initialize action record.

        Args:
            action_type: Type of action executed.
            parameters: Action parameters.
            result: Execution result.
            message: Result message.
            user_consent: Whether user provided explicit consent.
        """
        self.action_type = action_type
        self.parameters = parameters
        self.result = result
        self.message = message
        self.user_consent = user_consent
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.execution_time_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging.

        Returns:
            Dictionary representation of action record.
        """
        return {
            "action_type": self.action_type.value,
            "parameters": self.parameters,
            "result": self.result.value,
            "message": self.message,
            "user_consent": self.user_consent,
            "timestamp": self.timestamp,
            "execution_time_ms": self.execution_time_ms,
        }


class ProcessTerminator:
    """Handler for process termination actions."""

    @staticmethod
    def terminate_process(pid: int, force: bool = False) -> ActionRecord:
        """Terminate a process by PID.

        Args:
            pid: Process ID to terminate.
            force: Whether to force termination.

        Returns:
            ActionRecord with execution result.
        """
        start_time = time.time()
        parameters = {"pid": pid, "force": force}

        try:
            # Check if process exists
            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                # Get executable path with platform-aware error handling (for logging purposes)
                try:
                    _ = proc.exe() if hasattr(proc, "exe") else "Unknown"
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass  # Not critical for the operation
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return ActionRecord(
                    ActionType.TERMINATE_PROCESS,
                    parameters,
                    ActionResult.NOT_FOUND,
                    f"Process {pid} not found or access denied",
                )

            # Attempt termination with platform-aware approach
            try:
                if force:
                    proc.kill()  # SIGKILL on Unix, TerminateProcess on Windows
                    method = "kill"
                else:
                    proc.terminate()  # SIGTERM on Unix, graceful termination on Windows
                    method = "terminate"
            except psutil.AccessDenied:
                # Platform-specific error handling
                if IS_WINDOWS:
                    error_msg = f"Access denied when terminating process {pid}. May require admin privileges on Windows."
                else:
                    error_msg = f"Access denied when terminating process {pid}. Check permissions."
                    
                return ActionRecord(
                    ActionType.TERMINATE_PROCESS,
                    parameters,
                    ActionResult.UNAUTHORIZED,
                    error_msg,
                )

            # Wait for process to exit with platform-aware timeout
            try:
                timeout = 10 if IS_WINDOWS else 5  # Windows may need more time
                proc.wait(timeout=timeout)
                execution_time = (time.time() - start_time) * 1000

                record = ActionRecord(
                    ActionType.TERMINATE_PROCESS,
                    parameters,
                    ActionResult.SUCCESS,
                    f"Process {pid} ({proc_name}) terminated successfully using {method}",
                )
                record.execution_time_ms = execution_time

                logger.info(f"Process terminated: PID={pid}, name={proc_name}, method={method}, platform={'Windows' if IS_WINDOWS else 'Unix'}")
                return record

            except psutil.TimeoutExpired:
                timeout_msg = f"Process {pid} did not terminate within {timeout}s timeout ({'Windows' if IS_WINDOWS else 'Unix'} platform)"
                return ActionRecord(
                    ActionType.TERMINATE_PROCESS,
                    parameters,
                    ActionResult.FAILED,
                    timeout_msg,
                )

        except psutil.AccessDenied:
            return ActionRecord(
                ActionType.TERMINATE_PROCESS,
                parameters,
                ActionResult.UNAUTHORIZED,
                f"Access denied when terminating process {pid}",
            )
        except Exception as e:
            return ActionRecord(
                ActionType.TERMINATE_PROCESS,
                parameters,
                ActionResult.FAILED,
                f"Error terminating process {pid}: {e!s}",
            )


class MonitoringController:
    """Handler for monitoring control actions."""

    def __init__(self) -> None:
        """Initialize monitoring controller."""
        self._pause_until: float | None = None
        self._pause_task: asyncio.Task | None = None

    def pause_monitoring(self, duration_seconds: int) -> ActionRecord:
        """Pause monitoring for specified duration.

        Args:
            duration_seconds: Duration to pause monitoring.

        Returns:
            ActionRecord with execution result.
        """
        start_time = time.time()
        parameters = {"duration_seconds": duration_seconds}

        try:
            if duration_seconds <= 0:
                return ActionRecord(
                    ActionType.PAUSE_MONITORING,
                    parameters,
                    ActionResult.FAILED,
                    "Duration must be positive",
                )

            # Set pause time
            self._pause_until = time.time() + duration_seconds

            execution_time = (time.time() - start_time) * 1000

            record = ActionRecord(
                ActionType.PAUSE_MONITORING,
                parameters,
                ActionResult.SUCCESS,
                f"Monitoring paused for {duration_seconds} seconds",
            )
            record.execution_time_ms = execution_time

            logger.info(f"Monitoring paused for {duration_seconds} seconds")

            # Schedule automatic resume
            if self._pause_task:
                self._pause_task.cancel()

            self._pause_task = asyncio.create_task(self._auto_resume(duration_seconds))

            return record

        except Exception as e:
            return ActionRecord(
                ActionType.PAUSE_MONITORING,
                parameters,
                ActionResult.FAILED,
                f"Error pausing monitoring: {e!s}",
            )

    async def _auto_resume(self, duration: int) -> None:
        """Automatically resume monitoring after duration.

        Args:
            duration: Pause duration in seconds.
        """
        try:
            await asyncio.sleep(duration)
            self._pause_until = None
            logger.info("Monitoring automatically resumed")
        except asyncio.CancelledError:
            logger.debug("Auto-resume task cancelled")

    def is_paused(self) -> bool:
        """Check if monitoring is currently paused.

        Returns:
            True if monitoring is paused.
        """
        if self._pause_until is None:
            return False

        if time.time() >= self._pause_until:
            self._pause_until = None
            return False

        return True

    def get_pause_remaining(self) -> int | None:
        """Get remaining pause time in seconds.

        Returns:
            Remaining pause time, or None if not paused.
        """
        if not self.is_paused() or self._pause_until is None:
            return None

        remaining = self._pause_until - time.time()
        return max(0, int(remaining))

    def resume_monitoring(self) -> ActionRecord:
        """Manually resume monitoring.

        Returns:
            ActionRecord with execution result.
        """
        if not self.is_paused():
            return ActionRecord(
                ActionType.PAUSE_MONITORING,
                {},
                ActionResult.ALREADY_DONE,
                "Monitoring was not paused",
            )

        self._pause_until = None

        if self._pause_task:
            self._pause_task.cancel()
            self._pause_task = None

        logger.info("Monitoring manually resumed")

        return ActionRecord(
            ActionType.PAUSE_MONITORING,
            {"action": "resume"},
            ActionResult.SUCCESS,
            "Monitoring resumed manually",
        )


class DirectoryQuarantiner:
    """Handler for directory quarantine actions (STUB ONLY per actions.md)."""

    @staticmethod
    def quarantine_directory(path: str) -> ActionRecord:
        """Quarantine a directory (STUB IMPLEMENTATION).

        Args:
            path: Directory path to quarantine.

        Returns:
            ActionRecord indicating this is a stub.
        """
        return ActionRecord(
            ActionType.QUARANTINE_DIRECTORY,
            {"path": path},
            ActionResult.FAILED,
            "Directory quarantine is not implemented (stub only)",
        )


class ResponseActionsManager:
    """Main response actions manager implementing actions.md specifications."""

    def __init__(self, config: ResponsesConfig, operational_config: OperationalConfig | None = None) -> None:
        """Initialize response actions manager.

        Args:
            config: Response actions configuration.
            operational_config: Operational control configuration.
        """
        self.config = config
        self.operational_config = operational_config

        # Action handlers
        self.process_terminator = ProcessTerminator()
        self.monitoring_controller = MonitoringController()
        self.directory_quarantiner = DirectoryQuarantiner()

        # Action history
        self.action_history: list[ActionRecord] = []

        # User consent tracking (placeholder for UI integration)
        self._pending_consent_requests: dict[str, dict[str, Any]] = {}

        logger.info(f"ResponseActionsManager initialized: destructive_actions={config.allow_destructive_actions}")

    def _get_current_operational_mode(self) -> str:
        """Get current operational mode from storage.
        
        Returns:
            Current operational mode, or "observe" if unavailable.
        """
        try:
            from config.operational_mode import get_mode
            return get_mode()
        except Exception as e:
            logger.warning(f"Failed to get operational mode: {e}, using default 'observe'")
            return "observe"

    def _check_mode_enforcement(self, action_type: ActionType, action_description: str) -> ActionRecord | None:
        """Check operational mode enforcement for an action.
        
        Args:
            action_type: Type of action being attempted.
            action_description: Description of the action for logging.
            
        Returns:
            ActionRecord if action should be blocked, None if allowed.
        """
        current_mode = self._get_current_operational_mode()
        
        # Enforcement rules based on operational mode
        if current_mode == "offline":
            # offline: no outbound/destructive actions; log intent only
            if action_type in [ActionType.TERMINATE_PROCESS, ActionType.QUARANTINE_DIRECTORY]:
                logger.info(f"[OFFLINE MODE] Would perform: {action_description}")
                return ActionRecord(
                    action_type,
                    {"blocked_reason": "offline_mode"},
                    ActionResult.UNAUTHORIZED,
                    f"Action blocked in offline mode: {action_description}",
                )
                
        elif current_mode == "observe":
            # observe: log only; suppress side effects
            if action_type in [ActionType.TERMINATE_PROCESS, ActionType.QUARANTINE_DIRECTORY]:
                logger.info(f"[OBSERVE MODE] Would perform: {action_description}")
                return ActionRecord(
                    action_type,
                    {"blocked_reason": "observe_mode"},
                    ActionResult.UNAUTHORIZED,
                    f"Action logged only in observe mode: {action_description}",
                )
                
        elif current_mode == "alert":
            # alert: allow alerting/logging; block containment/quarantine actions
            if action_type in [ActionType.TERMINATE_PROCESS, ActionType.QUARANTINE_DIRECTORY]:
                logger.warning(f"[ALERT MODE] Blocking containment action: {action_description}")
                return ActionRecord(
                    action_type,
                    {"blocked_reason": "alert_mode"},
                    ActionResult.UNAUTHORIZED,
                    f"Containment action blocked in alert mode: {action_description}",
                )
                
        elif current_mode == "contain":
            # contain: allow containment; quarantine only if explicitly invoked
            if action_type == ActionType.QUARANTINE_DIRECTORY:
                logger.info(f"[CONTAIN MODE] Quarantine action requires explicit invocation: {action_description}")
                # For now, we'll allow it but log the restriction
                # In a full implementation, we might check if this was explicitly requested
                
        elif current_mode == "quarantine":
            # quarantine: allow all defensive actions
            logger.debug(f"[QUARANTINE MODE] Allowing action: {action_description}")
            
        return None  # Action is allowed

    def terminate_process(self, pid: int, user_consent: bool = False, force: bool = False) -> ActionRecord:
        """Terminate a process with safety checks.

        Args:
            pid: Process ID to terminate.
            user_consent: Whether user provided explicit consent.
            force: Whether to force termination.

        Returns:
            ActionRecord with execution result.
        """
        action_description = f"terminate process PID {pid}" + (" (force)" if force else "")
        
        # Check operational mode enforcement
        enforcement_result = self._check_mode_enforcement(ActionType.TERMINATE_PROCESS, action_description)
        if enforcement_result:
            enforcement_result.user_consent = user_consent
            self.action_history.append(enforcement_result)
            return enforcement_result
        
        # Check if destructive actions are allowed
        if not self.config.allow_destructive_actions:
            record = ActionRecord(
                ActionType.TERMINATE_PROCESS,
                {"pid": pid, "force": force},
                ActionResult.UNAUTHORIZED,
                "Destructive actions are disabled in configuration",
                user_consent=user_consent,
            )
            self.action_history.append(record)
            logger.warning(f"Process termination denied: destructive actions disabled (PID: {pid})")
            return record

        # Require user consent for destructive actions
        if not user_consent:
            record = ActionRecord(
                ActionType.TERMINATE_PROCESS,
                {"pid": pid, "force": force},
                ActionResult.UNAUTHORIZED,
                "User consent required for process termination",
                user_consent=user_consent,
            )
            self.action_history.append(record)
            logger.warning(f"Process termination denied: no user consent (PID: {pid})")
            return record

        # Execute termination
        record = self.process_terminator.terminate_process(pid, force)
        record.user_consent = user_consent
        self.action_history.append(record)

        # Log consent event
        logger.info(f"Process termination with user consent: PID={pid}, result={record.result.value}")

        return record

    def pause_monitoring(self, duration_seconds: int) -> ActionRecord:
        """Pause monitoring for specified duration.

        Args:
            duration_seconds: Duration to pause monitoring.

        Returns:
            ActionRecord with execution result.
        """
        record = self.monitoring_controller.pause_monitoring(duration_seconds)
        self.action_history.append(record)
        return record

    def resume_monitoring(self) -> ActionRecord:
        """Resume monitoring if paused.

        Returns:
            ActionRecord with execution result.
        """
        record = self.monitoring_controller.resume_monitoring()
        self.action_history.append(record)
        return record

    def quarantine_directory(self, path: str, user_consent: bool = False) -> ActionRecord:
        """Quarantine a directory (STUB ONLY).

        Args:
            path: Directory path to quarantine.
            user_consent: Whether user provided explicit consent.

        Returns:
            ActionRecord indicating this is a stub.
        """
        action_description = f"quarantine directory {path}"
        
        # Check operational mode enforcement
        enforcement_result = self._check_mode_enforcement(ActionType.QUARANTINE_DIRECTORY, action_description)
        if enforcement_result:
            enforcement_result.user_consent = user_consent
            self.action_history.append(enforcement_result)
            return enforcement_result
        
        record = self.directory_quarantiner.quarantine_directory(path)
        record.user_consent = user_consent
        self.action_history.append(record)

        logger.warning(f"Directory quarantine requested but not implemented: {path}")
        return record

    def is_monitoring_paused(self) -> bool:
        """Check if monitoring is currently paused.

        Returns:
            True if monitoring is paused.
        """
        return self.monitoring_controller.is_paused()

    def get_monitoring_pause_remaining(self) -> int | None:
        """Get remaining monitoring pause time.

        Returns:
            Remaining pause time in seconds, or None if not paused.
        """
        return self.monitoring_controller.get_pause_remaining()

    def get_action_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent action history.

        Args:
            limit: Maximum number of actions to return.

        Returns:
            List of action record dictionaries.
        """
        return [record.to_dict() for record in self.action_history[-limit:]]

    def get_stats(self) -> dict[str, Any]:
        """Get response actions statistics.

        Returns:
            Dictionary with action statistics.
        """
        # Count actions by type and result
        action_counts = {}
        result_counts = {}

        for record in self.action_history:
            action_type = record.action_type.value
            result = record.result.value

            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            result_counts[result] = result_counts.get(result, 0) + 1

        return {
            "config": {
                "allow_destructive_actions": self.config.allow_destructive_actions,
            },
            "monitoring": {
                "is_paused": self.is_monitoring_paused(),
                "pause_remaining_seconds": self.get_monitoring_pause_remaining(),
            },
            "action_history": {
                "total_actions": len(self.action_history),
                "by_type": action_counts,
                "by_result": result_counts,
            },
        }

    def clear_action_history(self) -> None:
        """Clear action history."""
        self.action_history.clear()
        logger.info("Action history cleared")

    def request_user_consent(self, action_type: str, parameters: dict[str, Any]) -> str:
        """Request user consent for destructive action (placeholder for UI integration).

        Args:
            action_type: Type of action requiring consent.
            parameters: Action parameters.

        Returns:
            Consent request ID for tracking.
        """
        import uuid

        request_id = str(uuid.uuid4())

        self._pending_consent_requests[request_id] = {
            "action_type": action_type,
            "parameters": parameters,
            "requested_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"User consent requested: {request_id} for {action_type}")
        return request_id

    def provide_user_consent(self, request_id: str, granted: bool) -> bool:
        """Provide user consent response (placeholder for UI integration).

        Args:
            request_id: Consent request ID.
            granted: Whether consent is granted.

        Returns:
            True if consent was recorded successfully.
        """
        if request_id not in self._pending_consent_requests:
            logger.warning(f"Unknown consent request: {request_id}")
            return False

        request = self._pending_consent_requests.pop(request_id)

        logger.info(f"User consent {'granted' if granted else 'denied'}: {request_id} for {request['action_type']}")

        # In a full implementation, this would trigger the actual action
        # if consent was granted

        return True

    def get_pending_consent_requests(self) -> list[dict[str, Any]]:
        """Get pending consent requests.

        Returns:
            List of pending consent request dictionaries.
        """
        return [
            {"request_id": req_id, **req_data}
            for req_id, req_data in self._pending_consent_requests.items()
        ]
