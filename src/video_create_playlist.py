#!/usr/bin/env python

"""
This script creates a playlist from the current folder

TODO:
if a filename has special characters in it then the playlist will not work.
Try to find a way around that...
"""

import os
import os.path

# sort according to basename
# now write the result


def main() -> None:
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
        ".vob",
        ".vid",
    }
    filenames = []
    for root, _dirs, files in os.walk("."):
        for file in files:
            full = os.path.join(root, file)
            _, extension = os.path.splitext(file)
            if extension.lower() not in extensions:
                continue
            filenames.append(full)
    filenames = sorted(filenames, key=os.path.basename)
    with open("playlist.m3u", "w") as f:
        for filename in filenames:
            f.write(filename)
            f.write("\n")


if __name__ == "__main__":
    main()
