# ruff: noqa: E402
from __future__ import annotations

"""Module: tools/read_metadata.py
Auto-added docstring to aid static analysis and navigation.
"""
# read_metadata.py -- self-installing, PNG/JPEG metadata inspector

import sys
import os
import json
import subprocess


# --- Auto-install required packages if missing ---
def install_if_missing(pip_name: str, import_name: str = None):
    mod = import_name or pip_name
    try:
        __import__(mod)
    except ImportError:
        print(f"[INFO] Installing missing package: {pip_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])


install_if_missing("pillow", "PIL")
install_if_missing("piexif", "piexif")

from PIL import Image, PngImagePlugin
import piexif


def read_png_info(path):
    im = Image.open(path)
    info = {}
    # PNG text chunks (where SD often stores 'parameters')
    if isinstance(im, PngImagePlugin.PngImageFile):
        for k, v in im.info.items():
            # Keep as strings when possible
            info[k] = v if isinstance(v, str) else str(v)
    # Always include basic image info
    info.setdefault("image_width", im.size[0])
    info.setdefault("image_height", im.size[1])
    info.setdefault("image_mode", im.mode)
    return info


def read_jpeg_exif(path):
    try:
        exif_dict = piexif.load(path)
    except Exception:
        exif_dict = None

    out = {}
    if exif_dict:
        for ifd in ("0th", "Exif", "GPS", "1st"):
            for tag, val in exif_dict.get(ifd, {}).items():
                name = piexif.TAGS[ifd].get(tag, {}).get("name", f"{ifd}:{tag}")
                if isinstance(val, bytes):
                    try:
                        val = val.decode("utf-8", "ignore")
                    except Exception:
                        val = repr(val)
                out[name] = val

    # Always include PIL basics
    with Image.open(path) as im:
        out.setdefault("image_width", im.size[0])
        out.setdefault("image_height", im.size[1])
        out.setdefault("image_mode", im.mode)
        out.setdefault("format", im.format)
    return out


def main(path):
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return

    ext = os.path.splitext(path)[1].lower()
    print(f"\n=== {path} ===")

    if ext == ".png":
        info = read_png_info(path)
        if not info:
            print("No PNG text metadata found.")
        else:
            print(json.dumps(info, indent=2, ensure_ascii=False))
            # Common A1111 key:
            params = info.get("parameters")
            if params:
                print("\n--- Stable Diffusion parameters ---\n")
                print(params)

    elif ext in (".jpg", ".jpeg"):
        info = read_jpeg_exif(path)
        if not info:
            print("No EXIF found (or stripped).")
        else:
            print(json.dumps(info, indent=2, ensure_ascii=False))

    else:
        # Fallback: still show basics via PIL
        with Image.open(path) as im:
            basics = {
                "format": im.format,
                "image_width": im.size[0],
                "image_height": im.size[1],
                "image_mode": im.mode,
            }
        print(f"(Unsupported metadata type for {ext}; showing basics only)")
        print(json.dumps(basics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    p = (
        sys.argv[1]
        if len(sys.argv) > 1
        else r"C:\Users\craig\Downloads\best face _ body is deformed.jpeg"
    )
    main(p)
