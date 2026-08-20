#!/usr/bin/python

"""
This is a wrapper for gnome-open(1) which does not pollute the screen.
"""

import subprocess
import sys

args = ["/usr/bin/gnome-open"]
args.extend(sys.argv[1:])
subprocess.check_call(
    args,
    stderr=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
)
