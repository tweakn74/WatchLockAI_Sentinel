"""Module: tools/select_ingest_targets.py
Auto-added docstring to aid static analysis and navigation.
"""
# =====================================================================
# File: tools/select_ingest_targets.py
# Developer: Craig & ChatGPT
# Version: 1.0.0
# Last Modified: 2025-08-25
# Purpose:
#   Use outputs from generate_manifests.py v3.4.0 to select top-N files
#   for ingestion (by priority) and optionally copy them into a bundle.
# =====================================================================

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = PROJECT_ROOT / "logs"
PRIORITY_FILE = LOGS_DIR / "ingest_priority.txt"


def parse_priority() -> List[Tuple[float, Path]]:
    lines = PRIORITY_FILE.read_text(encoding="utf-8").splitlines()
    out: List[Tuple[float, Path]] = []
    for line in lines:
        if not line or line.startswith("#"):
            continue
        try:
            score_str, path_str = line.strip().split(None, 1)
            score = float(score_str)
            out.append((score, PROJECT_ROOT / path_str))
        except Exception:
            continue
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Select top-N files for ingestion.")
    ap.add_argument(
        "-n",
        "--top",
        type=int,
        default=25,
        help="Number of files to select (default 25)",
    )
    ap.add_argument(
        "--bundle",
        action="store_true",
        help="Copy files into PROJECT_ROOT/ingest_bundle/",
    )
    args = ap.parse_args()

    if not PRIORITY_FILE.exists():
        raise SystemExit(
            f"Priority file not found: {PRIORITY_FILE}. Run generate_manifests.py v3.4.0 first."
        )

    ranked = parse_priority()
    topk = ranked[: args.top]

    print("=== Ingest Selection ===")
    for score, path in topk:
        rel = path.relative_to(PROJECT_ROOT)
        print(f"{score:6.2f}  {rel}")

    if args.bundle:
        bundle_dir = PROJECT_ROOT / "ingest_bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        for _, src in topk:
            if src.exists():
                dst = bundle_dir / src.relative_to(PROJECT_ROOT)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        print(f"\nBundle created at: {bundle_dir}")


if __name__ == "__main__":
    main()
