#!/usr/bin/python

"""
implementing grep in python
"""

import re
import sys
import os
import os.path

# command line usage...
if len(sys.argv) != 4:
    print("usage: grep.py [expr] [fileregexp] [folder]")
    sys.exit(1)
# first compile the regular expression to search for...
c = re.compile(sys.argv[1])
cf = re.compile(sys.argv[2])
folder = sys.argv[3]
debug = False
# debug=True
printOnlyFiles = False
printedFiles = set()

for root, dirs, files in os.walk(folder):
    for file in files:
        full = os.path.join(root, file)
        if debug:
            print(f"file is [{full}]")
        if cf.match(full):
            if debug:
                print(f"doing file [{full}]")
            with open(full) as f:
                for num, line in enumerate(f):
                    for x in c.finditer(line):
                        if printOnlyFiles:
                            if full not in printedFiles:
                                print(full)
                                printedFiles.add(full)
                        else:
                            print(f"{full}, {num}: {line[:-1]}")
