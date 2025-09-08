# __version__ = "1.0.0"
# __author__ = "CG & AI assistant"
# __creation_date__ = "2025-08-08"
# __modification_date__ = "2025-08-27"
# __purpose__ = "Utility script: preflight_check.py"
# ruff: noqa: E402
from __future__ import annotations

"""Module: preflight_check.py
Auto-added docstring to aid static analysis and navigation.
"""
# File: preflight_check.py
# Purpose: Basic system readiness verification for DevAgentZero
# Version: 1.0
# Author: Craig + ChatGPT
# Last Modified: 2025-08-08

import os


def run_preflight():
    required_dirs = [
        "agent_core",
        "aura",
        "auth",
        "backups",
        "cognition",
        "data",
        "devtools",
        "logs",
        "memory",
        "mesh_delivery",
        "outputs",
        "sentinel",
        "web_console",
        # New architectural components
        "watchlockai",
        "electrichulkai",
        "pulselet",
        "cognitive_os",
        "tests",
        "distributed",
        "networking",
        "deployment",
        "infrastructure",
        "enterprise",
        "compliance",
        "governance",
        "observability",
        "operations",
        "research",
        "innovation",
        "marketplace",
        "desktop",
        "voice",
        "documentation",
        "assets",
        "environments",
        "security",
        "benchmarks",
    ]

    print("Checking required directories...")
    all_exist = True
    for d in required_dirs:
        if not os.path.exists(d):
            print(f"❌ Missing directory: {d}")
            all_exist = False
        else:
            print(f"✅ {d} exists")

    return all_exist
