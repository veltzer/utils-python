#!/usr/bin/python3

"""
This script upgrades all packages according to a requirements.txt file
"""

import subprocess
import os
import sys

debug=False
debug=True

if not os.path.isfile("requirements.txt"):
    print("erorr: no requirements.txt file found", file=sys.stderr)
subprocess.check_call([
    "pip",
    "install",
    "-r",
    "requirements.txt",
    "--upgrade",
]
