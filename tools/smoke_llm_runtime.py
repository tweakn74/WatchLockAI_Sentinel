# ruff: noqa: E402
from __future__ import annotations

"""Module: tools/smoke_llm_runtime.py
Auto-added docstring to aid static analysis and navigation.
"""
# File: tools/smoke_llm_runtime.py
# Purpose: End-to-end smoke test for DevAgentZero LLM runtime with robust warm-up,
#          retries, controlled concurrency, progress bar, and trace discovery.
# Usage:   python tools/smoke_llm_runtime.py
# Author:  Craig + GPT-5 Thinking
# Version: 1.3.0
# Last Modified: 2025-08-09

import os
import sys
import time
import json
import asyncio
import pathlib
from typing import List, Tuple

# ---- Third-party ----
import httpx  # pip install httpx

# =============================================================================
# Path bootstrap (path-agnostic): climb up until a folder containing "core/" is found
# =============================================================================
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
for _ in range(6):
    if (ROOT / "core").is_dir():
        break
    ROOT = ROOT.parent
else:
    # If not found, fall back to two parents (legacy layout)
    ROOT = HERE.parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# =============================================================================
# Imports from project
# =============================================================================
os.environ.setdefault("DEVAZ_THINK_VIS", "on")

from core.llm_runtime import build_default_runtime, Budgets  # type: ignore

# llm_config compatibility: provider_mode may or may not exist (newer file has resolve_effective)
try:
    from core.llm_config import banner, provider_mode  # type: ignore
except ImportError:
    from core.llm_config import banner  # type: ignore

    provider_mode = None  # fallback handled below

# =============================================================================
# Settings (can be overridden via env)
# =============================================================================
# Batch degree for smoke (keep low for Windows/Ollama stability)
SMOKE_PAR = int(os.getenv("DEVAZ_SMOKE_PAR", "1"))  # 1 = serial (recommended)
# Time budgets
SINGLE_MS = int(os.getenv("DEVAZ_SMOKE_SINGLE_MS", "20000"))
CACHE_MS = int(os.getenv("DEVAZ_SMOKE_CACHE_MS", "20000"))
BATCH_MS = int(os.getenv("DEVAZ_SMOKE_BATCH_MS", "60000"))
# Ollama warm-up timeouts
SERVER_READY_S = int(os.getenv("DEVAZ_OLLAMA_SERVER_READY_S", "30"))
MODEL_READY_S = int(os.getenv("DEVAZ_OLLAMA_MODEL_READY_S", "180"))
# Model name for warm-up (must match your fast model in config/env)
WARM_MODEL = os.getenv("DEVAZ_FAST_MODEL", "mistral:7b-instruct-v0.2-q4_K_M")
OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# =============================================================================
# Lightweight smoke logger
# =============================================================================
SMOKE_LOG_DIR = ROOT / "logs"
SMOKE_LOG_DIR.mkdir(parents=True, exist_ok=True)
SMOKE_LOG_PATH = SMOKE_LOG_DIR / "smoke.log"


def log(msg: str) -> None:
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] [SMOKE] {msg}"
    print(line)
    try:
        with open(SMOKE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass  # best-effort


# =============================================================================
# Progress bar (inspired by your Whisper script)
# =============================================================================
def progress_bar(iteration: int, total: int, prefix: str = "", length: int = 30):
    total = max(total, 1)
    iteration = min(iteration, total)
    pct = f"{100 * (iteration / total):5.1f}"
    filled = int(length * iteration // total)
    bar = "#" * filled + "-" * (length - filled)
    sys.stdout.write(f"\r{prefix} |{bar}| {pct}%")
    sys.stdout.flush()
    if iteration >= total:
        print()


# =============================================================================
# Ollama warm-up (robust, with tolerant timeouts and retries)
# =============================================================================
async def wait_for_ollama(
    model: str = WARM_MODEL,
    base: str = OLLAMA_BASE,
    server_timeout_s: int = SERVER_READY_S,
    model_timeout_s: int = MODEL_READY_S,
) -> None:
    start = time.time()
    log(f"Ollama warm-up: waiting for server at {base}")
    # Wait for server (/api/tags) with short per-request timeout until server_timeout_s
    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            try:
                r = await client.get(f"{base}/api/tags")
                r.raise_for_status()
                break
            except Exception:
                if time.time() - start > server_timeout_s:
                    raise RuntimeError("Ollama not reachable on 127.0.0.1:11434")
                await asyncio.sleep(0.5)

    log(f"Ollama warm-up: loading model '{model}'")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are concise."},
            {"role": "user", "content": "ok"},
        ],
        "stream": False,
        "options": {"num_predict": 8},
    }
    # For model load we allow long per-request timeout and retry until model_timeout_s
    mstart = time.time()
    async with httpx.AsyncClient(timeout=60.0) as client:
        tries = 0
        while True:
            tries += 1
            try:
                r = await client.post(f"{base}/api/chat", json=payload)
                r.raise_for_status()
                log(f"Ollama warm-up: model responded on try {tries}")
                return
            except (httpx.ReadTimeout, httpx.ConnectError, httpx.HTTPStatusError) as e:
                if time.time() - mstart > model_timeout_s:
                    raise RuntimeError(
                        f"Ollama model warm-up failed after {tries} tries: {e}"
                    )
                await asyncio.sleep(0.5)


# =============================================================================
# Test helpers with retries (sequential fallback mindset)
# =============================================================================
async def ask_with_retries(
    rt, sys_msg: str, prompt: str, max_ms: int, tries: int = 3, pause_s: float = 0.5
) -> str:
    last_err = None
    for i in range(tries):
        try:
            return await rt.ask(
                sys_msg,
                prompt,
                prefer_fast=True,
                budgets=Budgets(max_ms=max_ms, max_in_tokens=4000, max_out_tokens=220),
            )
        except Exception as e:
            last_err = e
            log(f"ask_with_retries: attempt {i + 1} failed: {e}")
            await asyncio.sleep(pause_s)
    # If runtime returns partial in its own logic, we won't see an exception; otherwise, raise.
    raise RuntimeError(f"ask_with_retries: all {tries} attempts failed: {last_err}")


# =============================================================================
# Tests
# =============================================================================
def print_header() -> None:
    print("=" * 72)
    print("DevAgentZero LLM Smoke Test")
    print(banner())
    print("=" * 72)


async def test_single(rt) -> Tuple[str, float]:
    sys_msg = "You are a concise assistant."
    prompt = "Give me three bullet points explaining what a smoke test is."
    t0 = time.time()
    out = await ask_with_retries(rt, sys_msg, prompt, max_ms=SINGLE_MS, tries=3)
    dt_ms = (time.time() - t0) * 1000
    print(f"[single] {len(out)} chars in {int(dt_ms)} ms")
    return out, dt_ms


async def test_cache(rt) -> Tuple[str, float]:
    sys_msg = "You are a concise assistant."
    prompt = "Give me three bullet points explaining what a smoke test is."
    t0 = time.time()
    out = await ask_with_retries(rt, sys_msg, prompt, max_ms=CACHE_MS, tries=1)
    dt_ms = (time.time() - t0) * 1000
    print(
        f"[cache]  {len(out)} chars in {int(dt_ms)} ms (should be faster if cache hit)"
    )
    return out, dt_ms


async def test_batch(rt) -> Tuple[List[str], float]:
    """
    Deterministic batch test that avoids Ollama overload.
    - Respects SMOKE_PAR (default 1 = serial).
    - Shows a simple progress bar.
    """
    sys_msg = "You are a concise assistant."
    items = [
        (sys_msg, f"Write a 2-sentence test note for section {i}.") for i in range(6)
    ]

    t0 = time.time()
    outs: List[str] = []

    if SMOKE_PAR <= 1:
        # Serial (recommended for Windows + Ollama)
        total = len(items)
        for idx, (s, p) in enumerate(items, 1):
            out = await ask_with_retries(rt, s, p, max_ms=BATCH_MS, tries=2)
            outs.append(out)
            progress_bar(idx, total, prefix="batch")
    else:
        # Controlled parallelism (if you insist)
        sem = asyncio.Semaphore(SMOKE_PAR)

        async def one(pair):
            s, p = pair
            async with sem:
                return await ask_with_retries(rt, s, p, max_ms=BATCH_MS, tries=2)

        outs = await asyncio.gather(*(one(it) for it in items))

    dt_ms = (time.time() - t0) * 1000
    print(f"[batch ] {len(outs)} items in {int(dt_ms)} ms")
    return outs, dt_ms


# =============================================================================
# Trace discovery
# =============================================================================
def list_traces() -> List[pathlib.Path]:
    d = ROOT / "logs" / "reasoning"
    if not d.exists():
        print("[trace] no traces directory yet")
        return []
    files = sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    print(f"[trace] {len(files)} trace files at {d}")
    for p in files[:5]:
        print("       ", p.name)
    return files


# =============================================================================
# Main
# =============================================================================
async def main():
    # Warm-up only in mistral/ollama mode
    mode = None
    try:
        mode = (
            provider_mode()
            if provider_mode
            else os.getenv("DEVAZ_PROVIDER_MODE", "mistral").strip().lower()
        )
    except Exception:
        mode = os.getenv("DEVAZ_PROVIDER_MODE", "mistral").strip().lower()

    if mode in ("mistral", "ollama"):
        try:
            await wait_for_ollama()
        except Exception as e:
            log(f"Warm-up warning: {e} (continuing to run smoke anyway)")

    print_header()
    rt = build_default_runtime()

    # Single
    out1, dt1 = await test_single(rt)

    # Cache
    _out2, dt2 = await test_cache(rt)

    # Batch
    outs, dt3 = await test_batch(rt)

    # Summary
    print("-" * 72)
    summary = {
        "single_ms": int(dt1),
        "cache_ms": int(dt2),
        "batch_ms": int(dt3),
        "batch_items": len(outs),
        "single_chars": len(out1),
        "parallelism": SMOKE_PAR,
    }
    print(json.dumps(summary, indent=2))

    # Trace pointers
    files = list_traces()
    if files:
        print("\nOpen tools/trace_viewer.html in a browser and drag these in:")
        for p in files[:5]:
            print(" -", p)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted.")
