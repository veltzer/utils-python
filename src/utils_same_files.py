#!/usr/bin/env python

"""
say whether any several files have the same content or not.
"""

import hashlib
import os.path
import sys


def main() -> None:
    prog = os.path.basename(sys.argv[0])
    if len(sys.argv) == 1:
        print(f"{prog}: usage: {prog} [files...]")
        sys.exit(1)
    if len(sys.argv) == 2:
        print(f"{prog}: only one file given...")
        print(f"{prog}: usage: {prog} [files...]")
        sys.exit(1)
    files = sys.argv[1:]
    for file in files:
        if not os.path.isfile(file):
            print(f"{sys.argv[0]}: cannot find or access file [{file}]")
            sys.exit(1)
    file_hash = None
    for file in files:
        with open(file, "rb") as f:
            new_hash = hashlib.sha256(f.read())
        if file_hash is not None:
            if new_hash.hexdigest() != file_hash.hexdigest():
                print("they are different")
                sys.exit(1)
        else:
            file_hash = new_hash
    print("they are the same")


if __name__ == "__main__":
    main()
