#!/usr/bin/env python
import argparse
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix source files.")
    parser.add_argument("infile", help="Input file")
    parser.add_argument("outfile", help="Output file")
    args = parser.parse_args()
    debug = False
    infile = Path(args.infile)
    outfile = Path(args.outfile)
    if debug:
        print(f"infile is [{infile}]")
        print(f"outfile is [{outfile}]")
    pattern = re.compile(r"^	+attributes\['do")
    extract_pattern = re.compile(r"^	+(.*)$")
    with infile.open("r") as in_fh, outfile.open("w") as out_fh:
        for line in in_fh:
            line = line.rstrip("\n")
            if pattern.match(line):
                match = extract_pattern.match(line)
                if match:
                    content = match.group(1)
                    line = f"\t{content}"
            out_fh.write(f"{line}\n")


if __name__ == "__main__":
    main()
