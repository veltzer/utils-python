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
    root_folder = "."
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            full = os.path.join(root, file)
            yield full


if len(sys.argv)!=3:
    prog = os.path.basename(sys.argv[0])
    print('{prog}: usage: {prog} [bad_suffix] [good_suffix]'.format(prog=prog))
    print('{prog}: example: {prog} .MP3 .mp3'.format(prog=prog))
    print('{prog}: if files have no suffix use ""'.format(prog=prog))
    sys.exit(1)

bad_suffix = sys.argv[1]
good_suffix = sys.argv[2]

for filename in yield_files():
    #logger.debug(filename)
    all_but_suffix, suffix = os.path.splitext(filename)
    if suffix == bad_suffix:
        new_filename = all_but_suffix + good_suffix
        logger.debug("renaming %s to %s", filename, new_filename)
        os.rename(filename, new_filename)
