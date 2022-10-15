#!/usr/bin/python3

"""
This script runs a browser on the output of the current project
"""

import subprocess
import os

# project
project = os.getcwd().split("/")[-1]

subprocess.check_call(
    [
        "gnome-open",
        "https://localhost:8443/manager/html",
    ]
)
