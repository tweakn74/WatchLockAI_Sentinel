"""P4-004: Chaos/Resilience probes for WatchLockAI Sentinel.

Injection of failures to test system resilience and graceful degradation.
"""

from __future__ import annotations

import os
import time
import random
import asyncio
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable
from contextlib import contextmanager

# Feature flags
CHAOS_ENABLED = os.getenv("CHAOS_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
CHAOS_MAX_LATENCY_MS = int(os.getenv("CHAOS_MAX_LATENCY_MS", "5000"))  # 5 second max
CHAOS_ERROR_RATE = float(os.getenv("CHAOS_ERROR_RATE", "0.1"))  # 10% default error rate


class ChaosManager:
    """Manages chaos engineering probes and failure injection."""
    
    def __init__(self):
        """Initialize chaos manager."""
        self.active_probes = {}
        self.injection_history = []
        self._lock = threading.RLock()
        
    def inject_latency(self, component: str, latency_ms: int) -> Dict[str, Any]:
        """Inject artificial latency into system component.
        
        Args:
            component: Component to inject latency into
            latency_ms: Latency to inject in milliseconds
            
        Returns:
            dict: Injection result
        """
        if not CHAOS_ENABLED:
            return {
                "status": "disabled",
                "message": "Chaos testing is disabled",
                "enabled": False
            }
        
        # Validate latency bounds
        if latency_ms < 0 or latency_ms > CHAOS_MAX_LATENCY_MS:
            return {
                "status": "error",
                "error": f"Latency must be between 0 and {CHAOS_MAX_LATENCY_MS}ms",
                "enabled": True
            }
        
        try:
            with self._lock:
                # Record injection
                injection_id = f"latency_{component}_{int(time.time())}"
                
                probe_config = {
                    "id": injection_id,
                    "type": "latency",
                    "component": component,
                    "latency_ms": latency_ms,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "active": True
                }
                
                self.active_probes[injection_id] = probe_config
                self.injection_history.append(probe_config.copy())
                
                # Apply latency injection
                time.sleep(latency_ms / 1000.0)  # Convert to seconds
                
                return {
                    "status": "armed",
                    "injection_id": injection_id,
                    "component": component,
                    "latency_ms": latency_ms,
                    "timestamp": probe_config["started_at"],
                    "enabled": True
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def inject_error(self, component: str, error_type: str = "generic", error_rate: float = None) -> Dict[str, Any]:
        """Inject artificial errors into system component.
        
        Args:
            component: Component to inject errors into
            error_type: Type of error to inject
            error_rate: Probability of error injection (0.0-1.0)
            
        Returns:
            dict: Injection result
        """
        if not CHAOS_ENABLED:
            return {
                "status": "disabled",
                "message": "Chaos testing is disabled",
                "enabled": False
            }
        
        # Default error rate
        if error_rate is None:
            error_rate = CHAOS_ERROR_RATE
        
        # Validate error rate
        if not (0.0 <= error_rate <= 1.0):
            return {
                "status": "error",
                "error": "Error rate must be between 0.0 and 1.0",
                "enabled": True
            }
        
        try:
            with self._lock:
                # Record injection
                injection_id = f"error_{component}_{int(time.time())}"
                
                probe_config = {
                    "id": injection_id,
                    "type": "error",
                    "component": component,
                    "error_type": error_type,
                    "error_rate": error_rate,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "active": True
                }
                
                self.active_probes[injection_id] = probe_config
                self.injection_history.append(probe_config.copy())
                
                # Decide whether to inject error based on rate
                should_inject = random.random() < error_rate
                
                if should_inject:
                    # Inject the actual error
                    if error_type == "exception":
                        raise RuntimeError(f"Chaos-injected exception in {component}")
                    elif error_type == "timeout":
                        time.sleep(10)  # Simulate timeout
                    elif error_type == "network":
                        raise ConnectionError(f"Chaos-injected network error in {component}")
                    else:
                        raise Exception(f"Chaos-injected {error_type} error in {component}")
                
                return {
                    "status": "armed",
                    "injection_id": injection_id,
                    "component": component,
                    "error_type": error_type,
                    "error_rate": error_rate,
                    "error_injected": should_inject,
                    "timestamp": probe_config["started_at"],
                    "enabled": True
                }
                
        except Exception as e:
            # Don't catch chaos-injected errors, only real errors
            if "Chaos-injected" in str(e):
                raise  # Re-raise chaos errors
            
            return {
                "status": "error",
                "error": str(e),
                "enabled": True
            }
    
    def chaos_context(self, component: str, mode: str = "latency", **kwargs) -> "ChaosContext":
        """Create chaos injection context manager.
        
        Args:
            component: Component name
            mode: Chaos mode (latency, error)
            **kwargs: Additional chaos parameters
            
        Returns:
            ChaosContext: Context manager for chaos injection
        """
        return ChaosContext(self, component, mode, **kwargs)
    
    def list_active_probes(self) -> Dict[str, Any]:
        """List currently active chaos probes.
        
        Returns:
            dict: Active probes information
        """
        if not CHAOS_ENABLED:
            return {
                "status": "disabled",
                "probes": [],
                "enabled": False
            }
        
        with self._lock:
            active_probes = [probe for probe in self.active_probes.values() if probe.get("active")]
            
            return {
                "status": "ok",
                "probes": active_probes,
                "count": len(active_probes),
                "enabled": True
            }
    
    def stop_probe(self, injection_id: str) -> Dict[str, Any]:
        """Stop an active chaos probe.
        
        Args:
            injection_id: ID of probe to stop
            
        Returns:
            dict: Stop result
        """
        if not CHAOS_ENABLED:
            return {
                "status": "disabled",
                "message": "Chaos testing is disabled",
                "enabled": False
            }
        
        with self._lock:
            if injection_id not in self.active_probes:
                return {
                    "status": "error",
                    "error": f"Probe not found: {injection_id}",
                    "enabled": True
                }
            
            # Mark probe as inactive
            probe = self.active_probes[injection_id]
            probe["active"] = False
            probe["stopped_at"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "status": "stopped",
                "injection_id": injection_id,
                "component": probe["component"],
                "timestamp": probe["stopped_at"],
                "enabled": True
            }
    
    def stop_all_probes(self) -> Dict[str, Any]:
        """Stop all active chaos probes.
        
        Returns:
            dict: Stop result for all probes
        """
        if not CHAOS_ENABLED:
            return {
                "status": "disabled",
                "message": "Chaos testing is disabled",
                "enabled": False
            }
        
        with self._lock:
            stopped_count = 0
            timestamp = datetime.now(timezone.utc).isoformat()
            
            for probe in self.active_probes.values():
                if probe.get("active"):
                    probe["active"] = False
                    probe["stopped_at"] = timestamp
                    stopped_count += 1
            
            return {
                "status": "stopped_all",
                "stopped_count": stopped_count,
                "timestamp": timestamp,
                "enabled": True
            }
    
    def get_injection_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get history of chaos injections.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            dict: Injection history
        """
        if not CHAOS_ENABLED:
            return {
                "status": "disabled",
                "history": [],
                "enabled": False
            }
        
        with self._lock:
            # Get recent history (newest first)
            recent_history = list(reversed(self.injection_history[-limit:]))
            
            return {
                "status": "ok",
                "history": recent_history,
                "total_count": len(self.injection_history),
                "returned_count": len(recent_history),
                "enabled": True
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get chaos testing statistics.
        
        Returns:
            dict: Chaos testing statistics
        """
        if not CHAOS_ENABLED:
            return {
                "status": "disabled",
                "stats": {},
                "enabled": False
            }
        
        with self._lock:
            # Calculate statistics
            total_injections = len(self.injection_history)
            active_count = sum(1 for p in self.active_probes.values() if p.get("active"))
            
            # Group by type
            by_type = {}
            by_component = {}
            
            for injection in self.injection_history:
                injection_type = injection.get("type", "unknown")
                component = injection.get("component", "unknown")
                
                by_type[injection_type] = by_type.get(injection_type, 0) + 1
                by_component[component] = by_component.get(component, 0) + 1
            
            return {
                "status": "ok",
                "stats": {
                    "total_injections": total_injections,
                    "active_probes": active_count,
                    "by_type": by_type,
                    "by_component": by_component,
                    "max_latency_ms": CHAOS_MAX_LATENCY_MS,
                    "default_error_rate": CHAOS_ERROR_RATE
                },
                "enabled": True
            }


class ChaosContext:
    """Context manager for chaos injection."""
    
    def __init__(self, chaos_manager: ChaosManager, component: str, mode: str, **kwargs):
        """Initialize chaos context.
        
        Args:
            chaos_manager: Chaos manager instance
            component: Component name
            mode: Chaos mode
            **kwargs: Chaos parameters
        """
        self.chaos_manager = chaos_manager
        self.component = component
        self.mode = mode
        self.kwargs = kwargs
        self.injection_id = None
    
    def __enter__(self):
        """Enter chaos context and inject failure."""
        if not CHAOS_ENABLED:
            return self
        
        try:
            if self.mode == "latency":
                latency_ms = self.kwargs.get("latency_ms", 100)
                result = self.chaos_manager.inject_latency(self.component, latency_ms)
            elif self.mode == "error":
                error_type = self.kwargs.get("error_type", "generic")
                error_rate = self.kwargs.get("error_rate", None)
                result = self.chaos_manager.inject_error(self.component, error_type, error_rate)
            else:
                raise ValueError(f"Unknown chaos mode: {self.mode}")
            
            self.injection_id = result.get("injection_id")
            
        except Exception:
            # Swallow chaos injection errors in context manager
            pass
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit chaos context and clean up."""
        if self.injection_id and CHAOS_ENABLED:
            try:
                self.chaos_manager.stop_probe(self.injection_id)
            except Exception:
                # Swallow cleanup errors
                pass
        
        # Don't suppress exceptions
        return False


# Global instance
_chaos_manager = None


def get_chaos_manager() -> ChaosManager:
    """Get global chaos manager instance.
    
    Returns:
        ChaosManager: Global chaos manager
    """
    global _chaos_manager
    if _chaos_manager is None:
        _chaos_manager = ChaosManager()
    return _chaos_manager


# Decorator for chaos injection
def chaos_injection(component: str, mode: str = "latency", **kwargs):
    """Decorator for automatic chaos injection.
    
    Args:
        component: Component name
        mode: Chaos mode
        **kwargs: Chaos parameters
    """
    def decorator(func):
        def wrapper(*args, **func_kwargs):
            chaos_manager = get_chaos_manager()
            with chaos_manager.chaos_context(component, mode, **kwargs):
                return func(*args, **func_kwargs)
        return wrapper
    return decorator
