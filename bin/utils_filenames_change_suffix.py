#!/usr/bin/python3

"""
An app to help to you change suffix of files
"""

import logging
import os.path
import os
import sys

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def yield_files():
    """
    Get all files in a folder
    """
    root_folder = "."
    for root, _dirs, files in os.walk(root_folder):
        for file in files:
            full = os.path.join(root, file)
            yield full


if len(sys.argv) != 3:
    prog = os.path.basename(sys.argv[0])
    print(f"{prog}: usage: {prog} [bad_suffix] [good_suffix]")
    print(f"{prog}: example: {prog} .MP3 .mp3")
    print(f'{prog}: if files have no suffix use ""')
    sys.exit(1)

bad_suffix = sys.argv[1]
good_suffix = sys.argv[2]

for filename in yield_files():
    # logger.debug(filename)
    all_but_suffix, suffix = os.path.splitext(filename)
    if suffix == bad_suffix:
        new_filename = all_but_suffix + good_suffix
        logger.debug("renaming %s to %s", filename, new_filename)
        os.rename(filename, new_filename)
