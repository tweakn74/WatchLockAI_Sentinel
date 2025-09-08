# File: prompt_manager.py
# Location: C:\DevAgentZero\core
# Author: Craig (DevAgentZero Project)
# Version: 1.4.0
# Date: 2025-07-30
# Purpose: Manage DevAgentZero macros with enhanced validation, preflight readiness, and log management.
# Last Change Summary: Added preflight integration, macro version sync, improved input validation, and log rotation.

import os
import argparse
import re
from datetime import datetime


class PromptManager:
    """
    Handles loading and presenting macros stored in the prompts folder.
    Now includes preflight readiness checks, version validation, and improved robustness.
    """

    def __init__(
        self,
        prompts_path=r"C:\DevAgentZero\prompts",
        log_path=r"C:\DevAgentZero\logs\prompt_manager.log",
    ):
        self.prompts_path = prompts_path
        self.index_file = os.path.join(prompts_path, "index.txt")
        self.macro_pack_file = os.path.join(prompts_path, "devagentzero_macro_pack.txt")
        self.log_path = log_path
        self.macros = {}
        self.version = "unknown"
        self.load_macros()

    def _log(self, message, level="INFO"):
        """Append log entries with timestamp and basic severity to log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

            # Simple log rotation: keep max 100 KB
            if (
                os.path.exists(self.log_path)
                and os.path.getsize(self.log_path) > 102400
            ):
                archive_path = self.log_path + ".old"
                os.replace(self.log_path, archive_path)

            with open(self.log_path, "a") as log_file:
                log_file.write(f"[{timestamp}] [{level}] {message}\n")
        except Exception as e:
            print(f"[WARN] Logging failed: {e}")

    def load_macros(self):
        """Load macros and macro pack version from index file."""
        self.macros.clear()
        if not os.path.exists(self.index_file):
            print("[ERROR] Index file not found.")
            self._log("Index file missing.", "ERROR")
            return

        try:
            with open(self.index_file, "r") as file:
                content = file.read()

            # Extract version if present
            version_match = re.search(r"Version:\s*([\d\.]+)", content)
            if version_match:
                self.version = version_match.group(1)

            pattern = r"(\d+)\.\s+(.*?Macro)"
            for match in re.findall(pattern, content):
                self.macros[match[0]] = match[1]

            if not self.macros:
                print("[WARN] No macros detected in index.")
                self._log("Index parsed but contained no macros.", "WARN")

        except Exception as e:
            print(f"[ERROR] Failed to parse index file: {e}")
            self._log(f"Failed to parse index file: {e}", "ERROR")

    def _validate_macro_pack(self):
        """Validate macro pack structure and version alignment."""
        if not os.path.exists(self.macro_pack_file):
            print("[ERROR] Macro pack file not found.")
            self._log("Macro pack missing.", "ERROR")
            return False

        try:
            with open(self.macro_pack_file, "r") as file:
                content = file.read()

            # Check version sync
            if f"Version: {self.version}" not in content:
                print("[WARN] Macro pack version may be out of sync with index.")
                self._log("Version mismatch between index and macro pack.", "WARN")

            # Validate each macro exists
            for macro in self.macros.values():
                if macro.upper() not in content:
                    print(f"[ERROR] Macro section missing in pack: {macro}")
                    self._log(f"Macro missing: {macro}", "ERROR")
                    return False

        except Exception as e:
            print(f"[ERROR] Failed to validate macro pack: {e}")
            self._log(f"Validation error: {e}", "ERROR")
            return False

        return True

    def check_ready(self):
        """
        Preflight readiness check: verifies files and structure for DevAgentZero startup.
        Returns True if ready, False otherwise.
        """
        ready = os.path.exists(self.index_file) and os.path.exists(self.macro_pack_file)
        if not ready:
            self._log("PromptManager preflight check failed: missing files.", "ERROR")
        elif not self._validate_macro_pack():
            ready = False
        else:
            self._log("PromptManager preflight check passed.", "INFO")
        return ready

    def list_macros(self):
        """Display available macros."""
        if not self.macros:
            print("[INFO] No macros found in index.")
            return

        print("\n=== Available Macros ===")
        for key, name in self.macros.items():
            print(f"{key}. {name}")
        print("========================")

    def display_macro(self, macro_number):
        """Extract and display macro content by searching macro name in macro pack."""
        if macro_number not in self.macros:
            print("[ERROR] Invalid macro selection.")
            self._log(f"Invalid macro selection: {macro_number}", "ERROR")
            return

        macro_name = self.macros[macro_number]

        if not self._validate_macro_pack():
            return

        try:
            with open(self.macro_pack_file, "r") as file:
                content = file.read()

            section_header = macro_name.upper()
            start = content.find(section_header)
            if start == -1:
                print(f"[ERROR] Could not find macro section: {macro_name}")
                self._log(f"Missing section in macro pack: {macro_name}", "ERROR")
                return

            end = content.find(
                "============================================================",
                start + len(section_header),
            )
            print(content[start : end if end != -1 else len(content)])
            self._log(f"Displayed macro: {macro_name}", "INFO")

        except Exception as e:
            print(f"[ERROR] Failed to read macro content: {e}")
            self._log(f"Read macro error: {e}", "ERROR")

    def run_interactive(self):
        """Interactive mode for manual macro selection."""
        while True:
            self.list_macros()
            try:
                choice = (
                    input(
                        "Enter macro number to display (or 'q' to quit, 'r' to refresh): "
                    )
                    .strip()
                    .lower()
                )
            except (EOFError, KeyboardInterrupt):
                print("\n[INFO] Exiting PromptManager.")
                self._log("Exited via keyboard interrupt.", "INFO")
                break

            if choice == "q":
                print("[INFO] Exiting PromptManager.")
                break
            elif choice == "r":
                self.load_macros()
                print("[INFO] Macros reloaded.")
            else:
                self.display_macro(choice)

    def run_auto(self, macro_number):
        """Auto mode: directly display specified macro by number."""
        self.display_macro(macro_number)


def main():
    parser = argparse.ArgumentParser(description="Prompt Manager for DevAgentZero")
    parser.add_argument(
        "--auto", help="Automatically display macro by number (e.g., --auto 1)"
    )
    args = parser.parse_args()

    manager = PromptManager()

    if args.auto:
        manager.run_auto(args.auto)
    else:
        manager.run_interactive()


if __name__ == "__main__":
    main()
