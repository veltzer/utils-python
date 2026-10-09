#!/usr/bin/env python
from pathlib import Path


def main() -> None:
    num_lines = 7
    delim = "\t"
    fname = Path("file.xml")
    if not fname.exists():
        print(f"unable to open file {fname}")
        return
    with fname.open() as fh:
        while True:
            first_line = fh.readline()
            if not first_line:
                break
            arr = [first_line.rstrip("\n")]
            for _i in range(1, num_lines):
                line = fh.readline()
                if not line:
                    break
                arr.append(line.rstrip("\n"))
            if len(arr) == num_lines:
                print(delim.join(arr))


if __name__ == "__main__":
    main()
