#!/usr/bin/python

"""
List encdings of files
"""

import os

import chardet


def main() -> None:
    for n in os.listdir(b"."):
        result = chardet.detect(n)
        encoding = result["encoding"]
        confidence = result["confidence"]
        print(f"{n.decode()} => {encoding} ({confidence})")


if __name__ == "__main__":
    main()
