#!/usr/bin/env python

"""
This script re-encodes mp3 files. The idea is that this re-encoding
fixes lots of common problems with mp3 files like files which have bad
length because they were catenated badly.

Avconv supports many codecs. See "avconv -codecs".
we will use libmp3lame.
"""

import os
import os.path
import shutil
import subprocess
import sys
import tempfile

do_run = True
do_debug = False
do_check = True
# do you want to redirect standard output?
do_redirect = False
opt_codec = "copy"


def fix(filename: str) -> None:
    print(f"fixing [{filename}]...")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        out = f.name
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
    if do_run:
        if do_check:
            if do_redirect:
                subprocess.check_call(args, stdout=subprocess.DEVNULL)
            else:
                subprocess.check_call(args)
        elif do_redirect:
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


def main() -> None:
    for filename in sys.argv[1:]:
        assert os.path.isfile(filename)
        fix(filename)


if __name__ == "__main__":
    main()
