# File: verify_env.py
# Author: DevAgentZero
# Version: 1.1.0
# Last Modified: 2025-07-18
# Purpose: Verify system environment, validate Python version, install missing packages if confirmed

import sys
import os
import subprocess
import importlib.util

REQUIRED_PACKAGES = [
    "flask",
    "flask_socketio",
    "flask_cors",
    "requests",
    "openai",
    "markdown",
    "tqdm",
    "psutil",
    "uuid",
    "python_dotenv",
    "orjson",
    "sse_starlette",
    "chromadb",
    "llama_index",
    "nomic",
    "transformers",
    "torch",
    "huggingface_hub",
    "google_auth",
]

RECOMMENDED_OLLAMA = True


def check_python_version():
    print("[CHECK] Python version:")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"[OK] Python {version.major}.{version.minor} detected.")
        return True
    print(f"[ERROR] Python 3.10+ is required. Found {version.major}.{version.minor}")
    return False


def check_requirements_file():
    if not os.path.exists("requirements.txt"):
        print("[WARNING] requirements.txt not found.")
        return False
    print("[OK] requirements.txt is present.")
    return True


def check_required_packages():
    print("\n[CHECK] Required Python packages:")
    missing = []
    for pkg in REQUIRED_PACKAGES:
        module_name = pkg.replace("-", "_").replace(".", "_")
        if not importlib.util.find_spec(module_name):
            print(f"[MISSING] {pkg}")
            missing.append(pkg)
        else:
            print(f"[OK] {pkg}")
    return missing


def install_missing_packages(missing):
    if not missing:
        return
    print("\nWould you like to auto-install the missing packages? [y/n]")
    choice = input(">>> ").strip().lower()
    if choice != "y":
        print("[INFO] Skipping installation. Please install manually.")
        return
    print(f"[INSTALLING] Installing: {', '.join(missing)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("[SUCCESS] Packages installed.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] pip failed: {e}")
        sys.exit(1)


def check_ollama():
    if not RECOMMENDED_OLLAMA:
        return True
    print("\n[CHECK] Ollama CLI:")
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            print(f"[OK] Ollama detected: {result.stdout.strip()}")
            return True
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print(
            "[WARNING] Ollama not found. Download it from https://ollama.com/download if required."
        )
        return False


def run_all_checks():
    print("\n=== DevAgentZero Environment Preflight Check ===\n")
    success = True

    success &= check_python_version()
    check_requirements_file()
    missing = check_required_packages()
    install_missing_packages(missing)
    check_ollama()

    print("\n=== Preflight Check Complete ===")
    if success and not missing:
        print("[SUCCESS] Environment is ready.")
    else:
        print("[WARNING] One or more issues remain.")


if __name__ == "__main__":
    run_all_checks()

# End of Script: verify_env.py
