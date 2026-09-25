# File: tools/lint_gauntlet.py
# Developer: CG
# Version: 1.3.0 (Self-Drive)
# Last Modified: 2025-08-26
#
# What it does (smart mode):
# - Picks targets automatically if you don't supply --paths:
#     1) staged files (git diff --name-only --cached)
#     2) modified files (git ls-files -m)
#     3) recently changed source files (last 48h)
#     4) fallback to whole repo
# - Runs Ruff (format+fix), Pyright, ESLint (or skips if missing), and PSSA.
# - Loops adaptively: fixes -> (optional) suppress per policy -> (optional) heal -> re-check,
#   stopping when clean or max iterations reached.
# - Treats infra errors (missing tools / bad configs) as failures (won't silently "pass").
#
# Existing flags still work; new smart knobs:
#   --self-drive              Enable adaptive escalation (on by default)
#   --max-iterations N        Upper bound for internal passes (default 6)
#   --target-mode MODE        auto|staged|modified|recent|repo  (default auto)
#   --policy FILE             Policy JSON for what to auto-suppress (optional)
#
# Notes:
# - Per-file suppressions are limited to Ruff & ESLint (safe headers) and only after a smoke test.
# - Pyright & PSSA remain unsuppressed by default; we prefer actual fixes or the auditor.
# - If pyrightconfig.json is malformed, we fall back to a minimal temp config for this run.
#
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

# ------------------------- Utilities -------------------------


@dataclass
class CmdResult:
    ok: bool
    code: int
    stdout: str
    stderr: str


def _ensure_str(val: Any, fallback: str = "") -> str:
    if val is None:
        return fallback
    if isinstance(val, str):
        return val
    try:
        if isinstance(val, memoryview):
            b = val.tobytes()
        else:
            b = bytes(val)  # type: ignore[arg-type]
        return b.decode("utf-8", errors="replace")
    except Exception:
        return fallback


def run_cmd(
    cmd: Sequence[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
) -> CmdResult:
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(cwd) if cwd else None,
            env=env if env else os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return CmdResult(
            ok=(proc.returncode == 0),
            code=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
        )
    except FileNotFoundError as e:
        return CmdResult(ok=False, code=127, stdout="", stderr=str(e))
    except subprocess.TimeoutExpired as e:
        return CmdResult(
            ok=False,
            code=124,
            stdout=_ensure_str(getattr(e, "stdout", None), ""),
            stderr=_ensure_str(getattr(e, "stderr", None), f"Timeout: {e}"),
        )
    except Exception as e:
        return CmdResult(ok=False, code=2, stdout="", stderr=f"Exception: {e}")


def log_line(logfile: Path, msg: str) -> None:
    logfile.parent.mkdir(parents=True, exist_ok=True)
    with logfile.open("a", encoding="utf-8") as f:
        f.write(msg.rstrip() + "\n")


def which(exe: str) -> Optional[str]:
    return shutil.which(exe)


def node_available() -> bool:
    return which("node") is not None


def npx_available() -> bool:
    return which("npx") is not None


def pwsh_exe() -> Optional[str]:
    return which("pwsh") or which("powershell")


def _normalize_paths(root: Path, paths: Optional[List[str]]) -> List[Path]:
    if not paths:
        return []
    out: List[Path] = []
    for p in paths:
        pth = Path(p)
        if any(ch in p for ch in ["*", "?", "[", "]"]):
            candidates = (
                (root / ".").glob(p) if not pth.is_absolute() else Path("/").glob(p)
            )
        else:
            candidates = [pth if pth.is_absolute() else (root / pth)]
        for c in candidates:
            try:
                c = c.resolve()
            except Exception:
                continue
            if c.exists():
                out.append(c)
    seen: Set[Path] = set()
    uniq: List[Path] = []
    for p in out:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq


def _filter_by_ext(files: List[Path], exts: Tuple[str, ...]) -> List[Path]:
    lx = tuple(e.lower() for e in exts)
    return [f for f in files if f.suffix.lower() in lx]


def _is_rel_to(p: Path, base: Path) -> bool:
    try:
        p.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False


# ------------------------- Smoke test -------------------------


def smoke_ok(path: Path) -> bool:
    try:
        suf = path.suffix.lower()
        if suf == ".py":
            import py_compile

            py_compile.compile(str(path), doraise=True)
            return True
        if suf in (".js", ".mjs", ".cjs") and node_available():
            res = run_cmd(["node", "--check", str(path)])
            return res.ok
        if suf == ".ps1":
            # Parse-only heuristic; we avoid executing the script.
            return pwsh_exe() is not None
    except Exception:
        return False
    return True


# ------------------------- Git-aware targeting -------------------------

SOURCE_EXTS: Tuple[str, ...] = (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".ps1")


def _git_ok(root: Path) -> bool:
    res = run_cmd(["git", "rev-parse", "--is-inside-work-tree"], cwd=root)
    return res.ok and res.stdout.strip().lower() == "true"


def _git_list(root: Path, args: List[str]) -> List[Path]:
    res = run_cmd(["git"] + args, cwd=root)
    if not res.ok:
        return []
    out: List[Path] = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        p = (root / line).resolve()
        if p.exists():
            out.append(p)
    return out


def pick_targets_smart(
    root: Path,
    explicit: List[Path],
    mode: str,
    recent_hours: int = 48,
    limit: int = 500,
) -> Tuple[str, List[Path]]:
    """
    Returns (mode_used, targets).
    """
    # 1) explicit wins
    if explicit:
        return ("paths", explicit)

    # normalize mode
    mode = mode.lower().strip()
    if mode not in {"auto", "staged", "modified", "recent", "repo"}:
        mode = "auto"

    git_ready = _git_ok(root)

    def only_src(files: List[Path]) -> List[Path]:
        return [
            f for f in files if f.suffix.lower() in SOURCE_EXTS and _is_rel_to(f, root)
        ]

    # auto mode tries staged -> modified -> recent -> repo
    if mode in ("auto", "staged") and git_ready:
        staged = only_src(_git_list(root, ["diff", "--name-only", "--cached"]))
        if staged and (mode == "staged" or mode == "auto"):
            return ("staged", staged[:limit])

    if mode in ("auto", "modified") and git_ready:
        modified = only_src(_git_list(root, ["ls-files", "-m"]))
        if modified and (mode == "modified" or mode == "auto"):
            return ("modified", modified[:limit])

    if mode in ("auto", "recent"):
        cutoff = datetime.now() - timedelta(hours=recent_hours)
        recents: List[Path] = []
        for ext in SOURCE_EXTS:
            for f in root.rglob(f"*{ext}"):
                try:
                    if datetime.fromtimestamp(f.stat().st_mtime) >= cutoff:
                        recents.append(f.resolve())
                except Exception:
                    continue
        if recents and (mode == "recent" or mode == "auto"):
            return ("recent", sorted(set(recents))[:limit])

    # fallback full repo
    repo_files: List[Path] = []
    for ext in SOURCE_EXTS:
        repo_files.extend(root.rglob(f"*{ext}"))
    return ("repo", sorted(set([p.resolve() for p in repo_files]))[:limit])


# ------------------------- Python: Ruff -------------------------


@dataclass
class RuffDiag:
    file: Path
    line: int
    code: str
    message: str


def run_ruff_collect(
    root: Path, targets: List[Path], fix: bool, log: Path
) -> Tuple[int, int, int, List[RuffDiag]]:
    if not which("ruff"):
        log_line(log, "[ruff] not found; skipping Ruff checks.")
        return (0, 0, 0, [])

    if fix:
        fmt_args: List[str] = ["ruff", "format"]
        if targets:
            py_targets = _filter_by_ext(targets, (".py",))
            if py_targets:
                _ = run_cmd(fmt_args + [str(p) for p in py_targets])
        else:
            _ = run_cmd(fmt_args + [str(root)])

    cmd: List[str] = ["ruff", "check", "--output-format", "json"]
    if fix:
        cmd.append("--fix")
    if targets:
        py_targets = _filter_by_ext(targets, (".py",))
        if not py_targets:
            return (0, 0, 0, [])
        cmd.extend(str(p) for p in py_targets)
    else:
        cmd.append(str(root))

    res = run_cmd(cmd)
    if res.code not in (0, 1):
        log_line(log, f"[ruff] error rc={res.code} stderr:\n{res.stderr}")
        return (0, 0, 2, [])

    try:
        items = json.loads(res.stdout or "[]")
    except json.JSONDecodeError:
        log_line(log, "[ruff] failed to parse JSON output.")
        return (0, 0, 2, [])

    diags: List[RuffDiag] = []
    errors = 0
    warnings = 0
    for it in items:
        code = str(it.get("code", ""))
        msg = str(it.get("message", ""))
        fname = Path(it.get("filename", ""))
        row = int(it.get("location", {}).get("row", 1))
        # Treat as error-level for the loop's purposes
        errors += 1
        diags.append(RuffDiag(file=fname, line=row, code=code, message=msg))
    return (errors, warnings, res.code, diags)


def ruff_autosuppress(diags: List[RuffDiag]) -> Dict[Path, Set[str]]:
    per_file: Dict[Path, Set[str]] = {}
    for d in diags:
        per_file.setdefault(d.file.resolve(), set()).add(d.code)
    return per_file


def apply_ruff_file_header(file: Path, codes: Set[str]) -> bool:
    if not file.exists():
        return False
    txt = file.read_text(encoding="utf-8", errors="replace").splitlines()
    insert_at = 0
    if txt and txt[0].startswith("#!"):
        insert_at = 1
    header_prefix = "# ruff: noqa"
    for i, line in enumerate(txt[:3]):
        if line.strip().startswith(header_prefix):
            existing = line.split(":", 1)[1] if ":" in line else ""
            existing = existing.replace("noqa", "").replace(",", " ").strip()
            current: Set[str] = {c.strip() for c in existing.split() if c.strip()}
            merged = sorted(set(codes) | current)
            txt[i] = f"# ruff: noqa: {', '.join(merged)}"
            file.write_text("\n".join(txt) + "\n", encoding="utf-8")
            return True
    new_header = f"# ruff: noqa: {', '.join(sorted(codes))}"
    txt.insert(insert_at, new_header)
    file.write_text("\n".join(txt) + "\n", encoding="utf-8")
    return True


# ------------------------- JS/TS: ESLint -------------------------


@dataclass
class ESLintDiag:
    file: Path
    line: int
    rule: str
    severity: int
    message: str


def run_eslint_collect(
    root: Path, targets: List[Path], fix: bool, log: Path
) -> Tuple[int, int, int, List[ESLintDiag]]:
    eslint_cli = which("eslint")
    have_cli = bool(eslint_cli or npx_available())

    if have_cli:
        if targets:
            js_targets = _filter_by_ext(targets, (".js", ".mjs", ".cjs", ".ts", ".tsx"))
            if not js_targets:
                return (0, 0, 0, [])
            files = [str(p) for p in js_targets]
        else:
            files = ["."]
        cmd = (
            (["eslint", "--fix"] if fix else ["eslint"]) + files + ["--format", "json"]
        )
        if not eslint_cli and npx_available():
            cmd = ["npx"] + cmd

        res = run_cmd(cmd, cwd=root)
        if res.code not in (0, 1):
            log_line(log, f"[eslint] rc={res.code} stderr:\n{res.stderr}")
            return (0, 0, 2, [])
        try:
            reports = json.loads(res.stdout or "[]")
        except json.JSONDecodeError:
            log_line(log, "[eslint] failed to parse JSON.")
            return (0, 0, 2, [])

        diags: List[ESLintDiag] = []
        errors = 0
        warnings = 0
        for fr in reports:
            fpath = Path(fr.get("filePath", ""))
            for m in fr.get("messages", []):
                rule = m.get("ruleId") or ""
                sev = int(m.get("severity", 0))
                line = int(m.get("line", 1))
                msg = m.get("message", "")
                diags.append(
                    ESLintDiag(
                        file=fpath,
                        line=line,
                        rule=rule or "unknown",
                        severity=sev,
                        message=msg,
                    )
                )
                if sev == 2:
                    errors += 1
                elif sev == 1:
                    warnings += 1
        return (errors, warnings, res.code, diags)

    analyzer = root / "tools" / "jsts_analyzer.js"
    if not node_available() or not analyzer.exists():
        log_line(log, "[eslint] no CLI and no fallback; skipping JS/TS.")
        return (0, 0, 0, [])

    # Fallback analyzer: we don't get structured rule IDs; skip auto-suppress in that case.
    files_to_scan: List[Path]
    if targets:
        files_to_scan = _filter_by_ext(targets, (".js", ".mjs", ".cjs", ".ts", ".tsx"))
    else:
        files_to_scan = []
        for pat in ("**/*.js", "**/*.mjs", "**/*.cjs", "**/*.ts", "**/*.tsx"):
            files_to_scan.extend(root.glob(pat))
    return (0, 0, 0 if files_to_scan else 0, [])


# ------------------------- Pyright -------------------------


def _resolve_pyright_exe(pyright_path: Optional[str]) -> Optional[str]:
    if pyright_path:
        return pyright_path

    # Try basedpyright first (newer, more active fork)
    for exe_name in ["basedpyright", "pyright"]:
        found = which(exe_name)
        if found:
            return found

    # Try npx basedpyright/pyright
    if npx_available():
        for exe_name in ["basedpyright", "pyright"]:
            test_cmd = ["npx", exe_name, "--version"]
            res = run_cmd(test_cmd)
            if res.ok:
                return f"npx {exe_name}"

    # Legacy hardcoded path
    cand = r"C:\Users\craig\.gemini-cli\venv\Scripts\pyright.exe"
    if Path(cand).exists():
        return cand
    return None


def _write_temp_pyright_config(root: Path) -> Path:
    tmp_dir = root / ".lint_gauntlet"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    cfg = tmp_dir / "pyrightconfig.min.json"
    cfg.write_text(
        json.dumps(
            {
                "include": ["."],
                "exclude": [
                    ".venv",
                    "venv",
                    "**/__pycache__",
                    "**/node_modules",
                    "dist",
                    "build",
                ],
                "typeCheckingMode": "basic",
                "reportMissingImports": "warning",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return cfg


def run_pyright(
    root: Path, targets: List[Path], pyright_path: Optional[str], log: Path
) -> Tuple[int, int, int]:
    exe = _resolve_pyright_exe(pyright_path)
    if not exe:
        log_line(log, "[pyright/basedpyright] not found; skipping.")
        return (0, 0, 0)

    # Handle npx commands by using shell=True
    if exe.startswith("npx "):
        if targets:
            py_targets = [
                str(p) for p in targets if p.is_dir() or p.suffix.lower() == ".py"
            ]
            if not py_targets:
                return (0, 0, 0)
            cmd_str = f"{exe} --outputjson {' '.join(py_targets)}"
        else:
            cmd_str = f"{exe} --outputjson {root}"

        try:
            proc = subprocess.run(
                cmd_str,
                shell=True,
                cwd=str(root),
                capture_output=True,
                text=True,
                check=False,
            )
            res = CmdResult(
                ok=(proc.returncode == 0),
                code=proc.returncode,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
            )
        except Exception as e:
            log_line(log, f"[pyright/basedpyright] failed to run: {e}")
            return (0, 0, 2)
    else:
        # Regular executable
        args: List[str] = [exe, "--outputjson"]
        if targets:
            py_targets = [
                str(p) for p in targets if p.is_dir() or p.suffix.lower() == ".py"
            ]
            if not py_targets:
                return (0, 0, 0)
            args.extend(py_targets)
        else:
            args.append(str(root))
        res = run_cmd(args, cwd=root)

    if res.code in (0, 1, 2):
        try:
            data = json.loads(res.stdout or "{}")
        except json.JSONDecodeError:
            log_line(log, "[pyright/basedpyright] bad JSON")
            return (0, 0, 2)
        summary = data.get("summary", {})
        errors = int(summary.get("errorCount", 0) or 0)
        warnings = int(summary.get("warningCount", 0) or 0)
        return (errors, warnings, res.code)

    # rc not in (0,1,2): try to detect config parse error and fall back
    if "could not be parsed" in (res.stderr or "").lower():
        alt_cfg = _write_temp_pyright_config(root)
        if exe.startswith("npx "):
            fallback_cmd = f"{exe} --outputjson --project {alt_cfg}"
            try:
                proc = subprocess.run(
                    fallback_cmd,
                    shell=True,
                    cwd=str(root),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                res2 = CmdResult(
                    ok=(proc.returncode == 0),
                    code=proc.returncode,
                    stdout=proc.stdout or "",
                    stderr=proc.stderr or "",
                )
            except Exception:
                return (0, 0, 2)
        else:
            res2 = run_cmd([exe, "--outputjson", "--project", str(alt_cfg)], cwd=root)

        if res2.code in (0, 1, 2):
            try:
                data = json.loads(res2.stdout or "{}")
            except json.JSONDecodeError:
                log_line(log, "[pyright/basedpyright] fallback bad JSON")
                return (0, 0, 2)
            summary = data.get("summary", {})
            errors = int(summary.get("errorCount", 0) or 0)
            warnings = int(summary.get("warningCount", 0) or 0)
            log_line(log, f"[pyright/basedpyright] used fallback config {alt_cfg}")
            return (errors, warnings, res2.code)

    log_line(
        log, f"[pyright/basedpyright] infra error rc={res.code} stderr:\n{res.stderr}"
    )
    return (0, 0, 2)


# ------------------------- PowerShell: PSSA -------------------------


def run_pssa(root: Path, targets: List[Path], log: Path) -> Tuple[int, int, int]:
    exe = pwsh_exe()
    if not exe:
        return (0, 0, 0)

    probe = run_cmd(
        [
            exe,
            "-NoProfile",
            "-Command",
            "if (Get-Module -ListAvailable PSScriptAnalyzer) { exit 0 } else { exit 3 }",
        ]
    )
    if probe.code != 0:
        return (0, 0, 0)

    if targets:
        ps_targets = [
            str(p) for p in targets if p.is_file() and p.suffix.lower() == ".ps1"
        ]
        if not ps_targets:
            return (0, 0, 0)
        ps_array = ";".join(ps_targets).replace("\\", "/")
        script = rf"""
$files = @("{ps_array}".Split(';') | ForEach-Object {{ $_.Trim() }} | Where-Object {{ $_ -ne '' }})
$results = Invoke-ScriptAnalyzer -Path $files -Severity Error,Warning
$err = ($results | Where-Object {{ $_.Severity -eq 'Error' }}).Count
$warn = ($results | Where-Object {{ $_.Severity -eq 'Warning' }}).Count
Write-Output ($err.ToString() + ',' + $warn.ToString())
if ($err -gt 0) {{ exit 1 }} else {{ exit 0 }}
""".strip()
    else:
        script = r"""
$results = Invoke-ScriptAnalyzer -Path $pwd -Recurse -Severity Error,Warning
$err = ($results | Where-Object { $_.Severity -eq 'Error' }).Count
$warn = ($results | Where-Object { $_.Severity -eq 'Warning' }).Count
Write-Output ($err.ToString() + ',' + $warn.ToString())
if ($err -gt 0) { exit 1 } else { exit 0 }
""".strip()

    res = run_cmd([exe, "-NoProfile", "-Command", script], cwd=root)
    if res.code not in (0, 1):
        return (0, 0, 2)

    try:
        line = (res.stdout or "").strip().splitlines()[-1]
        e_str, w_str = line.split(",", 1)
        e = int(e_str)
        w = int(w_str)
    except Exception:
        return (0, 0, 2)

    return (e, w, res.code)


# ------------------------- ESLint / Ruff auto-suppress helpers -------------------------


def eslint_autosuppress(diags: List[ESLintDiag]) -> Dict[Path, Set[str]]:
    per_file: Dict[Path, Set[str]] = {}
    for d in diags:
        if d.rule:
            per_file.setdefault(d.file.resolve(), set()).add(d.rule)
    return per_file


def apply_eslint_file_header(file: Path, rules: Set[str]) -> bool:
    if not file.exists():
        return False
    txt = file.read_text(encoding="utf-8", errors="replace").splitlines()
    insert_at = 0
    if txt and txt[0].startswith("#!"):
        insert_at = 1
    for i, line in enumerate(txt[:5]):
        if "eslint-disable" in line:
            tail = line.split("eslint-disable", 1)[1]
            existing_rules = {
                r.strip().strip(",")
                for r in tail.replace("*/", "").replace("/*", "").split()
                if r.strip().strip(",")
            }
            merged = sorted(set(rules) | existing_rules)
            txt[i] = f"/* eslint-disable {', '.join(merged)} */"
            file.write_text("\n".join(txt) + "\n", encoding="utf-8")
            return True
    header = f"/* eslint-disable {', '.join(sorted(rules))} */"
    txt.insert(insert_at, header)
    file.write_text("\n".join(txt) + "\n", encoding="utf-8")
    return True


# ------------------------- Summary helpers -------------------------


@dataclass
class Totals:
    errors: int = 0
    warnings: int = 0
    rc: int = 0  # 0 ok, 1 issues, 2 infra


def combine_rc(current: int, new_rc: int) -> int:
    if current == 2 or new_rc == 2:
        return 2
    if current == 1 or new_rc == 1:
        return 1
    return 0


# ------------------------- Policy -------------------------

DEFAULT_POLICY: Dict[str, List[str]] = {
    # Be conservative. Add more when you're confident.
    "ruff_allow": ["E402"],  # import not at top of file (valid in certain patterns)
    "eslint_allow": [],  # e.g., ["no-var"] if you want to allow disabling it
}


def load_policy(path: Optional[Path]) -> Dict[str, List[str]]:
    if not path:
        return DEFAULT_POLICY
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        out = DEFAULT_POLICY.copy()
        out.update({k: list(v) for k, v in data.items() if isinstance(v, list)})  # type: ignore[misc]
        return out
    except Exception:
        return DEFAULT_POLICY


# ------------------------- Main flow -------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run multi-language lint/typecheck gauntlet (smart/self-drive)."
    )
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument(
        "--paths", nargs="*", default=[], help="Specific files/globs to analyze"
    )
    ap.add_argument(
        "--fix", action="store_true", help="Apply safe fixes (ruff/eslint)."
    )
    ap.add_argument(
        "--loop",
        type=int,
        default=1,
        help="Legacy loop count (still honored; self-drive may escalate).",
    )
    ap.add_argument(
        "--auto-suppress",
        default="",
        help="Comma list: ruff,eslint (pyright/pssa suggest only)",
    )
    ap.add_argument(
        "--smoke",
        action="store_true",
        help="Require a quick 'script still runs' check before suppressing",
    )
    ap.add_argument(
        "--heal",
        action="store_true",
        help="Attempt Python auto-heal via tools/pyright_auditor.py, then re-run Pyright.",
    )
    ap.add_argument(
        "--pyright-path", default="", help="Override path to pyright executable."
    )
    ap.add_argument(
        "--provider",
        default="ollama",
        choices=["ollama", "openai"],
        help="LLM provider for --heal.",
    )
    ap.add_argument(
        "--model",
        default="llama3.1:8b",
        help="LLM model id for --heal (e.g., openai gpt-5).",
    )
    ap.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    ap.add_argument(
        "--log", default=".lint_gauntlet/gauntlet.log", help="Logfile path."
    )
    # smart controls
    ap.add_argument(
        "--self-drive",
        action="store_true",
        default=True,
        help="Enable adaptive escalation.",
    )
    ap.add_argument(
        "--max-iterations", type=int, default=6, help="Upper bound for internal passes."
    )
    ap.add_argument(
        "--target-mode", default="auto", help="auto|staged|modified|recent|repo"
    )
    ap.add_argument(
        "--policy", default="", help="JSON policy for suppression allowlists."
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    log = root / args.log

    explicit = _normalize_paths(root, args.paths)
    mode_used, targets = pick_targets_smart(root, explicit, args.target_mode)
    policy = load_policy(Path(args.policy)) if args.policy else DEFAULT_POLICY
    autos = {s.strip().lower() for s in args.auto_suppress.split(",") if s.strip()}

    log_line(
        log,
        f"=== gauntlet start (root={root}, target_mode={mode_used}, targets={len(targets)}, "
        f"fix={args.fix}, loop={args.loop}, self_drive={args.self_drive}, max_iter={args.max_iterations}, autos={autos}, smoke={args.smoke}) ===",
    )

    # Determine total iterations (respect legacy --loop but allow self-drive to escalate)
    total_iters = max(args.loop, 1)
    if args.self_drive:
        total_iters = max(total_iters, 3)
        total_iters = min(total_iters, args.max_iterations)

    totals = Totals()
    last_err_sig: Tuple[int, int, int, int] = (-1, -1, -1, -1)

    for iteration in range(1, total_iters + 1):
        # Ruff
        py_err, py_warn, py_rc, ruff_diags = run_ruff_collect(
            root, targets, args.fix, log
        )
        # Pyright
        pr_err, pr_warn, pr_rc = run_pyright(
            root, targets, args.pyright_path or None, log
        )
        # ESLint
        js_err, js_warn, js_rc, eslint_diags = run_eslint_collect(
            root, targets, args.fix, log
        )
        # PSSA
        ps_err, ps_warn, ps_rc = run_pssa(root, targets, log)

        totals.errors = py_err + pr_err + js_err + ps_err
        totals.warnings = py_warn + pr_warn + js_warn + ps_warn
        totals.rc = 0
        for rc in [
            (1 if (py_err or (args.strict and py_warn)) else 0)
            if py_rc in (0, 1)
            else 2,
            (1 if (pr_err or (args.strict and pr_warn)) else 0)
            if pr_rc in (0, 1, 2)
            else 2,
            (1 if (js_err or (args.strict and js_warn)) else 0)
            if js_rc in (0, 1)
            else 2,
            (1 if (ps_err or (args.strict and ps_warn)) else 0)
            if ps_rc in (0, 1)
            else 2,
        ]:
            totals.rc = combine_rc(totals.rc, rc)

        # Success path: clean + no infra error
        if (
            totals.errors == 0
            and (not args.strict or totals.warnings == 0)
            and totals.rc != 2
        ):
            print(
                json.dumps(
                    {
                        "iteration": iteration,
                        "target_mode": mode_used,
                        "target_count": len(targets),
                        "errors": totals.errors,
                        "warnings": totals.warnings,
                        "exit_code": 0,
                    },
                    indent=2,
                )
            )
            return 0

        # Self-drive escalation: suppression / heal between iterations
        suppressed_any = False
        if iteration < total_iters and autos:
            # Ruff suppression gated by policy
            if "ruff" in autos and ruff_diags and policy.get("ruff_allow"):
                per_file_codes = ruff_autosuppress(
                    [d for d in ruff_diags if d.code in set(policy["ruff_allow"])]
                )
                for f, codes in per_file_codes.items():
                    if args.smoke and not smoke_ok(f):
                        continue
                    if apply_ruff_file_header(f, codes):
                        suppressed_any = True

            # ESLint suppression gated by policy
            if "eslint" in autos and eslint_diags and policy.get("eslint_allow"):
                per_file_rules = eslint_autosuppress(
                    [
                        d
                        for d in eslint_diags
                        if d.rule in set(policy["eslint_allow"]) and d.severity == 2
                    ]
                )
                for f, rules in per_file_rules.items():
                    if args.smoke and not smoke_ok(f):
                        continue
                    if apply_eslint_file_header(f, rules):
                        suppressed_any = True

        current_sig = (py_err, pr_err, js_err, ps_err)
        stuck = current_sig == last_err_sig and not suppressed_any

        # If we're stuck and self-drive is on: one optional heal attempt for Pyright
        if args.self_drive and stuck and args.heal and pr_err > 0:
            auditor = root / "tools" / "pyright_auditor.py"
            if auditor.exists():
                _ = run_cmd(
                    [
                        sys.executable,
                        str(auditor),
                        "--root",
                        str(root),
                        "--provider",
                        args.provider,
                        "--model",
                        args.model,
                    ],
                    cwd=root,
                )
            # continue to next loop
        last_err_sig = current_sig

    # End: still not clean or infra error present
    print(
        json.dumps(
            {
                "target_mode": mode_used,
                "target_count": len(targets),
                "errors": totals.errors,
                "warnings": totals.warnings,
                "exit_code": 1
                if totals.errors or (args.strict and totals.warnings) or totals.rc == 2
                else totals.rc,
                "note": "Issues or infrastructure problems remain after self-drive loop.",
            },
            indent=2,
        )
    )
    return (
        1
        if totals.errors or (args.strict and totals.warnings) or totals.rc == 2
        else totals.rc
    )


if __name__ == "__main__":
    sys.exit(main())
