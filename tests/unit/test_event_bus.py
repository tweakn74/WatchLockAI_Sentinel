"""Unit tests for event bus."""

import asyncio

import pytest

from app_core.bus import EventBus, get_event_bus, initialize_event_bus
from app_core.schemas import EventType, FileEvent, ProcessEvent, ProcessEventType


@pytest.fixture()
async def event_bus():
    """Create and start an event bus for testing."""
    bus = EventBus(max_history=100)
    await bus.start()
    yield bus
    await bus.stop()


@pytest.mark.asyncio()
async def test_event_bus_initialization():
    """Test event bus initialization and cleanup."""
    bus = EventBus()
    assert not bus._running
    assert bus._queue.qsize() == 0

    await bus.start()
    assert bus._running
    assert bus._worker_task is not None

    await bus.stop()
    assert not bus._running


@pytest.mark.asyncio()
async def test_event_publishing(event_bus):
    """Test event publishing and delivery."""
    received_events = []

    def handler(event):
        received_events.append(event)

    # Subscribe to FileEvent
    subscription = event_bus.subscribe(FileEvent, handler, "test_handler")

    # Publish an event
    test_event = FileEvent(
        event_type=EventType.CREATED,
        path="test.txt",
    )

    await event_bus.publish(test_event)

    # Wait for delivery
    await asyncio.sleep(0.1)

    # Check event was delivered
    assert len(received_events) == 1
    assert received_events[0] == test_event

    # Cleanup
    event_bus.unsubscribe(subscription)


@pytest.mark.asyncio()
async def test_multiple_subscribers(event_bus):
    """Test multiple subscribers receiving the same event."""
    received_events_1 = []
    received_events_2 = []

    def handler_1(event):
        received_events_1.append(event)

    def handler_2(event):
        received_events_2.append(event)

    # Subscribe multiple handlers
    sub1 = event_bus.subscribe(FileEvent, handler_1, "handler_1")
    sub2 = event_bus.subscribe(FileEvent, handler_2, "handler_2")

    # Publish event
    test_event = FileEvent(
        event_type=EventType.CREATED,
        path="test.txt",
    )

    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)

    # Both handlers should receive the event
    assert len(received_events_1) == 1
    assert len(received_events_2) == 1
    assert received_events_1[0] == test_event
    assert received_events_2[0] == test_event

    # Cleanup
    event_bus.unsubscribe(sub1)
    event_bus.unsubscribe(sub2)


@pytest.mark.asyncio()
async def test_event_type_filtering(event_bus):
    """Test that subscribers only receive events of subscribed types."""
    file_events = []
    process_events = []

    def file_handler(event):
        file_events.append(event)

    def process_handler(event):
        process_events.append(event)

    # Subscribe to different event types
    file_sub = event_bus.subscribe(FileEvent, file_handler, "file_handler")
    proc_sub = event_bus.subscribe(ProcessEvent, process_handler, "process_handler")

    # Publish different event types
    file_event = FileEvent(event_type=EventType.CREATED, path="test.txt")
    process_event = ProcessEvent(event_type=ProcessEventType.STARTED, pid=1234)

    await event_bus.publish(file_event)
    await event_bus.publish(process_event)
    await asyncio.sleep(0.1)

    # Check filtering
    assert len(file_events) == 1
    assert len(process_events) == 1
    assert file_events[0] == file_event
    assert process_events[0] == process_event

    # Cleanup
    event_bus.unsubscribe(file_sub)
    event_bus.unsubscribe(proc_sub)


@pytest.mark.asyncio()
async def test_event_filtering_with_custom_filter(event_bus):
    """Test custom event filtering function."""
    received_events = []

    def handler(event):
        received_events.append(event)

    # Filter only events with specific path
    def path_filter(event):
        return event.path == "important.txt"

    subscription = event_bus.subscribe(
        FileEvent,
        handler,
        "filtered_handler",
        filter_func=path_filter,
    )

    # Publish events
    important_event = FileEvent(event_type=EventType.CREATED, path="important.txt")
    normal_event = FileEvent(event_type=EventType.CREATED, path="normal.txt")

    await event_bus.publish(important_event)
    await event_bus.publish(normal_event)
    await asyncio.sleep(0.1)

    # Only filtered event should be received
    assert len(received_events) == 1
    assert received_events[0] == important_event

    # Cleanup
    event_bus.unsubscribe(subscription)


@pytest.mark.asyncio()
async def test_async_handler(event_bus):
    """Test async event handlers."""
    received_events = []

    async def async_handler(event):
        await asyncio.sleep(0.01)  # Simulate async work
        received_events.append(event)

    subscription = event_bus.subscribe(FileEvent, async_handler, "async_handler")

    test_event = FileEvent(event_type=EventType.CREATED, path="test.txt")
    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)

    assert len(received_events) == 1
    assert received_events[0] == test_event

    # Cleanup
    event_bus.unsubscribe(subscription)


@pytest.mark.asyncio()
async def test_error_handling_in_handler(event_bus):
    """Test that handler errors don't crash the event bus."""
    received_events = []

    def good_handler(event):
        received_events.append(event)

    def bad_handler(event):
        msg = "Handler error"
        raise ValueError(msg)

    # Subscribe both handlers
    good_sub = event_bus.subscribe(FileEvent, good_handler, "good_handler")
    bad_sub = event_bus.subscribe(FileEvent, bad_handler, "bad_handler")

    test_event = FileEvent(event_type=EventType.CREATED, path="test.txt")
    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)

    # Good handler should still receive event despite bad handler error
    assert len(received_events) == 1
    assert received_events[0] == test_event

    # Cleanup
    event_bus.unsubscribe(good_sub)
    event_bus.unsubscribe(bad_sub)


@pytest.mark.asyncio()
async def test_subscription_statistics(event_bus):
    """Test subscription tracking and statistics."""
    initial_stats = event_bus.get_stats()
    assert initial_stats["active_subscriptions"] == 0

    def handler(event):
        pass

    # Add subscription
    subscription = event_bus.subscribe(FileEvent, handler, "test_handler")

    stats = event_bus.get_stats()
    assert stats["active_subscriptions"] == 1

    # Remove subscription
    event_bus.unsubscribe(subscription)

    stats = event_bus.get_stats()
    assert stats["active_subscriptions"] == 0


@pytest.mark.asyncio()
async def test_event_history(event_bus):
    """Test event history tracking."""
    test_event = FileEvent(event_type=EventType.CREATED, path="test.txt")

    # Publish event
    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)

    # Check history
    recent_events = event_bus.get_recent_events(5)
    assert len(recent_events) == 1
    assert recent_events[0]["type"] == "FileEvent"


@pytest.mark.asyncio()
async def test_subscription_info(event_bus):
    """Test subscription information retrieval."""
    def handler(event):
        pass

    subscription = event_bus.subscribe(FileEvent, handler, "test_handler")

    info = event_bus.get_subscription_info()
    assert len(info) == 1
    assert info[0]["subscriber_name"] == "test_handler"
    assert info[0]["event_type"] == "FileEvent"
    assert info[0]["event_count"] == 0

    # Cleanup
    event_bus.unsubscribe(subscription)


@pytest.mark.asyncio()
async def test_publish_sync(event_bus):
    """Test synchronous publish method."""
    received_events = []

    def handler(event):
        received_events.append(event)

    subscription = event_bus.subscribe(FileEvent, handler, "test_handler")

    test_event = FileEvent(event_type=EventType.CREATED, path="test.txt")

    # Use sync publish
    event_bus.publish_sync(test_event)
    await asyncio.sleep(0.1)

    assert len(received_events) == 1
    assert received_events[0] == test_event

    # Cleanup
    event_bus.unsubscribe(subscription)


@pytest.mark.asyncio()
async def test_global_event_bus():
    """Test global event bus functions."""
    # Get global instance
    global_bus = get_event_bus()
    assert global_bus is not None

    # Initialize should start it
    initialized_bus = await initialize_event_bus()
    assert initialized_bus == global_bus
    assert global_bus._running

    # Stop for cleanup
    await global_bus.stop()


@pytest.mark.asyncio()
async def test_event_bus_stats_tracking(event_bus):
    """Test statistics tracking for published and delivered events."""
    def handler(event):
        pass

    subscription = event_bus.subscribe(FileEvent, handler, "test_handler")

    initial_stats = event_bus.get_stats()
    initial_published = initial_stats["events_published"]
    initial_delivered = initial_stats["events_delivered"]

    # Publish event
    test_event = FileEvent(event_type=EventType.CREATED, path="test.txt")
    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)

    # Check stats
    updated_stats = event_bus.get_stats()
    assert updated_stats["events_published"] == initial_published + 1
    assert updated_stats["events_delivered"] == initial_delivered + 1

    # Cleanup
    event_bus.unsubscribe(subscription)
