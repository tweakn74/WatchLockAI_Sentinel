from __future__ import annotations

import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, List, Optional


ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "target",
    ".ruff_cache",
}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)


def iter_py_files(base: Path) -> List[Path]:
    items: List[Path] = []
    for p in base.rglob("*.py"):
        if should_skip(p):
            continue
        # Skip very large generated or binary-like files by size
        try:
            if p.stat().st_size > 1_000_000:
                continue
        except Exception:
            pass
        items.append(p)
    return sorted(items)


def get_docstring_first_line(node: Any) -> Optional[str]:
    ds = ast.get_docstring(node)
    if not ds:
        return None
    line = ds.strip().splitlines()[0].strip()
    return line or None


def format_args(args: ast.arguments) -> str:
    parts: List[str] = []
    for a in args.posonlyargs:
        parts.append(a.arg)
    if args.posonlyargs:
        parts.append("/")
    for a in args.args:
        parts.append(a.arg)
    if args.vararg:
        parts.append("*" + args.vararg.arg)
    elif args.kwonlyargs:
        parts.append("*")
    for a in args.kwonlyargs:
        parts.append(a.arg + ("=?" if a in (args.kw_defaults or []) else ""))
    if args.kwarg:
        parts.append("**" + args.kwarg.arg)
    return ", ".join(parts)


@dataclass
class FuncInfo:
    name: str
    async_fn: bool
    args: str
    doc: Optional[str]
    lineno: int


@dataclass
class ClassInfo:
    name: str
    doc: Optional[str]
    lineno: int
    methods: List[FuncInfo]


@dataclass
class ModuleInfo:
    path: str
    doc: Optional[str]
    top_level_funcs: List[FuncInfo]
    classes: List[ClassInfo]
    lines: int


def analyze_module(path: Path) -> Optional[ModuleInfo]:
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return ModuleInfo(
            path=path.relative_to(ROOT).as_posix(),
            doc=None,
            top_level_funcs=[],
            classes=[],
            lines=src.count("\n") + 1,
        )

    mod_doc = get_docstring_first_line(tree)
    funcs: List[FuncInfo] = []
    classes: List[ClassInfo] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(
                FuncInfo(
                    name=node.name,
                    async_fn=isinstance(node, ast.AsyncFunctionDef),
                    args=format_args(node.args),
                    doc=get_docstring_first_line(node),
                    lineno=getattr(node, "lineno", 1),
                )
            )
        elif isinstance(node, ast.ClassDef):
            methods: List[FuncInfo] = []
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(
                        FuncInfo(
                            name=sub.name,
                            async_fn=isinstance(sub, ast.AsyncFunctionDef),
                            args=format_args(sub.args),
                            doc=get_docstring_first_line(sub),
                            lineno=getattr(sub, "lineno", 1),
                        )
                    )
            classes.append(
                ClassInfo(
                    name=node.name,
                    doc=get_docstring_first_line(node),
                    lineno=getattr(node, "lineno", 1),
                    methods=methods,
                )
            )

    return ModuleInfo(
        path=path.relative_to(ROOT).as_posix(),
        doc=mod_doc,
        top_level_funcs=funcs,
        classes=classes,
        lines=src.count("\n") + 1,
    )


def to_markdown(mods: List[ModuleInfo]) -> str:
    lines: List[str] = []
    lines.append("# Python Modules Index — DevAgentZero.V2")
    lines.append("")
    lines.append(f"Modules: {len(mods)}")
    lines.append("")
    for m in mods:
        lines.append(f"## `{m.path}`  (lines: {m.lines})")
        if m.doc:
            lines.append(f"- Doc: {m.doc}")
        if m.top_level_funcs:
            lines.append("- Functions:")
            for f in sorted(m.top_level_funcs, key=lambda x: x.lineno):
                sig = ("async " if f.async_fn else "") + f"def {f.name}({f.args})"
                doc = f.doc or ""
                lines.append(f"  - {sig} @L{f.lineno} — {doc}")
        if m.classes:
            lines.append("- Classes:")
            for c in sorted(m.classes, key=lambda x: x.lineno):
                lines.append(f"  - class {c.name} @L{c.lineno} — {c.doc or ''}")
                for meth in sorted(c.methods, key=lambda x: x.lineno):
                    sig = (
                        "async " if meth.async_fn else ""
                    ) + f"def {meth.name}({meth.args})"
                    lines.append(f"      - {sig} @L{meth.lineno} — {meth.doc or ''}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    mods: List[ModuleInfo] = []
    for p in iter_py_files(ROOT):
        mi = analyze_module(p)
        if mi is not None:
            mods.append(mi)

    out_md = ROOT / "PY_INDEX.md"
    out_json = ROOT / "PY_INDEX.json"
    out_md.write_text(to_markdown(mods), encoding="utf-8")
    out_json.write_text(
        json.dumps([asdict(m) for m in mods], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {out_md} and {out_json} ({len(mods)} modules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
