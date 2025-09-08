# __version__ = "1.0.0"
# __author__ = "CG & AI assistant"
# __creation_date__ = "2025-08-29"
# __modification_date__ = "2025-08-29"
# __purpose__ = "Cleans bullet markers and formatting around file names and normalizes spacing/symbols."
import os
import re

root_dir = r"C:\DevAgentZero"
report_path = os.path.join(root_dir, "index_audit_report.txt")

# Regex to detect file references in markdown (handles **filename.py**, bullet lists, etc.)
FILE_PATTERN = re.compile(r"([A-Za-z0-9_\-+ ]+\.(?:py|txt|md|docx))", re.IGNORECASE)


def clean_filename(name):
    """Cleans bullet markers and formatting around file names and normalizes spacing/symbols."""
    # Strip markdown and bullets
    cleaned = name.strip("*- ").strip()
    # Normalize multiple spaces and handle special symbols consistently
    cleaned = re.sub(r"\s+", " ", cleaned)  # collapse multiple spaces
    cleaned = cleaned.replace("–", "-")  # normalize en-dash to hyphen
    cleaned = cleaned.replace("+", "+")  # keep plus signs consistent
    return cleaned


def extract_listed_files(lines):
    """Extract file names mentioned in index lines (handles markdown bullets and bold)."""
    listed = set()
    for line in lines:
        matches = FILE_PATTERN.findall(line)
        for match in matches:
            # Clean and add
            listed.add(clean_filename(match))
    return listed


def audit_index_file(path):
    """Audits an index.txt file for structure and file listing accuracy."""
    output = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]

        # Capture first 10 lines (header preview)
        header_preview = "\n".join(lines[:10])

        # Check for canonical/supplemental sections
        has_canonical = any("Canonical" in line for line in lines)
        has_supplemental = any("Supplemental" in line for line in lines)

        output.append(f"--- {path} ---")
        output.append(f"Size: {os.path.getsize(path)} bytes")
        output.append("Header Preview:")
        output.append(header_preview)
        if not has_canonical:
            output.append("WARNING: Missing Canonical section")
        if not has_supplemental:
            output.append("WARNING: Missing Supplemental section")

        # Verify files listed vs actual files in folder
        folder = os.path.dirname(path)
        actual_files = {
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and f.lower() != "index.txt"
        }
        listed_files = extract_listed_files(lines)

        # Ignore example refs (e.g., 1.txt, 2.txt) used in cross-references
        listed_files = {f for f in listed_files if f not in ["1.txt", "2.txt"]}

        missing_files = listed_files - actual_files
        extra_files = actual_files - listed_files

        if missing_files:
            output.append(
                f"Files listed in index but missing in folder: {sorted(missing_files)}"
            )
        if extra_files:
            output.append(
                f"Files present in folder but NOT listed in index: {sorted(extra_files)}"
            )

        return "\n".join(output)

    except Exception as e:
        return f"--- {path} ---\nError reading file: {e}\n"


def run_audit():
    report = []
    total_indexes = 0
    total_warnings = 0

    print("Starting audit of index files...\n")

    for folder, subdirs, files in os.walk(root_dir):
        print(f"Scanning: {folder}")  # Progress feedback
        for file in files:
            if file.lower() == "index.txt":
                full_path = os.path.join(folder, file)
                result = audit_index_file(full_path)
                report.append(result)
                total_indexes += 1
                if "WARNING" in result or "missing" in result or "NOT listed" in result:
                    total_warnings += 1

    # Write combined report
    with open(report_path, "w", encoding="utf-8") as out:
        out.write("\n\n".join(report))
        out.write(
            f"\n\nSummary: {total_indexes} indexes scanned, {total_warnings} with warnings.\n"
        )

    print(f"\nAudit complete. Report saved to: {report_path}")


if __name__ == "__main__":
    run_audit()
