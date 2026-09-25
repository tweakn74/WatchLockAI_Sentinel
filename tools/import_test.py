#!/usr/bin/env python3
"""
Comprehensive Import Test for Core Consciousness Components

This script tests imports of all core consciousness components to identify
any Pylance issues that need superhero-level fixing.

Author: Superhero AI Architect
Date: 2025-08-29
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_import(module_name: str, import_path: str) -> bool:
    """Test importing a module and report success or failure."""
    try:
        __import__(import_path)
        print(f"[PASS] {module_name}: Import SUCCESS")
        return True
    except Exception as e:
        print(f"[FAIL] {module_name}: Import FAILED - {e}")
        return False


def run_import_tests():
    """Run comprehensive import tests for core consciousness components."""
    print("[BRAIN] CONSCIOUSNESS CORE IMPORT TEST")
    print("=" * 50)

    # Test core dopamine components
    core_modules = [
        ("Dopamine Engine", "core.dopamine_core.dopamine_engine"),
        ("Reward Predictor", "core.dopamine_core.reward_predictor"),
        ("Motivation Tracker", "core.dopamine_core.motivation_tracker"),
        ("Curiosity Engine", "core.dopamine_core.curiosity_engine"),
    ]

    # Test agent core components
    agent_modules = [
        ("Planner", "agent_core.planner"),
        ("Generator", "agent_core.generator"),
        ("Executor", "agent_core.executor"),
        ("LLM Mesh Orchestrator", "agent_core.llm_mesh_orchestrator"),
    ]

    # Test other critical components
    critical_modules = [
        ("Main Module", "main"),
        ("Personality Core", "core.personality_core"),
        ("LLM Runtime", "core.llm_runtime"),
        ("Neuromod Pulse", "core.neuromod.neuromod_pulse"),
    ]

    # Track results
    all_modules = core_modules + agent_modules + critical_modules
    success_count = 0
    total_count = len(all_modules)

    # Test all modules
    for module_name, import_path in all_modules:
        if test_import(module_name, import_path):
            success_count += 1

    # Summary
    print()
    print("=" * 50)
    print("[BARS] IMPORT TEST RESULTS")
    print("=" * 50)
    print(f"[PASS] Successful Imports: {success_count}/{total_count}")

    if success_count == total_count:
        print("\n[U+1F389] ALL CORE MODULES IMPORT SUCCESSFULLY!")
        print("[U+1F9B8] CONSCIOUSNESS CORE IS BULLETPROOF!")
        return True
    else:
        print(f"\n[U+1F4A5] {total_count - success_count} MODULES FAILED TO IMPORT")
        print("[U+1F527] SUPERHERO INTERVENTION REQUIRED!")
        return False


if __name__ == "__main__":
    success = run_import_tests()
    sys.exit(0 if success else 1)
