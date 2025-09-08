# File Read/Write Suite

This directory contains a modular, extensible suite of tools for file operations, primarily focused on reading the content of various file types.

## Core Design

The suite is built around a central manager script (`tool_manager.py`) that uses a configuration file (`tool_config.json`) to dispatch tasks to the most appropriate specialized tool. This design allows for easy extension and maintenance without modifying the core logic of the agent that calls it.

### Key Components

- **`tool_manager.py`**: The single entry point for the entire suite. It reads the configuration and intelligently selects the best tool for the job.

- **`tool_config.json`**: A JSON file that defines the "strategies" for handling different file types. It maps file extensions to a prioritized list of tool scripts and the commands needed to run them.

- **Tool Scripts (`read_any_file.py`, `read_docx_text.py`, etc.)**: These are the individual scripts that perform the actual work for a specific task or file type.

## Usage

All interactions should go through the `tool_manager.py` script.

**Example:**

To read the contents of a file, use the `--task read` and `--path` arguments:

```bash
python tool_manager.py --task read --path "C:\path\to\your\document.docx"
```

The manager will automatically look up the strategy for `.docx` files in the config and execute the best available tool.

## How to Extend the Suite

Adding new capabilities is simple:

1.  **Add Your Script:** Place your new tool script (e.g., `read_new_format.py`) inside this directory.
2.  **Update the Config:** Open `tool_config.json` and add a new entry for the file type you want to support, pointing to your new script.

    ```json
    {
      "tool_strategies": {
        ".new_format": [
          {
            "name": "My New Format Reader",
            "tool": "read_new_format.py",
            "command": "python {script_path} --input {file_path}"
          }
        ],
        // ... existing strategies
      }
    }
    ```

This modular approach ensures the system can easily grow to support more file types and operations in the future.
