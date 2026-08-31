#!/usr/bin/env python

"""
Install this repo into the user account using symlinks.

Everything lives under "src": the .py files there are standalone scripts and
the directories there are support packages they import. The scripts become
commands in ~/.local/bin and the packages become importable packages in the
user site-packages folder, both as symlinks back into the git checkout, so
editing a file here changes the installed version immediately.

Dead symlinks in the target folders that point back into this checkout are
removed first, so files deleted from the repo do not linger as dead links.
Links that are already correct are left untouched, so a rerun only reports
what actually changed.
"""

import argparse
import os
import os.path
import site
import sys


def unlink_stale(target_folder: str, source_folder: str, doit: bool, debug: bool) -> None:
    """remove dead links in target_folder which point back into source_folder

    Live links are left in place; do_install checks each one and only touches
    those that are wrong, so repeated runs are quiet no-ops.
    """
    if not os.path.isdir(target_folder):
        return
    for filename in os.listdir(target_folder):
        full = os.path.join(target_folder, filename)
        if not os.path.islink(full):
            continue
        if not os.path.realpath(full).startswith(source_folder):
            continue
        if os.path.exists(full):
            continue
        if debug:
            print(f"unlinking [{full}]")
        if doit:
            os.unlink(full)


def do_install(source: str, target: str, doit: bool, debug: bool) -> None:
    """install a single symlink, replacing whatever link is already there"""
    if os.path.islink(target):
        if os.readlink(target) == source:
            return
        if debug:
            print(f"unlinking [{target}]")
        if doit:
            os.unlink(target)
    if os.path.exists(target):
        print(f"not a symlink, leaving alone [{target}]", file=sys.stderr)
        return
    if debug:
        print(f"symlinking [{source}] -> [{target}]")
    if doit:
        os.symlink(source, target)


def install(source_folder: str, target_folder: str, want_dirs: bool, doit: bool, debug: bool) -> None:
    """symlink entries of source_folder into target_folder

    want_dirs selects which kind of entry to install: the directories in
    src are packages, the files are scripts.
    """
    source_folder = os.path.abspath(os.path.expanduser(source_folder))
    target_folder = os.path.abspath(os.path.expanduser(target_folder))
    if not os.path.isdir(source_folder):
        print(f"no such source folder [{source_folder}]", file=sys.stderr)
        sys.exit(1)
    unlink_stale(target_folder, source_folder, doit, debug)
    if not os.path.isdir(target_folder):
        if debug:
            print(f"mkdir [{target_folder}]")
        if doit:
            os.makedirs(target_folder)
    for entry in sorted(os.listdir(source_folder)):
        if entry in {"__init__.py", "__pycache__"}:
            continue
        source = os.path.join(source_folder, entry)
        if os.path.isdir(source) != want_dirs:
            continue
        do_install(source, os.path.join(target_folder, entry), doit, debug)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n", maxsplit=1)[0])
    parser.add_argument(
        "--source_scripts",
        default="src",
        help="folder of scripts to install as commands (default: %(default)s)",
    )
    parser.add_argument(
        "--target_scripts",
        default="~/.local/bin",
        help="folder to install the commands into (default: %(default)s)",
    )
    parser.add_argument(
        "--source_packages",
        default="src",
        help="folder of python packages to install (default: %(default)s)",
    )
    parser.add_argument(
        "--target_packages",
        default=site.getusersitepackages(),
        help="folder to install the packages into (default: %(default)s)",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="only show what would be done",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="do not print what is being done",
    )
    args = parser.parse_args()
    doit = not args.dry_run
    debug = not args.quiet
    install(args.source_scripts, args.target_scripts, False, doit, debug)
    install(args.source_packages, args.target_packages, True, doit, debug)


if __name__ == "__main__":
    main()
