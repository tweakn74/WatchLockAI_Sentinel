from pathlib import Path

TARGETS = [
    "main.py",
    "agent_core/planner.py",
    "agent_core/generator.py",
    "agent_core/executor.py",
    "memory_reader.py",
    "audit_devagent.py",
]

log_path = Path("devagent_code_dump.txt")

with log_path.open("w", encoding="utf-8") as log:
    log.write("🧠 DevAgent Code Dump\n")
    log.write("=" * 60 + "\n\n")
    for file in TARGETS:
        path = Path(file)
        if path.exists():
            log.write(f"\n# ===== {file} =====\n\n")
            log.write(path.read_text(encoding="utf-8"))
        else:
            log.write(f"\n# ===== {file} MISSING =====\n\n")

print(f"\n✅ Code dump complete: {log_path.resolve()}")
