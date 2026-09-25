# File: generate_readme.py
# Location: root
# Developer: Craig & GPT-4
# Version: 1.2.0
# Last Modified: 2025-07-18
# Purpose: Create a basic README in the output folder per session
# Notes: Unicode/emojis removed; ASCII-safe and error-tolerant

from pathlib import Path

def create_readme_if_needed(session_id):
    try:
        out_folder = Path(f"outputs/{session_id}")
        readme = out_folder / "README.md"

        if readme.exists():
            return  # Avoid overwriting

        out_folder.mkdir(parents=True, exist_ok=True)

        content = f"""# DevAgent Zero

DevAgent Zero is a fully local, agentic AI software engineer powered by open-source LLMs like Mistral via Ollama. It generates project plans, builds code, executes it, and stores session memory -- all without using the cloud.

---

## Features

- AI dev planning powered by local Mistral-7B
- Step-by-step task execution and code generation
- Memory logging for all prompts, plans, and code output
- CLI interface (web UI coming soon)
- Fully offline and free -- no API keys, no cloud, no limits

---

## Requirements

- Python 3.10+
- Ollama installed
- Mistral model downloaded via: ollama run mistral

---

## Usage

From terminal:

    cd DevAgentZero
    python main.py

---

Files generated during this session:

"""

        # Write the base content
        with open(readme, "w", encoding="utf-8") as f:
            f.write(content)

            # Append file list
            for file in out_folder.glob("*.py"):
                f.write(f"- {file.name}\n")

    except Exception as e:
        print(f"[generate_readme] Error creating README for session {session_id}: {e}")

"""
