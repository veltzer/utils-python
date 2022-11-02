#!/usr/bin/python

import sys
import subprocess
import time

if len(sys.argv) != 3:
    raise ValueError("usage: num dec")

num = int(sys.argv[1])
dec = int(sys.argv[2])

while num > 0:
    subprocess.check_call(
        [
            "espeak",
            f"there are {num} seconds to end of exercise",
        ]
    )
    time.sleep(dec)
    num -= dec
subprocess.check_call(
    [
        "espeak",
        "the exercise is over!",
    ]
)
