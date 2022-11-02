#!/usr/bin/python3

"""
This script upgrades all packages according to a requirements.txt file
"""

import subprocess
import os


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
