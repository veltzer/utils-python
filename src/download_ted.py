#!/usr/bin/python

"""
A simple script to download stuff from ted.com via the command line
"""

import sys
import download.ted  # type: ignore

if len(sys.argv) != 3:
    print("usage: ted_download.py [url] [file]", file=sys.stderr)
    print(
        "example: ted_download.py http://www.ted.com/talks/david_cameron.html /tmp/foo.mp4",
        file=sys.stderr,
    )
    sys.exit(1)
url = sys.argv[1]
file = sys.argv[2]
download.ted.get(url, file)
