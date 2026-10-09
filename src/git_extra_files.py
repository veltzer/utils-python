#!/usr/bin/env python
import os
import subprocess
from pathlib import Path


def main() -> None:
    debug = False
    files_map = set()
    for root, _dirs, files in os.walk("."):
        if ".git" in root.split(os.sep):
            continue
        for file in files:
            path = Path(root) / file
            file_path = f"./{path.as_posix()}" if root != "." else f"./{file}"
            if debug:
                print(f"saw file [{file_path}]")
            files_map.add(file_path)
    try:
        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if debug:
                print(f"saw line [{line}]")
            files_map.discard(f"./{line}")
    except subprocess.CalledProcessError:
        print("unable to run git")
        return
    for file in sorted(files_map):
        print(f"extra file [{file}]")


if __name__ == "__main__":
    main()
