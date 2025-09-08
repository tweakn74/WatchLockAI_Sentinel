# Purpose: Preserve and migrate prior config/logs/knowledge without breaking old behavior.
from __future__ import annotations

import json
import shutil
from pathlib import Path


def copy_if(src: Path, dst: Path)->None:
    if src.exists() and src != dst:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            if dst.exists():
                return
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
def main()->int:
    root=Path(".").resolve()
    prev = {
        "config": root/"config.yaml",
        "logs": root/"logs",
        "knowledge": root/"detection/knowledge/packs",
        "index": root/"detection/knowledge/index"
    }
    target = {
        "config": root/"config.yaml",
        "logs": root/"logs",
        "knowledge": root/"detection/knowledge/packs",
        "index": root/"detection/knowledge/index"
    }
    report={}
    for k in prev:
        src, dst = prev[k], target[k]
        before = dst.exists()
        copy_if(src, dst)
        report[k] = {"copied": (not before and dst.exists())}
    Path("DOCS").mkdir(exist_ok=True, parents=True)
    Path("DOCS/Migration_Report.json").write_text(json.dumps(report, indent=2), "utf-8")
    print(json.dumps(report, indent=2))
    return 0
if __name__=="__main__":
    raise SystemExit(main())