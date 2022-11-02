#!/usr/bin/python

"""
replace first line of many files
"""

import sys
import os
import os.path

# command line usage...
me = os.path.basename(sys.argv[0])
if len(sys.argv) < 2:
    print(f"usage: {me} [file] ...", file=sys.stderr)
    sys.exit(1)

replacement = "#!/usr/bin/python\n\n"
files = sys.argv[1:]
for file in files:
    new_file = file + ".tmp"
    first = True
    with open(file, "r") as old_stream, open(new_file, "w") as new_stream:
        for line in old_stream:
            if first:
                new_stream.write(replacement)
                first = False
            else:
                new_stream.write(line)
    # switch the files
    os.unlink(file)
    os.rename(new_file, file)
