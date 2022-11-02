#!/usr/bin/python

"""
say whether any several files have the same content or not.
"""

import sys
import os.path
import hashlib

if len(sys.argv) == 1:
    print("{sys.argv[0]}: usage: {sys.argv[0]} [files...]")
    sys.exit(1)
if len(sys.argv) == 2:
    print(f"{sys.argv[0]}: only one file given...")
    print(f"{sys.argv[0]}: usage: {sys.argv[0]} [files...]")
    sys.exit(1)

files = sys.argv[1:]
for file in files:
    if not os.path.isfile(file):
        print(f"{sys.argv[0]}: cannot find or access file [{file}]")
        sys.exit(1)
md5 = None
for file in files:
    with open(file) as f:
        new_md5 = hashlib.md5(f.read().encode())
    if md5 is not None:
        if new_md5.hexdigest() != md5.hexdigest():
            print("they are different")
            sys.exit(1)
    else:
        md5 = new_md5
print("they are the same")
