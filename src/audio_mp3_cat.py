#!/usr/bin/python3

"""
This script will catenate mp3 files correctly using ffmpeg.
see: http://superuser.com/questions/314239/how-to-join-merge-many-mp3-files
"""

import subprocess  # for check_call
import argparse
import os.path  # for isfile
import sys  # for exit

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="output file")
options, filenames = parser.parse_known_args()

# check that all free files are there
for filename in filenames:
    if not os.path.isfile(filename):
        print(f"file [{filename}] is not there...")
        sys.exit(1)
if options.output is None:
    print("must supply -o argument")
    sys.exit(1)
if os.path.isfile(options.output):
    print(f"file [{options.output}] is there...")
    sys.exit(1)

args = [
    # "avconv",
    "ffmpeg",
    "-i",
    "concat:" + "|".join(filenames),
    "-acodec",
    "copy",
    options.output,
    # "-loglevel", "quiet",
]
print(args)
subprocess.check_call(args)
