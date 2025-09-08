#!/usr/bin/env python3
"""
Import Checker - Simple script to check if core modules can be imported
"""


def check_imports():
    """Check if all core dopamine modules can be imported."""
    modules_to_check = [
        "core.dopamine_core.dopamine_engine",
        "core.dopamine_core.reward_predictor",
        "core.dopamine_core.curiosity_engine",
        "core.dopamine_core.motivation_tracker",
    ]

    results = {}

    for module in modules_to_check:
        try:
            __import__(module)
            results[module] = "✅ OK"
            print(f"{module}: ✅ OK")
        except Exception as e:
            results[module] = f"❌ ERROR: {e}"
            print(f"{module}: ❌ ERROR: {e}")

    return results


if __name__ == "__main__":
    print("Checking core dopamine module imports...")
    print("=" * 50)
    results = check_imports()
    print("=" * 50)

    failed_imports = [module for module, result in results.items() if "ERROR" in result]
    if failed_imports:
        print(f"\n💥 {len(failed_imports)} modules failed to import")
        exit(1)
    else:
        print("\n🎉 All modules imported successfully!")
        exit(0)
