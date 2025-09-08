#!/usr/bin/env python3
"""
Code Anomaly Scanner for WatchLockAI
====================================

Enterprise-grade security scanner designed to detect non-standard characters
and potential obfuscation attempts in Python source code.

This scanner uses AST (Abstract Syntax Tree) parsing to intelligently analyze
only the actual code logic, ignoring string literals and comments where
non-ASCII characters are legitimate.

Author: Senior Python Developer
Version: 1.0.0
License: Proprietary - WatchLockAI Security Tools
"""

import argparse
import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set, Union


class AnomalyLocation(NamedTuple):
    """Represents the location of a detected anomaly."""

    file_path: str
    line_number: int
    column_number: int
    character: str
    unicode_code: str
    context: str


class CodeAnomalyScanner:
    """
    Enterprise-grade scanner for detecting non-standard characters in Python code.

    Uses AST parsing to analyze only code elements (identifiers, operators, etc.)
    while ignoring legitimate non-ASCII usage in strings and comments.
    """

    # Standard printable ASCII range (U+0020 to U+007E)
    PRINTABLE_ASCII_START = 0x20  # Space character
    PRINTABLE_ASCII_END = 0x7E    # Tilde character

    # Critical invisible characters to always flag
    CRITICAL_INVISIBLE_CHARS = {
        '\u200B',  # Zero-Width Space
        '\u200C',  # Zero-Width Non-Joiner
        '\u200D',  # Zero-Width Joiner
        '\u2060',  # Word Joiner
        '\uFEFF',  # Zero-Width No-Break Space (BOM)
    }

    def __init__(self) -> None:
        """Initialize the scanner with empty results."""
        self.anomalies: List[AnomalyLocation] = []
        self.scanned_files: int = 0
        self.failed_files: List[str] = []

    def is_anomalous_character(self, char: str) -> bool:
        """
        Determine if a character is anomalous for Python code.

        Args:
            char: Single character to check

        Returns:
            True if character is outside printable ASCII or is a critical invisible char
        """
        if char in self.CRITICAL_INVISIBLE_CHARS:
            return True

        char_code = ord(char)
        return not (self.PRINTABLE_ASCII_START <= char_code <= self.PRINTABLE_ASCII_END)

    def extract_code_elements(self, source_code: str) -> Set[str]:
        """
        Extract only the code elements (identifiers, operators) from Python source.

        This method uses AST parsing to identify actual code tokens while
        excluding string literals and comments where non-ASCII is legitimate.

        Args:
            source_code: Python source code to analyze

        Returns:
            Set of code element strings that should be checked for anomalies
        """
        code_elements: Set[str] = set()

        try:
            # Parse the source code into an Abstract Syntax Tree
            tree = ast.parse(source_code)

            # Walk through all AST nodes to extract code elements
            for node in ast.walk(tree):
                # Extract variable names, function names, class names, etc.
                if isinstance(node, ast.Name):
                    code_elements.add(node.id)

                # Extract attribute names (e.g., obj.method_name)
                elif isinstance(node, ast.Attribute):
                    code_elements.add(node.attr)

                # Extract function/method names from function definitions
                elif isinstance(node, ast.FunctionDef):
                    code_elements.add(node.name)

                # Extract class names from class definitions
                elif isinstance(node, ast.ClassDef):
                    code_elements.add(node.name)

                # Extract argument names from function signatures
                elif isinstance(node, ast.arg):
                    code_elements.add(node.arg)

                # Extract keyword argument names
                elif isinstance(node, ast.keyword) and node.arg:
                    code_elements.add(node.arg)

        except SyntaxError:
            # If AST parsing fails, we'll fall back to line-by-line analysis
            # This handles files with syntax errors or incomplete code
            pass

        return code_elements

    def scan_file_content(self, file_path: Path, content: str) -> None:
        """
        Scan a single file's content for anomalies in code elements.

        Args:
            file_path: Path to the file being scanned
            content: File content as string
        """
        # Extract code elements using AST parsing
        code_elements = self.extract_code_elements(content)

        # If AST parsing failed, fall back to scanning non-string/comment lines
        if not code_elements:
            self._scan_fallback_method(file_path, content)
            return

        # Check each code element for anomalous characters
        lines = content.splitlines()

        for element in code_elements:
            for char in element:
                if self.is_anomalous_character(char):
                    # Find the line and column where this element appears
                    location = self._find_element_location(lines, element, char)
                    if location:
                        self.anomalies.append(AnomalyLocation(
                            file_path=str(file_path),
                            line_number=location[0],
                            column_number=location[1],
                            character=char,
                            unicode_code=f"U+{ord(char):04X}",
                            context=element
                        ))

    def _find_element_location(self, lines: List[str], element: str, char: str) -> Optional[tuple[int, int]]:
        """
        Find the line and column number where a code element appears.

        Args:
            lines: List of source code lines
            element: Code element containing the anomalous character
            char: The specific anomalous character

        Returns:
            Tuple of (line_number, column_number) or None if not found
        """
        for line_idx, line in enumerate(lines, 1):
            if element in line:
                # Find the column position of the anomalous character
                element_start = line.find(element)
                if element_start != -1:
                    char_pos = element.find(char)
                    if char_pos != -1:
                        return (line_idx, element_start + char_pos + 1)
        return None

    def _scan_fallback_method(self, file_path: Path, content: str) -> None:
        """
        Fallback scanning method when AST parsing fails.

        Scans line-by-line, excluding obvious string literals and comments.
        This is less precise but provides coverage for unparseable files.

        Args:
            file_path: Path to the file being scanned
            content: File content as string
        """
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            # Skip comment lines (basic heuristic)
            stripped_line = line.strip()
            if stripped_line.startswith('#'):
                continue

            # Basic string literal detection (not perfect, but reasonable fallback)
            in_string = False
            quote_char = None

            for col_num, char in enumerate(line, 1):
                # Basic string detection
                if char in ('"', "'") and (col_num == 1 or line[col_num - 2] != '\\'):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None

                # Only check characters outside of strings
                if not in_string and self.is_anomalous_character(char):
                    self.anomalies.append(AnomalyLocation(
                        file_path=str(file_path),
                        line_number=line_num,
                        column_number=col_num,
                        character=char,
                        unicode_code=f"U+{ord(char):04X}",
                        context=line.strip()[:50] + "..." if len(line.strip()) > 50 else line.strip()
                    ))

    def scan_file(self, file_path: Path) -> None:
        """
        Scan a single Python file for anomalies.

        Args:
            file_path: Path to the Python file to scan
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()

            self.scan_file_content(file_path, content)
            self.scanned_files += 1

        except (OSError, UnicodeDecodeError) as e:
            self.failed_files.append(f"{file_path}: {e}")

    def scan_directory(self, directory_path: Path) -> None:
        """
        Recursively scan all Python files in a directory.

        Args:
            directory_path: Path to the directory to scan
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not directory_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")

        # Recursively find all Python files
        python_files = list(directory_path.rglob("*.py"))

        if not python_files:
            print(f"⚠️  No Python files found in {directory_path}")
            return

        # Scan each Python file
        for py_file in python_files:
            self.scan_file(py_file)

    def generate_report(self) -> str:
        """
        Generate a comprehensive Markdown report of scan results.

        Returns:
            Formatted Markdown report as string
        """
        if not self.anomalies and not self.failed_files:
            return "✅ Scan complete. No anomalies found."

        report_lines = ["# 🔍 Code Anomaly Scanner Report", ""]

        # Summary section
        report_lines.extend([
            "## 📊 Scan Summary",
            "",
            f"- **Files Scanned**: {self.scanned_files}",
            f"- **Anomalies Found**: {len(self.anomalies)}",
            f"- **Failed Files**: {len(self.failed_files)}",
            ""
        ])

        # Anomalies section
        if self.anomalies:
            report_lines.extend([
                "## 🚨 Detected Anomalies",
                "",
                "| File | Line | Col | Character | Unicode | Context |",
                "|------|------|-----|-----------|---------|---------|"
            ])

            for anomaly in self.anomalies:
                # Escape pipe characters in context for Markdown table
                safe_context = anomaly.context.replace("|", "\\|")
                char_display = repr(anomaly.character) if anomaly.character.isprintable() else "�"

                report_lines.append(
                    f"| `{anomaly.file_path}` | {anomaly.line_number} | {anomaly.column_number} | "
                    f"`{char_display}` | `{anomaly.unicode_code}` | `{safe_context}` |"
                )

            report_lines.append("")

        # Failed files section
        if self.failed_files:
            report_lines.extend([
                "## ⚠️ Failed to Scan",
                ""
            ])

            for failed_file in self.failed_files:
                report_lines.append(f"- `{failed_file}`")

            report_lines.append("")

        return "\n".join(report_lines)


def main() -> None:
    """Main entry point for the Code Anomaly Scanner."""
    parser = argparse.ArgumentParser(
        description="Scan Python files for non-standard characters in code elements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project
  %(prog)s ./src
  %(prog)s .
        """
    )

    parser.add_argument(
        "directory",
        type=str,
        help="Directory path to scan recursively for Python files"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Code Anomaly Scanner 1.0.0"
    )

    args = parser.parse_args()

    try:
        directory_path = Path(args.directory).resolve()
        scanner = CodeAnomalyScanner()

        print(f"🔍 Scanning directory: {directory_path}")
        scanner.scan_directory(directory_path)

        # Generate and print the report
        report = scanner.generate_report()
        print("\n" + report)

        # Exit with appropriate code
        sys.exit(1 if scanner.anomalies else 0)

    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Scan interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
