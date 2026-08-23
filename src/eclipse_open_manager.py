#!/usr/bin/env python

"""
This script runs a browser on the output of the current project
"""

import subprocess

# project


def main() -> None:
    subprocess.check_call(
        [
            "gnome-open",
            "https://localhost:8443/manager/html",
        ]
    )


if __name__ == "__main__":
    main()
