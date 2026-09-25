# File: mark_task_done.py
# Author: DevAgentZero
# Version: 1.1.0
# Last Modified: 2025-07-18
# Purpose: Mark one or more tasks as done in devagent_master_tasks.md using fuzzy matching and optional category

import argparse
import re
import shutil
import os
import datetime
import difflib

MD_FILE = "devagent_master_tasks.md"
BACKUP_FILE = "devagent_master_tasks_backup.md"
FUZZY_THRESHOLD = 0.6  # Match ratio


def backup_md():
    try:
        shutil.copyfile(MD_FILE, BACKUP_FILE)
        print(f"[INFO] Backup created: {BACKUP_FILE}")
    except Exception as e:
        print(f"[ERROR] Could not create backup: {e}")
        exit(1)


def update_timestamp(lines):
    for i, line in enumerate(lines):
        if line.strip().startswith("**Last Updated:**"):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines[i] = f"**Last Updated:** {now}  \n"
            return lines
    print("[WARNING] Timestamp line not found.")
    return lines


def find_matches(lines, keyword, category=None):
    matches = []
    current_category = None
    inside_category = False

    for i, line in enumerate(lines):
        if line.strip().startswith("## "):
            current_category = line.strip().replace("##", "").strip()
            inside_category = (
                category is None or current_category.lower() == category.lower()
            )
            continue

        match = re.match(r"- \[ \] \*\*(.*?)\*\*", line)
        if match and inside_category:
            task_title = match.group(1)
            similarity = difflib.SequenceMatcher(
                None, keyword.lower(), task_title.lower()
            ).ratio()
            if similarity >= FUZZY_THRESHOLD or keyword.lower() in task_title.lower():
                matches.append((i, task_title, similarity, current_category))

    return matches


def mark_tasks(lines, matches):
    changed = False
    for i, title, score, cat in matches:
        print(f"\n[FOUND in '{cat}'] -> {title}  (Similarity: {score:.2f})")
        confirm = input("Mark this task as done? (y/n): ").strip().lower()
        if confirm == "y":
            lines[i] = lines[i].replace("- [ ]", "- [x]", 1)
            changed = True
        else:
            print("Skipped.")
    return update_timestamp(lines) if changed else lines, changed


def save_file(lines):
    try:
        with open(MD_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("[SUCCESS] Markdown updated.")
    except Exception as e:
        print(f"[ERROR] Could not write to markdown file: {e}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Mark tasks as done in devagent_master_tasks.md using fuzzy keyword match."
    )
    parser.add_argument("keyword", help="Approximate keyword to match task titles")
    parser.add_argument(
        "--category", help="Optional category name (case-insensitive)", default=None
    )
    args = parser.parse_args()

    if not os.path.exists(MD_FILE):
        print(f"[ERROR] Markdown file '{MD_FILE}' not found.")
        exit(1)

    try:
        with open(MD_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[ERROR] Could not read markdown file: {e}")
        exit(1)

    backup_md()
    matches = find_matches(lines, args.keyword, args.category)

    if not matches:
        print("[INFO] No matching tasks found.")
        return

    updated_lines, changed = mark_tasks(lines, matches)
    if changed:
        save_file(updated_lines)


if __name__ == "__main__":
    main()

# End of Script
