#!/usr/bin/env python

"""
This script gives track number according to order.
use like this: [script name] *.mp3

It works using id3v2 something like this:
let y=1; for x in *; do id3v2 -T $y/36 "$x" ; let "y=y+1"; done
"""

import os.path
import subprocess
import sys

# first check that all files are there


def main() -> None:
    set_size = len(sys.argv) - 1
    for i, filename in enumerate(sys.argv[1:]):
        assert os.path.isfile(filename)
        subprocess.check_call(
            [
                "id3v2",
                "-T",
                f"{i + 1}/{set_size}",
                filename,
            ]
        )


if __name__ == "__main__":
    main()
