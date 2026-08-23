#!/usr/bin/env python

"""
This script upgrades all packages according to a requirements.txt file
"""

import os
import subprocess


def main() -> None:
    assert os.path.isfile("requirements.txt"), "no requirements.txt file found"
    subprocess.check_call(
        [
            "pip",
            "install",
            "-r",
            "requirements.txt",
            "--upgrade",
        ]
    )


if __name__ == "__main__":
    main()
