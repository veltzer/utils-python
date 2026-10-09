#!/usr/bin/env python3

"""
apparent-du - recursive listing plus total apparent size of a folder.

Unlike du(1), which reports allocated blocks, this sums the apparent
size (st_size) of every regular file found, so sparse files and files
smaller than a block count for what they claim to be.

usage: apparent-du [-q] [-a] [DIR...]

	-q  quiet: print only the totals, skip the per-file listing
	-a  include non-regular files (symlinks, fifos, sockets) in the listing
	    and in the size total; by default only regular files are summed

With no DIR, the current directory is used. Hidden files are included.
Symlinks are never followed; their own size is counted only with -a.
"""

import os
import sys
from pathlib import Path


def human(bytes_count: int) -> str:
    if bytes_count < 1024:
        return f"{bytes_count} B"
    units = ["KiB", "MiB", "GiB", "TiB", "PiB"]
    i = 0
    scaled = bytes_count
    value = bytes_count * 100
    while scaled >= 1048576 and i < 4:
        value //= 1024
        scaled //= 1024
        i += 1
    value //= 1024
    return f"{value // 100}.{value % 100:02d} {units[i]}"


def main() -> None:
    args = sys.argv[1:]
    quiet = False
    all_types = False
    dirs = []

    while args:
        arg = args[0]
        if arg == '-q':
            quiet = True
            args.pop(0)
        elif arg == '-a':
            all_types = True
            args.pop(0)
        elif arg == '-h':
            print(__doc__.strip())
            sys.exit(0)
        elif arg.startswith('-'):
            print(f"apparent-du: invalid option -- {arg}\n", file=sys.stderr)
            print(__doc__.strip(), file=sys.stderr)
            sys.exit(2)
        else:
            dirs.append(arg)
            args.pop(0)

    if not dirs:
        dirs = ["."]

    status = 0

    for d in dirs:
        dir_path = Path(d)
        if not dir_path.is_dir():
            print(f"apparent-du: {d}: not a directory", file=sys.stderr)
            status = 1
            continue

        total = 0
        count = 0
        dir_count = 0

        # Walk manually to match 'find' behavior and avoid following symlinks to dirs
        for root, dnames, fnames in os.walk(d):
            dir_count += 1
            entries = dnames + fnames
            for name in entries:
                path = os.path.join(root, name)
                try:
                    # Do not follow symlinks
                    stat = os.lstat(path)
                except OSError:
                    continue

                is_dir = sum([1 for _ in dnames if _ == name]) > 0  # True if entry is in dnames
                is_symlink = os.path.islink(path)

                if is_dir and not is_symlink:
                    continue

                if not all_types and not (not is_symlink and os.path.isfile(path)):
                    continue

                size = stat.st_size
                total += size
                count += 1
                if not quiet:
                    print(f"{size:12d}  {path}")

        if not quiet and count > 0:
            print()
        
        print(f"{d}: {human(total)} apparent in {count} files, {dir_count} directories")
        print(f"  exact: {total} bytes")

    sys.exit(status)


if __name__ == '__main__':
    main()
