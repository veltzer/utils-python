#!/usr/bin/python

"""
replace first line of many files
"""

import sys
import os
import os.path

# command line usage...
me = os.path.basename(sys.argv[0])
if len(sys.argv) < 3:
    print(f"usage: {me} [firstline] [file] ...", file=sys.stderr)
    print("firstline should come with no newline")
    sys.exit(1)

replacement = sys.argv[1]
for file in sys.argv[2:]:
    new_file = file + ".tmp"
    first = True
    with open(file, "r") as old_stream, open(new_file, "w") as new_stream:
        for line in old_stream:
            if first:
                new_stream.write(replacement + "\n")
                first = False
            else:
                new_stream.write(line)
    # switch old and new versions
    os.unlink(file)
    os.rename(new_file, file)
