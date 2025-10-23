#!/usr/bin/env python
"""
Simple ELF File Finder
Recursively finds and prints all ELF files in a directory.
"""

import sys
from pathlib import Path


def is_elf_file(filepath):
    """Check if a file is an ELF binary by examining its magic number."""
    try:
        with open(filepath, "rb") as f:
            magic = f.read(4)
            return magic == b"\x7fELF"
    except (IOError, OSError, PermissionError):
        return False


def find_elf_files(directory):
    """Find all ELF files in a directory recursively."""
    directory = Path(directory)

    if not directory.exists():
        print(f"Error: Directory [{directory}] does not exist", file=sys.stderr)
        return

    if not directory.is_dir():
        print(f"Error: [{directory}] is not a directory", file=sys.stderr)
        return

    try:
        for filepath in directory.rglob("*"):
            if filepath.is_file() and is_elf_file(filepath):
                print(filepath)
    except PermissionError:
        print(f"Error: Permission denied accessing [{directory}]", file=sys.stderr)


def main():
    """Main function."""
    # Use command line argument or default to current directory
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    find_elf_files(directory)


if __name__ == "__main__":
    main()
