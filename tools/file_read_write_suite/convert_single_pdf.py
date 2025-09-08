"""Module: tools/convert_single_pdf.py
Utility script to convert a single PDF file to text and save it to a specific location.
"""
# File: convert_single_pdf.py
# Location: tools/
# Developer: Qoder IDE
# Version: 1.0.0
# Last Modified: 2025-08-29
# Purpose: Convert a single PDF file to text and save it to a specific location.

from __future__ import annotations

import sys
from pathlib import Path

# Add the parent directory to sys.path to import convert_to_text
sys.path.append(str(Path(__file__).parent))

from convert_to_text import convert_pdf


def convert_single_pdf(input_path: str, output_path: str) -> None:
    """
    Convert a single PDF file to text and save it to the specified location.

    Args:
        input_path: Path to the input PDF file
        output_path: Path where the output text file should be saved
    """
    try:
        # Convert the PDF to text
        input_file = Path(input_path)
        if not input_file.exists():
            print(f"Error: Input file does not exist: {input_path}")
            return

        print(f"Converting {input_path} to text...")
        text = convert_pdf(input_file)

        # Ensure the output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write the text to the output file
        output_file.write_text(text, encoding="utf-8")
        print(f"Successfully converted {input_path} to {output_path}")

    except Exception as e:
        print(f"Error converting PDF: {e}")
        return


if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python convert_single_pdf.py <input_pdf_path> <output_txt_path>")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    output_txt_path = sys.argv[2]

    convert_single_pdf(input_pdf_path, output_txt_path)
