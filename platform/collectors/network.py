"""Network Monitor implementing net_monitor.md specifications."""

from __future__ import annotations

import asyncio
import contextlib
from typing import TYPE_CHECKING, Any, TypedDict

import psutil
from loguru import logger

from core.schemas import NetworkEvent, NetworkEventType, NetworkProtocol

if TYPE_CHECKING:
    from core.bus import EventBus
    from core.config import NetworkConfig


class ConnectionInfo(TypedDict):
    """Type definition for connection information dictionary."""

    pid: int | None
    proc_name: str | None
    laddr: tuple[str, int]
    raddr: tuple[str, int]
    status: str
    proto: str


class ConnectionState:
    """Track connection state for change detection."""

    def __init__(
        self,
        pid: int | None,
        laddr: tuple[str, int],
        raddr: tuple[str, int],
        status: str,
        proto: str,
    ) -> None:
        """Initialize connection state.

        Args:
            pid: Process ID.
            laddr: Local address tuple (ip, port).
            raddr: Remote address tuple (ip, port).
            status: Connection status.
            proto: Protocol (TCP/UDP).
        """
        self.pid = pid
        self.laddr = laddr
        self.raddr = raddr
        self.status = status
        self.proto = proto
        self.first_seen = asyncio.get_event_loop().time()
        self.last_seen = self.first_seen

    def __eq__(self, other: object) -> bool:
        """Check equality based on connection tuple."""
        if not isinstance(other, ConnectionState):
            return False
        return (self.pid, self.laddr, self.raddr, self.proto) == (
            other.pid,
            other.laddr,
            other.raddr,
            other.proto,
        )

    def __hash__(self) -> int:
        """Hash based on connection tuple."""
        return hash((self.pid, self.laddr, self.raddr, self.proto))

    @property
    def connection_key(
        self,
    ) -> tuple[int | None, tuple[str, int], tuple[str, int], str]:
        """Get unique connection key."""
        return (self.pid, self.laddr, self.raddr, self.proto)


class NetworkMonitor:
    """Network monitor implementing net_monitor.md specifications."""

    def __init__(self, config: NetworkConfig, event_bus: EventBus) -> None:
        """Initialize network monitor.

        Args:
            config: Network monitoring configuration.
            event_bus: Event bus for publishing NetworkEvent objects.
        """
        self.config = config
        self.event_bus = event_bus
        self._running = False
        self._task: asyncio.Task[None] | None = None

        # Connection tracking
        self._known_connections: dict[
            tuple[int | None, tuple[str, int], tuple[str, int], str], ConnectionState
        ] = {}
        self._known_listeners: set[tuple[int | None, str, int, str]] = (
            set()
        )  # (pid, ip, port, proto)

        logger.info(
            f"NetworkMonitor initialized: poll_interval={config.poll_interval_ms}ms"
        )

    async def start(self) -> None:
        """Start network monitoring."""
        if self._running:
            logger.warning("NetworkMonitor already running")
            return

        if not self.config.enabled:
            logger.info("NetworkMonitor disabled by configuration")
            return

        self._running = True

        # Initialize with current connections
        await self._initialize_network_state()

        # Start monitoring loop
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("NetworkMonitor started")

    async def stop(self) -> None:
        """Stop network monitoring."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

        logger.info("NetworkMonitor stopped")

    async def _initialize_network_state(self) -> None:
        """Initialize tracking state with current network connections."""
        try:
            connections = self._get_network_connections()

            for conn_info in connections:
                conn_state = ConnectionState(
                    pid=conn_info["pid"],
                    laddr=conn_info["laddr"],
                    raddr=conn_info["raddr"],
                    status=conn_info["status"],
                    proto=conn_info["proto"],
                )
                self._known_connections[conn_state.connection_key] = conn_state

                # Track listeners
                if conn_info["status"] == "LISTEN":
                    listener_key = (
                        conn_info["pid"],
                        conn_info["laddr"][0],
                        conn_info["laddr"][1],
                        conn_info["proto"],
                    )
                    self._known_listeners.add(listener_key)

            logger.debug(
                f"Initialized with {len(self._known_connections)} connections, {len(self._known_listeners)} listeners"
            )

        except Exception as e:
            logger.error(f"Failed to initialize network state: {e}")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop checking for network changes."""
        while self._running:
            try:
                await self._check_network_changes()

                # Sleep based on configured interval
                sleep_time = self.config.poll_interval_ms / 1000.0
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                await asyncio.sleep(1.0)  # Brief pause on error

    def _get_network_connections(self) -> list[ConnectionInfo]:
        """Get current network connections using psutil.

        Returns:
            List of connection information dictionaries.
        """
        connections: list[ConnectionInfo] = []

        try:
            # Get TCP and UDP connections
            connection_kinds = ["tcp"]
            if self.config.include_udp:
                connection_kinds.append("udp")

            for kind in connection_kinds:
                try:
                    for conn in psutil.net_connections(kind=kind):
                        # Skip connections without addresses
                        if not conn.laddr:
                            continue

                        # Get process info if enabled
                        pid = None
                        proc_name = None

                        if self.config.track_process_association and conn.pid:
                            try:
                                proc = psutil.Process(conn.pid)
                                pid = conn.pid
                                proc_name = proc.name()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass

                        # Format addresses
                        laddr = (conn.laddr.ip, conn.laddr.port)
                        raddr = (
                            (conn.raddr.ip, conn.raddr.port) if conn.raddr else ("", 0)
                        )

                        # Map protocol
                        proto = (
                            NetworkProtocol.TCP
                            if kind == "tcp"
                            else NetworkProtocol.UDP
                        )

                        connections.append(
                            {
                                "pid": pid,
                                "proc_name": proc_name,
                                "laddr": laddr,
                                "raddr": raddr,
                                "status": conn.status,
                                "proto": proto.value,
                            }
                        )

                except Exception as e:
                    logger.debug(f"Error getting {kind} connections: {e}")

        except Exception as e:
            logger.error(f"Error getting network connections: {e}")

        return connections

    async def _check_network_changes(self) -> None:
        """Check for network connection changes and emit events."""
        try:
            current_connections: dict[
                tuple[int | None, tuple[str, int], tuple[str, int], str],
                ConnectionState,
            ] = {}
            current_listeners: set[tuple[int | None, str, int, str]] = set()

            # Get current network state
            for conn_info in self._get_network_connections():
                conn_state = ConnectionState(
                    pid=conn_info["pid"],
                    laddr=conn_info["laddr"],
                    raddr=conn_info["raddr"],
                    status=conn_info["status"],
                    proto=conn_info["proto"],
                )
                current_connections[conn_state.connection_key] = conn_state

                # Track listeners
                if conn_info["status"] == "LISTEN":
                    listener_key = (
                        conn_info["pid"],
                        conn_info["laddr"][0],
                        conn_info["laddr"][1],
                        conn_info["proto"],
                    )
                    current_listeners.add(listener_key)

            # Find new connections
            new_connections = set(current_connections.keys()) - set(
                self._known_connections.keys()
            )
            for conn_key in new_connections:
                conn_state = current_connections[conn_key]

                # Determine event type
                if conn_state.status == "LISTEN":
                    await self._emit_network_event(NetworkEventType.LISTEN, conn_state)
                else:
                    await self._emit_network_event(
                        NetworkEventType.CONNECTION, conn_state
                    )

            # Find closed connections (best-effort)
            closed_connections = set(self._known_connections.keys()) - set(
                current_connections.keys()
            )
            for conn_key in closed_connections:
                old_conn_state = self._known_connections[conn_key]
                await self._emit_network_event(NetworkEventType.CLOSE, old_conn_state)

            # Update tracking state
            self._known_connections = current_connections
            self._known_listeners = current_listeners

        except Exception as e:
            logger.error(f"Error checking network changes: {e}")

    async def _emit_network_event(
        self, event_type: NetworkEventType, conn_state: ConnectionState
    ) -> None:
        """Emit network event.

        Args:
            event_type: Type of network event.
            conn_state: Connection state information.
        """
        try:
            # Get process name if available
            proc_name = None
            if conn_state.pid and self.config.track_process_association:
                try:
                    proc = psutil.Process(conn_state.pid)
                    proc_name = proc.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Create event
            event = NetworkEvent(
                event_type=event_type,
                pid=conn_state.pid,
                proc_name=proc_name,
                laddr_ip=conn_state.laddr[0],
                laddr_port=conn_state.laddr[1],
                raddr_ip=conn_state.raddr[0] if conn_state.raddr[0] else None,
                raddr_port=conn_state.raddr[1] if conn_state.raddr[1] else None,
                proto=NetworkProtocol(conn_state.proto),
                status=conn_state.status,
            )

            await self.event_bus.publish(event)
            logger.debug(
                f"Network event: {event_type.value} {conn_state.laddr} -> {conn_state.raddr} (PID: {conn_state.pid})"
            )

        except Exception as e:
            logger.warning(f"Error emitting network event: {e}")

    def get_connection_stats(self) -> dict[str, Any]:
        """Get connection statistics.

        Returns:
            Dictionary with connection statistics.
        """
        tcp_count = sum(
            1 for conn in self._known_connections.values() if conn.proto == "TCP"
        )
        udp_count = sum(
            1 for conn in self._known_connections.values() if conn.proto == "UDP"
        )

        established_count = sum(
            1
            for conn in self._known_connections.values()
            if conn.status == "ESTABLISHED"
        )
        listen_count = len(self._known_listeners)

        return {
            "total_connections": len(self._known_connections),
            "tcp_connections": tcp_count,
            "udp_connections": udp_count,
            "established_connections": established_count,
            "listening_sockets": listen_count,
        }

    def get_stats(self) -> dict[str, Any]:
        """Get monitoring statistics.

        Returns:
            Dictionary with monitoring statistics.
        """
        stats = {
            "enabled": self.config.enabled,
            "running": self._running,
            "poll_interval_ms": self.config.poll_interval_ms,
            "track_process_association": self.config.track_process_association,
            "include_udp": self.config.include_udp,
        }

        if self._running:
            stats.update(self.get_connection_stats())

        return stats

    def get_process_connections(self, pid: int) -> list[dict[str, Any]]:
        """Get connections for a specific process.

        Args:
            pid: Process ID.

        Returns:
            List of connection information for the process.
        """
        process_connections: list[dict[str, Any]] = []

        for conn_state in self._known_connections.values():
            if conn_state.pid == pid:
                process_connections.append(
                    {
                        "laddr": conn_state.laddr,
                        "raddr": conn_state.raddr,
                        "status": conn_state.status,
                        "proto": conn_state.proto,
                        "first_seen": conn_state.first_seen,
                        "last_seen": conn_state.last_seen,
                    }
                )

        return process_connections
