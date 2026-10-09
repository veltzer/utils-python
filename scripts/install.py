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


def unlink_stale(target_folder: str, source_folder: str, doit: bool, debug: bool) -> int:
    """remove dead links in target_folder which point back into source_folder

    Live links are left in place; do_install checks each one and only touches
    those that are wrong, so repeated runs are quiet no-ops.
    """
    removed = 0
    if not os.path.isdir(target_folder):
        return 0
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
        removed += 1
    return removed


def do_install(source: str, target: str, doit: bool, debug: bool) -> str:
    """install a single symlink, replacing whatever link is already there"""
    replaced = False
    if os.path.islink(target):
        if os.readlink(target) == source:
            return "unchanged"
        if debug:
            print(f"unlinking [{target}]")
        if doit:
            os.unlink(target)
        replaced = True
    elif os.path.exists(target):
        print(f"not a symlink, leaving alone [{target}]", file=sys.stderr)
        return "skipped"

    if debug:
        print(f"symlinking [{source}] -> [{target}]")
    if doit:
        os.symlink(source, target)
    return "replaced" if replaced else "created"


def install(source_folder: str, target_folder: str, want_dirs: bool, doit: bool, debug: bool) -> dict:
    """symlink entries of source_folder into target_folder

    want_dirs selects which kind of entry to install: the directories in
    src are packages, the files are scripts.
    """
    stats = {"removed_stale": 0, "created": 0, "replaced": 0, "unchanged": 0, "skipped": 0}
    source_folder = os.path.abspath(os.path.expanduser(source_folder))
    target_folder = os.path.abspath(os.path.expanduser(target_folder))
    if not os.path.isdir(source_folder):
        print(f"no such source folder [{source_folder}]", file=sys.stderr)
        sys.exit(1)
    stats["removed_stale"] = unlink_stale(target_folder, source_folder, doit, debug)
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
        res = do_install(source, os.path.join(target_folder, entry), doit, debug)
        stats[res] += 1
    return stats


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
    stats_scripts = install(args.source_scripts, args.target_scripts, False, doit, debug)
    stats_packages = install(args.source_packages, args.target_packages, True, doit, debug)
    
    total_stats = {k: stats_scripts[k] + stats_packages.get(k, 0) for k in stats_scripts}
    
    print("\n--- Installation Statistics ---")
    print(f"removed [{total_stats['removed_stale']}] stale symlinks")
    print(f"created [{total_stats['created']}] new symlinks")
    print(f"replaced [{total_stats['replaced']}] existing symlinks")
    print(f"left alone [{total_stats['unchanged']}] already correct symlinks")
    if total_stats["skipped"] > 0:
        print(f"skipped [{total_stats['skipped']}] paths that exist but are not symlinks")


if __name__ == "__main__":
    main()
