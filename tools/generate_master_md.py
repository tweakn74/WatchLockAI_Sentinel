# File: generate_master_md.py
# Author: DevAgentZero
# Version: 1.0.0
# Last Modified: 2025-07-18
# Purpose: Generate live-updated Markdown task tracker from structured data

import datetime

# ---- Define Task Data ---- #
task_data = {
    "Core Infrastructure": [
        {
            "task": "Finalize `self_upgrade.py`",
            "priority": "High",
            "description": "Hook into CLI, support partial + full self-upgrade logic.",
            "file": "self_upgrade.py",
            "status": "pending",
        },
        {
            "task": "Manifest Snapshots Over Time",
            "priority": "Low",
            "description": "Track historical drift and support version delta auditing.",
            "file": "manifest_checker.py",
            "status": "pending",
        },
    ],
    "System Resource Awareness": [
        {
            "task": "Windows Event Log Reader (Local Monitor)",
            "priority": "Medium",
            "description": "Scan recent logs for key event patterns. Phase 2.7 use only.",
            "file": "event_log_reader.py",
            "status": "pending",
        },
        {
            "task": "RAM / CPU / Disk Load Detection",
            "priority": "High",
            "description": "Assign readiness score and adjust task pacing accordingly.",
            "file": "system_monitor.py",
            "status": "pending",
        },
    ],
    # Add more categories here...
}


# ---- Generate Markdown ---- #
def generate_markdown(task_data):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = "# DevAgentZero - Master Task Tracker\n"
    md += "**Version:** Phase 2.6+ into 2.7  \n"
    md += f"**Last Updated:** {now}  \n"
    md += "**Maintainer:** DevAgentZero Core\n"
    md += "**Purpose:** Live-tracked checklist for all major development goals.\n\n"

    for category, tasks in task_data.items():
        md += f"## {category}\n\n"
        for t in tasks:
            box = "[x]" if t["status"] == "done" else "[ ]"
            md += f"- {box} **{t['task']}** *(Priority: {t['priority']})*  \n"
            md += f"  {t['description']}  \n"
            if t.get("file"):
                md += f"  *File: {t['file']}*\n"
            md += "\n"
    md += "---\n*End of Document*\n"
    return md


# ---- Write to File ---- #
if __name__ == "__main__":
    content = generate_markdown(task_data)
    with open("devagent_master_tasks.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("[PASS] devagent_master_tasks.md generated successfully.")
