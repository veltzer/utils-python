#!/usr/bin/env python

"""
I need a python script that accepts marp/markdown files as input
and searches for mermaid inlined diagrams in them. When it finds
a mermaid diagram it prompts the user with the content of the current
slide and asks for the name of the diagram. When it gets the name it saves the diagrams
as a .mmd file and leaves a link to the file in the original marp file erasing the inline diagram.

It continues to do this until all mermaid diagrams have been removed from the file.

You must process the matches in reverse order in order not to screw up the "start" and "end" positions
"""

import re
import sys


def extract_mermaid_diagrams(file_path:str):
    with open(file_path, "r") as file:
        content = file.read()

    # Regular expression to match Mermaid diagrams
    pattern = r"```mermaid\n(.*?)\n```"
    matches = list(re.finditer(pattern, content, re.DOTALL))

    # Process matches in reverse order
    for num, match in reversed(list(enumerate(matches))):
        diagram = match.group(1)
        start = match.start()
        end = match.end()

        # Find the start of the current slide
        slide_start = content.rfind("---", 0, start)
        if slide_start == -1:
            slide_start = 0

        # Find the end of the current slide
        slide_end = content.find("---", end)
        if slide_end == -1:
            slide_end = len(content)

        # Extract the current slide content
        # slide_content = content[slide_start:slide_end].strip()

        # Prompt user for diagram name
        # print("\nCurrent slide content:")
        # print(slide_content)
        # diagram_name = input("Enter a name for this diagram: ").strip()
        diagram_name = str(num)

        # Create .mmd file
        mmd_filename = f"{diagram_name}.mmd"
        with open(mmd_filename, "w") as mmd_file:
            mmd_file.write(diagram)

        # Replace the diagram with a link in the original content
        replace = f"![{diagram_name}]({mmd_filename})"
        content = content[:start] + replace + content[end:]

    # Write the modified content back to the file
    with open(file_path, "w") as file:
        file.write(content)


def main():
    if len(sys.argv) <= 2:
        print(f"Usage: {sys.argv[0]} [marp files...]")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        print(f"Processing file: {file_path}")
        extract_mermaid_diagrams(file_path)


if __name__ == "__main__":
    main()
