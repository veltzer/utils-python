#!/usr/bin/python

"""
This script re-encodes mp3 files. The idea is that this re-encoding
fixes lots of common problems with mp3 files like files which have bad
length because they were catenated badly.

Avconv supports many codecs. See "avconv -codecs".
we will use libmp3lame.
"""

import subprocess
import sys
import tempfile
import shutil
import os
import os.path

doRun = True
doDebug = False
doCheck = True
# do you want to redirect standard output?
doRedirect = False
opt_codec = "copy"
# opt_codec='libmp3lame'


def fix(filename):
    print(f"fixing [{filename}]...")
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        out = f.name
    # args=[
    #    "ffmpeg",
    #    "-i",
    #    filename,
    #    "-acodec",
    #    opt_codec,
    #    out,
    #    "-loglevel",
    #    'quiet'
    # ]
    args = [
        "lame",
        "-m",
        "s",
        "--resample",
        "11.025",
        "--quiet",
        filename,
        out,
    ]
    if doRun:
        if doCheck:
            if doRedirect:
                subprocess.check_call(args, stdout=subprocess.DEVNULL)
            else:
                subprocess.check_call(args)
        else:
            if doRedirect:
                subprocess.call(args, stdout=subprocess.DEVNULL)
            else:
                subprocess.call(args)
    else:
        print(args)
    # copy the mp3 tag data
    subprocess.call(
        [
            "id3cp",
            filename,
            out,
        ]
    )
    os.unlink(filename)
    shutil.move(out, filename)


def main():
    for filename in sys.argv[1:]:
        assert os.path.isfile(filename)
        fix(filename)


main()
