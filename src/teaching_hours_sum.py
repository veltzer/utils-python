#!/usr/bin/env python

"""
teaching_hours_sum
"""

import re
import sys


def main() -> None:
    c = re.compile(r"^.* \((\d+) hours\)$")
    if len(sys.argv) != 2:
        raise ValueError("usage: num dec")
    filename = sys.argv[1]
    hours = 0
    with open(filename) as stream:
        for raw_line in stream:
            line = raw_line.rstrip()
            m = c.match(line)
            if m:
                current_hours = int(m.group(1))
                hours += current_hours
    print(f"hours is {hours}")


if __name__ == "__main__":
    main()
