#!/usr/bin/env python3
# Blocks committing user documents from blueprint/docs_in/*
import subprocess
import sys
import pathlib

DOC_DIRS = ["blueprint/docs_in", "blueprint/docs_in/converted_txt"]
DOC_EXTS = {
    ".pdf",
    ".doc",
    ".docx",
    ".rtf",
    ".odt",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
}


def staged_files():
    out = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], text=True, encoding="utf-8"
    )
    return [p.strip() for p in out.splitlines() if p.strip()]


def in_doc_area(p: str) -> bool:
    posix = pathlib.Path(p).as_posix()
    return any(posix == d or posix.startswith(d + "/") for d in DOC_DIRS)


def blocked(p: str) -> bool:
    posix = pathlib.Path(p).as_posix()
    if in_doc_area(posix):
        # Block everything under doc areas (documents & accidental code)
        return True
    return False


bad = [p for p in staged_files() if blocked(p)]
if bad:
    sys.stderr.write(
        "ERROR: The following staged files are blocked (user documents / doc areas):\n"
    )
    for b in bad:
        sys.stderr.write(f"  - {b}\n")
    sys.stderr.write(
        "\nMove documents outside the repo or add them to an ignored path.\n"
    )
    sys.exit(1)
sys.exit(0)
