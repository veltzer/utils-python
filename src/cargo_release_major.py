#!/usr/bin/env python

"""
Bump the major version, commit, publish to crates.io, tag and push, all in
one go (cargo-release does the work; see release.toml in the repo).

cargo-release is a separate crate, not part of the toolchain, so a rebuilt
CARGO_HOME loses it. Check for it up front.

The crates.io token lives in pass(1) only, under keys/crates.io, so there is
no ~/.cargo/credentials file for cargo to fall back on. cargo-release runs
"cargo publish" as a child process, which reads the token from
CARGO_REGISTRY_TOKEN; hand it over through the environment of this one
process, so it never lands on disk.
"""

import os
import shutil
import subprocess
import sys


def main() -> None:
    if not shutil.which("cargo-release"):
        script_name = os.path.basename(sys.argv[0])
        print(
            f"{script_name}: cargo-release is not installed, run: cargo install cargo-release",
            file=sys.stderr,
        )
        sys.exit(1)

    res = subprocess.run(
        ["pass", "show", "keys/crates.io"], capture_output=True, text=True, check=False
    )
    if res.returncode != 0:
        print("Failed to get crates.io token from pass", file=sys.stderr)
        sys.exit(res.returncode)

    token = res.stdout.strip()

    env = os.environ.copy()
    env["CARGO_REGISTRY_TOKEN"] = token

    cargo_bin = shutil.which("cargo")
    if not cargo_bin:
        print("cargo is not installed", file=sys.stderr)
        sys.exit(1)

    os.execvpe(
        cargo_bin, ["cargo", "release", "major", "--execute", "--no-confirm"], env
    )


if __name__ == "__main__":
    main()
