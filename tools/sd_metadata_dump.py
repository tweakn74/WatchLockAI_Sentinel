# ruff: noqa: E402
from __future__ import annotations

"""Module: tools/sd_metadata_dump.py
Auto-added docstring to aid static analysis and navigation.
"""
# sd_metadata_dump.py  -- self-installing edition
# Scans a folder for PNG/JPG/JPEG/WEBP, extracts Stable Diffusion PNG text chunks
# and JPEG/WEBP EXIF, writes a CSV report + per-image _metadata.txt sidecars.

import os
import re
import csv
import sys
import json
from datetime import datetime
from typing import Dict, Any

# --- Auto-install required packages if missing -------------------------------
import subprocess


def install_if_missing(pip_name: str, import_name: str = None):
    """Install a package by pip_name if import import_name fails."""
    mod = import_name or pip_name
    try:
        __import__(mod)
    except ImportError:
        print(f"[INFO] Installing missing package: {pip_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])


# pillow is imported as PIL; piexif is imported as piexif
install_if_missing("pillow", "PIL")
install_if_missing("piexif", "piexif")

from PIL import Image, PngImagePlugin, UnidentifiedImageError
import piexif
# ---------------------------------------------------------------------------

SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}

PARAM_KV_RE = re.compile(
    r"""
    (?:
      ^ | ,\s*
    )
    (?P<key>
      Steps|Sampler|CFG\s*scale|CFG|Seed|Model|Model\s+hash|Model\s+hashes|Clip\s+skip|
      Size|Hires\s+upsample|Hires\s+upscaler|Hires\s+steps|Denoising\s+strength|
      Version
    )
    \s*:\s*
    (?P<val>[^,]+)
""",
    re.IGNORECASE | re.VERBOSE,
)


def parse_a1111_parameters_block(s: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    m_prompt = re.search(
        r"(?i)(?:^|[\n\r])\s*Prompt:\s*(.*?)(?:\s*Negative\s*prompt:|[\n\r]Steps:|$)",
        s,
        re.DOTALL,
    )
    if m_prompt:
        out["prompt"] = m_prompt.group(1).strip()
    m_neg = re.search(r"(?i)Negative\s*prompt:\s*(.*?)(?:[\n\r]Steps:|$)", s, re.DOTALL)
    if m_neg:
        out["negative_prompt"] = m_neg.group(1).strip()

    if "prompt" not in out:
        up_to = re.search(r"(?i)(Negative\s*prompt:|[\n\r]Steps:)", s)
        out["prompt"] = s[: up_to.start()].strip() if up_to else s.strip()

    for m in PARAM_KV_RE.finditer(s):
        key = m.group("key").strip().lower()
        val = m.group("val").strip()
        key = (
            key.replace("cfg scale", "cfg")
            .replace("model hash", "model_hash")
            .replace("model hashes", "model_hashes")
            .replace("clip skip", "clip_skip")
            .replace("hires upsample", "hires_upsample")
            .replace("hires upscaler", "hires_upscaler")
            .replace("hires steps", "hires_steps")
            .replace("denoising strength", "denoise")
            .replace("size", "size")
            .replace("sampler", "sampler")
            .replace("steps", "steps")
            .replace("seed", "seed")
            .replace("model", "model")
        )
        out[key] = val

    if "size" in out:
        size = out["size"].lower().replace(" ", "")
        if "x" in size:
            w, h = size.split("x", 1)
            out["width"], out["height"] = w, h
    return out


def read_png_text(path: str) -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    im = Image.open(path)
    if isinstance(im, PngImagePlugin.PngImageFile):
        for k, v in im.info.items():
            # skip large binary blobs (icc profile etc.)
            if isinstance(v, (bytes, bytearray)) and len(v) > 4096:
                continue
            info[str(k)] = v if isinstance(v, str) else str(v)
    info["image_width"], info["image_height"] = im.size
    info["image_mode"] = im.mode
    return info


def read_exif_jpeg_webp(path: str) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}
    try:
        exif = piexif.load(path)
    except Exception:
        exif = None
    if exif:
        for ifd in ("0th", "Exif", "GPS"):
            for tag, val in exif.get(ifd, {}).items():
                name = piexif.TAGS[ifd].get(tag, {}).get("name", f"{ifd}:{tag}")
                if isinstance(val, bytes):
                    try:
                        val = val.decode("utf-8", "ignore")
                    except Exception:
                        val = repr(val)
                meta[name] = val
    with Image.open(path) as im:
        meta["image_width"], meta["image_height"] = im.size
        meta["image_mode"] = im.mode
        meta["format"] = im.format
    return meta


def ensure_sidecar(path: str, text: str):
    side = os.path.splitext(path)[0] + "_metadata.txt"
    with open(side, "w", encoding="utf-8") as f:
        f.write(text)


def process_image(path: str):
    ext = os.path.splitext(path)[1].lower()
    flat = {
        "file": path,
        "ext": ext,
        "has_sd_params": False,
        "prompt": "",
        "negative_prompt": "",
        "sampler": "",
        "steps": "",
        "cfg": "",
        "seed": "",
        "model": "",
        "width": "",
        "height": "",
        "software": "",
        "datetime": "",
    }
    raw: Dict[str, Any] = {}

    try:
        if ext == ".png":
            raw = read_png_text(path)
            params = None
            for k in ("parameters", "Parameters", "sd-metadata", "Software"):
                if k in raw and isinstance(raw[k], str) and raw[k]:
                    if k == "Software" and "automatic" not in raw[k].lower():
                        continue
                    params = raw[k]
                    break
            if params:
                parsed = parse_a1111_parameters_block(params)
                flat.update(
                    {
                        "has_sd_params": True,
                        "prompt": parsed.get("prompt", ""),
                        "negative_prompt": parsed.get("negative_prompt", ""),
                        "sampler": parsed.get("sampler", ""),
                        "steps": parsed.get("steps", ""),
                        "cfg": parsed.get("cfg", ""),
                        "seed": parsed.get("seed", ""),
                        "model": parsed.get("model", ""),
                        "width": parsed.get("width", raw.get("image_width", "")),
                        "height": parsed.get("height", raw.get("image_height", "")),
                    }
                )
                raw["parsed_parameters"] = parsed
            else:
                flat["width"] = raw.get("image_width", "")
                flat["height"] = raw.get("image_height", "")
        else:
            raw = read_exif_jpeg_webp(path)
            flat["width"] = raw.get("image_width", "")
            flat["height"] = raw.get("image_height", "")
            flat["software"] = str(raw.get("Software", ""))
            flat["datetime"] = str(raw.get("DateTimeOriginal", raw.get("DateTime", "")))
            # rare: prompts in EXIF comment/description
            for k in ("UserComment", "ImageDescription", "XPComment"):
                if k in raw and isinstance(raw[k], str):
                    lower = raw[k].lower()
                    if "prompt:" in lower or "negative prompt:" in lower:
                        flat["has_sd_params"] = True
                        flat["prompt"] = raw[k]
                        break
    except UnidentifiedImageError:
        raw = {"error": "Unidentified image"}
    except Exception as e:
        raw = {"error": repr(e)}
    return flat, raw


def walk_folder(root: str):
    rows = []
    sidecars = 0
    for dirpath, _, files in os.walk(root):
        for name in files:
            if os.path.splitext(name)[1].lower() in SUPPORTED:
                path = os.path.join(dirpath, name)
                flat, raw = process_image(path)
                rows.append(flat)
                # write sidecars for PNG (text chunks) and any file with params
                if flat["has_sd_params"] or flat["ext"] == ".png":
                    ensure_sidecar(
                        path,
                        json.dumps(
                            {"file": path, "summary": flat, "raw_metadata": raw},
                            indent=2,
                            ensure_ascii=False,
                        ),
                    )
                    sidecars += 1
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(root, f"sd_metadata_report_{stamp}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        cols = [
            "file",
            "ext",
            "has_sd_params",
            "prompt",
            "negative_prompt",
            "sampler",
            "steps",
            "cfg",
            "seed",
            "model",
            "width",
            "height",
            "software",
            "datetime",
        ]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(
        f"\nScanned: {len(rows)} image(s)\nSidecars written: {sidecars}\nCSV saved to: {csv_path}"
    )


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\craig\Downloads"
    if not os.path.isdir(root):
        print(f"Folder not found: {root}")
    else:
        walk_folder(root)
