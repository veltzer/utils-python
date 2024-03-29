#!/usr/bin/python

"""
This script preps eclipse for my use by installing cdt and vrapper
on it

TODO:
- check if the features we install exist before we install them.
This will save time (see my eclipse notes about how to do that)
and only install the feature if it is missing.
- the name 'neon' is hardcoded in this script. find out how to find
the version of a specific eclipse without running it and remove
this hardcoding.
"""

import subprocess
import os
import os.path
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
            "http://download.eclipse.org/releases/neon/",
            "-installIU",
            feature + ".feature.group",
        ]
        if debug:
            subprocess.check_call(args)
        else:
            subprocess.check_call(
                args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
