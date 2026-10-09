#!/usr/bin/env python

"""
A simple script to download stuff from ted.com via the command line
"""

import sys

import download.ted


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: download_ted.py [url] [file]", file=sys.stderr)
        print(
            "example: download_ted.py http://www.ted.com/talks/david_cameron.html /tmp/foo.mp4",
            file=sys.stderr,
        )
        sys.exit(1)
    url = sys.argv[1]
    file = sys.argv[2]
    download.ted.get(url, file)


if __name__ == "__main__":
    main()
