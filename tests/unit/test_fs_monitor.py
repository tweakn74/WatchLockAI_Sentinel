"""Unit tests for file system monitor."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from app_core.bus import EventBus
from app_core.config import FileSystemConfig
from app_core.schemas import EventType, FileEvent
from collectors.fs_monitor import FileSystemMonitor


@pytest.fixture()
async def event_bus():
    """Create event bus for testing."""
    bus = EventBus(max_history=100)
    await bus.start()
    yield bus
    await bus.stop()


@pytest.fixture()
def temp_dir():
    """Create temporary directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="fs_monitor_test_")
    yield Path(temp_dir)

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture()
def fs_config(temp_dir):
    """Create file system configuration for testing."""
    return FileSystemConfig(
        enabled=True,
        paths=[str(temp_dir)],
        exclude_globs=["*.tmp"],
        method="polling",  # Use polling for reliable testing
        compute_entropy=False,
        compute_hash_small_files=False,
        small_file_threshold_bytes=1024,
        burst_window_sec=10,
    )


@pytest.fixture()
async def fs_monitor(fs_config, event_bus):
    """Create file system monitor for testing."""
    monitor = FileSystemMonitor(fs_config, event_bus)
    await monitor.start()
    yield monitor
    await monitor.stop()


class EventCollector:
    """Helper to collect file events during testing."""

    def __init__(self, event_bus):
        self.events = []
        self.subscription = None
        self.event_bus = event_bus

    async def start(self):
        self.subscription = self.event_bus.subscribe(
            FileEvent,
            self._handle_event,
            "EventCollector",
        )

    async def stop(self):
        if self.subscription:
            self.event_bus.unsubscribe(self.subscription)

    def _handle_event(self, event):
        self.events.append(event)

    def get_events_by_type(self, event_type):
        return [e for e in self.events if e.event_type == event_type]


@pytest.mark.asyncio()
async def test_fs_monitor_initialization(fs_config, event_bus):
    """Test file system monitor initialization."""
    monitor = FileSystemMonitor(fs_config, event_bus)
    assert not monitor.running

    await monitor.start()
    assert monitor.running

    await monitor.stop()
    assert not monitor.running


@pytest.mark.asyncio()
async def test_file_creation_detection(fs_monitor, event_bus, temp_dir):
    """Test detection of file creation."""
    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create a test file
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("test content")

        # Wait for detection
        await asyncio.sleep(2)

        # Check for file creation event
        create_events = collector.get_events_by_type(EventType.CREATED)
        assert len(create_events) >= 1

        # Verify event details
        event = create_events[0]
        assert str(test_file) in event.path
        assert event.event_type == EventType.CREATED

    finally:
        await collector.stop()


@pytest.mark.asyncio()
async def test_file_modification_detection(fs_monitor, event_bus, temp_dir):
    """Test detection of file modification."""
    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create and modify a test file
        test_file = temp_dir / "modify_test.txt"
        test_file.write_text("initial content")

        # Wait for creation event
        await asyncio.sleep(2)

        # Clear events and modify file
        collector.events.clear()
        test_file.write_text("modified content")

        # Wait for modification event
        await asyncio.sleep(2)

        # Check for file modification event
        modify_events = collector.get_events_by_type(EventType.MODIFIED)
        assert len(modify_events) >= 1

        event = modify_events[0]
        assert str(test_file) in event.path
        assert event.event_type == EventType.MODIFIED

    finally:
        await collector.stop()


@pytest.mark.asyncio()
async def test_file_deletion_detection(fs_monitor, event_bus, temp_dir):
    """Test detection of file deletion."""
    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create a test file
        test_file = temp_dir / "delete_test.txt"
        test_file.write_text("content to delete")

        # Wait for creation
        await asyncio.sleep(2)

        # Clear events and delete file
        collector.events.clear()
        test_file.unlink()

        # Wait for deletion event
        await asyncio.sleep(2)

        # Check for file deletion event
        delete_events = collector.get_events_by_type(EventType.DELETED)
        assert len(delete_events) >= 1

        event = delete_events[0]
        assert str(test_file) in event.path
        assert event.event_type == EventType.DELETED

    finally:
        await collector.stop()


@pytest.mark.asyncio()
async def test_file_rename_detection(fs_monitor, event_bus, temp_dir):
    """Test detection of file rename."""
    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create a test file
        old_file = temp_dir / "old_name.txt"
        new_file = temp_dir / "new_name.txt"
        old_file.write_text("content to rename")

        # Wait for creation
        await asyncio.sleep(2)

        # Clear events and rename file
        collector.events.clear()
        old_file.rename(new_file)

        # Wait for rename event
        await asyncio.sleep(2)

        # Check for rename event (may appear as delete + create)
        events = collector.events

        # Should have events related to the rename operation
        assert len(events) >= 1

        # Check if we have old_path set for renamed events
        rename_events = [e for e in events if e.event_type == EventType.RENAMED]
        if rename_events:
            event = rename_events[0]
            assert event.old_path is not None

    finally:
        await collector.stop()


@pytest.mark.asyncio()
async def test_exclude_globs_filtering(event_bus, temp_dir):
    """Test that exclude globs filter out unwanted files."""
    config = FileSystemConfig(
        enabled=True,
        paths=[str(temp_dir)],
        exclude_globs=["*.tmp", "*.log"],
        method="polling",
    )

    monitor = FileSystemMonitor(config, event_bus)
    await monitor.start()

    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create files that should be excluded
        temp_file = temp_dir / "test.tmp"
        log_file = temp_dir / "test.log"
        normal_file = temp_dir / "test.txt"

        temp_file.write_text("temp content")
        log_file.write_text("log content")
        normal_file.write_text("normal content")

        # Wait for detection
        await asyncio.sleep(2)

        # Check events
        events = collector.events
        event_paths = [e.path for e in events]

        # Should have event for normal file
        assert any("test.txt" in path for path in event_paths)

        # Should NOT have events for excluded files
        assert not any("test.tmp" in path for path in event_paths)
        assert not any("test.log" in path for path in event_paths)

    finally:
        await collector.stop()
        await monitor.stop()


@pytest.mark.asyncio()
async def test_entropy_computation(event_bus, temp_dir):
    """Test entropy computation when enabled."""
    config = FileSystemConfig(
        enabled=True,
        paths=[str(temp_dir)],
        method="polling",
        compute_entropy=True,
        small_file_threshold_bytes=1024,
    )

    monitor = FileSystemMonitor(config, event_bus)
    await monitor.start()

    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create small file with repetitive content (low entropy)
        low_entropy_file = temp_dir / "low_entropy.txt"
        low_entropy_file.write_text("a" * 100)  # Very repetitive

        # Create small file with random content (high entropy)
        high_entropy_file = temp_dir / "high_entropy.txt"
        import random
        import string
        random_content = "".join(random.choices(string.ascii_letters + string.digits, k=100))
        high_entropy_file.write_text(random_content)

        # Wait for detection
        await asyncio.sleep(2)

        # Check events
        events = collector.events

        # Should have entropy values for small files
        entropy_events = [e for e in events if e.entropy is not None]
        assert len(entropy_events) >= 1

        # Entropy should be between 0 and 8
        for event in entropy_events:
            assert 0 <= event.entropy <= 8

    finally:
        await collector.stop()
        await monitor.stop()


@pytest.mark.asyncio()
async def test_hash_computation(event_bus, temp_dir):
    """Test hash computation when enabled."""
    config = FileSystemConfig(
        enabled=True,
        paths=[str(temp_dir)],
        method="polling",
        compute_hash_small_files=True,
        small_file_threshold_bytes=1024,
    )

    monitor = FileSystemMonitor(config, event_bus)
    await monitor.start()

    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create small file
        test_file = temp_dir / "hash_test.txt"
        test_content = "content for hashing"
        test_file.write_text(test_content)

        # Wait for detection
        await asyncio.sleep(2)

        # Check events
        events = collector.events
        hash_events = [e for e in events if e.sha256 is not None]

        assert len(hash_events) >= 1

        # Verify hash format (64 hex characters)
        event = hash_events[0]
        assert len(event.sha256) == 64
        assert all(c in "0123456789abcdef" for c in event.sha256)

    finally:
        await collector.stop()
        await monitor.stop()


@pytest.mark.asyncio()
async def test_large_file_handling(event_bus, temp_dir):
    """Test handling of large files (above threshold)."""
    config = FileSystemConfig(
        enabled=True,
        paths=[str(temp_dir)],
        method="polling",
        compute_entropy=True,
        compute_hash_small_files=True,
        small_file_threshold_bytes=100,  # Small threshold for testing
    )

    monitor = FileSystemMonitor(config, event_bus)
    await monitor.start()

    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create large file (above threshold)
        large_file = temp_dir / "large_file.txt"
        large_file.write_text("x" * 200)  # Above 100 byte threshold

        # Wait for detection
        await asyncio.sleep(2)

        # Check events
        events = collector.events
        large_file_events = [e for e in events if "large_file.txt" in e.path]

        assert len(large_file_events) >= 1

        # Large files should not have entropy or hash computed
        event = large_file_events[0]
        assert event.entropy is None
        assert event.sha256 is None

    finally:
        await collector.stop()
        await monitor.stop()


@pytest.mark.asyncio()
async def test_multiple_path_monitoring(event_bus, temp_dir):
    """Test monitoring multiple paths."""
    # Create second temp directory
    temp_dir2 = tempfile.mkdtemp(prefix="fs_monitor_test2_")
    temp_path2 = Path(temp_dir2)

    try:
        config = FileSystemConfig(
            enabled=True,
            paths=[str(temp_dir), str(temp_path2)],
            method="polling",
        )

        monitor = FileSystemMonitor(config, event_bus)
        await monitor.start()

        collector = EventCollector(event_bus)
        await collector.start()

        try:
            # Create files in both directories
            file1 = temp_dir / "file1.txt"
            file2 = temp_path2 / "file2.txt"

            file1.write_text("content 1")
            file2.write_text("content 2")

            # Wait for detection
            await asyncio.sleep(2)

            # Check events from both paths
            events = collector.events
            event_paths = [e.path for e in events]

            assert any("file1.txt" in path for path in event_paths)
            assert any("file2.txt" in path for path in event_paths)

        finally:
            await collector.stop()
            await monitor.stop()

    finally:
        # Cleanup second temp directory
        import shutil
        shutil.rmtree(temp_dir2, ignore_errors=True)


@pytest.mark.asyncio()
async def test_watchdog_vs_polling_method(event_bus, temp_dir):
    """Test both watchdog and polling methods."""
    methods = ["watchdog", "polling"]

    for method in methods:
        config = FileSystemConfig(
            enabled=True,
            paths=[str(temp_dir)],
            method=method,
        )

        monitor = FileSystemMonitor(config, event_bus)
        await monitor.start()

        collector = EventCollector(event_bus)
        await collector.start()

        try:
            # Create test file
            test_file = temp_dir / f"test_{method}.txt"
            test_file.write_text(f"content for {method}")

            # Wait for detection
            await asyncio.sleep(2)

            # Should detect file creation regardless of method
            events = collector.events
            assert len(events) >= 1

        finally:
            await collector.stop()
            await monitor.stop()

            # Clean up for next iteration
            if test_file.exists():
                test_file.unlink()


@pytest.mark.asyncio()
async def test_fs_monitor_stats(fs_monitor):
    """Test file system monitor statistics."""
    stats = fs_monitor.get_stats()

    # Should have basic stats structure
    assert "events_generated" in stats
    assert "paths_monitored" in stats
    assert "method" in stats
    assert stats["method"] == "polling"


@pytest.mark.asyncio()
async def test_burst_window_tracking(fs_monitor, event_bus, temp_dir):
    """Test burst window tracking for rules engine."""
    collector = EventCollector(event_bus)
    await collector.start()

    try:
        # Create many files quickly (simulate burst)
        for i in range(10):
            test_file = temp_dir / f"burst_{i}.txt"
            test_file.write_text(f"burst content {i}")

        # Wait for detection
        await asyncio.sleep(3)

        # Should have events for all files
        events = collector.events
        assert len(events) >= 10

        # Events should have timestamps for burst analysis
        for event in events:
            assert event.ts is not None

    finally:
        await collector.stop()


@pytest.mark.asyncio()
async def test_error_handling_invalid_path(event_bus):
    """Test error handling with invalid paths."""
    config = FileSystemConfig(
        enabled=True,
        paths=["/nonexistent/path"],
        method="polling",
    )

    monitor = FileSystemMonitor(config, event_bus)

    # Should handle invalid paths gracefully
    await monitor.start()
    assert monitor.running  # Should still be running despite invalid path
    await monitor.stop()
