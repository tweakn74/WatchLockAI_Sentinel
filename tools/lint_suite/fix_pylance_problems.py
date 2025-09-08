# tools/fix_pylance_problems.py
"""
Run lint_gauntlet.py only on files that Pyright reports as problematic.

Usage (repo root):
  python tools/fix_pylance_problems.py
  python tools/fix_pylance_problems.py --include-warnings --attempts 3

Exit codes:
  0 = all targeted files cleaned (or no problem files found)
  1 = some files still failing after attempts
  2 = infrastructure error (pyright/gauntlet not callable, bad JSON, etc.)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple


@dataclass
class CmdResult:
    ok: bool
    code: int
    out: str
    err: str


@dataclass
class PyrightAnalysis:
    """Results from Pyright analysis"""

    files_with_problems: List[Path]
    total_errors: int
    total_warnings: int
    problems_by_file: Dict[Path, Tuple[int, int]]  # (errors, warnings) per file


def run(
    cmd: Sequence[str], cwd: Optional[Path] = None, timeout: Optional[int] = None
) -> CmdResult:
    try:
        p = subprocess.run(
            list(cmd),
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return CmdResult(
            p.returncode == 0, p.returncode, p.stdout or "", p.stderr or ""
        )
    except FileNotFoundError as e:
        return CmdResult(False, 127, "", str(e))
    except subprocess.TimeoutExpired as e:
        stdout = (
            e.stdout.decode("utf-8", errors="replace")
            if isinstance(e.stdout, bytes)
            else (e.stdout or "")
        )
        return CmdResult(False, 124, stdout, f"Timeout: {e}")
    except Exception as e:  # pragma: no cover
        return CmdResult(False, 2, "", f"Exception: {e}")


def which(exe: str) -> Optional[str]:
    return shutil.which(exe)


def find_pyright() -> Optional[str]:
    # Prefer the venv `pyright` on PATH
    return which("pyright")


def find_gauntlet(root: Path) -> Optional[Path]:
    # Default location: tools/lint_gauntlet.py relative to repo root
    cand = root / "tools" / "lint_gauntlet.py"
    return cand if cand.exists() else None


def analyze_pyright_problems(root: Path, include_warnings: bool) -> PyrightAnalysis:
    exe = find_pyright()
    if not exe:
        raise RuntimeError("pyright CLI not found on PATH (inside venv).")

    res = run([exe, "--outputjson"], cwd=root)
    if res.code not in (0, 1, 2):
        raise RuntimeError(f"pyright failed rc={res.code}\n{res.err}")

    try:
        data = json.loads(res.out or "{}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"pyright produced invalid JSON: {e}")

    diags = data.get("generalDiagnostics") or data.get("diagnostics") or []
    severities = {"error"} | ({"warning"} if include_warnings else set())

    files: List[Path] = []
    problems_by_file: Dict[Path, Tuple[int, int]] = {}  # (errors, warnings)
    total_errors = 0
    total_warnings = 0

    for d in diags:
        sev = str(d.get("severity", "")).lower()
        if sev not in severities:
            continue
        fp = d.get("file") or d.get("filePath") or ""
        if not fp:
            continue
        p = Path(fp)
        # Ensure file is under root and exists
        try:
            rp = p if p.is_absolute() else (root / p)
            rp = rp.resolve()
        except Exception:
            continue
        if rp.exists():
            files.append(rp)

            # Count problems by file and severity
            if rp not in problems_by_file:
                problems_by_file[rp] = (0, 0)

            errors, warnings = problems_by_file[rp]
            if sev == "error":
                errors += 1
                total_errors += 1
            elif sev == "warning":
                warnings += 1
                total_warnings += 1
            problems_by_file[rp] = (errors, warnings)

    # Deduplicate files, preserve order
    seen: Set[Path] = set()
    unique_files: List[Path] = []
    for f in files:
        if f not in seen:
            unique_files.append(f)
            seen.add(f)

    return PyrightAnalysis(
        files_with_problems=unique_files,
        total_errors=total_errors,
        total_warnings=total_warnings,
        problems_by_file=problems_by_file,
    )


def run_gauntlet_on_file(
    root: Path,
    gauntlet: Path,
    target: Path,
    per_call_loop: int,
    attempts: int,
) -> Tuple[int, int, int]:
    """
    Returns (final_exit_code, errors, warnings) after attempts.
    """
    cmd_base = [
        sys.executable,
        str(gauntlet),
        "--paths",
        str(target),
        "--fix",
        "--loop",
        str(per_call_loop),
        "--auto-suppress",
        "ruff,eslint",
        "--smoke",
        "--self-drive",
        "--max-iterations",
        "6",
    ]
    exit_code = 1
    errors = 0
    warnings = 0

    for _ in range(max(1, attempts)):
        res = run(cmd_base, cwd=root)
        try:
            obj = json.loads(res.out or "{}")
        except json.JSONDecodeError:
            # Treat as infra failure for this file
            return (2, 0, 0)
        exit_code = int(obj.get("exit_code", 1))
        errors = int(obj.get("errors", 0))
        warnings = int(obj.get("warnings", 0))
        if exit_code == 0:
            break
    return (exit_code, errors, warnings)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fix Pylance (Pyright) problem files using lint_gauntlet.py."
    )
    ap.add_argument("--root", default=".", help="Repo root (default: current dir)")
    ap.add_argument(
        "--attempts",
        type=int,
        default=3,
        help="Max gauntlet runs per file (default: 3)",
    )
    ap.add_argument(
        "--per-call-loop",
        type=int,
        default=3,
        help="--loop value passed to gauntlet (default: 3)",
    )
    ap.add_argument(
        "--include-warnings",
        action="store_true",
        help="Also process files that only have warnings",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    gauntlet = find_gauntlet(root)
    if not gauntlet:
        sys.stderr.write(
            "ERROR: tools/lint_gauntlet.py not found; copy it into this repo.\n"
        )
        return 2

    try:
        analysis = analyze_pyright_problems(
            root, include_warnings=args.include_warnings
        )
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 2

    if not analysis.files_with_problems:
        print(
            json.dumps(
                {
                    "processed": 0,
                    "remaining_failures": 0,
                    "total_problems": 0,
                    "note": "No Pyright problem files found",
                }
            )
        )
        return 0

    total_problems = analysis.total_errors + analysis.total_warnings

    # Print initial analysis
    print(
        json.dumps(
            {
                "analysis": {
                    "files_with_problems": len(analysis.files_with_problems),
                    "total_problems": total_problems,
                    "total_errors": analysis.total_errors,
                    "total_warnings": analysis.total_warnings,
                    "attempts_per_file": args.attempts,
                }
            }
        )
    )

    # Print problem breakdown
    for file_path, (errors, warnings) in analysis.problems_by_file.items():
        rel_path = (
            file_path.relative_to(root) if file_path.is_relative_to(root) else file_path
        )
        print(
            json.dumps(
                {
                    "file_analysis": {
                        "file": str(rel_path),
                        "errors": errors,
                        "warnings": warnings,
                        "total": errors + warnings,
                    }
                }
            )
        )

    failures: List[str] = []
    processed = 0

    for f in analysis.files_with_problems:
        processed += 1
        ec, errs, warns = run_gauntlet_on_file(
            root, gauntlet, f, args.per_call_loop, args.attempts
        )
        print(
            json.dumps(
                {"file": str(f), "exit_code": ec, "errors": errs, "warnings": warns}
            )
        )
        if ec != 0:
            failures.append(str(f))

    # Run final analysis to see remaining problems
    try:
        final_analysis = analyze_pyright_problems(
            root, include_warnings=args.include_warnings
        )
        remaining_problems = final_analysis.total_errors + final_analysis.total_warnings
    except Exception:
        remaining_problems = -1  # Unknown

    summary = {
        "initial_analysis": {
            "files": len(analysis.files_with_problems),
            "total_problems": total_problems,
            "errors": analysis.total_errors,
            "warnings": analysis.total_warnings,
        },
        "processing_results": {
            "files_processed": processed,
            "files_with_remaining_failures": len(failures),
            "failure_files": failures[:50],  # keep output compact
        },
        "final_analysis": {
            "remaining_problems": remaining_problems,
            "problems_fixed": max(0, total_problems - remaining_problems)
            if remaining_problems >= 0
            else "unknown",
        },
    }
    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
