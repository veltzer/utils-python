#!/usr/bin/python

import sys
import re

c = re.compile(r"^.* \((\d+) hours\)$")

if len(sys.argv) != 2:
    raise ValueError("usage: num dec")

filename = sys.argv[1]

hours = 0
with open(filename) as stream:
    for line in stream:
        line = line.rstrip()
        # print(f"line is {line}")
        m = c.match(line)
        if m:
            # print(f"line {line} matches")
            current_hours = int(m.group(1))
            # print(f"current_hours is {current_hours}")
            hours += current_hours

print(f"hours is {hours}")
