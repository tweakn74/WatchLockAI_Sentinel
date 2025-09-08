"""Module: memory/memory_core.py
Auto-added docstring to aid static analysis and navigation.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict


def _ensure_json(path: Path) -> None:
    if not path.exists():
        path.write_text("{}\n", encoding="utf-8")


def read_memory(data_dir: Path) -> Dict[str, Any]:
    path = data_dir / "memory.json"
    _ensure_json(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        # simple repair: archive & reset
        (data_dir / "fix_history.json").write_text(
            '{"memory_repaired": true}\n', encoding="utf-8"
        )
        path.write_text("{}\n", encoding="utf-8")
        return {}


def write_memory(data_dir: Path, obj: Dict[str, Any]) -> None:
    path = data_dir / "memory.json"
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
