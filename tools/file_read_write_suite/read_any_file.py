# File: tools/read_any_file.py
# Developer: Craig and Chatgpt 4o
# Location: tools/
# Version: 3.0.0
# Created or Last Modified Date: 2025-09-06
# Purpose: Ultimate, non-regressive, capability-aware reader for DevAgentZero.v2.
#          Reads .md, .txt, .json, .docx, .doc, .pdf (with OCR fallback), .rtf,
#          .html/.htm, .epub, images via OCR (.png/.jpg/.jpeg/.tif/.tiff/.bmp/.gif/.webp),
#          plus basic .xml, .csv, .yaml/.yml as text. Extensible via readers/.
#          Includes probing, caching, scaffolding, non-regression warnings.
# Recent Change: Major extension: RTF, HTML, EPUB, XML, CSV, YAML; content cache;
#                chunked reads; env flag defaults; atomic capabilities tracking.

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable, Dict, Iterable, List, Optional, Tuple
from xml.etree import ElementTree as ET

# Paths and files
THIS_DIR = os.path.dirname(__file__)
CAPS_FILE = os.path.join(THIS_DIR, "read_any_file.capabilities.json")
CACHE_DIR = os.path.join(THIS_DIR, ".cache")
CACHE_MAP = os.path.join(CACHE_DIR, "read_cache_index.json")

# Supported sets
TEXT_EXTS = {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".xml"}
CORE_EXTS = {
    ".md",
    ".txt",
    ".json",
    ".docx",
    ".doc",
    ".pdf",
    ".rtf",
    ".html",
    ".htm",
    ".epub",
    ".xml",
    ".csv",
    ".yaml",
    ".yml",
}
IMAGE_OCR_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
    ".gif",
    ".webp",
}

# Exit codes
EXIT_OK = 0
EXIT_RUNTIME = 1
EXIT_USAGE = 2


class ReadFileError(Exception):
    """Raised when file reading fails."""


# ----------------------------
# Utilities
# ----------------------------

def _is_windows() -> bool:
    return os.name == "nt"


def _which(cmd: str) -> Optional[str]:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    exts = [""] + os.environ.get("PATHEXT", ".EXE;.BAT;.CMD;.COM").split(os.pathsep)
    for p in paths:
        candidate = os.path.join(p, cmd)
        for ext in exts:
            target = candidate + ext
            if os.path.isfile(target) and os.access(target, os.X_OK):
                return target
    return None


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def _sha256_of_file(path: str, block: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(block)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _guard_file_size(path: str, max_bytes: Optional[int]) -> None:
    if max_bytes is None:
        return
    try:
        size = os.path.getsize(path)
    except OSError as e:
        raise ReadFileError(f"Cannot stat file: {e}") from e
    if size > max_bytes:
        raise ReadFileError(
            f"File exceeds max_bytes limit ({size} > {max_bytes}). Use --chunk-bytes."
        )


def _squeeze_blank_lines(lines: List[str]) -> List[str]:
    out: List[str] = []
    prev_blank = False
    for line in lines:
        is_blank = len(line.strip()) == 0
        if is_blank and prev_blank:
            continue
        out.append(line)
        prev_blank = is_blank
    return out


def _stdout_write(s: str, ascii_safe: bool = False) -> None:
    if ascii_safe:
        try:
            sys.stdout.write(s.encode("ascii", "backslashreplace").decode("ascii"))
        except Exception:
            sys.stdout.write(s)
    else:
        try:
            sys.stdout.write(s)
        except UnicodeEncodeError:
            sys.stdout.write(s.encode("ascii", "backslashreplace").decode("ascii"))
    sys.stdout.flush()


# ----------------------------
# Simple readers for text-ish formats
# ----------------------------

def _read_text(path: str, max_bytes: Optional[int]) -> str:
    _guard_file_size(path, max_bytes)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _read_json(path: str, max_bytes: Optional[int]) -> str:
    import json as _json
    _guard_file_size(path, max_bytes)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        try:
            data = _json.load(f)
        except _json.JSONDecodeError as e:
            raise ReadFileError(f"Invalid JSON: {e}") from e
    return _json.dumps(data, indent=2, ensure_ascii=True)


def _read_yaml(path: str, max_bytes: Optional[int]) -> str:
    # Read as plain text to avoid external deps. This is stable for LLM use.
    return _read_text(path, max_bytes)


def _read_csv(path: str, max_bytes: Optional[int]) -> str:
    # Emit as plain text. Pretty formatting would risk large memory use.
    return _read_text(path, max_bytes)


def _read_xml_plain(path: str, max_bytes: Optional[int]) -> str:
    _guard_file_size(path, max_bytes)
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        # Fall back to raw text if XML parse fails
        return _read_text(path, max_bytes)
    texts: List[str] = []

    def rec(node: ET.Element) -> None:
        if node.text:
            texts.append(node.text)
        for child in node:
            rec(child)
        if node.tail:
            texts.append(node.tail)

    rec(root)
    out = "\n".join(_squeeze_blank_lines([t.strip() for t in texts if t]))
    return out


# ----------------------------
# DOCX
# ----------------------------

def _read_docx(path: str, max_bytes: Optional[int]) -> str:
    _guard_file_size(path, max_bytes)
    try:
        with zipfile.ZipFile(path) as zf:
            try:
                xml_bytes = zf.read("word/document.xml")
            except KeyError as e:
                raise ReadFileError("word/document.xml not found in docx") from e
    except zipfile.BadZipFile as e:
        raise ReadFileError(f"Corrupt docx: {e}") from e

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        raise ReadFileError(f"XML parse error in docx: {e}") from e

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    out_lines: List[str] = []

    for p in root.findall(".//w:p", ns):
        texts = []
        for t in p.findall(".//w:t", ns):
            if t.text:
                texts.append(t.text)
        line = "".join(texts).strip()
        out_lines.append(line)

    return "\n".join(_squeeze_blank_lines(out_lines))


# ----------------------------
# DOC (legacy) strategies
# ----------------------------

def _read_doc_via_word_com(path: str, max_bytes: Optional[int]) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    try:
        import win32com.client  # type: ignore
        from win32com.client.dynamic import Dispatch  # type: ignore
    except Exception:
        return None

    try:
        word = Dispatch("Word.Application")
    except Exception:
        return None

    try:
        word.Visible = False  # type: ignore[attr-defined]
        doc = word.Documents.Open(
            path, ReadOnly=True, AddToRecentFiles=False, ConfirmConversions=False
        )  # type: ignore[attr-defined]
        try:
            text = doc.Content.Text  # type: ignore[attr-defined]
        finally:
            doc.Close(False)  # type: ignore[attr-defined]
        return text.replace("\r\n", "\n").replace("\r", "\n")
    except Exception:
        return None
    finally:
        try:
            word.Quit()  # type: ignore[attr-defined]
        except Exception:
            pass


def _read_doc_via_antiword(path: str, max_bytes: Optional[int]) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    exe = _which("antiword")
    if not exe:
        return None
    for args in (["-m", "UTF-8.txt", path], [path]):
        try:
            out = subprocess.check_output([exe] + args, stderr=subprocess.STDOUT)
            return out.decode("utf-8", errors="replace")
        except subprocess.CalledProcessError:
            continue
        except Exception:
            return None
    return None


def _read_doc_via_catdoc(path: str, max_bytes: Optional[int]) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    exe = _which("catdoc")
    if not exe:
        return None
    try:
        out = subprocess.check_output([exe, "-w", path], stderr=subprocess.STDOUT)
        return out.decode("utf-8", errors="replace")
    except Exception:
        return None


def _read_doc_via_soffice(path: str, max_bytes: Optional[int]) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    exe = _which("soffice")
    if not exe:
        return None
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            subprocess.check_call(
                [exe, "--headless", "--convert-to", "txt:Text", "--outdir", tmpdir, path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            base = os.path.splitext(os.path.basename(path))[0]
            candidate = os.path.join(tmpdir, base + ".txt")
            if os.path.exists(candidate):
                with open(candidate, "r", encoding="utf-8", errors="replace") as f:
                    return f.read()
        except Exception:
            return None
    return None


def _read_doc(path: str, max_bytes: Optional[int]) -> str:
    for strat in (
        _read_doc_via_word_com,
        _read_doc_via_antiword,
        _read_doc_via_catdoc,
        _read_doc_via_soffice,
    ):
        text = strat(path, max_bytes)
        if text:
            return text
    raise ReadFileError(
        "Unable to read .doc. Tried Word COM, antiword, catdoc, LibreOffice."
    )


# ----------------------------
# RTF minimal reader
# ----------------------------

_RTF_CTRL_RE = re.compile(r"\\[a-zA-Z]+(-?\\d+)?[ ]?")
_RTF_GROUP_RE = re.compile(r"[{}]")

def _read_rtf_minimal(path: str, max_bytes: Optional[int]) -> str:
    # Very simple RTF text extractor: strips control words and braces.
    # For high fidelity, install unrtf or use soffice conversion.
    raw = _read_text(path, max_bytes)
    # Remove control words
    s = _RTF_CTRL_RE.sub("", raw)
    # Remove braces
    s = _RTF_GROUP_RE.sub("", s)
    # Decode escaped hex like \'xx
    s = re.sub(r"\\'[0-9a-fA-F]{2}", "", s)
    # Collapse whitespace
    lines = [line.strip() for line in s.splitlines()]
    return "\n".join(_squeeze_blank_lines(lines))


def _read_rtf_via_unrtf(path: str, max_bytes: Optional[int]) -> Optional[str]:
    exe = _which("unrtf")
    if not exe:
        return None
    try:
        out = subprocess.check_output([exe, "--text", path], stderr=subprocess.STDOUT)
        return out.decode("utf-8", errors="replace")
    except Exception:
        return None


# ----------------------------
# HTML reader
# ----------------------------

class _HTMLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "div", "li"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        text = "".join(self._parts)
        lines = [ln.strip() for ln in text.splitlines()]
        return "\n".join(_squeeze_blank_lines(lines))


def _read_html(path: str, max_bytes: Optional[int]) -> str:
    raw = _read_text(path, max_bytes)
    stripper = _HTMLStripper()
    try:
        stripper.feed(raw)
    except Exception:
        return raw
    return stripper.get_text()


# ----------------------------
# EPUB reader (best effort)
# ----------------------------

def _read_epub(path: str, max_bytes: Optional[int]) -> str:
    _guard_file_size(path, max_bytes)
    try:
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith((".xhtml", ".html"))]
            if not names:
                # Fallback to container.xml search for spine would be heavy; return raw list
                return ""
            texts: List[str] = []
            for n in sorted(names):
                try:
                    data = zf.read(n).decode("utf-8", errors="replace")
                except Exception:
                    continue
                stripper = _HTMLStripper()
                try:
                    stripper.feed(data)
                    texts.append(stripper.get_text())
                except Exception:
                    texts.append(data)
            return "\n".join(_squeeze_blank_lines([t.strip() for t in texts if t.strip()]))
    except zipfile.BadZipFile:
        raise ReadFileError("Corrupt epub")


# ----------------------------
# PDF strategies
# ----------------------------

def _read_pdf_via_pdfminer(path: str, max_bytes: Optional[int]) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    try:
        from pdfminer.high_level import extract_text  # type: ignore
    except Exception:
        return None
    try:
        text = extract_text(path)
        if text and text.strip():
            return text
    except Exception:
        return None
    return None


def _read_pdf_via_pdftotext(path: str, max_bytes: Optional[int], timeout: int) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    exe = _which("pdftotext")
    if not exe:
        return None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_out:
            tmp_out_path = tmp_out.name
        try:
            subprocess.check_call([exe, "-layout", path, tmp_out_path], timeout=timeout)
            with open(tmp_out_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            return text
        finally:
            try:
                os.remove(tmp_out_path)
            except OSError:
                pass
    except Exception:
        return None


def _read_pdf_via_mutool(path: str, max_bytes: Optional[int], timeout: int) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    exe = _which("mutool")
    if not exe:
        return None
    try:
        out = subprocess.check_output([exe, "draw", "-F", "txt", path, "-"], timeout=timeout)
        return out.decode("utf-8", errors="replace")
    except Exception:
        return None


def _read_pdf_via_ocr(path: str, max_bytes: Optional[int], timeout: int) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    pdftoppm = _which("pdftoppm")
    tesseract = _which("tesseract")
    if not pdftoppm or not tesseract:
        return None
    all_text: List[str] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            base = os.path.join(tmpdir, "page")
            subprocess.check_call([pdftoppm, path, base, "-r", "300"], timeout=timeout)
            images = sorted(p for p in os.listdir(tmpdir) if p.startswith("page"))
            if not images:
                return None
            for img in images:
                img_path = os.path.join(tmpdir, img)
                try:
                    out = subprocess.check_output(
                        ["tesseract", img_path, "stdout", "-l", "eng"],
                        timeout=timeout,
                    )
                    all_text.append(out.decode("utf-8", errors="replace"))
                except Exception:
                    continue
        except Exception:
            return None
    text = "\n".join(all_text).strip()
    return text if text else None


# ----------------------------
# Image OCR
# ----------------------------

def _read_image_via_tesseract(path: str, max_bytes: Optional[int], timeout: int) -> Optional[str]:
    _guard_file_size(path, max_bytes)
    tesseract = _which("tesseract")
    if not tesseract:
        return None
    try:
        out = subprocess.check_output([tesseract, path, "stdout", "-l", "eng"], timeout=timeout)
        text = out.decode("utf-8", errors="replace")
        return text if text.strip() else None
    except Exception:
        return None


# ----------------------------
# Strategy registry
# ----------------------------

@dataclass
class Strategy:
    name: str
    func: Callable[..., Optional[str]]
    kind: str  # "native" or "external"


def _build_strategies(enable_ocr: bool, timeout: int) -> Dict[str, List[Strategy]]:
    strategies: Dict[str, List[Strategy]] = {
        ".md": [Strategy("text", lambda p, m: _read_text(p, m), "native")],
        ".txt": [Strategy("text", lambda p, m: _read_text(p, m), "native")],
        ".json": [Strategy("json", lambda p, m: _read_json(p, m), "native")],
        ".yaml": [Strategy("yaml", lambda p, m: _read_yaml(p, m), "native")],
        ".yml": [Strategy("yaml", lambda p, m: _read_yaml(p, m), "native")],
        ".csv": [Strategy("csv", lambda p, m: _read_csv(p, m), "native")],
        ".xml": [Strategy("xml", lambda p, m: _read_xml_plain(p, m), "native")],
        ".html": [Strategy("html", lambda p, m: _read_html(p, m), "native")],
        ".htm": [Strategy("html", lambda p, m: _read_html(p, m), "native")],
        ".docx": [Strategy("docx", lambda p, m: _read_docx(p, m), "native")],
        ".rtf": [
            Strategy("unrtf", _read_rtf_via_unrtf, "external"),
            Strategy("rtf_minimal", lambda p, m: _read_rtf_minimal(p, m), "native"),
        ],
        ".doc": [
            Strategy("word_com", _read_doc_via_word_com, "external"),
            Strategy("antiword", _read_doc_via_antiword, "external"),
            Strategy("catdoc", _read_doc_via_catdoc, "external"),
            Strategy("soffice", _read_doc_via_soffice, "external"),
        ],
        ".pdf": [
            Strategy("pdfminer", lambda p, m: _read_pdf_via_pdfminer(p, m), "external"),
            Strategy("pdftotext", lambda p, m: _read_pdf_via_pdftotext(p, m, timeout), "external"),
            Strategy("mutool", lambda p, m: _read_pdf_via_mutool(p, m, timeout), "external"),
        ] + ([Strategy("ocr", lambda p, m: _read_pdf_via_ocr(p, m, timeout), "external")] if enable_ocr else []),
        ".epub": [Strategy("epub", lambda p, m: _read_epub(p, m), "native")],
    }

    if enable_ocr:
        for ext in IMAGE_OCR_EXTS:
            strategies[ext] = [Strategy("tesseract", lambda p, m: _read_image_via_tesseract(p, m, timeout), "external")]

    # Dynamic plugin loader
    readers_dir = os.path.join(THIS_DIR, "readers")
    if os.path.isdir(readers_dir):
        for name in os.listdir(readers_dir):
            if not name.startswith("reader_") or not name.endswith(".py"):
                continue
            mod_path = os.path.join(readers_dir, name)
            try:
                module_name = f"tools.readers.{name[:-3]}" if __package__ else name[:-3]
                # Safe import via runpy to avoid sys.path issues
                import runpy
                mod = runpy.run_path(mod_path)
                for k, v in list(mod.items()):
                    if k.startswith("read_") and callable(v):
                        ext = "." + k.split("read_", 1)[1]
                        strategies.setdefault(ext, [])
                        strategies[ext].insert(0, Strategy(k, v, "native"))
            except Exception:
                continue

    return strategies


# ----------------------------
# Capabilities probing and non-regression bookkeeping
# ----------------------------

def _probe_capabilities(enable_ocr: bool, timeout: int) -> Dict[str, Dict[str, bool]]:
    strategies = _build_strategies(enable_ocr, timeout)
    caps: Dict[str, Dict[str, bool]] = {}
    for ext, strat_list in strategies.items():
        caps[ext] = {}
        for s in strat_list:
            available = True
            if s.name == "word_com":
                available = bool(_is_windows())
            caps[ext][s.name] = available
    # Executable checks
    if ".doc" in caps:
        caps[".doc"]["antiword"] = bool(_which("antiword"))
        caps[".doc"]["catdoc"] = bool(_which("catdoc"))
        caps[".doc"]["soffice"] = bool(_which("soffice"))
    if ".rtf" in caps:
        caps[".rtf"]["unrtf"] = bool(_which("unrtf"))
    if ".pdf" in caps:
        caps[".pdf"]["pdftotext"] = bool(_which("pdftotext"))
        caps[".pdf"]["mutool"] = bool(_which("mutool"))
        if enable_ocr:
            caps[".pdf"]["ocr"] = bool(_which("pdftoppm") and _which("tesseract"))
    if enable_ocr:
        for ext in IMAGE_OCR_EXTS:
            caps.setdefault(ext, {})
            caps[ext]["tesseract"] = bool(_which("tesseract"))
    # pdfminer availability
    try:
        from pdfminer.high_level import extract_text as _  # type: ignore
        caps.setdefault(".pdf", {})
        caps[".pdf"]["pdfminer"] = True
    except Exception:
        caps.setdefault(".pdf", {})
        caps[".pdf"]["pdfminer"] = False
    return caps


def _load_caps_file() -> Dict[str, Dict[str, bool]]:
    if not os.path.exists(CAPS_FILE):
        return {}
    try:
        with open(CAPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_caps_file(caps: Dict[str, Dict[str, bool]]) -> None:
    try:
        with open(CAPS_FILE, "w", encoding="utf-8") as f:
            json.dump(caps, f, indent=2, ensure_ascii=True)
    except Exception:
        pass


def _non_regression_warn(prev: Dict[str, Dict[str, bool]], new: Dict[str, Dict[str, bool]]) -> List[str]:
    warnings: List[str] = []
    for ext, prev_map in prev.items():
        new_map = new.get(ext, {})
        if ext not in new:
            warnings.append(f"Extension {ext} was previously present but is now missing.")
            continue
        for strat, prev_available in prev_map.items():
            if prev_available and not new_map.get(strat, False):
                warnings.append(
                    f"For {ext}, strategy {strat} was previously available but is now unavailable."
                )
    return warnings


# ----------------------------
# Caching and chunking
# ----------------------------

def _cache_key_for(path: str) -> str:
    try:
        st = os.stat(path)
    except OSError:
        return ""
    sig = f"{path}|{st.st_size}|{int(st.st_mtime)}"
    return hashlib.sha256(sig.encode("utf-8")).hexdigest()


def _load_cache_map() -> Dict[str, str]:
    if not os.path.exists(CACHE_MAP):
        return {}
    try:
        with open(CACHE_MAP, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache_map(m: Dict[str, str]) -> None:
    _ensure_dir(CACHE_DIR)
    try:
        with open(CACHE_MAP, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2, ensure_ascii=True)
    except Exception:
        pass


def _write_cache_blob(key: str, text: str) -> str:
    _ensure_dir(CACHE_DIR)
    p = os.path.join(CACHE_DIR, f"{key}.txt")
    try:
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        return ""
    return p


def _read_cache_blob(p: str) -> Optional[str]:
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _maybe_from_cache(path: str) -> Optional[str]:
    key = _cache_key_for(path)
    if not key:
        return None
    idx = _load_cache_map()
    blob = idx.get(key)
    if not blob:
        return None
    return _read_cache_blob(blob)


def _store_in_cache(path: str, text: str) -> None:
    key = _cache_key_for(path)
    if not key:
        return
    p = _write_cache_blob(key, text)
    if not p:
        return
    idx = _load_cache_map()
    idx[key] = p
    _save_cache_map(idx)


def _emit_chunk(text: str, chunk_bytes: int, chunk_index: int) -> str:
    if chunk_bytes <= 0:
        return text
    raw = text.encode("utf-8", errors="replace")
    total = len(raw)
    start = chunk_index * chunk_bytes
    if start >= total:
        return ""
    end = min(start + chunk_bytes, total)
    return raw[start:end].decode("utf-8", errors="replace")


# ----------------------------
# Reader core
# ----------------------------

@dataclass
class StrategyMeta:
    strategy: str
    ext: str


def read_file(
    path: str,
    max_bytes: Optional[int] = None,
    enable_ocr: bool = False,
    prefer: Optional[str] = None,
    timeout: int = 120,
    use_cache: bool = True,
) -> Tuple[str, Dict[str, str]]:
    if not path:
        raise ReadFileError("Empty path")
    if not os.path.exists(path):
        raise ReadFileError(f"File not found: {path}")
    if os.path.isdir(path):
        raise ReadFileError(f"Path is a directory: {path}")

    _, ext = os.path.splitext(path)
    ext = ext.lower()

    # Try cache first
    if use_cache:
        cached = _maybe_from_cache(path)
        if cached is not None and cached != "":
            return cached, {"strategy": "cache", "ext": ext}

    strategies = _build_strategies(enable_ocr, timeout)

    # Supported sanity
    if ext not in strategies and ext not in TEXT_EXTS and ext not in IMAGE_OCR_EXTS:
        raise ReadFileError(f"Unsupported extension: {ext}")

    # Simple text-ish formats
    if ext in {".md", ".txt"}:
        text = _read_text(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "text", "ext": ext}

    if ext == ".json":
        text = _read_json(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "json", "ext": ext}

    if ext in {".yaml", ".yml"}:
        text = _read_yaml(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "yaml", "ext": ext}

    if ext == ".csv":
        text = _read_csv(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "csv", "ext": ext}

    if ext == ".xml":
        text = _read_xml_plain(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "xml", "ext": ext}

    if ext in {".html", ".htm"}:
        text = _read_html(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "html", "ext": ext}

    if ext == ".epub":
        text = _read_epub(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "epub", "ext": ext}

    if ext == ".rtf":
        text = _read_rtf_via_unrtf(path, max_bytes)
        if text:
            _store_in_cache(path, text)
            return text, {"strategy": "unrtf", "ext": ext}
        text = _read_rtf_minimal(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "rtf_minimal", "ext": ext}

    # Preference reorder
    strat_chain = strategies.get(ext, [])
    if prefer:
        for i, s in enumerate(strat_chain):
            if s.name == prefer:
                strat_chain.insert(0, strat_chain.pop(i))
                break

    if ext == ".docx":
        text = _read_docx(path, max_bytes)
        _store_in_cache(path, text)
        return text, {"strategy": "docx", "ext": ext}

    if ext == ".doc":
        for s in strat_chain:
            text_opt = s.func(path, max_bytes)
            if text_opt:
                _store_in_cache(path, text_opt)
                return text_opt, {"strategy": s.name, "ext": ext}
        raise ReadFileError(
            "No working .doc strategy. Install Word+pywin32, antiword, catdoc, or LibreOffice."
        )

    if ext == ".pdf":
        text = None
        for s in strat_chain:
            text = s.func(path, max_bytes)
            if text:
                break
        if not text:
            text = _read_pdf_via_ocr(path, max_bytes, timeout) if enable_ocr else None
        if not text:
            raise ReadFileError(
                "Unable to read .pdf. Install pdfminer.six, Xpdf pdftotext, MuPDF mutool, "
                "or enable OCR with Tesseract and pdftoppm."
            )
        _store_in_cache(path, text)
        return text, {"strategy": "pdf", "ext": ext}

    if ext in IMAGE_OCR_EXTS:
        if not enable_ocr:
            raise ReadFileError("Image OCR requires --enable-ocr")
        text_opt = _read_image_via_tesseract(path, max_bytes, timeout)
        if text_opt:
            _store_in_cache(path, text_opt)
            return text_opt, {"strategy": "tesseract", "ext": ext}
        raise ReadFileError("Tesseract not available or OCR failed")

    raise ReadFileError(f"Unhandled extension: {ext}")


# ----------------------------
# Self-test and scaffolding
# ----------------------------

def _self_test(workspace_root: str) -> Tuple[bool, str]:
    try:
        os.makedirs(workspace_root, exist_ok=True)
        tmp_txt = os.path.join(workspace_root, ".read_file_selftest.txt")
        tmp_json = os.path.join(workspace_root, ".read_file_selftest.json")

        with open(tmp_txt, "w", encoding="utf-8") as f:
            f.write("selftest-ok")

        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump({"ok": True, "n": 1}, f)

        txt_out, meta1 = read_file(tmp_txt, use_cache=False)
        json_out, meta2 = read_file(tmp_json, use_cache=False)

        if "selftest-ok" not in txt_out:
            return False, "Text roundtrip failed"
        if '"ok": true' not in json_out.replace(" ", "").lower():
            return False, "JSON pretty print failed"

        try:
            os.remove(tmp_txt)
            os.remove(tmp_json)
        except OSError:
            pass

        return True, f"Self-test passed using strategies: {meta1.get('strategy')}, {meta2.get('strategy')}"
    except Exception as e:
        return False, f"Self-test error: {e}"


def _scaffold_reader(ext: str) -> str:
    ext = ext.lower().strip()
    if not ext.startswith("."):
        ext = "." + ext
    readers_dir = os.path.join(THIS_DIR, "readers")
    os.makedirs(readers_dir, exist_ok=True)
    target = os.path.join(readers_dir, f"reader_{ext[1:]}.py")
    if os.path.exists(target):
        return f"Reader already exists: {target}"
    template = f'''"""
Reader stub for {ext}. Fill in strategy functions and update registry as needed.
ASCII only in this file. Avoid external dependencies unless necessary.
"""

from typing import Optional

def read_{ext[1:]}(path: str, max_bytes: Optional[int]) -> Optional[str]:
    # TODO: implement robust extraction for {ext}
    # Return None to allow fallback to other strategies
    return None
'''
    with open(target, "w", encoding="utf-8") as f:
        f.write(template)
    return f"Scaffold created: {target}"


# ----------------------------
# CLI
# ----------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read a file and emit plain text. Broad format support with fallbacks and OCR."
    )
    parser.add_argument("--path", type=str, help="Relative or absolute path to file to read")
    parser.add_argument("--max-bytes", type=int, default=None, help="Max allowed size before abort")
    parser.add_argument("--self-test", action="store_true", help="Run a local sanity test")
    parser.add_argument("--probe", action="store_true", help="Probe environment and save capabilities.json")
    parser.add_argument("--list", action="store_true", help="List extensions and strategies")
    parser.add_argument("--enable-ocr", action="store_true", help="Enable OCR for PDF and images")
    parser.add_argument("--prefer", type=str, default=None, help="Preferred strategy name")
    parser.add_argument("--timeout", type=int, default=120, help="Subprocess timeout seconds")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON envelope")
    parser.add_argument("--ascii", dest="ascii_safe", action="store_true", help="Force ASCII-safe output")
    parser.add_argument("--cwd", type=str, default=".", help="Working directory for relative paths")
    parser.add_argument("--scaffold", type=str, default=None, help="Scaffold reader for an extension, e.g., .rtf")
    parser.add_argument("--chunk-bytes", type=int, default=0, help="If >0, emit chunk bytes of output")
    parser.add_argument("--chunk-index", type=int, default=0, help="Chunk index when using chunked output")
    parser.add_argument("--no-cache", action="store_true", help="Disable read cache")
    # Env defaults
    env_enable_ocr = os.environ.get("READ_ANY_FILE_ENABLE_OCR", "").lower() in {"1", "true", "yes"}
    env_cache = os.environ.get("READ_ANY_FILE_CACHE", "1").lower() not in {"0", "false", "no"}

    args = parser.parse_args(argv)

    if args.scaffold:
        msg = _scaffold_reader(args.scaffold)
        _stdout_write(msg + "\n", ascii_safe=args.ascii_safe)
        return EXIT_OK

    enable_ocr = bool(args.enable_ocr or env_enable_ocr)
    use_cache = not args.no_cache and env_cache
    timeout = int(args.timeout)

    if args.probe or args.list:
        caps_new = _probe_capabilities(enable_ocr=enable_ocr, timeout=timeout)
        caps_prev = _load_caps_file()
        warnings = _non_regression_warn(caps_prev, caps_new)
        if args.probe:
            _save_caps_file(caps_new)
        lines: List[str] = []
        lines.append("Capabilities:")
        for ext in sorted(caps_new.keys()):
            methods = [f"{k}={str(v).lower()}" for k, v in sorted(caps_new[ext].items())]
            lines.append(f"  {ext}: " + ", ".join(methods))
        if warnings:
            lines.append("Non-regression warnings:")
            for w in warnings:
                lines.append(f"  - {w}")
        _stdout_write("\n".join(lines) + "\n", ascii_safe=args.ascii_safe)
        return EXIT_OK

    if args.self_test:
        ok, msg = _self_test(args.cwd)
        _stdout_write(msg + "\n", ascii_safe=args.ascii_safe)
        return EXIT_OK if ok else EXIT_USAGE

    if not args.path:
        _stdout_write("Error: --path is required unless probe/list/self-test/scaffold is used.\n", ascii_safe=True)
        return EXIT_USAGE

    try:
        target = args.path
        if not os.path.isabs(target):
            target = os.path.normpath(os.path.join(args.cwd, target))
        text, meta = read_file(
            target,
            max_bytes=args.max_bytes,
            enable_ocr=enable_ocr,
            prefer=args.prefer,
            timeout=timeout,
            use_cache=use_cache,
        )
        # Chunking support for huge outputs
        if args.chunk_bytes and args.chunk_bytes > 0:
            text = _emit_chunk(text, args.chunk_bytes, args.chunk_index)

        if args.as_json:
            payload = {"text": text, "meta": {"path": target, **meta}}
            _stdout_write(json.dumps(payload, ensure_ascii=True), ascii_safe=True)
        else:
            if not text.endswith("\n"):
                text += "\n"
            _stdout_write(text, ascii_safe=args.ascii_safe)
        return EXIT_OK
    except ReadFileError as e:
        _stdout_write(f"Read error: {e}\n", ascii_safe=True)
        return EXIT_USAGE
    except Exception as e:
        msg = textwrap.fill(f"Unexpected error: {e}", width=100)
        _stdout_write(msg + "\n", ascii_safe=True)
        return EXIT_RUNTIME


if __name__ == "__main__":
    sys.exit(main())
