#!/usr/bin/python

"""
marp_check_images
"""

import os
import sys
import re
from pathlib import Path


def find_marp_files(root_dir: str) -> list[Path]:
    """Find all markdown files that might be Marp presentations recursively."""
    root_path = Path(root_dir)
    marp_files = []

    for path in root_path.rglob("*.md"):
        marp_files.append(path)
    return marp_files


def extract_image_links(file_path: Path) -> list[tuple[str, int]]:
    """Extract all image links from a markdown file with their line numbers."""
    image_links = []

    # Regex for both ![]() and ![alt](url "title") formats
    image_pattern = r"!\[([^\]]*)\]\(([^)\"]+)(?:\"[^\"]*\")?\)"

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            matches = re.finditer(image_pattern, line)
            for match in matches:
                image_path = match.group(2)
                # Skip URLs
                if not image_path.startswith(("http://", "https://", "data:")):
                    image_links.append((image_path, line_num))
    return image_links


def validate_image_links(root_dir: str) -> bool:
    """Validate all image links in all Marp files under root_dir."""
    all_valid = True
    marp_files = find_marp_files(root_dir)

    if not marp_files:
        print("No Marp files found!")
        return False

    # print(f"Found {len(marp_files)} Marp files")

    for marp_file in marp_files:
        # print(f"Checking {marp_file}...")
        image_links = extract_image_links(marp_file)

        if not image_links:
            # print("  No image links found")
            continue

        for image_path, line_num in image_links:
            # Convert to absolute path relative to the Marp file
            abs_image_path = (marp_file.parent / Path(image_path)).resolve()

            if not abs_image_path.exists():
                print(f"{marp_file}: {line_num}: {image_path}")
                all_valid = False
            else:
                pass
                # print(f"  ✓ Line {line_num}: Found {image_path}")

    return all_valid


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <root_directory>")
        sys.exit(1)
    root_dir = sys.argv[1]
    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a directory")
        sys.exit(1)
    success = validate_image_links(root_dir)
    if not success:
        # print("\n⚠️ Some images are missing!")
        sys.exit(1)
    else:
        pass
        # print("\n✓ All images exist!")


if __name__ == "__main__":
    main()
