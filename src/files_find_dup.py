#!/usr/bin/python

import os
import hashlib
from collections import defaultdict


def calculate_checksum(filename):
    """Calculates the SHA-256 checksum of a file."""
    with open(filename, "rb") as f:
        file_hash = hashlib.sha256()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def find_duplicates(directory):
    """Recursively scans the directory and finds duplicate files based on checksum."""
    checksum_map = defaultdict(list)
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            checksum = calculate_checksum(filepath)
            checksum_map[checksum].append(filepath)
    return {k: v for k, v in checksum_map.items() if len(v) > 1}


def get_user_choice(duplicates):
    """Prompts the user to choose which files to keep from the duplicates."""
    for checksum, files in duplicates.items():
        print(f"\nDuplicate files found with checksum {checksum}:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {file}")

        while True:
            try:
                choice = int(input("Enter the number of the file to keep (or 0 to keep all): "))
                if 0 <= choice <= len(files):
                    break
                print("Invalid choice. Please enter a number between 0 and", len(files))
            except ValueError:
                print("Invalid input. Please enter a number.")

        if choice != 0:
            files_to_delete = [f for i, f in enumerate(files) if i + 1 != choice]
            for file in files_to_delete:
                os.remove(file)
                print(f"Deleted: {file}")


if __name__ == "__main__":
    current_directory = os.getcwd()
    dups = find_duplicates(current_directory)

    if dups:
        get_user_choice(dups)
    else:
        print("No duplicate files found.")
