#!/usr/bin/python

"""
utils_python_filetype
"""

import sys
import os
import shelve
import pickle


def check_file_type(file_path):
    if not os.path.exists(file_path):
        return "File does not exist"

    # Check if its a shelf file
    # pylint: disable=broad-except
    try:
        with shelve.open(file_path, "r"):
            # If we can open it as a shelf, its likely a shelf file
            return "Shelf file"
    except Exception:
        # Not a shelf file, continue to check if its a pickle file
        pass

    # Check if its a pickle file
    # pylint: disable=broad-except
    try:
        with open(file_path, "rb") as f:
            pickle.load(f)
        return "Pickle file"
    except pickle.UnpicklingError:
        return "Pickle file (but corrupted or incomplete)"
    except Exception:
        return "Not a shelf or pickle file"


def main():
    file_path = sys.argv[1]
    result = check_file_type(file_path)
    print(f"The file is: {result}")


# Example usage
if __name__ == "__main__":
    main()
