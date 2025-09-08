"""Internal async event bus for WatchLockAI Sentinel component communication."""

from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, cast
from weakref import WeakSet

from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from .schemas import SentinelEvent


class EventSubscription:
    """Represents a subscription to specific event types."""

    def __init__(
        self,
        event_types: set[type[SentinelEvent]],
        callback: Callable[[SentinelEvent], None],
        subscriber_name: str,
        filter_func: Callable[[SentinelEvent], bool] | None = None,
    ) -> None:
        """Initialize subscription.

        Args:
            event_types: Set of event types to subscribe to.
            callback: Callback function to invoke for matching events.
            subscriber_name: Name of the subscriber for logging.
            filter_func: Optional filter function for additional event filtering.
        """
        self.event_types = event_types
        self.callback = callback
        self.subscriber_name = subscriber_name
        self.filter_func = filter_func
        self.created_at = datetime.now(timezone.utc)
        self.event_count = 0
        self.last_event_at: datetime | None = None


class EventBus:
    """Async event bus for loosely coupled component communication."""

    def __init__(self, max_history: int = 1000) -> None:
        """Initialize event bus.

        Args:
            max_history: Maximum number of events to keep in history.
        """
        self._subscriptions: dict[type[SentinelEvent], WeakSet[EventSubscription]] = defaultdict(WeakSet)
        self._event_history: deque[SentinelEvent] = deque(maxlen=max_history)
        self._stats = {
            "events_published": 0,
            "events_delivered": 0,
            "active_subscriptions": 0,
            "started_at": datetime.now(timezone.utc),
        }
        # Private error tracking counters for P1-001
        self._deliver_ok = 0
        self._deliver_fail = 0
        self._running = False
        self._queue: asyncio.Queue[SentinelEvent] = asyncio.Queue()
        self._worker_task: asyncio.Task[None] | None = None
        logger.debug("EventBus initialized")

    async def start(self) -> None:
        """Start the event bus worker."""
        if self._running:
            logger.warning("EventBus already running")
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("EventBus started")

    async def stop(self) -> None:
        """Stop the event bus worker."""
        if not self._running:
            return

        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker_task

        logger.info("EventBus stopped")

    async def _worker(self) -> None:
        """Background worker to process events asynchronously."""
        logger.debug("EventBus worker started")

        while self._running:
            try:
                # Wait for event with timeout to allow graceful shutdown
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._deliver_event(event)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue  # Normal timeout, check if still running
            except Exception as e:
                logger.error(f"EventBus worker error: {e}")

    async def _deliver_event(self, event: SentinelEvent) -> None:
        """Deliver event to all matching subscribers.

        Args:
            event: Event to deliver.
        """
        event_type = type(event)
        delivered_count = 0

        # Add to history
        self._event_history.append(event)

        # Find matching subscriptions (create list copy to allow modification during iteration)
        subscriptions = list(self._subscriptions.get(event_type, []))
        dead_subscriptions: list[EventSubscription] = []

        for subscription in subscriptions:
            try:
                # Apply filter if present
                if subscription.filter_func and not subscription.filter_func(event):
                    continue

                # Deliver event (callback should be non-blocking)
                if asyncio.iscoroutinefunction(subscription.callback):
                    await subscription.callback(event)
                else:
                    subscription.callback(event)

                # Update subscription stats and counters on success
                subscription.event_count += 1
                subscription.last_event_at = datetime.now(timezone.utc)
                delivered_count += 1
                self._deliver_ok += 1

            except (ReferenceError, AttributeError):
                # Dead weakref or invalid subscription - mark for cleanup
                self._deliver_fail += 1
                dead_subscriptions.append(subscription)
                logger.exception(
                    f"Dead subscription detected during delivery - "
                    f"event_type={event_type.__name__}, "
                    f"subscriber={getattr(subscription, 'subscriber_name', 'unknown')}"
                )
            except Exception as exc:
                # Other callback exceptions - log with stack trace but continue
                self._deliver_fail += 1
                logger.exception(
                    f"Event delivery failed - "
                    f"event_type={event_type.__name__}, "
                    f"subscriber={getattr(subscription, 'subscriber_name', 'unknown')}, "
                    f"error={str(exc)}"
                )

        # Clean up dead subscribers
        if dead_subscriptions:
            for dead_sub in dead_subscriptions:
                # Robust cleanup - try event_types first, fallback to full scan
                if hasattr(dead_sub, 'event_types'):
                    for evt_type in dead_sub.event_types:
                        self._subscriptions.get(evt_type, set()).discard(dead_sub)
                else:
                    # Fallback: scan all event type sets
                    for evt_set in self._subscriptions.values():
                        evt_set.discard(dead_sub)
                logger.debug(f"Cleaned up dead subscription: {getattr(dead_sub, 'subscriber_name', 'unknown')}")

        # Update stats
        self._stats["events_delivered"] = cast(int, self._stats["events_delivered"]) + delivered_count

        logger.debug(
            f"Event {event_type.__name__} delivered to {delivered_count} subscribers",
        )

    def subscribe(
        self,
        event_types: type[SentinelEvent] | list[type[SentinelEvent]],
        callback: Callable[[SentinelEvent], None],
        subscriber_name: str,
        filter_func: Callable[[SentinelEvent], bool] | None = None,
    ) -> EventSubscription:
        """Subscribe to one or more event types.

        Args:
            event_types: Event type(s) to subscribe to.
            callback: Callback function to invoke for matching events.
            subscriber_name: Name of the subscriber for logging.
            filter_func: Optional filter function for additional event filtering.

        Returns:
            EventSubscription object that can be used to unsubscribe.
        """
        if not isinstance(event_types, list):
            event_types = [event_types]

        event_type_set = set(event_types)
        subscription = EventSubscription(
            event_type_set, callback, subscriber_name, filter_func,
        )

        # Add subscription for each event type
        for event_type in event_type_set:
            self._subscriptions[event_type].add(subscription)

        self._stats["active_subscriptions"] = sum(
            len(subs) for subs in self._subscriptions.values()
        )

        logger.info(
            f"Subscription added: {subscriber_name} -> {[t.__name__ for t in event_type_set]}",
        )

        return subscription

    def unsubscribe(self, subscription: EventSubscription) -> None:
        """Remove a subscription.

        Args:
            subscription: Subscription to remove.
        """
        for event_type in subscription.event_types:
            if event_type in self._subscriptions:
                self._subscriptions[event_type].discard(subscription)

        self._stats["active_subscriptions"] = sum(
            len(subs) for subs in self._subscriptions.values()
        )

        logger.info(f"Subscription removed: {subscription.subscriber_name}")

    async def publish(self, event: SentinelEvent) -> None:
        """Publish an event to the bus.

        Args:
            event: Event to publish.
        """
        if not self._running:
            logger.warning("EventBus not running, event will be queued")

        await self._queue.put(event)
        self._stats["events_published"] = cast(int, self._stats["events_published"]) + 1

        logger.debug(f"Event published: {type(event).__name__}")

    def publish_sync(self, event: SentinelEvent) -> None:
        """Synchronous publish (creates task for async handling).

        Args:
            event: Event to publish.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.publish(event))
            else:
                loop.run_until_complete(self.publish(event))
        except RuntimeError:
            # No event loop, create one
            asyncio.run(self.publish(event))

    def get_stats(self) -> dict[str, Any]:
        """Get event bus statistics.

        Returns:
            Dictionary with core bus statistics (stable public shape).
        """
        return {
            **self._stats,
            "active_subscriptions": sum(len(subs) for subs in self._subscriptions.values()),
            "queue_size": self._queue.qsize(),
            "history_size": len(self._event_history),
            "uptime_seconds": (
                datetime.now(timezone.utc) - cast(datetime, self._stats["started_at"])
            ).total_seconds(),
            "running": self._running,
        }

    def get_observability_metrics(self) -> dict[str, int]:
        """Internal observability counters for delivery outcomes.

        Returns:
            {
                "delivery_success_count": int,
                "delivery_failure_count": int
            }
        """
        # Keep counters private to the main stats dict to preserve the public API shape.
        # Expose them here for ops/telemetry callers that explicitly opt in.
        return {
            "delivery_success_count": self._deliver_ok,
            "delivery_failure_count": self._deliver_fail,
        }

    @property
    def is_running(self) -> bool:
        """Check if the event bus is currently running."""
        return self._running

    def get_subscription_info(self) -> list[dict[str, Any]]:
        """Get information about active subscriptions.

        Returns:
            List of subscription information dictionaries.
        """
        subscription_info: list[dict[str, Any]] = []

        for event_type, subscriptions in self._subscriptions.items():
            for subscription in subscriptions:
                subscription_info.append({
                    "subscriber_name": subscription.subscriber_name,
                    "event_type": event_type.__name__,
                    "event_count": subscription.event_count,
                    "created_at": subscription.created_at.isoformat(),
                    "last_event_at": (
                        subscription.last_event_at.isoformat()
                        if subscription.last_event_at else None
                    ),
                    "has_filter": subscription.filter_func is not None,
                })

        return subscription_info

    def get_recent_events(self, count: int = 10) -> list[dict[str, Any]]:
        """Get recent events from history.

        Args:
            count: Number of recent events to return.

        Returns:
            List of recent event dictionaries.
        """
        recent_events = list(self._event_history)[-count:]
        return [
            {
                "type": type(event).__name__,
                "timestamp": event.ts,
                "data": event.model_dump(),
            }
            for event in recent_events
        ]


# Global event bus instance
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.

    Returns:
        Global EventBus instance.
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


async def initialize_event_bus() -> EventBus:
    """Initialize and start the global event bus.

    Returns:
        Started EventBus instance.
    """
    bus = get_event_bus()
    if not bus.is_running:
        await bus.start()
    return bus


async def shutdown_event_bus() -> None:
    """Shutdown the global event bus."""
    global _event_bus
    if _event_bus:
        await _event_bus.stop()
        _event_bus = None
