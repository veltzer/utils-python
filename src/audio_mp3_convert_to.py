#!/usr/bin/python

"""
Convert files to mp3 from whatever they are.
The idea is to do something like this:
$ for x in *.m4b; do ffmpeg -i "$x" "`basename "$x" .m4b`.mp3"; done
"""

import subprocess
import sys
import os.path

doRun = True
doDebug = True
doRedirect = False

for filename in sys.argv[1:]:
    assert os.path.isfile(filename)
    base, suffix = os.path.splitext(filename)
    if suffix == ".mp3":
        print(f"skipping {filename}...")
        continue
    new_name = base + ".mp3"
    args = [
        "ffmpeg",
        "-i",
        filename,
        new_name,
    ]
    if doDebug:
        print(f"arguments are [{args}]")
    if doRun:
        if doRedirect:
            subprocess.check_call(
                args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
        else:
            subprocess.check_call(args)
