#!/usr/bin/env python
import argparse
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Touch a file with the latest time of any found files."
    )
    parser.add_argument("compare", help="File to touch")
    parser.add_argument("folders", nargs="+", help="Folders to search")
    args = parser.parse_args()
    debug = False
    compare_path = Path(args.compare)
    if debug:
        print(f"compare is {compare_path}")
        print(f"folders is {','.join(args.folders)}")
    max_mtime = 0.0
    max_filename = None
    for folder in args.folders:
        for root, _dirs, files in os.walk(folder):
            for file in files:
                filepath = Path(root) / file
                try:
                    stat = filepath.stat()
                    if stat.st_mtime > max_mtime:
                        max_mtime = stat.st_mtime
                        max_filename = filepath
                except OSError:
                    pass
    if compare_path.exists():
        stat = compare_path.stat()
        if stat.st_mtime < max_mtime:
            os.utime(compare_path, (stat.st_atime, max_mtime))
    else:
        compare_path.touch()
        os.utime(compare_path, (max_mtime, max_mtime))
    if debug:
        print(f"max is {max_mtime}")
        print(f"max_filename is {max_filename}")


if __name__ == "__main__":
    main()
