#!/usr/bin/env python
"""
This script adds a header with the base name of the file to Python files
if they dont already have it.
"""

import sys
import os
import tempfile
import shutil


def add_header_to_file(filename):
    """
    Add a header with the base name to the file if it doesnt already exist.
    """
    # Get the base name of the file (without path and extension)
    base_name = os.path.splitext(os.path.basename(filename))[0]

    # Create the header text
    header = f"\"\"\" {base_name}.py \"\"\"\n\n"

    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File [{filename}] does not exist")
        return False

    # Read the file content
    with open(filename, "r") as file:
        content = file.read()

    # Check if the file already begins with triple quotes
    if content.lstrip().startswith("\"\"\""):
        print(f"File [{filename}] already begins with triple quotes. Skipping.")
        return True

    # Create a temporary file for writing
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        # Write the header and original content to the temporary file
        temp_file.write(header + content)
        temp_file.close()

    # Replace the original file with the new one
    shutil.move(temp_file.name, filename)
    print(f"Successfully added header to [{filename}]")
    return True


def main():
    # Check if any filenames were provided
    if len(sys.argv) < 2:
        print("Usage: python add_headers.py file1.py file2.py [file3.py ...]")
        return 1

    # Process each file
    success_count = 0
    for filename in sys.argv[1:]:
        # Only process Python files
        if not filename.endswith(".py"):
            print(f"Skipping [{filename}]: Not a Python file.")
            continue

        if add_header_to_file(filename):
            success_count += 1

    print(f"Processed {success_count} file(s) successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
