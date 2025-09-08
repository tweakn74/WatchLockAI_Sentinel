# File: ollama_debug_agent.py
# Location: root
# Developer: Craig & GPT-4
# Version: 1.1.0
# Last Modified: 2025-07-18
# Purpose: Check Ollama install health, model presence, and basic response flow
# Notes: Hardened and emoji-free with timeout fallback and prompt test

import subprocess
from rich.console import Console

console = Console()


def check_ollama():
    console.print("\n[ollama_debug] Running Ollama System Check")

    try:
        # Check if Ollama CLI is accessible
        version = subprocess.run(
            ["ollama", "--version"], capture_output=True, text=True
        )
        if version.returncode != 0:
            raise Exception("Ollama CLI not found or returned error.")
        console.print(f"[ollama_debug] Ollama CLI found: {version.stdout.strip()}")

        # Check if 'mistral' model is present
        list_models = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "mistral" not in list_models.stdout.lower():
            console.print(
                "[ollama_debug] 'mistral' model not found. Attempting to pull..."
            )
            pull = subprocess.run(
                ["ollama", "pull", "mistral"], capture_output=True, text=True
            )
            if pull.returncode != 0:
                raise Exception("Failed to pull 'mistral' model.")
            console.print("[ollama_debug] Successfully pulled 'mistral' model.")
        else:
            console.print("[ollama_debug] 'mistral' model is available.")

        # Test basic prompt
        prompt = "You are a Python assistant. List 3 basic file operations."
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise Exception("Ollama exited with an error.")
        if not result.stdout.strip():
            raise Exception("Ollama returned empty output.")

        console.print("[ollama_debug] Ollama responded successfully to test prompt.")
        console.print("[ollama_debug] Ollama is fully operational.")

    except subprocess.TimeoutExpired:
        console.print("[ollama_debug] Error: Ollama timed out during prompt test.")
    except Exception as e:
        console.print(f"[ollama_debug] Ollama check failed: {e}")


if __name__ == "__main__":
    check_ollama()
