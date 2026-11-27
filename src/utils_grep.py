#!/usr/bin/env python

"""
implementing grep in python
"""

import os
import os.path
import re
import sys


def main() -> None:
    # command line usage...
    if len(sys.argv) != 4:
        print("usage: grep.py [expr] [fileregexp] [folder]")
        sys.exit(1)
    # first compile the regular expression to search for...
    c = re.compile(sys.argv[1])
    cf = re.compile(sys.argv[2])
    folder = sys.argv[3]
    debug = False
    print_only_files = False
    printed_files = set()

    for root, _dirs, files in os.walk(folder):
        for file in files:
            full = os.path.join(root, file)
            if debug:
                print(f"file is [{full}]")
            if cf.match(full):
                if debug:
                    print(f"doing file [{full}]")
                try:
                    with open(full) as f:
                        for num, line in enumerate(f):
                            for _ in c.finditer(line):
                                if print_only_files:
                                    if full not in printed_files:
                                        print(full)
                                        printed_files.add(full)
                                else:
                                    print(f"{full}, {num}: {line[:-1]}")
                except UnicodeDecodeError, PermissionError:
                    pass


if __name__ == "__main__":
    main()
