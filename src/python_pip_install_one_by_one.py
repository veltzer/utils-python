#!/usr/bin/python

"""
Install requirements one by one
"""

import subprocess


def main():
    with open("requirements.thawed.txt", "r") as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith("#"):  # Ignore empty lines and comments
                print(f"Installing: [{package}]")
                subprocess.run(["pip", "install", package], check=True)
                # You could add a pause here if needed
                # input("Press Enter to continue...")


if __name__ == "__main__":
    main()
