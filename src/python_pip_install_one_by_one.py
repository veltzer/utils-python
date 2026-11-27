#!/usr/bin/env python

"""
Install requirements one by one
"""

import subprocess


def main():
    with open("requirements.thawed.txt") as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith(
                "#"
            ):  # Ignore empty lines and comments
                print(f"Installing: [{package}]")
                subprocess.run(["pip", "install", package], check=True)


if __name__ == "__main__":
    main()
