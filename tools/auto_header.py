from __future__ import annotations
import os
import re
import ast
import logging
from datetime import datetime
import json

# --- Configuration ---
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
LOG_FILE = os.path.join(LOG_DIR, "auto_header_process.log")
OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
MANIFEST_FILE = os.path.join(OUTPUTS_DIR, "header_manifest.json")
TODO_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "blueprint", "todo", "todo.txt")
)
EXCLUDE_PATTERNS = ["**/venv/**", "**/__pycache__/**", "**/node_modules/**"]

# --- Logging Setup ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)


def infer_purpose(file_path):
    """
    Infers the purpose of a Python file by analyzing its AST.
    Prioritizes main functions, then classes, then other functions.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)

        # Try to find purpose from docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    return docstring.split("\n")[0].strip()

        # Fallback to filename
        return f"Utility script: {os.path.basename(file_path)}"
    except Exception as e:
        logging.warning(
            f"Could not infer purpose for {file_path} due to error: {e}. Using filename as fallback."
        )
        return f"Utility script: {os.path.basename(file_path)}"


def generate_header_content(
    version="1.0.0",
    author="CG & AI assistant",
    creation_date=None,
    modification_date=None,
    purpose="No purpose specified.",
):
    """Generates the standard header content as comments."""
    if creation_date is None:
        creation_date = datetime.now().strftime("%Y-%m-%d")
    if modification_date is None:
        modification_date = datetime.now().strftime("%Y-%m-%d")

    header = f"""# __version__ = "{version}"
# __author__ = "{author}"
# __creation_date__ = "{creation_date}"
# __modification_date__ = "{modification_date}"
# __purpose__ = "{purpose}"
"""
    return header


def update_todo_txt(file_name, status):
    """Appends a status message to the todo.txt file."""
    try:
        with open(TODO_FILE, "r+", encoding="utf-8") as f:
            lines = f.readlines()
            # Find the target section
            for i, line in enumerate(lines):
                if (
                    "--Non Auto, this section below is a list and not for automation--"
                    in line
                ):
                    lines.insert(
                        i + 1,
                        f"{status} - {file_name} header {'added' if status == 'completed' else 'existed'}.\n",
                    )
                    f.seek(0)
                    f.writelines(lines)
                    logging.info(f"Updated todo.txt for {file_name}")
                    return
    except Exception as e:
        logging.error(f"Could not update todo.txt: {e}")


def manage_file_header(file_path, project_root):
    """
    Reads, checks, infers, and adds/updates headers for a given Python file.
    Returns a dictionary with file info and action taken.
    """
    now = datetime.now()
    modification_date = now.strftime("%Y-%m-%d")
    file_info = {
        "file_path": os.path.relpath(file_path, project_root),
        "action": "error",
        "message": "",
    }
    header_info = {
        "version": "1.0.0",
        "author": "CG & AI assistant",
        "creation_date": None,
        "modification_date": modification_date,
        "purpose": None,
    }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.readlines()

        header_found = False
        header_end_line = 0

        # Check for existing commented-out header
        for i, line in enumerate(original_content[:10]):
            if line.startswith("#"):
                if "__version__" in line:
                    match = re.search(r'__version__\s*=\s*"(.*?)"', line)
                    if match:
                        header_info["version"] = match.group(1)
                    header_found = True
                if "__author__" in line:
                    header_found = True
                if "__purpose__" in line:
                    match = re.search(r'__purpose__\s*=\s*"(.*?)"', line)
                    if match:
                        header_info["purpose"] = match.group(1)
                    header_found = True
                if "__creation_date__" in line:
                    match = re.search(r'__creation_date__\s*=\s*"(.*?)"', line)
                    if match:
                        header_info["creation_date"] = match.group(1)
                if line.strip() == "#":  # End of header block
                    header_end_line = i + 1
                    break

        # A simple check to see if the header is just a single line comment
        if header_found and header_end_line == 0:
            for i, line in enumerate(original_content[:10]):
                if not line.startswith("#"):
                    header_end_line = i
                    break

        if header_found and header_info["purpose"]:
            logging.info(
                f"Header already complete for {file_info['file_path']}. No changes made."
            )
            file_info["action"] = "skipped"
            file_info["message"] = "Header already complete."
            update_todo_txt(os.path.basename(file_path), "skipped")
        else:
            logging.info(
                f"Header missing or incomplete for {file_info['file_path']}. Generating new header."
            )

            if not header_info["creation_date"]:
                try:
                    ctime = os.path.getctime(file_path)
                    header_info["creation_date"] = datetime.fromtimestamp(
                        ctime
                    ).strftime("%Y-%m-%d")
                except Exception:
                    header_info["creation_date"] = modification_date

            if not header_info["purpose"]:
                header_info["purpose"] = infer_purpose(file_path)

            new_header_content = generate_header_content(**header_info)

            # Remove old header if it exists
            content_without_header = "".join(original_content[header_end_line:])
            new_file_content = new_header_content + content_without_header

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_file_content)

            file_info["action"] = "added_or_updated"
            file_info["message"] = "Header added or updated."
            logging.info(f"SUCCESS: Added/Updated header for {file_info['file_path']}")
            update_todo_txt(os.path.basename(file_path), "completed")

    except Exception as e:
        logging.error(f"FAILURE: Error processing {file_info['file_path']}: {e}")
        file_info["message"] = str(e)

    file_info.update(header_info)
    return file_info


def auto_header_main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    logging.info(f"Starting header management scan in: {project_root}")

    # Load manifest of already processed files
    processed_files = {}
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            try:
                manifest_data = json.load(f)
                for item in manifest_data:
                    processed_files[item["file_path"]] = item["action"]
            except json.JSONDecodeError:
                logging.warning("Manifest file is corrupted. Starting fresh.")

    python_files = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_root)

                # Skip excluded patterns and already skipped files
                if any(
                    re.match(pattern.replace("**", ".*"), relative_path)
                    for pattern in EXCLUDE_PATTERNS
                ):
                    continue
                if processed_files.get(relative_path) == "skipped":
                    continue
                python_files.append(file_path)

    manifest_data = []
    processed_count = 0
    for file_path in python_files:
        if processed_count >= 10:  # Process 10 files per run
            logging.info("Reached processing limit for this run.")
            break

        file_info = manage_file_header(file_path, project_root)
        manifest_data.append(file_info)
        processed_count += 1

    # Update manifest
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r+", encoding="utf-8") as f:
            try:
                existing_manifest = json.load(f)
                # Create a dictionary for quick lookups
                existing_files = {item["file_path"]: item for item in existing_manifest}
                for item in manifest_data:
                    existing_files[item["file_path"]] = item  # Add or update

                f.seek(0)
                f.truncate()
                json.dump(list(existing_files.values()), f, indent=4)
            except json.JSONDecodeError:
                with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                    json.dump(manifest_data, f, indent=4)
    else:
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)

    logging.info(f"Manifest successfully updated at {MANIFEST_FILE}")
    logging.info("Header management scan complete.")


if __name__ == "__main__":
    auto_header_main()
