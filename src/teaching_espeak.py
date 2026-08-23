#!/usr/bin/python

"""
teaching_espeak
"""

import subprocess
import sys
import time


def main() -> None:
    if len(sys.argv) != 3:
        raise ValueError("usage: num dec")
    num = int(sys.argv[1])
    dec = int(sys.argv[2])
    if dec <= 0:
        raise ValueError("dec must be positive")
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


if __name__ == "__main__":
    main()
