"""Module: tools/convert_to_text.py
Auto-added docstring to aid static analysis and navigation.
"""
# File: convert_to_text.py
# Location: tools/
# Developer: ChatGPT (for CG)
# Version: 1.3.0
# Last Modified: 2025-08-25 15:40 ET
# Purpose: Recursively convert documents under blueprint/docs_in to .txt (plain UTF-8),
#          mirroring folder structure into .../converted_txt for ingestion.
# Most Recent Change: Replace direct imports with guarded lazy imports + type ignores to
#                     eliminate Pylance reportMissingImports; add robust logging and idempotency.

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

# === Configuration ===
INPUT_DIR = Path(r"C:\Users\craig\DevAgentZero.V2\blueprint\docs_in")
OUTPUT_ROOT = INPUT_DIR / "converted_txt"
LOG_PATH = OUTPUT_ROOT / "_convert_to_text.log"

SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".rtf", ".txt", ".md", ".odt"}
RECURSIVE = True  # set False if you want only top-level

# === Logging setup ===
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(console)


# === Utility: safe read with chardet fallback ===
def read_text_best_effort(file_path: Path) -> str:
    """
    Read a text-like file (.txt, .md) using UTF-8, then chardet if needed.
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception:
        try:
            # Lazy import to avoid Pylance noise if not installed
            import chardet  # type: ignore[import-not-found]

            raw = file_path.read_bytes()
            enc = chardet.detect(raw).get("encoding") or "utf-8"
            return raw.decode(enc, errors="replace")
        except Exception as e:
            raise RuntimeError(f"Failed text decode: {e}")


def file_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# === Converters (each returns plain text) ===


def convert_docx(path: Path) -> str:
    try:
        import docx  # type: ignore[import-not-found]
    except Exception as e:
        raise RuntimeError("Missing dependency: python-docx") from e

    try:
        doc = docx.Document(str(path))
        parts = []
        for para in doc.paragraphs:
            parts.append(para.text)
        # tables (optional but handy)
        for tbl in doc.tables:
            for row in tbl.rows:
                row_text = [cell.text for cell in row.cells]
                parts.append("\t".join(row_text))
        return "\n".join(parts).strip()
    except Exception as e:
        raise RuntimeError(f"DOCX parse error: {e}")


def convert_pdf(path: Path) -> str:
    try:
        from pdfminer.high_level import extract_text  # type: ignore[import-not-found]
    except Exception as e:
        raise RuntimeError("Missing dependency: pdfminer.six") from e

    try:
        text = extract_text(str(path)) or ""
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"PDF parse error: {e}")


def convert_rtf(path: Path) -> str:
    try:
        from striprtf.striprtf import rtf_to_text  # type: ignore[import-not-found]
    except Exception as e:
        raise RuntimeError("Missing dependency: striprtf") from e

    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        return (rtf_to_text(raw) or "").strip()
    except Exception as e:
        raise RuntimeError(f"RTF parse error: {e}")


def convert_odt(path: Path) -> str:
    try:
        from odf.opendocument import load  # type: ignore[import-not-found]
        from odf import text as odf_text  # type: ignore[import-not-found]
        from odf import teletype  # type: ignore[import-not-found]
    except Exception as e:
        raise RuntimeError("Missing dependency: odfpy") from e

    try:
        doc = load(str(path))
        paragraphs = doc.getElementsByType(odf_text.P)
        parts = [teletype.extractText(p) for p in paragraphs]
        return "\n".join(parts).strip()
    except Exception as e:
        raise RuntimeError(f"ODT parse error: {e}")


def passthrough_text(path: Path) -> str:
    try:
        return read_text_best_effort(path).strip()
    except Exception as e:
        raise RuntimeError(f"Text read error: {e}")


# Map extension to converter
CONVERTERS: Dict[str, Callable[[Path], str]] = {
    ".docx": convert_docx,
    ".pdf": convert_pdf,
    ".rtf": convert_rtf,
    ".odt": convert_odt,
    ".txt": passthrough_text,
    ".md": passthrough_text,
}

# === Core processing ===


def relative_output_path(src: Path) -> Path:
    rel = src.relative_to(INPUT_DIR)
    out_dir = OUTPUT_ROOT / rel.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / (src.stem + ".txt")


def needs_write(out_path: Path, new_text: str) -> bool:
    if not out_path.exists():
        return True
    try:
        existing = out_path.read_text(encoding="utf-8")
    except Exception:
        return True
    return file_sha256(existing) != file_sha256(new_text)


def convert_one(src: Path) -> Tuple[Optional[Path], str]:
    ext = src.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return None, f"SKIP (unsupported ext): {src}"
    converter = CONVERTERS.get(ext)
    if not converter:
        return None, f"SKIP (no converter): {src}"
    try:
        text = converter(src)
        out_path = relative_output_path(src)
        if needs_write(out_path, text):
            out_path.write_text(text, encoding="utf-8", newline="\n")
            return out_path, f"OK  -> {src}  ->  {out_path}"
        else:
            return out_path, f"OK  (no change) {src}"
    except Exception as e:
        return None, f"ERROR: {src} :: {e}"


def iter_sources(root: Path) -> Tuple[Path, ...]:
    if not RECURSIVE:
        return tuple(p for p in root.iterdir() if p.is_file())
    return tuple(p for p in root.rglob("*") if p.is_file())


def main() -> None:
    if not INPUT_DIR.exists():
        logging.error(f"INPUT_DIR does not exist: {INPUT_DIR}")
        return
    total = 0
    ok = 0
    skipped = 0
    errors = 0
    for src in iter_sources(INPUT_DIR):
        total += 1
        out_path, msg = convert_one(src)
        if msg.startswith("OK"):
            ok += 1
            logging.info(msg)
        elif msg.startswith("SKIP"):
            skipped += 1
            logging.info(msg)
        else:
            errors += 1
            logging.error(msg)
    logging.info("-" * 72)
    logging.info(f"Done. total={total} ok={ok} skipped={skipped} errors={errors}")
    logging.info(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
