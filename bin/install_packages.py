#!/usr/bin/python3

# This script will install a packages.txt file using sudo

import sys
import os.path
import subprocess

filename = "packages.txt"
if not os.path.exists(filename):
    print(f"You need to run this script where a ${filename} file exists")
    sys.exit(1)

packages = []
with open(filename) as f:
    for line in f:
        line = line.rstrip()
        if line.startswith("#"):
            continue
        packages.append(line)
args = [
    "sudo",
    "apt",
    "install",
]
args.extend(packages)
subprocess.check_call(args)
