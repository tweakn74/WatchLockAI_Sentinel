# ruff: noqa: E402
# File: tools/llm_mode.py
# Purpose: CLI to view/change DevAgentZero LLM mode and models
# Version: 1.0.0
# Author: Craig + GPT-5 Thinking
# Last Modified: 2025-08-09

import sys
from typing import List
from pathlib import Path

# Make relative imports work when run as a script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.llm_config import load_config, save_config, banner, SUPPORTED_MODES

USAGE = f"""\
DevAgentZero LLM Mode CLI

Usage:
  python tools/llm_mode.py show
  python tools/llm_mode.py set-mode <{"|".join(sorted(SUPPORTED_MODES))}>
  python tools/llm_mode.py set-fast <model_name>
  python tools/llm_mode.py set-strong <model_name>

Examples:
  python tools/llm_mode.py show
  python tools/llm_mode.py set-mode mistral
  python tools/llm_mode.py set-fast  mistral:7b-instruct-v0.2-q4_K_M
  python tools/llm_mode.py set-strong gpt-5-thinking
"""


def main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help", "help"}:
        print(USAGE)
        return 0

    cmd = argv[1]

    if cmd == "show":
        print(banner())
        print(load_config())
        return 0

    if cmd == "set-mode":
        if len(argv) < 3:
            print("Error: missing <mode>\n")
            print(USAGE)
            return 2
        mode = argv[2].lower()
        if mode not in SUPPORTED_MODES:
            print(
                f"Error: unsupported mode '{mode}'. Supported: {sorted(SUPPORTED_MODES)}"
            )
            return 2
        cfg = save_config(mode=mode)
        print(banner())
        print(cfg)
        return 0

    if cmd == "set-fast":
        if len(argv) < 3:
            print("Error: missing <model_name>\n")
            print(USAGE)
            return 2
        cfg = save_config(fast_model=argv[2])
        print(banner())
        print(cfg)
        return 0

    if cmd == "set-strong":
        if len(argv) < 3:
            print("Error: missing <model_name>\n")
            print(USAGE)
            return 2
        cfg = save_config(strong_model=argv[2])
        print(banner())
        print(cfg)
        return 0

    print(f"Unknown command: {cmd}\n")
    print(USAGE)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
