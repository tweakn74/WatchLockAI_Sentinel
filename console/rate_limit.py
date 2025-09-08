# File: console/rate_limit.py
# Purpose: Standard-library rate limiting (token bucket) for FastAPI routes.
# Behavior: Default OFF via RATE_LIMIT_ENABLED; per-route, per-client buckets.

from __future__ import annotations
import threading
import time
import os
from typing import Dict, Tuple

RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}

try:
    from fastapi import HTTPException  # type: ignore
except Exception:
    class HTTPException(Exception):  # minimal fallback to keep imports safe
        def __init__(self, status_code: int, detail: str):
            super().__init__(f"{status_code}: {detail}")
            self.status_code = status_code
            self.detail = detail

class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_s: float) -> None:
        self.capacity = max(1, int(capacity))
        self.tokens = float(self.capacity)
        self.refill_rate = max(0.0, float(refill_rate_per_s))
        self.updated = time.monotonic()
        self.lock = threading.Lock()

    def allow(self, cost: float = 1.0) -> bool:
        now = time.monotonic()
        with self.lock:
            elapsed = max(0.0, now - self.updated)
            self.updated = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            if self.tokens >= cost:
                self.tokens -= cost
                return True
            return False

_buckets: Dict[Tuple[str, str], TokenBucket] = {}
_buckets_lock = threading.Lock()

def rate_limit_dependency(route_key: str, max_calls: int, window_s: int):
    """
    Returns a dependency callable suitable for FastAPI's Depends. No FastAPI imports at module import time.
    """
    def _dep(request):
        if not RATE_LIMIT_ENABLED:
            return
        try:
            client = getattr(request, "client", None)
            client_id = getattr(client, "host", "unknown") or "unknown"
        except Exception:
            client_id = "unknown"

        key = (route_key, client_id)
        with _buckets_lock:
            bucket = _buckets.get(key)
            if bucket is None:
                refill = max_calls / float(max(1, window_s))
                bucket = _buckets[key] = TokenBucket(max_calls, refill)

        if not bucket.allow():
            raise HTTPException(status_code=429, detail="rate limit exceeded")
    return _dep