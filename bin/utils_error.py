#!/usr/bin/python3

"""
A small app exiting with the error code you want.
"""

import sys

if len(sys.argv)!=2:
    print(f"usage: {sys.argv[0]} [error_code]")
    sys.exit(1)
print("this is stdout", file=sys.stdout)
print("this is stderr", file=sys.stderr)
sys.exit(int(sys.argv[1]))
