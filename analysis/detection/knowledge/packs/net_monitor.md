# Network Monitor — Spec

Purpose: Observe new outbound connections and listening sockets.

Config:
- track_process_association: bool (default true)
- poll_interval_ms: int (default 1000)
- include_udp: bool (default true)

Behavior:
- Use psutil.net_connections() with kind='inet'.
- For new tuple (pid,laddr,raddr) emit NetworkEvent@v1(event_type='connection').
- For listen sockets emit NetworkEvent@v1(event_type='listen').
- Track closes best-effort.