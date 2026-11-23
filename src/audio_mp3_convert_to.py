#!/usr/bin/env python

"""
Convert files to mp3 from whatever they are.
The idea is to do something like this:
$ for x in *.m4b; do ffmpeg -i "$x" "`basename "$x" .m4b`.mp3"; done
"""

import os.path
import subprocess
import sys


def main() -> None:
    do_run = True
    do_debug = True
    do_redirect = False
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
        if do_debug:
            print(f"arguments are [{args}]")
        if do_run:
            if do_redirect:
                subprocess.check_call(
                    args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
                )
            else:
                subprocess.check_call(args)


if __name__ == "__main__":
    main()
