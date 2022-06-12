#!/usr/bin/python3

"""
implemting grep in python
"""

import sys
import os.path
import os

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} [folder]")
    sys.exit(1)

times = 3
pattern = "\n" * times
folder = sys.argv[1]

for root, dirs, files in os.walk(folder):
    for file in files:
        full = os.path.join(root, file)
        # print(f"doing {full}")
        with open(full) as f:
            content = f.read()
            if pattern in content:
                print(f"{full}")
