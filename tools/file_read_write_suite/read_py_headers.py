import os
import re


def read_py_headers():
    """
    Reads Python files to extract version, purpose, and last modification from headers.
    Assumes header information is in the first 20 lines of the file,
    and looks for patterns like:
    __version__ = "..."
    Purpose: ...
    Last Modified: ...
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Scanning Python files in: {project_root}\n")

    # Exclude venv and __pycache__ directories
    exclude_patterns = ["**/venv/**", "**/__pycache__/**"]

    python_files = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Check against exclude patterns
                if not any(
                    re.match(
                        pattern.replace("**", ".*"),
                        file_path.replace(project_root + os.sep, ""),
                    )
                    for pattern in exclude_patterns
                ):
                    python_files.append(file_path)

    for file_path in python_files:
        version = "N/A"
        purpose = "N/A"
        last_modified = "N/A"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [f.readline() for _ in range(20)]  # Read first 20 lines
                content = "".join(lines)

                version_match = re.search(r"__version__\s*=\s*[\"'](.*?)[\"']", content)
                if version_match:
                    version = version_match.group(1)

                purpose_match = re.search(r"Purpose:\s*(.*)", content, re.IGNORECASE)
                if purpose_match:
                    purpose = purpose_match.group(1).strip()

                modified_match = re.search(
                    r"Last Modified:\s*(.*)", content, re.IGNORECASE
                )
                if modified_match:
                    last_modified = modified_match.group(1).strip()

            print(f"--- {os.path.relpath(file_path, project_root)} ---")
            print(f"  Version: {version}")
            print(f"  Purpose: {purpose}")
            print(f"  Last Modified: {last_modified}\n")

        except Exception as e:
            print(f"Error reading {file_path}: {e}\n")


if __name__ == "__main__":
    read_py_headers()
