#!/usr/bin/python3

"""
This script creates a playlist from the current folder

TODO:
if a filename has special characters in it then the playlist will not work.
Try to find a way around that...
"""

import os.path
import os

extensions = {
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
for root, dirs, files in os.walk("."):
    for file in files:
        full = os.path.join(root, file)
        _, extension = os.path.splitext(file)
        if extension not in extensions:
            continue
        filenames.append(full)
# sort according to basename
filenames = sorted(filenames, key=os.path.basename)
# now write the result
with open("playlist.m3u", "w") as f:
    for filename in filenames:
        f.write(filename)
        f.write("\n")
