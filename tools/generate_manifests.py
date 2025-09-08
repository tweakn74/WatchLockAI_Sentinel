# __version__ = "1.0.0"
# __author__ = "CG & AI assistant"
# __creation_date__ = "2025-08-25"
# __modification_date__ = "2025-08-27"
# __purpose__ = "Return (start_line, end_line) if available."
# ruff: noqa: F841
"""Module: generate_manifests.py
Auto-added docstring to aid static analysis and navigation.
"""
# =====================================================================
# File: generate_manifests.py
# Developer: Craig & ChatGPT (refactor + diff-mode + ingest catalog)
# Location: root
# Version: 3.4.0
# Last Modified: 2025-08-25
# Purpose:
#   Manifest generator with:
#     - Function & class census (AST-based), helpers/core split
#     - Diff mode vs. last snapshot (Added/Removed by file/func/class)
#     - Ingest catalog for targeted file selection (per-function records)
#     - Import graph + priority scoring to rank "important" files
# Outputs:
#   - fv_manifests/*.manifest
#   - logs/manifest_generation_report.txt
#   - logs/manifest_snapshot.json
#   - logs/ingest_catalog.jsonl          (one JSON per line)
#   - logs/import_graph.json             (module imports adjacency)
#   - logs/ingest_priority.txt           (ranked file list)
# =====================================================================

from __future__ import annotations

import os
import ast
import json
from pathlib import Path
from datetime import datetime
from typing import Iterable, List, Tuple, Dict, Set, Union, Optional

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
MANIFEST_DIR = PROJECT_ROOT / "fv_manifests"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORT_FILE = LOGS_DIR / "manifest_generation_report.txt"
SYSTEM_MANIFEST_FILE = LOGS_DIR / "preflight_manifest.txt"
SNAPSHOT_FILE = LOGS_DIR / "manifest_snapshot.json"
INGEST_CATALOG = LOGS_DIR / "ingest_catalog.jsonl"
IMPORT_GRAPH_JSON = LOGS_DIR / "import_graph.json"
INGEST_PRIORITY_TXT = LOGS_DIR / "ingest_priority.txt"

# Case-insensitive excludes (folder names only)
EXCLUDE_DIRS_CI: Set[str] = {
    "venv",
    ".venv",
    "__pycache__",
    "fv_manifests",
    "backups",
    "logs",
    ".git",
    "dist",
    "build",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}


# ---------------------------------------------------------------------
# Helpers (I/O, AST utilities)
# ---------------------------------------------------------------------
def _safe_read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return p.read_text(encoding="latin-1", errors="ignore")


def _format_default(d: ast.AST | None) -> str:
    if d is None:
        return ""
    try:
        return ast.unparse(d)  # type: ignore[attr-defined]
    except Exception:
        if isinstance(d, ast.Constant):
            return repr(d.value)
        return "<expr>"


def _node_span(node: ast.AST) -> Tuple[Optional[int], Optional[int]]:
    """Return (start_line, end_line) if available."""
    start = getattr(node, "lineno", None)
    end = getattr(node, "end_lineno", None)
    return start, end


def _module_name_from_path(py_path: Path) -> str:
    rel = py_path.relative_to(PROJECT_ROOT).as_posix()
    if rel.endswith(".py"):
        rel = rel[:-3]
    return rel.replace("/", ".")


def _build_signature(fn: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
    a = fn.args
    posonly = [arg.arg for arg in getattr(a, "posonlyargs", [])]
    regular = [arg.arg for arg in a.args]
    kwonly = [arg.arg for arg in a.kwonlyargs]
    vararg = a.vararg.arg if a.vararg else None
    kwarg = a.kwarg.arg if a.kwarg else None

    pos_params = posonly + regular
    pos_defaults: List[str] = []
    if a.defaults:
        fill = len(pos_params) - len(a.defaults)
        pos_defaults.extend([""] * max(fill, 0))
        pos_defaults.extend([_format_default(d) for d in a.defaults])
    else:
        pos_defaults = [""] * len(pos_params)

    kwonly_defaults_raw = getattr(a, "kw_defaults", [])
    kwonly_defaults: List[str] = [
        (_format_default(d) if d is not None else "") for d in kwonly_defaults_raw
    ]

    parts: List[str] = []
    for name, dv in zip(posonly, pos_defaults[: len(posonly)]):
        parts.append(f"{name}={dv}" if dv else name)
    if posonly:
        parts.append("/")

    for idx, name in enumerate(regular):
        dv = pos_defaults[len(posonly) + idx]
        parts.append(f"{name}={dv}" if dv else name)

    if vararg:
        parts.append(f"*{vararg}")
    else:
        if kwonly:
            parts.append("*")

    for name, dv in zip(kwonly, kwonly_defaults):
        parts.append(f"{name}={dv}" if dv else name)

    if kwarg:
        parts.append(f"**{kwarg}")

    kind = "async def" if isinstance(fn, ast.AsyncFunctionDef) else "def"
    return f"{kind} {fn.name}({', '.join(parts)})"


AstDocNode = Union[ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef]


def _docstring_of(node: AstDocNode) -> str:
    ds = ast.get_docstring(node)
    return ds.strip() if ds else "(No docstring found — describe capability manually)"


def _is_helper(name: str) -> bool:
    return name.startswith("_")


def _excluded_dir(name: str) -> bool:
    return name.lower() in EXCLUDE_DIRS_CI


# ---------------------------------------------------------------------
# Parsing per module
# ---------------------------------------------------------------------
class ModuleScan:
    def __init__(self, path: Path):
        self.path = path
        self.module_name = _module_name_from_path(path)
        self.functions: List[Dict[str, object]] = []
        self.classes: List[str] = []
        self.imports_out: Set[str] = set()  # module names this module imports
        self.loc: int = 0


def parse_python_file(py_path: Path) -> ModuleScan:
    scan = ModuleScan(py_path)
    try:
        src = _safe_read_text(py_path)
        scan.loc = src.count("\n") + 1
        tree = ast.parse(src)
    except SyntaxError:
        return scan
    except Exception:
        return scan

    # imports
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    scan.imports_out.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                scan.imports_out.add(node.module.split(".")[0])

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = _build_signature(node)
            start, end = _node_span(node)
            scan.functions.append(
                {
                    "name": node.name,
                    "signature": sig,
                    "docstring": _docstring_of(node),
                    "is_helper": _is_helper(node.name),
                    "start_line": start,
                    "end_line": end,
                }
            )
        elif isinstance(node, ast.ClassDef):
            scan.classes.append(node.name)

    return scan


# ---------------------------------------------------------------------
# System manifest append
# ---------------------------------------------------------------------
def append_to_system_manifest(capabilities: Iterable[str]) -> None:
    SYSTEM_MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing: Set[str] = set()
    if SYSTEM_MANIFEST_FILE.exists():
        existing.update(
            line.rstrip("\n")
            for line in SYSTEM_MANIFEST_FILE.read_text(encoding="utf-8").splitlines()
        )
    to_add = []
    for cap in capabilities:
        entry = f"- {cap} (AUTO-ADDED FROM FUNCTION SCAN) (ACTIVE)"
        if entry not in existing:
            to_add.append(entry)
    if to_add:
        with SYSTEM_MANIFEST_FILE.open("a", encoding="utf-8", newline="\n") as f:
            for line in to_add:
                f.write(line + "\n")


# ---------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------
def write_manifest(
    py_path: Path, scan: ModuleScan, report_lines: List[str]
) -> Tuple[int, int]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_name = f"{py_path.name}.manifest"
    manifest_path = MANIFEST_DIR / manifest_name
    if manifest_path.exists():
        report_lines.append(f"[SKIPPED] {manifest_name} already exists.")
        return -1, -1

    core_funcs = [fn for fn in scan.functions if not fn["is_helper"]]
    secondary_funcs = [fn for fn in scan.functions if fn["is_helper"]]

    if not scan.functions and not scan.classes:
        report_lines.append(
            f"[WARNING] {py_path.name} has no functions/classes — manual review required."
        )

    with manifest_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Manifest for {py_path.name}\n")
        f.write(f"# Source Path: {py_path.relative_to(PROJECT_ROOT)}\n")
        if scan.classes:
            f.write(f"# Classes Detected: {', '.join(scan.classes)}\n")

        if core_funcs:
            f.write("\n# Core Functions\n")
            for func in core_funcs:
                f.write(f"- {func['signature']}: {func['docstring']}\n")
                f.write("  Test Input: (define example input)\n")
                f.write("  Expected Output: (define expected output)\n")

        if secondary_funcs:
            f.write("\n# Secondary Functions (Helpers)\n")
            for func in secondary_funcs:
                f.write(f"- {func['signature']}: {func['docstring']}\n")

        if not scan.functions and not scan.classes:
            f.write("\n- No functions or classes detected; review file manually.\n")

    report_lines.append(
        f"[CREATED] {manifest_name} "
        f"(Core: {len(core_funcs)}, Helpers: {len(secondary_funcs)}, Classes: {len(scan.classes)})"
    )
    return len(core_funcs), len(secondary_funcs)


# ---------------------------------------------------------------------
# Diff snapshot helpers
# ---------------------------------------------------------------------
def build_snapshot_from_manifests() -> Dict[str, Dict[str, List[str]]]:
    snapshot: Dict[str, Dict[str, List[str]]] = {}
    for manifest_file in MANIFEST_DIR.glob("*.manifest"):
        try:
            lines = manifest_file.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue

        functions, helpers, classes = [], [], []
        section = None
        for line in lines:
            if line.startswith("# Core Functions"):
                section = "core"
            elif line.startswith("# Secondary Functions"):
                section = "helpers"
            elif line.startswith("# Classes Detected"):
                parts = line.split(":")
                if len(parts) > 1:
                    classes.extend(
                        [c.strip() for c in parts[1].split(",") if c.strip()]
                    )
            elif line.startswith("- "):
                sig = line[2:].split(":")[0].strip()
                if section == "core":
                    functions.append(sig)
                elif section == "helpers":
                    helpers.append(sig)

        snapshot[manifest_file.name] = {
            "core": functions,
            "helpers": helpers,
            "classes": classes,
        }
    return snapshot


def append_diff_section(
    report_lines: List[str], snapshot: Dict[str, Dict[str, List[str]]]
) -> None:
    previous: Dict[str, Dict[str, List[str]]] = {}
    if SNAPSHOT_FILE.exists():
        try:
            previous = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        except Exception:
            previous = {}

    diff_lines: List[str] = []
    diff_lines.append("=== Delta Since Last Run ===")

    all_files = set(snapshot.keys()) | set(previous.keys())
    for file in sorted(all_files):
        new = snapshot.get(file, {"core": [], "helpers": [], "classes": []})
        old = previous.get(file, {"core": [], "helpers": [], "classes": []})

        added_core = sorted(set(new["core"]) - set(old["core"]))
        removed_core = sorted(set(old["core"]) - set(new["core"]))

        for f in added_core:
            diff_lines.append(f"[ADDED] {file}::{f}")
        for f in removed_core:
            diff_lines.append(f"[REMOVED] {file}::{f}")

        added_helpers = sorted(set(new["helpers"]) - set(old["helpers"]))
        removed_helpers = sorted(set(old["helpers"]) - set(new["helpers"]))
        for f in added_helpers:
            diff_lines.append(f"[ADDED] (helper) {file}::{f}")
        for f in removed_helpers:
            diff_lines.append(f"[REMOVED] (helper) {file}::{f}")

        added_classes = sorted(set(new["classes"]) - set(old["classes"]))
        removed_classes = sorted(set(old["classes"]) - set(new["classes"]))
        for c in added_classes:
            diff_lines.append(f"[ADDED] (class) {file}::{c}")
        for c in removed_classes:
            diff_lines.append(f"[REMOVED] (class) {file}::{c}")

    report_lines.append("")
    report_lines.extend(diff_lines)

    # Save new snapshot for next run
    SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------
# Ingest Catalog & Import Graph & Priority
# ---------------------------------------------------------------------
def write_ingest_catalog(scans: List[ModuleScan]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with INGEST_CATALOG.open("w", encoding="utf-8", newline="\n") as out:
        for scan in scans:
            for fn in scan.functions:
                record = {
                    "file": str(scan.path.relative_to(PROJECT_ROOT)),
                    "module": scan.module_name,
                    "function": fn["name"],
                    "signature": fn["signature"],
                    "is_core": not fn["is_helper"],
                    "start_line": fn["start_line"],
                    "end_line": fn["end_line"],
                    "docstring": fn["docstring"],
                    "classes_in_file": scan.classes,
                    "loc": scan.loc,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_import_graph(scans: List[ModuleScan]) -> Dict[str, List[str]]:
    graph: Dict[str, List[str]] = {}
    for s in scans:
        # keep only local-looking modules (those that start with our top-level package names)
        # minimal heuristic: include modules that appear in repo
        graph[s.module_name] = sorted(set(s.imports_out))
    return graph


def rank_files(
    scans: List[ModuleScan], graph: Dict[str, List[str]]
) -> List[Tuple[str, float]]:
    # inbound degree
    inbound: Dict[str, int] = {s.module_name: 0 for s in scans}
    for src, outs in graph.items():
        for tgt in outs:
            if tgt in inbound:
                inbound[tgt] += 1

    # per-file metrics
    scores: List[Tuple[str, float]] = []
    by_module: Dict[str, ModuleScan] = {s.module_name: s for s in scans}
    for s in scans:
        core = sum(1 for f in s.functions if not f["is_helper"])
        helpers = sum(1 for f in s.functions if f["is_helper"])
        classes = len(s.classes)
        indeg = inbound.get(s.module_name, 0)
        # simple score: weight core higher, then classes, then helpers, then inbound
        score = core * 3.0 + classes * 1.5 + helpers * 1.0 + indeg * 0.5
        scores.append((str(s.path.relative_to(PROJECT_ROOT)), score))

    # sort high-to-low
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def write_ingest_priority(scores: List[Tuple[str, float]]) -> None:
    with INGEST_PRIORITY_TXT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Ingest Priority (highest first)\n")
        for path_str, score in scores:
            f.write(f"{score:6.2f}  {path_str}\n")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def generate_manifests() -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    created_count = 0
    skipped_count = 0
    warning_count = 0
    report_lines: List[str] = []

    report_lines.append("=== Manifest Generation Report ===")
    report_lines.append(f"Timestamp: {datetime.now().isoformat(timespec='seconds')}")
    report_lines.append(f"Scanning root: {PROJECT_ROOT}")
    report_lines.append("")

    scans: List[ModuleScan] = []

    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        dirnames[:] = [d for d in dirnames if not _excluded_dir(d)]
        for file in filenames:
            if not file.endswith(".py"):
                continue
            py_path = Path(dirpath) / file
            scan = parse_python_file(py_path)
            scans.append(scan)

            core_count, helper_count = write_manifest(py_path, scan, report_lines)
            if core_count == -1 and helper_count == -1:
                skipped_count += 1
            else:
                if core_count == 0 and helper_count == 0 and not scan.classes:
                    warning_count += 1
                created_count += 1

            # Update system manifest with new core functions
            core_names = [
                f"{py_path.name}::{fn['name']}"
                for fn in scan.functions
                if not fn["is_helper"]
            ]
            append_to_system_manifest(core_names)

    # Summary
    report_lines.append("")
    report_lines.append(f"Total manifests created: {created_count}")
    report_lines.append(f"Total manifests skipped (already exist): {skipped_count}")
    report_lines.append(
        f"Total files flagged for review (no functions/classes): {warning_count}"
    )
    report_lines.append("")

    # Build snapshot & diff
    snapshot = build_snapshot_from_manifests()
    append_diff_section(report_lines, snapshot)

    # Ingest outputs
    write_ingest_catalog(scans)
    graph = build_import_graph(scans)
    IMPORT_GRAPH_JSON.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    scores = rank_files(scans, graph)
    write_ingest_priority(scores)

    # Write report
    with REPORT_FILE.open("a", encoding="utf-8", newline="\n") as log:
        log.write("\n".join(report_lines))
        log.write("\n" + "=" * 60 + "\n")

    # Console
    print("\n".join(report_lines))
    print(f"\nReport saved to: {REPORT_FILE}")
    print(f"Ingest catalog: {INGEST_CATALOG}")
    print(f"Import graph:   {IMPORT_GRAPH_JSON}")
    print(f"Priority list:  {INGEST_PRIORITY_TXT}")


# ---------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------
if __name__ == "__main__":
    generate_manifests()

# =====================================================================
# End of Script
# Version: 3.4.0
# Date: 2025-08-25
# =====================================================================
