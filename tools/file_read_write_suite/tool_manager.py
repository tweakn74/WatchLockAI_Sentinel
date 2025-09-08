
import argparse
import json
import os
import subprocess
import sys

# --- Constants ---
CONFIG_FILE = "tool_config.json"


def get_script_dir() -> str:
    """Gets the directory where this script is located."""
    return os.path.dirname(os.path.realpath(__file__))

def load_config() -> dict:
    """Loads the tool configuration file."""
    config_path = os.path.join(get_script_dir(), CONFIG_FILE)
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not parse {CONFIG_FILE}. Invalid JSON.", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to manage and dispatch tools."""
    parser = argparse.ArgumentParser(description="A tool manager for the file read/write suite.")
    parser.add_argument("--task", type=str, required=True, choices=["read"], help="The task to perform.")
    parser.add_argument("--path", type=str, required=True, help="The absolute path to the target file.")
    args = parser.parse_args()

    config = load_config()
    strategies = config.get("tool_strategies", {})

    file_path = args.path
    if not os.path.isabs(file_path):
        print(f"Error: Please provide an absolute path for the file.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    _, file_ext = os.path.splitext(file_path)
    file_ext = file_ext.lower()

    # Get the list of strategies for the file type, or use the default
    strategy_list = strategies.get(file_ext, strategies.get("default"))

    if not strategy_list:
        print(f"Error: No tool strategy found for file type '{file_ext}' and no default is configured.", file=sys.stderr)
        sys.exit(1)

    for strategy in strategy_list:
        tool_script = strategy.get("tool")
        command_template = strategy.get("command")
        strategy_name = strategy.get("name", "Unknown Strategy")

        if not tool_script or not command_template:
            print(f"Warning: Skipping invalid strategy '{strategy_name}'.", file=sys.stderr)
            continue

        script_path = os.path.join(get_script_dir(), tool_script)
        if not os.path.exists(script_path):
            print(f"Warning: Tool script '{tool_script}' for strategy '{strategy_name}' not found. Skipping.", file=sys.stderr)
            continue

        # Construct the command
        command = command_template.format(script_path=script_path, file_path=file_path)
        
        print(f"--- Attempting strategy: '{strategy_name}' ---", file=sys.stderr)
        print(f"Executing: {command}", file=sys.stderr)

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if process.returncode == 0:
                # Success
                print(process.stdout) # Print the result to my stdout
                return # Exit after the first successful strategy
            else:
                # Failure, print error and try next strategy
                print(f"Strategy '{strategy_name}' failed.", file=sys.stderr)
                print(f"Stderr: {process.stderr}", file=sys.stderr)

        except Exception as e:
            print(f"An unexpected error occurred while running strategy '{strategy_name}': {e}", file=sys.stderr)

    # If all strategies failed
    print(f"Error: All configured strategies for '{file_ext}' failed.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()

