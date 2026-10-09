#!/usr/bin/env python3

"""
This script backs up your /etc folder (where 90% of your configuration lives)
and the selection of packages you are using.
"""

import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path


def main() -> None:
    # this script should not be run as root since it needs the user name to change
    # the file ownership to
    if os.environ.get("USER") == "root" or os.geteuid() == 0:
        print("do not run me as root...", file=sys.stderr)
        sys.exit(1)

    home = Path.home()
    folder = home / "insync" / "backups" / "system"
    folder.mkdir(parents=True, exist_ok=True)

    hostname = socket.gethostname()
    tmp_etc = Path(f"/tmp/etc.{hostname}.tar.bz2")
    target_etc = folder / f"etc.{hostname}.tar.bz2"
    target_dpkg_selections = folder / f"dpkg_selections.{hostname}.txt"
    target_alternatives = folder / f"alternatives.{hostname}.txt"

    # We sudo since we are running as a regular user and cannot enter into some folders...
    # We do not create the final output file directly because it will
    # have root ownership and we want a file with the user's ownership.
    print(f"creating [{target_etc}]...")
    subprocess.run(["sudo", "tar", "--create", "--bzip2", "--absolute-names", "--file", str(tmp_etc), "/etc"], check=True)
    
    shutil.copy(str(tmp_etc), str(target_etc))
    subprocess.run(["sudo", "rm", str(tmp_etc)], check=True)

    # These steps can be done by any user
    print(f"creating [{target_dpkg_selections}]...")
    with open(target_dpkg_selections, "w", encoding="utf-8") as f:
        subprocess.run(["dpkg", "--get-selections"], stdout=f, check=True)

    print(f"creating [{target_alternatives}]...")
    with open(target_alternatives, "w", encoding="utf-8") as f:
        # Note: Fixed a bug from the original bash script where it redirected to dpkg_selections
        subprocess.run(["update-alternatives", "--get-selections"], stdout=f, check=True)


if __name__ == "__main__":
    main()
