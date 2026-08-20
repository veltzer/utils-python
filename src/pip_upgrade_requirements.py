#!/usr/bin/python

"""
This script upgrades all packages according to a requirements.txt file
"""

import os
import subprocess

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
