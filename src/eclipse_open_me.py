#!/usr/bin/python

"""
This script runs a browser on the output of the current project
"""

import os
import subprocess


def main() -> None:
    project = os.getcwd().split("/")[-1]
    subprocess.check_call(
        [
            "gnome-open",
            f"https://localhost:8443/{project}",
        ]
    )


if __name__ == "__main__":
    main()
