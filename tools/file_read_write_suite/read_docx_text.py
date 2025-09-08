from __future__ import annotations

import re
import sys
from pathlib import Path
import zipfile


def read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        data = z.read("word/document.xml").decode("utf-8", errors="ignore")
    # strip xml tags
    text = re.sub(r"<[^>]+>", "\n", data)
    text = re.sub(r"\n+", "\n", text)
    return text


if __name__ == "__main__":
    p = Path(sys.argv[1])
    if not p.exists():
        print("MISSING")
        sys.exit(1)
    print(read_docx(p))
