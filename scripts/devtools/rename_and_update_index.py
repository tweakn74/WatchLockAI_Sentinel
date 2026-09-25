import os
import re
import shutil
import datetime

# Toggle dry run (True = preview only, False = apply changes)
DRY_RUN = True

# Root directory for DevAgentZero blueprints
ROOT_DIR = r"C:\DevAgentZero\Blueprints"

# Target subfolders
TARGET_FOLDERS = [
    "architecture",
    "DevAgentZero_Foundations",
    "DevAgentZero_Foundations_Extended",
]


def normalize_name(filename):
    """Normalize file names: underscores, lowercase, simplified to 2-4 words."""
    name, ext = os.path.splitext(filename)
    name = name.lower()

    # Replace spaces, hyphens, +, parentheses with underscores
    name = re.sub(r"[ \-\+\(\)]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")

    # Limit to 4 words max
    parts = name.split("_")
    if len(parts) > 4:
        name = "_".join(parts[:4])

    return name + ext


def create_backup(folder):
    """Create timestamped backup folder and copy all files into it."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bu_path = os.path.join(folder, f"_bu_{timestamp}")
    if not os.path.exists(bu_path):
        os.makedirs(bu_path)

    # Copy everything into backup
    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)
        if os.path.isfile(full_path):
            shutil.copy2(full_path, bu_path)

    print(f"Backup created at: {bu_path}")
    return bu_path


def update_index(folder, old_name, new_name):
    """Update index.txt: comment out old entry and add new entry."""
    index_path = os.path.join(folder, "index.txt")
    if not os.path.exists(index_path):
        print(f"No index.txt found in {folder}, skipping index update.")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    pattern = rf"\b{re.escape(old_name)}\b"

    for line in lines:
        if re.search(pattern, line):
            updated_lines.append(f"### {line.strip()}  (old reference)\n")
            updated_lines.append(line.replace(old_name, new_name))
        else:
            updated_lines.append(line)

    if not DRY_RUN:
        with open(index_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)
    else:
        print(f"[Dry Run] Would update index: {old_name} -> {new_name}")


def rename_files_in_folder(folder):
    """Propose renames and handle confirmation + index updates."""
    proposals = []
    for file in os.listdir(folder):
        if file.lower() == "index.txt":
            continue
        full_path = os.path.join(folder, file)
        if os.path.isfile(full_path):
            new_name = normalize_name(file)
            if new_name != file:
                proposals.append((file, new_name))

    if not proposals:
        print(f"No rename needed in {folder}")
        return

    print(f"\nProposed renames for {folder}:")
    renamed_count = 0
    skipped_count = 0

    for old, new in proposals:
        print(f"{old} -> {new}")
        choice = input("Rename this file? (Y/n): ").strip().lower()
        if choice in ["", "y", "yes"]:
            if not DRY_RUN:
                os.rename(os.path.join(folder, old), os.path.join(folder, new))
                update_index(folder, old, new)
            else:
                print(f"[Dry Run] Would rename {old} -> {new}")
            renamed_count += 1
        else:
            print(f"Skipped: {old}")
            skipped_count += 1

    print(f"\nSummary for {folder}: {renamed_count} renamed, {skipped_count} skipped")


def process_blueprint_folders():
    """Process all target blueprint folders sequentially."""
    for subfolder in TARGET_FOLDERS:
        folder = os.path.join(ROOT_DIR, subfolder)
        if not os.path.exists(folder):
            print(f"Folder not found: {folder}")
            continue

        print(f"\nProcessing folder: {folder}")
        create_backup(folder)
        rename_files_in_folder(folder)

        proceed = input("\nProceed to next folder? (Y/n): ").strip().lower()
        if proceed in ["n", "no"]:
            break


if __name__ == "__main__":
    process_blueprint_folders()
