#!/usr/bin/env python

"""
this script sorts file on disk. it does so by moving them around so that the order of creation seems right.
to see its effect use "ls -f" before and after the sort.
this script will only run on linux and only on filesystems where create order is the naturl order
of files on them.

References:
http://www.linuxforums.org/forum/newbie/111044-change-order-files-directory.html
"""

import os
import os.path
import sys
import tempfile

# this iterates in disk order
# create a temporary directory


def main() -> None:
    if len(sys.argv) != 1:
        print(f"usage: {sys.argv[0]}", file=sys.stderr)
        sys.exit(1)
    file_list = [x for x in os.listdir(".") if os.path.isfile(x)]
    sorted_file_list = sorted(file_list)
    if file_list == sorted_file_list:
        print("in this folder natural order is already sort order", file=sys.stderr)
        sys.exit(0)
    with tempfile.TemporaryDirectory(dir=".") as tmpdir:
        # move everything to the temp folder
        for file in file_list:
            os.rename(file, os.path.join(tmpdir, file))
        # move back in sorted order
        for file in sorted_file_list:
            os.rename(os.path.join(tmpdir, file), file)


if __name__ == "__main__":
    main()
