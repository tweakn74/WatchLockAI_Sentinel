# Sentinel Event Schemas (authoritative)

Use Pydantic v2 models named below. All timestamps are UTC ISO 8601 strings. 
All events include `host_id: str`, `sentinel_version: str`, `ts: str`.

## FileEvent@v1
fields:
  event_type: enum['created','modified','deleted','renamed']
  path: str
  old_path: Optional[str]
  size_bytes: Optional[int]
  sha256: Optional[str]         # compute only for small/changed files if configured
  entropy: Optional[float]      # 0..8, compute only when enabled
  proc_pid: Optional[int]
  proc_name: Optional[str]

## ProcessEvent@v1
fields:
  event_type: enum['started','exited']
  pid: int
  ppid: Optional[int]
  exe: Optional[str]
  cmdline: Optional[str]
  username: Optional[str]
  hash_sha256: Optional[str]    # best-effort
  start_ts: Optional[str]
  end_ts: Optional[str]

## RegistryEvent@v1
fields:
  event_type: enum['created','modified','deleted']
  hive: enum['HKCU','HKLM','HKU','HKCR']
  key_path: str
  value_name: Optional[str]
  value_type: Optional[str]
  data_preview: Optional[str]
  proc_pid: Optional[int]
  proc_name: Optional[str]

## NetworkEvent@v1
fields:
  event_type: enum['connection','listen','close']
  pid: Optional[int]
  proc_name: Optional[str]
  laddr_ip: Optional[str]
  laddr_port: Optional[int]
  raddr_ip: Optional[str]
  raddr_port: Optional[int]
  proto: enum['TCP','UDP','OTHER']
  status: Optional[str]         # e.g., ESTABLISHED, TIME_WAIT

## HealthMetric@v1
fields:
  cpu_pct: float
  ram_pct: float
  disk_pct_free: float
  temp_c: Optional[float]