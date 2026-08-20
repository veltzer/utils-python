#!/usr/bin/python

"""
This script runs a browser on the output of the current project
"""

import os
import subprocess

project = os.getcwd().split("/")[-1]

subprocess.check_call(
    [
        "gnome-open",
        f"https://localhost:8443/{project}",
    ]
)
