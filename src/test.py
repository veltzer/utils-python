#!/usr/bin/env python

"""
Smoke test for this repo.

Runs the shallow checks in test_mod.py: that the packages under src still
import, that the scripts all carry the same shebang and parse, that everything
they import is installed, and that the generated pyproject.toml still matches
the dependency list it is generated from.

It answers "is the layout intact", not "is any given script correct". Exits
non-zero when a check fails, so it is usable from a build.
"""

import os.path
import sys

# realpath so this works when run through the symlink in ~/.local/bin
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import test_mod  # pylint: disable=wrong-import-position


def main() -> int:
    failed = 0
    for title, check in test_mod.CHECKS:
        problems = check()
        if problems:
            failed += 1
            print(f"FAIL {title}")
            for problem in problems:
                print(f"       {problem}")
        else:
            print(f"ok   {title}")
    if failed:
        print(f"\n{failed} of {len(test_mod.CHECKS)} checks failed", file=sys.stderr)
        return 1
    print(f"\nall {len(test_mod.CHECKS)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
