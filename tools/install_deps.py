# File: install_deps.py
# Author: DevAgentZero
# Version: 1.0.0
# Last Modified: 2025-07-18
# Purpose: Install all required DevAgentZero dependencies from requirements.txt

import subprocess
import sys
import os


def install_requirements():
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"[ERROR] {requirements_file} not found.")
        sys.exit(1)

    try:
        print("[INFO] Installing dependencies from requirements.txt...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file]
        )
        print("[SUCCESS] All dependencies installed.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install requirements: {e}")
        sys.exit(1)


if __name__ == "__main__":
    install_requirements()

# End of Script: install_deps.py
