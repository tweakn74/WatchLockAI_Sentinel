"""Tamperproofing implementation for WatchLockAI Sentinel."""

from .core import TamperproofCore
from .watchdog import WatchdogService
from .obfuscation import ProcessObfuscation

__all__ = ["TamperproofCore", "WatchdogService", "ProcessObfuscation"]
