#!/usr/bin/env python3

import os.path
import os

"""
This script creates a playlist from the current folder
"""

extensions={
    ".avi",
    ".flv",
    ".wmv",
    ".mpg",
    ".asf",
    ".mpeg",
    ".rm",
    ".mov",
    ".mkv",
    ".3gp",
    ".ram",
    ".m4v",
    ".rmvb",
    ".qt",
    ".mp4",
    ".VOB",
    ".vid",
}
filenames = []
for root, dirs, files in os.walk('.'):
    for file in files:
        full = os.path.join(root, file)
        _, extension = os.path.splitext(file)
        if extension not in extensions:
            continue
        filenames.append(full)
# sort according to basename
filenames = sorted(filenaes, key=os.path.basename)
# now write the result
with open("playlist.m3u", "w") as f:
    for filename in filenames:
        f.write(filename)
        f.write("\n")
