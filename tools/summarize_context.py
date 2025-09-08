from __future__ import annotations

import re
import json
from pathlib import Path
from collections import Counter


ROOT = Path(__file__).resolve().parents[1]

# Folders to scan for context docs
CONTEXT_DIRS = [
    ROOT / "context",
    ROOT / "ingested",
]

EXTS = {".txt", ".md"}

# Very small stopword set; enough to make keywords readable
STOP = set(
    """
    the a an and or but if in into on onto at by for from of to with without within while
    is are was were be being been this that these those it its as not no yes you your we our they their
    about across after again against all also am any because before between both can could did do does doing down during each few
    further had has have having here how i just more most other out over same should some such than then there through under up very
    will would via per etc using use used using
    """.split()
)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for base in CONTEXT_DIRS:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in EXTS:
                # Heuristic: only include text-like context under blueprint/docs_in/converted_txt, plus any MD
                rel = p.relative_to(ROOT).as_posix()
                if (
                    "/converted_txt/" in rel
                    or p.suffix.lower() == ".md"
                    or "/context/" in rel
                ):
                    files.append(p)
    return sorted(files)


def clean_text(s: str) -> str:
    # Normalize whitespace
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s


def top_keywords(text: str, k: int = 12) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}", text)
    tokens = [t.lower() for t in tokens]
    cnt = Counter(t for t in tokens if t not in STOP and len(t) > 2)
    return [w for w, _ in cnt.most_common(k)]


def first_heading_or_title(text: str, default: str = "(untitled)") -> str:
    # Use first non-empty line; prefer lines that look like titles
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # Trim markdown heading markers
        s = re.sub(r"^#+\s*", "", s)
        return s[:160]
    return default


def first_paragraph(text: str, max_chars: int = 500) -> str:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paras:
        return ""
    p = paras[0]
    return (p[: max_chars - 3] + "...") if len(p) > max_chars else p


def summarize_files(files: list[Path]) -> dict:
    summaries = []
    corpus_counter = Counter()
    total_words = 0

    for p in files:
        try:
            txt = clean_text(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue

        words = re.findall(r"\w+", txt)
        total_words += len(words)
        corpus_counter.update(
            w.lower() for w in words if w.lower() not in STOP and len(w) > 2
        )

        title = first_heading_or_title(txt, default=p.stem)
        para = first_paragraph(txt)
        keys = top_keywords(txt, 12)

        summaries.append(
            {
                "path": p.relative_to(ROOT).as_posix(),
                "title": title,
                "words": len(words),
                "keywords": keys,
                "blurb": para,
            }
        )

    summaries.sort(key=lambda x: (-x["words"], x["path"]))

    return {
        "doc_count": len(summaries),
        "total_words": total_words,
        "top_corpus_terms": [w for w, _ in corpus_counter.most_common(50)],
        "docs": summaries,
    }


def to_markdown(report: dict) -> str:
    lines: list[str] = []
    lines.append("# DevAgentZero Context Documents — Summary Index")
    lines.append("")
    lines.append(
        f"Documents: {report['doc_count']}  |  Total words (approx): {report['total_words']}"
    )
    lines.append("")
    if report.get("top_corpus_terms"):
        top = ", ".join(report["top_corpus_terms"][:30])
        lines.append(f"Top corpus terms: {top}")
        lines.append("")

    lines.append("## Documents")
    for d in report.get("docs", [])[:500]:  # hard cap for file size
        lines.append(f"- Path: `{d['path']}`")
        lines.append(f"  - Title: {d['title']}")
        lines.append(f"  - Words: {d['words']}")
        if d.get("keywords"):
            lines.append(f"  - Keywords: {', '.join(d['keywords'][:12])}")
        if d.get("blurb"):
            one = d["blurb"].replace("\n", " ")
            lines.append(f"  - Blurb: {one}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    files = iter_files()
    report = summarize_files(files)
    out_md = ROOT / "CONTEXT_SUMMARY.md"
    out_json = ROOT / "CONTEXT_SUMMARY.json"
    out_md.write_text(to_markdown(report), encoding="utf-8")
    out_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote {out_md} and {out_json} ({report['doc_count']} docs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
