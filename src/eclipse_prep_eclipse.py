#!/usr/bin/env python

"""
This script preps eclipse for my use by installing cdt and vrapper
on it.
"""

import os
import os.path
import subprocess
import sys


def die(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)


def main():
    # what file to check to see that we are in an eclipse folder
    checkfile = "eclipse"
    # show progress?
    progress = True
    # debug
    debug = False
    # what features do I want installed?
    features = [
        "org.eclipse.cdt",
        "net.sourceforge.vrapper",
    ]
    # first check if this is an eclipse folder
    if not os.path.isfile(checkfile):
        die("this is not an eclipse folder")
    if not os.access(checkfile, os.X_OK):
        die("this is not an eclipse folder")

    for feature in features:
        if progress:
            print(f"doing feature [{feature}]")
        args = [
            "./eclipse",
            "-nosplash",
            "-application",
            "org.eclipse.equinox.p2.director",
            "-repository",
            "http://download.eclipse.org/releases/latest/",
            "-installIU",
            feature + ".feature.group",
        ]
        if debug:
            subprocess.check_call(args)
        else:
            subprocess.check_call(
                args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )


if __name__ == "__main__":
    main()
