#!/usr/bin/env python3
"""
Memory Loader for WatchLockAI_Sentinel
Generated automatically by Claude Memory Integration System
"""

import sys
from pathlib import Path

# Add claude_memory to path
memory_path = Path.home() / 'claude_memory'
if memory_path not in sys.path:
    sys.path.insert(0, str(memory_path))

from memory_engine import MemoryEngine

def load_project_context():
    """Load persistent memory context for this project."""
    engine = MemoryEngine()
    project_memory = engine.load_project_memory("WatchLockAI_Sentinel")
    
    print(f"Loaded memory for WatchLockAI_Sentinel")
    print(f"Development history entries: {len(project_memory.development_history)}")
    print(f"Architecture evolution: {len(project_memory.architecture_evolution)}")
    print(f"Success patterns: {len(project_memory.success_patterns)}")
    
    return project_memory, engine

def record_session_start():
    """Record that we started working on this project."""
    engine = MemoryEngine()
    engine.record_conversation(
        f"Started working on WatchLockAI_Sentinel",
        role="system",
        project_context="WatchLockAI_Sentinel",
        importance=6
    )
    return engine

if __name__ == "__main__":
    project_memory, engine = load_project_context()
    record_session_start()
