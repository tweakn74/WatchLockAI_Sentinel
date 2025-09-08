# __version__ = "1.0.0"
# __author__ = "CG & AI assistant"
# __creation_date__ = "2025-08-25"
# __modification_date__ = "2025-08-27"
# __purpose__ = "Utility script: run_auto_tasks.py"
"""
__version__ = "0.1.0"
Purpose: Contains the run_auto_tasks function
Last Modified: 2025-08-25 17:40:37
"""

import os
import subprocess
import logging

# Setup logging
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs"))
LOG_FILE = os.path.join(LOG_DIR, "run_auto_tasks.log")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)


def run_auto_tasks():
    todo_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "blueprint", "todo", "todo.txt")
    )

    # New: Open todo.txt on desktop
    try:
        logging.info(f"Attempting to open todo.txt: {todo_file_path}")
        subprocess.Popen(["start", todo_file_path], shell=True)
    except Exception as e:
        logging.error(f"Failed to open todo.txt: {e}")

    auto_section_start_marker = "--Auto, run this section at startup--"
    auto_section_end_marker = (
        "--Non Auto, this section below is a list and not for automation--"
    )

    logging.info(f"Reading todo file: {todo_file_path}")

    auto_tasks = []
    in_auto_section = False

    try:
        with open(todo_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line == auto_section_start_marker:
                    in_auto_section = True
                    continue
                if line == auto_section_end_marker:
                    in_auto_section = False
                    break  # Stop reading after the auto section ends

                if in_auto_section and line.startswith("*"):
                    auto_tasks.append(line[1:].strip())  # Remove the bullet point

        logging.info(f"Found auto tasks: {auto_tasks}")

        for task in auto_tasks:
            if "Run auto_header.py" in task:
                logging.info(f"Executing task: {task}")
                auto_header_script_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "tools", "auto_header.py")
                )
                try:
                    result = subprocess.run(
                        ["python", auto_header_script_path],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    logging.info(f"auto_header.py Stdout:\n{result.stdout}")
                    logging.info(f"auto_header.py Stderr:\n{result.stderr}")
                    logging.info(f"Task '{task}' completed successfully.")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Task '{task}' failed with error: {e}")
                    logging.error(f"Stderr: {e.stderr}")
                except FileNotFoundError:
                    logging.error(
                        "Python executable not found. Ensure Python is in your PATH."
                    )
            else:
                logging.warning(f"Unknown auto task: {task}. Skipping.")

    except FileNotFoundError:
        logging.error(f"Todo file not found at: {todo_file_path}")
    except Exception as e:
        logging.error(f"An error occurred while processing auto tasks: {e}")


if __name__ == "__main__":
    run_auto_tasks()
